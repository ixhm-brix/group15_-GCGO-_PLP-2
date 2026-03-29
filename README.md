# Student Grade Tracker  Group 15 (GCGO)

ALU Peer Learning Days — Python Project

---

## Overview

A command-line application for tracking and reporting student grades across cohorts, subjects, and grade categories. The system supports three distinct roles — **Head Teacher**, **Subject Teacher**, and **Student** — each with their own level of access.

Data is persisted in a **MySQL database hosted on Aiven** (a managed cloud service), replacing local file storage.

---

## Features

- Role-based login with password authentication (3-attempt limit)
- Manage multiple cohorts (class groups) independently
- Add students and log grades per subject and category
- Configurable grade categories with percentage weights (e.g. Exam 40%, Midterm 30%, CA 30%)
- Weighted average calculations per subject and overall
- Letter grade (A–F) and GPA (4.0 scale) conversion
- Per-student report views: Continuous Assessment, Midterm, Exam, or Full Combined
- Class overview table showing all students across all subjects
- Export student reports to `.txt` files
- Head Teacher can manage subject teachers (add / remove)

---

## User Roles

| Role | What they can do |
|------|-----------------|
| **Head Teacher** | Full access: create cohorts, add students, log grades for any subject, manage teachers and grade categories, view any class overview |
| **Subject Teacher** | Restricted to their assigned subject: add students, log and view grades only for their subject, view class overview filtered to their subject |
| **Student** | Read-only: view their own grade reports by entering their Student ID (no password required) |

---

## Grading Scale

| Score | Letter | GPA |
|-------|--------|-----|
| 90–100 | A | 4.0 |
| 80–89  | B | 3.0 |
| 70–79  | C | 2.0 |
| 60–69  | D | 1.0 |
| 0–59   | F | 0.0 |

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd group15_-GCGO-_PLP-2
```

### 2. Install dependencies

```bash
pip install mysql-connector-python python-dotenv
```

### 3. Create a `.env` file

In the project root, create a file named `.env` with your Aiven credentials:

```
DB_HOST=your-aiven-host
DB_PORT=your-aiven-port
DB_USER=your-aiven-username
DB_PASSWORD=your-aiven-password
DB_NAME=your-aiven-database
DB_SSL=true
ADMIN_PASSWORD=your-head-teacher-password
```

You can find the database values in your Aiven console under **Services → your MySQL service → Connection info**.

> **Important:** `.env` is listed in `.gitignore` and must **never** be committed.
> If `ADMIN_PASSWORD` is not set, the default head teacher password is `admin123`.

### 4. Create the database tables

```bash
python setup_db.py
```

Safe to run multiple times — uses `IF NOT EXISTS` so it never overwrites existing data.
Tables are also created automatically on first run of the main app.

### 5. Run the app

```bash
python main.py
```

---

## Usage

On startup you are asked to select your role:

```
============================================
  Who are you?
============================================
  1.  Head Teacher
  2.  Subject Teacher
  3.  Student  (view my grades)
  4.  Exit
```

### Head Teacher

After entering the admin password you can:

1. **Select / Create a cohort** — then add students, log grades for any subject, view reports
2. **Manage subject teachers** — add or remove teacher accounts
3. **Manage grade categories** — add/remove categories and set their percentage weights
4. **Save all data** — persists everything to the database

### Subject Teacher

After entering your password you are identified automatically and locked to your assigned subject. You can:

- Select an existing cohort (cannot create new ones)
- Add students to the cohort
- Log grades for your subject only
- View per-student reports and a class overview filtered to your subject

### Student

Enter your Student ID (no password needed) to view:

- Continuous Assessment breakdown
- Midterm scores
- Exam scores
- Full Combined Report (weighted average, letter grade, GPA)

You can also export your report to a `.txt` file.

---

## Database Tables

| Table        | What it stores |
|--------------|----------------|
| `cohorts`    | Cohort names |
| `students`   | Student ID, full name, and cohort |
| `categories` | Grade category names and percentage weights |
| `grades`     | Individual scores linked by student, cohort, subject, and category |
| `teachers`   | Subject teacher accounts (name, username, hashed password, subject) |

---

## Project Files

| File                | Purpose |
|---------------------|---------|
| `main.py`           | Entry point  runs the interactive menu and all user flows |
| `auth.py`           | Password login for Head Teacher and Subject Teachers |
| `storage.py`        | Reads and writes all data to Aiven MySQL |
| `setup_db.py`       | Creates database tables if they do not exist |
| `student.py`        | `Student` class  holds grades and validates IDs |
| `cohort.py`         | `Cohort` class  groups students together |
| `grade.py`          | `GradeCategory` and `CategoryManager` : define and weight categories |
| `calculator.py`     | Weighted averages, letter grades, and GPA calculations |
| `reports.py`        | All report views and the class overview table |
| `populate_sample.py`| Script to insert sample data for testing |
| `.env`              | **Your credentials  never commit this file** |
| `.gitignore`        | Excludes `.env` and other generated files from Git |
