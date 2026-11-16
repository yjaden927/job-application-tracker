# app.py
import json
import os
import re
from datetime import date, datetime
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

# Importing from the custom database.py file
from database import execute, fetch_all, fetch_one

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-dev-key")

# Dropdown options 
JOB_TYPES = ["Full-time", "Part-time", "Contract", "Internship"]
STATUSES = ["Applied", "Screening", "Interview", "Offer", "Rejected", "Withdrawn"]
INTERVIEW_TYPES = ["Phone", "Video", "Onsite", "Technical", "Other"]

# =====================================================
# Basic Helper Functions
# =====================================================

def clean_input(val):
    """Simple helper to strip spaces and turn empty strings into None for the DB"""
    if not val or val.strip() == "":
        return None
    return val.strip()

def parse_db_json(val):
    """Fixes how MySQL returns JSON so Python can read it properly"""
    if not val:
        return None
    # sometimes it's already a list/dict, sometimes it's a string or bytes
    if type(val) is dict or type(val) is list:
        return val
    if type(val) is bytes:
        val = val.decode("utf-8")
    try:
        return json.loads(val)
    except:
        return None

def get_skills_list(skills_string):
    """Takes a comma separated string and returns a list of unique skills"""
    if not skills_string:
        return []
    
    skills_list = []
    # split by comma and remove spaces
    for s in skills_string.split(","):
        clean_skill = s.strip()
        # avoid duplicates (case insensitive) and empty strings
        if clean_skill != "":
            lower_skills = [x.lower() for x in skills_list]
            if clean_skill.lower() not in lower_skills:
                skills_list.append(clean_skill)
    return skills_list

# =====================================================
# Dashboard Route
# =====================================================

@app.route("/")
def dashboard():
    # Get total counts for the cards
    counts = fetch_one("""
        SELECT
            (SELECT COUNT(*) FROM companies) AS companies,
            (SELECT COUNT(*) FROM jobs) AS jobs,
            (SELECT COUNT(*) FROM applications) AS applications,
            (SELECT COUNT(*) FROM contacts) AS contacts
    """)

    # Figure out the application statuses for the chart/stats
    status_rows = fetch_all("SELECT status, COUNT(*) AS total FROM applications GROUP BY status")
    
    # Initialize all statuses to 0 first
    by_status = {s: 0 for s in STATUSES}
    for row in status_rows:
        by_status[row["status"]] = row["total"]

    # Calculate response rate (anything not "Applied")
    total_apps = counts["applications"]
    responded = total_apps - by_status["Applied"]
    
    if total_apps > 0:
        response_rate = int(round((responded / total_apps) * 100))
    else:
        response_rate = 0

    # Get recent apps for the table
    recent_apps = fetch_all("""
        SELECT a.application_id, a.application_date, a.status,
               j.job_title, c.company_name
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        JOIN companies c ON j.company_id = c.company_id
        ORDER BY a.application_date DESC
        LIMIT 5
    """)

    return render_template(
        "dashboard.html",
        counts=counts,
        by_status=by_status,
        response_rate=response_rate,
        recent=recent_apps,
    )

# =====================================================
# Companies CRUD
# =====================================================

@app.route("/companies")
def companies():
    # Get all companies and count how many jobs/contacts they have
    sql = """
        SELECT c.*,
               (SELECT COUNT(*) FROM jobs WHERE company_id = c.company_id) as job_count,
               (SELECT COUNT(*) FROM contacts WHERE company_id = c.company_id) as contact_count
        FROM companies c
        ORDER BY c.company_name
    """
    all_comps = fetch_all(sql)
    return render_template("companies.html", companies=all_comps)

@app.route("/companies/<int:company_id>")
def company_detail(company_id):
    company = fetch_one("SELECT * FROM companies WHERE company_id = %s", (company_id,))
    if not company:
        flash("That company doesn't exist.", "danger")
        return redirect(url_for("companies"))
    
    jobs = fetch_all("SELECT * FROM jobs WHERE company_id = %s", (company_id,))
    contacts = fetch_all("SELECT * FROM contacts WHERE company_id = %s", (company_id,))
    
    return render_template("company_detail.html", company=company, jobs=jobs, contacts=contacts)

