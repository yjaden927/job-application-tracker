-- =====================================================
-- Job Application Tracker - Database Schema
-- Run this whole file to (re)create the database.
-- WARNING: it drops and recreates every table.
-- =====================================================

CREATE DATABASE IF NOT EXISTS job_tracker;
USE job_tracker;

-- Drop child tables first so the foreign keys don't block the drops
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS contacts;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS companies;

-- -----------------------------------------------------
-- companies
-- -----------------------------------------------------
CREATE TABLE companies (
    company_id   INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(100) NOT NULL,
    industry     VARCHAR(50),
    website      VARCHAR(200),
    city         VARCHAR(50),
    state        VARCHAR(50),
    notes        TEXT
);

-- -----------------------------------------------------
-- jobs  (requirements = JSON array of skills)
-- -----------------------------------------------------
CREATE TABLE jobs (
    job_id       INT PRIMARY KEY AUTO_INCREMENT,
    company_id   INT,
    job_title    VARCHAR(100) NOT NULL,
    job_type     ENUM('Full-time','Part-time','Contract','Internship'),
    salary_min   INT,
    salary_max   INT,
    job_url      VARCHAR(300),
    date_posted  DATE,
    requirements JSON,
    CONSTRAINT fk_jobs_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE CASCADE,
    CONSTRAINT chk_salary_range
        CHECK (salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max)
);

-- -----------------------------------------------------
-- applications  (interview_data = JSON object)
-- -----------------------------------------------------
CREATE TABLE applications (
    application_id    INT PRIMARY KEY AUTO_INCREMENT,
    job_id            INT,
    application_date  DATE NOT NULL,
    status            ENUM('Applied','Screening','Interview','Offer','Rejected','Withdrawn')
                      DEFAULT 'Applied',
    resume_version    VARCHAR(50),
    cover_letter_sent BOOLEAN DEFAULT FALSE,
    interview_data    JSON,
    CONSTRAINT fk_applications_job
        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        ON DELETE CASCADE
);

-- -----------------------------------------------------
-- contacts
-- -----------------------------------------------------
CREATE TABLE contacts (
    contact_id   INT PRIMARY KEY AUTO_INCREMENT,
    company_id   INT,
    contact_name VARCHAR(100) NOT NULL,
    title        VARCHAR(100),
    email        VARCHAR(100),
    phone        VARCHAR(20),
    linkedin_url VARCHAR(200),
    notes        TEXT,
    CONSTRAINT fk_contacts_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE CASCADE
);

-- =====================================================
-- Sample data
-- =====================================================
INSERT INTO companies (company_name, industry, website, city, state, notes) VALUES
('TechCorp',     'Software',      'https://techcorp.example.com',     'Miami',    'FL', 'Fast-growing SaaS company'),
('DataCo',       'Analytics',     'https://dataco.example.com',       'Orlando',  'FL', 'Heavy on BI and dashboards'),
('CloudNine',    'Cloud',         'https://cloudnine.example.com',    'Austin',   'TX', 'Remote-friendly'),
('HealthBridge', 'Healthcare IT', 'https://healthbridge.example.com', 'Tampa',    'FL', 'EHR integrations'),
('FinEdge',      'FinTech',       'https://finedge.example.com',      'New York', 'NY', 'Payments platform');

INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements) VALUES
(1, 'Software Developer',          'Full-time',  75000, 95000,  'https://techcorp.example.com/jobs/1',      '2026-10-01', '["Python", "SQL", "Flask"]'),
(1, 'Software Engineering Intern', 'Internship', 40000, 50000,  'https://techcorp.example.com/jobs/2',      '2026-10-10', '["Python", "Git"]'),
(2, 'Data Analyst',                'Full-time',  65000, 80000,  'https://dataco.example.com/careers/7',     '2026-09-25', '["Python", "SQL", "Tableau"]'),
(3, 'Cloud Engineer',              'Full-time',  90000, 120000, 'https://cloudnine.example.com/jobs/cloud', '2026-10-05', '["AWS", "Docker", "Linux", "Python"]'),
(4, 'Backend Developer',           'Contract',   60000, 80000,  'https://healthbridge.example.com/jobs/3',  '2026-10-12', '["Java", "SQL", "REST APIs"]'),
(5, 'Full Stack Developer',        'Full-time',  85000, 110000, 'https://finedge.example.com/jobs/fs',      '2026-10-15', '["JavaScript", "React", "Python", "SQL"]'),
(2, 'BI Developer',                'Part-time',  30000, 40000,  'https://dataco.example.com/careers/9',     '2026-10-20', '["SQL", "Power BI", "Excel"]');

INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent, interview_data) VALUES
(1, '2026-10-03', 'Interview', 'v2-software', TRUE,
    '{"date": "2026-10-20", "type": "Video", "interviewer": "Maria Lopez", "notes": "Technical round, asked about SQL joins"}'),
(2, '2026-10-12', 'Applied',   'v2-software', FALSE, NULL),
(3, '2026-09-28', 'Screening', 'v1-data',     TRUE,
    '{"date": "2026-10-08", "type": "Phone", "interviewer": "Recruiter", "notes": "30 min phone screen"}'),
(4, '2026-10-07', 'Rejected',  'v2-software', FALSE, NULL),
(6, '2026-10-16', 'Offer',     'v3-fullstack', TRUE,
    '{"date": "2026-10-28", "type": "Onsite", "interviewer": "James Chen", "notes": "Final round with team lead"}'),
(7, '2026-10-21', 'Withdrawn', 'v1-data',     FALSE, NULL);

INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes) VALUES
(1, 'Maria Lopez', 'Engineering Manager', 'maria@techcorp.example.com', '305-555-0101', 'https://linkedin.com/in/marialopez', 'Met at FIU career fair'),
(2, 'Sam Patel',   'Recruiter',           'sam@dataco.example.com',     '407-555-0144', 'https://linkedin.com/in/sampatel',   'Responds quickly by email'),
(5, 'James Chen',  'Tech Lead',           'james@finedge.example.com',  '212-555-0190', 'https://linkedin.com/in/jameschen',  'Referred me for the full stack role'),
(3, 'Ava Johnson', 'Talent Acquisition',  'ava@cloudnine.example.com',  '512-555-0122', NULL,                                 NULL);