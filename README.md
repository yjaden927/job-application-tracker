# Job Application Tracker

A full-stack web application for tracking job applications, built for COP 4751.
It stores companies, job postings, applications, and contacts in MySQL, serves
them through a Python/Flask backend, and includes a **Job Match** feature that
ranks jobs by how many of their required skills you have.

**Stack:** MySQL · Python 3 · Flask · HTML/CSS (Bootstrap 5 + custom design system) · Lucide icons

---

## Features

- **Dashboard** with totals, applications by status, response rate, and recent applications
- **Full CRUD** (create, read, update, delete) for all four tables, with server-side
  validation and a confirmation prompt before every delete
- **Companies, Jobs, Applications, Contacts** list pages, plus detail pages for
  companies and jobs
- **JSON columns:** `jobs.requirements` stores a skill list, `applications.interview_data`
  stores interview date, type, interviewer, and notes
- **Job Match:** enter your skills and see every job ranked by match percentage,
  with matched and missing skills listed
- **Light and dark mode**, saved per browser

---

## Requirements

- Python 3.10 or newer
- MySQL 8.0 or newer (MySQL Server running locally)
- Git

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yjaden927/job-application-tracker.git
cd job-application-tracker
```

### 2. Create the database

This creates the `job_tracker` database, all four tables, and sample data.
It drops and recreates the tables, so it is also how you reset the data.

```bash
mysql -u root -p < schema.sql
```

(Or open `schema.sql` in MySQL Workbench and run the whole script.)

### 3. Create a virtual environment and install dependencies

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Add your database credentials

Copy the example settings file, then open `.env` and set `DB_PASSWORD` to your
MySQL root password.

macOS / Linux:

```bash
cp .env.example .env
```

Windows:

```bash
copy .env.example .env
```

`.env` is listed in `.gitignore`, so your password is never committed.

### 5. Run the app

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## Project Structure

```
job-application-tracker/
├── app.py              # Flask app: routes, validation, Job Match algorithm
├── database.py         # MySQL connection and query helpers
├── schema.sql          # Creates the database, tables, and sample data
├── requirements.txt    # Python dependencies
├── .env.example        # Template for database credentials
├── templates/          # Jinja2 HTML templates
│   ├── base.html             # Shared layout, navigation, theme toggle
│   ├── dashboard.html
│   ├── companies.html        # + company_form.html, company_detail.html
│   ├── jobs.html             # + job_form.html, job_detail.html
│   ├── applications.html     # + application_form.html
│   ├── contacts.html         # + contact_form.html
│   └── job_match.html
├── static/
│   └── style.css       # Design system (OKLCH colors, light/dark themes)
├── AI_USAGE.md         # How AI tools were used in this project
└── README.md
```

---

## Database Design

| Table | Key columns | Relationships |
|---|---|---|
| `companies` | `company_id` (PK), `company_name`, `industry`, `website`, `city`, `state`, `notes` | Parent of `jobs` and `contacts` |
| `jobs` | `job_id` (PK), `company_id` (FK), `job_title`, `job_type` (ENUM), `salary_min`, `salary_max`, `job_url`, `date_posted`, `requirements` (**JSON**) | Belongs to a company; parent of `applications` |
| `applications` | `application_id` (PK), `job_id` (FK), `application_date`, `status` (ENUM), `resume_version`, `cover_letter_sent`, `interview_data` (**JSON**) | Belongs to a job |
| `contacts` | `contact_id` (PK), `company_id` (FK), `contact_name`, `title`, `email`, `phone`, `linkedin_url`, `notes` | Belongs to a company |

All foreign keys use `ON DELETE CASCADE`: deleting a company also deletes its
jobs, their applications, and its contacts. A `CHECK` constraint keeps
`salary_min <= salary_max`.

---

## Job Match Algorithm

1. The user's skills are split on commas, trimmed, and de-duplicated.
2. For every job, the `requirements` JSON array is compared to the user's skills
   (case-insensitive).
3. **Match % = required skills the user has ÷ total required skills × 100**
4. Jobs with at least one matching skill are shown, sorted by match % (highest
   first), then by number of matched skills, then by title.
5. Each result lists the matched skills and the missing ones.

Example with the sample data, skills `Python, SQL, Flask`:

```
1. Software Developer at TechCorp - 100% (3/3 skills)
2. Data Analyst at DataCo - 67% (2/3 skills)   Missing: Tableau
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Access denied for user 'root'@'localhost'` | The password in `.env` is wrong. |
| `Unknown database 'job_tracker'` | Run `mysql -u root -p < schema.sql`. |
| `Can't connect to MySQL server` | Start the MySQL server (macOS: System Settings → MySQL → Start). |
| `zsh: command not found: mysql` (macOS) | Use `/usr/local/mysql/bin/mysql`, or add that folder to your PATH. |
| `ModuleNotFoundError: No module named 'flask'` | Activate the virtual environment, then `pip install -r requirements.txt`. |

---

## Demo Video

See the recorded demo in this repository: `demo.mov`.