@app.route("/companies/add", methods=["GET", "POST"])
def add_company():
    if request.method == "POST":
        name = clean_input(request.form.get("company_name"))
        industry = clean_input(request.form.get("industry"))
        website = clean_input(request.form.get("website"))
        city = clean_input(request.form.get("city"))
        state = clean_input(request.form.get("state"))
        notes = clean_input(request.form.get("notes"))

        errors = []
        if not name:
            errors.append("Company name is required.")
        if website and not website.startswith("http"):
            errors.append("Website must start with http:// or https://")

        if len(errors) > 0:
            for err in errors:
                flash(err, "danger")
            return render_template("company_form.html", company=request.form, action="Add")

        execute("""
            INSERT INTO companies (company_name, industry, website, city, state, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, industry, website, city, state, notes))
        
        flash("Company added!", "success")
        return redirect(url_for("companies"))

    return render_template("company_form.html", company={}, action="Add")

@app.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
def edit_company(company_id):
    company = fetch_one("SELECT * FROM companies WHERE company_id = %s", (company_id,))
    
    if request.method == "POST":
        name = clean_input(request.form.get("company_name"))
        industry = clean_input(request.form.get("industry"))
        website = clean_input(request.form.get("website"))
        city = clean_input(request.form.get("city"))
        state = clean_input(request.form.get("state"))
        notes = clean_input(request.form.get("notes"))

        if not name:
            flash("Company name is required.", "danger")
            # pass the id back so the form doesn't break
            form_data = dict(request.form)
            form_data["company_id"] = company_id
            return render_template("company_form.html", company=form_data, action="Edit")

        execute("""
            UPDATE companies
            SET company_name = %s, industry = %s, website = %s,
                city = %s, state = %s, notes = %s
            WHERE company_id = %s
        """, (name, industry, website, city, state, notes, company_id))
        
        flash("Company updated successfully.", "success")
        return redirect(url_for("companies"))

    return render_template("company_form.html", company=company, action="Edit")

@app.route("/companies/<int:company_id>/delete", methods=["POST"])
def delete_company(company_id):
    execute("DELETE FROM companies WHERE company_id = %s", (company_id,))
    flash("Company deleted.", "success")
    return redirect(url_for("companies"))

# =====================================================
# Jobs CRUD
# =====================================================

@app.route("/jobs")
def jobs():
    sql = """
        SELECT j.*, c.company_name
        FROM jobs j
        JOIN companies c ON j.company_id = c.company_id
        ORDER BY j.date_posted DESC
    """
    all_jobs = fetch_all(sql)
    
    # parse the JSON skills for the UI
    for j in all_jobs:
        j["skills"] = parse_db_json(j["requirements"]) or []
        
    return render_template("jobs.html", jobs=all_jobs)

@app.route("/jobs/<int:job_id>")
def job_detail(job_id):
    job = fetch_one("""
        SELECT j.*, c.company_name
        FROM jobs j
        JOIN companies c ON j.company_id = c.company_id
        WHERE j.job_id = %s
    """, (job_id,))
    
    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for("jobs"))
        
    job["skills"] = parse_db_json(job["requirements"]) or []
    apps = fetch_all("SELECT * FROM applications WHERE job_id = %s", (job_id,))
    
    return render_template("job_detail.html", job=job, applications=apps)

@app.route("/jobs/add", methods=["GET", "POST"])
def add_job():
    companies = fetch_all("SELECT company_id, company_name FROM companies ORDER BY company_name")
    
    if request.method == "POST":
        comp_id = clean_input(request.form.get("company_id"))
        title = clean_input(request.form.get("job_title"))
        j_type = clean_input(request.form.get("job_type"))
        min_sal = clean_input(request.form.get("salary_min"))
        max_sal = clean_input(request.form.get("salary_max"))
        url = clean_input(request.form.get("job_url"))
        posted = clean_input(request.form.get("date_posted"))
        reqs_str = clean_input(request.form.get("requirements"))

        errors = []
        if not title:
            errors.append("Job title is required.")
        if not comp_id:
            errors.append("You must select a company.")
            
        # check salaries
        if min_sal and max_sal:
            try:
                if int(min_sal) > int(max_sal):
                    errors.append("Min salary can't be bigger than max salary.")
            except ValueError:
                errors.append("Salaries must be numbers.")

        skills_list = get_skills_list(reqs_str)
        if not skills_list:
            errors.append("You need to enter at least one skill requirement.")
            
        if len(errors) > 0:
            for err in errors:
                flash(err, "danger")
            return render_template("job_form.html", job=request.form, action="Add", 
                                   companies=companies, job_types=JOB_TYPES)

        # save skills as json string in db
        skills_json = json.dumps(skills_list)

        execute("""
            INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
                              job_url, date_posted, requirements)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (comp_id, title, j_type, min_sal, max_sal, url, posted, skills_json))
        
        flash("Job added!", "success")
        return redirect(url_for("jobs"))

    # if GET, handle auto-selecting company if coming from company page
    prefill = {"company_id": request.args.get("company_id")}
    return render_template("job_form.html", job=prefill, action="Add", 
                           companies=companies, job_types=JOB_TYPES)

