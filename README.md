# Student Grade Tracker — Group 15 (GCGO)


ALU Peer Learning Days — Python Project


---


## Database Setup


This project uses **MySQL hosted on Aiven** (a managed cloud database service).
All student, cohort, category, and grade data is stored in the Aiven database instead of local CSV files.


### 1. Create a `.env` file


In the project root, create a file named `.env` with your Aiven credentials:


```
DB_HOST=your-aiven-host
DB_PORT=your-aiven-port
DB_USER=your-aiven-username
DB_PASSWORD=your-aiven-password
DB_NAME=your-aiven-database
DB_SSL=true
```


You can find these values in your Aiven console under **Services → your MySQL service → Connection info**.


> **Important:** `.env` is listed in `.gitignore` and must **never** be committed to GitHub.
> Credentials pushed to a public repository are a serious security risk.


### 2. Install dependencies


```bash
pip install mysql-connector-python python-dotenv
```


### 3. Create the database tables


Run this once to create all required tables on Aiven:


```bash
python setup_db.py
```


It is safe to run multiple times — every `CREATE TABLE` uses `IF NOT EXISTS`
so it will never overwrite existing data.


Tables are also created automatically when you run `python main.py`.


### 4. Run the app


```bash
python main.py
```


---


## Database Tables


| Table        | What it stores |
|--------------|----------------|
| `cohorts`    | The name of each cohort (class group) |
| `students`   | Each student's ID, full name, and which cohort they belong to |
| `categories` | Grade category names and their percentage weights (e.g. Exam = 40%) |
| `grades`     | Individual grade scores — linked by student ID, cohort, subject, and category |


---


## Project Files


| File            | Purpose |
|-----------------|---------|
| `main.py`       | Entry point — runs the interactive menu |
| `storage.py`    | Saves and loads all data to/from Aiven MySQL |
| `setup_db.py`   | Creates the database tables if they do not exist |
| `student.py`    | Student class |
| `cohort.py`     | Cohort class |
| `grade.py`      | GradeCategory and CategoryManager classes |
| `calculator.py` | Grade calculation logic |
| `reports.py`    | Report generation and display |
| `auth.py`       | Teacher login authentication |
| `.env`          | **Your credentials — never commit this file** |
| `.gitignore`    | Tells Git to ignore `.env` and other generated files |