@app.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def edit_job(job_id):
    job = fetch_one("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
    companies = fetch_all("SELECT company_id, company_name FROM companies ORDER BY company_name")

    if request.method == "POST":
        comp_id = clean_input(request.form.get("company_id"))
        title = clean_input(request.form.get("job_title"))
        j_type = clean_input(request.form.get("job_type"))
        min_sal = clean_input(request.form.get("salary_min"))
        max_sal = clean_input(request.form.get("salary_max"))
        url = clean_input(request.form.get("job_url"))
        posted = clean_input(request.form.get("date_posted"))
        reqs_str = clean_input(request.form.get("requirements"))

        errors = []
        if not title:
            errors.append("Job title is required.")
        if not comp_id:
            errors.append("You must select a company.")

        # check salaries
        if min_sal and max_sal:
            try:
                if int(min_sal) > int(max_sal):
                    errors.append("Min salary can't be bigger than max salary.")
            except ValueError:
                errors.append("Salaries must be numbers.")

        skills_list = get_skills_list(reqs_str)
        if not skills_list:
            errors.append("You need to enter at least one skill requirement.")

        if len(errors) > 0:
            for err in errors:
                flash(err, "danger")
            form_data = dict(request.form)
            form_data["job_id"] = job_id
            return render_template("job_form.html", job=form_data, action="Edit",
                                   companies=companies, job_types=JOB_TYPES)

        skills_json = json.dumps(skills_list)

        execute("""
            UPDATE jobs
            SET company_id = %s, job_title = %s, job_type = %s, salary_min = %s,
                salary_max = %s, job_url = %s, date_posted = %s, requirements = %s
            WHERE job_id = %s
        """, (comp_id, title, j_type, min_sal, max_sal, url, posted, skills_json, job_id))
        
        flash("Job updated!", "success")
        return redirect(url_for("jobs"))

    # convert the JSON skills back to a comma string for the edit text box
    existing_skills = parse_db_json(job["requirements"])
    if existing_skills:
        job["requirements"] = ", ".join(existing_skills)
        
    return render_template("job_form.html", job=job, action="Edit", 
                           companies=companies, job_types=JOB_TYPES)

@app.route("/jobs/<int:job_id>/delete", methods=["POST"])
def delete_job(job_id):
    execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))
    flash("Job deleted.", "success")
    return redirect(url_for("jobs"))


# =====================================================
# Applications CRUD
# =====================================================

@app.route("/applications")
def applications():
    # allow filtering by status in the URL query string
    filter_val = request.args.get("status")
    
    sql = """
        SELECT a.*, j.job_title, c.company_name
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        JOIN companies c ON j.company_id = c.company_id
    """
    params = ()
    
    if filter_val in STATUSES:
        sql += " WHERE a.status = %s"
        params = (filter_val,)
        
    sql += " ORDER BY a.application_date DESC"
    
    apps = fetch_all(sql, params)
    
    for a in apps:
        a["interview"] = parse_db_json(a["interview_data"]) or {}
        
    return render_template("applications.html", applications=apps, 
                           statuses=STATUSES, status_filter=filter_val)

@app.route("/applications/add", methods=["GET", "POST"])
def add_application():
    # get jobs for the dropdown menu
    jobs_list = fetch_all("""
        SELECT j.job_id, j.job_title, c.company_name 
        FROM jobs j JOIN companies c ON j.company_id = c.company_id
    """)

    if request.method == "POST":
        job_id = clean_input(request.form.get("job_id"))
        app_date = clean_input(request.form.get("application_date"))
        status = clean_input(request.form.get("status"))
        resume = clean_input(request.form.get("resume_version"))
        cl_sent = True if request.form.get("cover_letter_sent") == "on" else False
        
        # Interview fields
        i_date = clean_input(request.form.get("interview_date"))
        i_type = clean_input(request.form.get("interview_type"))
        i_person = clean_input(request.form.get("interviewer"))
        i_notes = clean_input(request.form.get("interview_notes"))

        errors = []
        if not job_id:
            errors.append("You must select a job.")
        if not app_date:
            errors.append("Application date is required.")
            
        if len(errors) > 0:
            for err in errors:
                flash(err, "danger")
            return render_template("application_form.html", application=request.form, 
                                   action="Add", jobs=jobs_list, statuses=STATUSES, 
                                   interview_types=INTERVIEW_TYPES)

        # pack interview stuff into a json object
        interview_dict = {}
        if i_date: interview_dict["date"] = i_date
        if i_type: interview_dict["type"] = i_type
        if i_person: interview_dict["interviewer"] = i_person
        if i_notes: interview_dict["notes"] = i_notes
        
        interview_json = json.dumps(interview_dict) if interview_dict else None

        execute("""
            INSERT INTO applications (job_id, application_date, status, resume_version,
                                      cover_letter_sent, interview_data)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (job_id, app_date, status, resume, cl_sent, interview_json))
        
        flash("Application tracked!", "success")
        return redirect(url_for("applications"))

    # set default date to today to save time filling out the form
    defaults = {
        "job_id": request.args.get("job_id"),
        "application_date": date.today().isoformat(),
        "status": "Applied"
    }
    return render_template("application_form.html", application=defaults, action="Add",
                           jobs=jobs_list, statuses=STATUSES, interview_types=INTERVIEW_TYPES)

@app.route("/applications/<int:app_id>/edit", methods=["GET", "POST"])
def edit_application(app_id):
    app_data = fetch_one("SELECT * FROM applications WHERE application_id = %s", (app_id,))
    jobs_list = fetch_all("""
        SELECT j.job_id, j.job_title, c.company_name 
        FROM jobs j JOIN companies c ON j.company_id = c.company_id
    """)

    if request.method == "POST":
        job_id = clean_input(request.form.get("job_id"))
        app_date = clean_input(request.form.get("application_date"))
        status = clean_input(request.form.get("status"))
        resume = clean_input(request.form.get("resume_version"))
        cl_sent = True if request.form.get("cover_letter_sent") == "on" else False
        
        i_date = clean_input(request.form.get("interview_date"))
        i_type = clean_input(request.form.get("interview_type"))
        i_person = clean_input(request.form.get("interviewer"))
        i_notes = clean_input(request.form.get("interview_notes"))

        if not app_date:
            flash("Date is required", "danger")
            return redirect(url_for("edit_application", app_id=app_id))

        interview_dict = {}
        if i_date: interview_dict["date"] = i_date
        if i_type: interview_dict["type"] = i_type
        if i_person: interview_dict["interviewer"] = i_person
        if i_notes: interview_dict["notes"] = i_notes
        
        interview_json = json.dumps(interview_dict) if interview_dict else None

        execute("""
            UPDATE applications
            SET job_id = %s, application_date = %s, status = %s, resume_version = %s,
                cover_letter_sent = %s, interview_data = %s
            WHERE application_id = %s
        """, (job_id, app_date, status, resume, cl_sent, interview_json, app_id))
        
        flash("Application updated.", "success")
        return redirect(url_for("applications"))

    # unpack the json so it displays in the separate form inputs
    interview_info = parse_db_json(app_data["interview_data"]) or {}
    app_data["interview_date"] = interview_info.get("date")
    app_data["interview_type"] = interview_info.get("type")
    app_data["interviewer"] = interview_info.get("interviewer")
    app_data["interview_notes"] = interview_info.get("notes")
    
    return render_template("application_form.html", application=app_data, action="Edit",
                           jobs=jobs_list, statuses=STATUSES, interview_types=INTERVIEW_TYPES)

@app.route("/applications/<int:app_id>/delete", methods=["POST"])
def delete_application(app_id):
    execute("DELETE FROM applications WHERE application_id = %s", (app_id,))
    flash("Application deleted.", "success")
    return redirect(url_for("applications"))

# =====================================================
# Contacts CRUD
# =====================================================

@app.route("/contacts")
def contacts():
    sql = """
        SELECT k.*, c.company_name
        FROM contacts k
        JOIN companies c ON k.company_id = c.company_id
        ORDER BY k.contact_name
    """
    rows = fetch_all(sql)
    return render_template("contacts.html", contacts=rows)

@app.route("/contacts/add", methods=["GET", "POST"])
def add_contact():
    companies = fetch_all("SELECT company_id, company_name FROM companies ORDER BY company_name")
    
    if request.method == "POST":
        comp_id = clean_input(request.form.get("company_id"))
        name = clean_input(request.form.get("contact_name"))
        title = clean_input(request.form.get("title"))
        email = clean_input(request.form.get("email"))
        phone = clean_input(request.form.get("phone"))
        link = clean_input(request.form.get("linkedin_url"))
        notes = clean_input(request.form.get("notes"))

        if not name or not comp_id:
            flash("Name and Company are required.", "danger")
            return render_template("contact_form.html", contact=request.form, action="Add", companies=companies)

        execute("""
            INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (comp_id, name, title, email, phone, link, notes))
        
        flash("Contact saved!", "success")
        return redirect(url_for("contacts"))

    prefill = {"company_id": request.args.get("company_id")}
    return render_template("contact_form.html", contact=prefill, action="Add", companies=companies)

@app.route("/contacts/<int:contact_id>/edit", methods=["GET", "POST"])
def edit_contact(contact_id):
    contact = fetch_one("SELECT * FROM contacts WHERE contact_id = %s", (contact_id,))
    companies = fetch_all("SELECT company_id, company_name FROM companies ORDER BY company_name")

    if request.method == "POST":
        comp_id = clean_input(request.form.get("company_id"))
        name = clean_input(request.form.get("contact_name"))
        title = clean_input(request.form.get("title"))
        email = clean_input(request.form.get("email"))
        phone = clean_input(request.form.get("phone"))
        link = clean_input(request.form.get("linkedin_url"))
        notes = clean_input(request.form.get("notes"))

        execute("""
            UPDATE contacts
            SET company_id = %s, contact_name = %s, title = %s, email = %s,
                phone = %s, linkedin_url = %s, notes = %s
            WHERE contact_id = %s
        """, (comp_id, name, title, email, phone, link, notes, contact_id))
        
        flash("Contact updated.", "success")
        return redirect(url_for("contacts"))
        
    return render_template("contact_form.html", contact=contact, action="Edit", companies=companies)

@app.route("/contacts/<int:contact_id>/delete", methods=["POST"])
def delete_contact(contact_id):
    execute("DELETE FROM contacts WHERE contact_id = %s", (contact_id,))
    flash("Contact deleted.", "success")
    return redirect(url_for("contacts"))

# =====================================================
# Job Match Algorithm
# =====================================================

@app.route("/job-match", methods=["GET", "POST"])
def job_match():
    user_skills_raw = ""
    results = None
    
    if request.method == "POST":
        user_skills_raw = request.form.get("skills", "")
        my_skills = get_skills_list(user_skills_raw)
        
        if len(my_skills) == 0:
            flash("Enter at least one skill to match.", "warning")
        else:
            # lower everything for comparison so 'Python' matches 'python'
            my_skills_lower = [s.lower() for s in my_skills]
            
            all_jobs = fetch_all("""
                SELECT j.job_id, j.job_title, j.job_type, j.requirements, c.company_name
                FROM jobs j
                JOIN companies c ON j.company_id = c.company_id
            """)
            
            results = []
            for j in all_jobs:
                job_reqs = parse_db_json(j["requirements"])
                if not job_reqs:
                    continue # skip jobs that have no requirements to match against
                    
                matched = []
                missing = []
                
                for req in job_reqs:
                    if req.lower() in my_skills_lower:
                        matched.append(req)
                    else:
                        missing.append(req)
                        
                # calculate score
                total_reqs = len(job_reqs)
                if len(matched) > 0:
                    score = int(round((len(matched) / total_reqs) * 100))
                    
                    results.append({
                        "job_id": j["job_id"],
                        "job_title": j["job_title"],
                        "company_name": j["company_name"],
                        "matched": matched,
                        "missing": missing,
                        "total": total_reqs,
                        "percent": score
                    })
            
            # sort highest match percentage first
            # if percentages tie, sort by number of matches, then alphabetically
            results.sort(key=lambda r: (-r["percent"], -len(r["matched"]), r["job_title"]))
            
    return render_template("job_match.html", skills_text=user_skills_raw, results=results)


if __name__ == "__main__":
    app.run(debug=True)