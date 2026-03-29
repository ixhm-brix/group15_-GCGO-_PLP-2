"""
populate_sample.py — Seeds all tables with realistic sample data.
Safe to re-run — uses INSERT IGNORE / ON DUPLICATE KEY UPDATE.

What gets inserted:
  - 4 subject teachers  (one per subject)
  - 3 cohorts           (10 students each)
  - 5 grade categories
  - 4 subjects with grades for every student × every category
"""

from dotenv import load_dotenv
load_dotenv()

import random
from storage import Storage
from cohort import Cohort
from student import Student
from grade import CategoryManager

random.seed(42)   # fixed seed — same scores every run

# Subject teachers
# Each entry: (full_name, username, password, subject)
# Password is all they need to log in.

TEACHERS = [
    ("Mr. Jean Bosco Niyonsenga", "jbosco",   "math2025",    "Mathematics"),
    ("Ms. Clarisse Uwimana",      "clarisse",  "python2025",  "Python Programming"),
    ("Mr. Patrick Habimana",      "patrick",   "dsa2025",     "Data Structures"),
    ("Ms. Diane Mukamana",        "diane",     "english2025", "English Communication"),
]

# Cohorts and students

COHORT_DATA = {
    "2025-Cohort-A": [
        ("Alice Uwera",       "STU-A01"),
        ("Brian Mugisha",     "STU-A02"),
        ("Chloe Ndayisaba",   "STU-A03"),
        ("David Hakizimana",  "STU-A04"),
        ("Eve Uwimana",       "STU-A05"),
        ("Frank Niyonzima",   "STU-A06"),
        ("Grace Mukamana",    "STU-A07"),
        ("Henry Habimana",    "STU-A08"),
        ("Iris Uwineza",      "STU-A09"),
        ("James Bizimana",    "STU-A10"),
    ],
    "2025-Cohort-B": [
        ("Karen Ingabire",    "STU-B01"),
        ("Leo Nkurunziza",    "STU-B02"),
        ("Mia Umutesi",       "STU-B03"),
        ("Noah Nsabimana",    "STU-B04"),
        ("Olivia Mutesi",     "STU-B05"),
        ("Paul Nshimiyimana", "STU-B06"),
        ("Quinn Umubyeyi",    "STU-B07"),
        ("Rachel Iradukunda", "STU-B08"),
        ("Sam Ndikumana",     "STU-B09"),
        ("Tina Uwase",        "STU-B10"),
    ],
    "2025-Cohort-C": [
        ("Uma Mukandoli",     "STU-C01"),
        ("Victor Nzeyimana",  "STU-C02"),
        ("Wendy Uwamariya",   "STU-C03"),
        ("Xavier Kabera",     "STU-C04"),
        ("Yara Niyomugabo",   "STU-C05"),
        ("Zoe Habiyaremye",   "STU-C06"),
        ("Alex Twizeyimana",  "STU-C07"),
        ("Bella Mukagasana",  "STU-C08"),
        ("Chris Nizeyimana",  "STU-C09"),
        ("Diana Uwingabire",  "STU-C10"),
    ],
}

SUBJECTS = ["Mathematics", "Python Programming", "Data Structures", "English Communication"]


def seed_teachers(storage):
    print("\n[1/3] Seeding subject teachers...")
    for full_name, username, password, subject in TEACHERS:
        added = storage.add_teacher(full_name, username, password, subject)
        status = "added" if added else "already exists"
        print(f"      {full_name:<35}  subject: {subject:<25}  password: {password}  [{status}]")


def build_cohorts():
    category_manager = CategoryManager()  # Exam 40, Midterm 25, Quiz 20, Exercise 10, Assignment 5
    cohorts_dict     = {}

    for cohort_name, students in COHORT_DATA.items():
        cohort = Cohort(cohort_name)
        for full_name, student_id in students:
            student = Student(full_name, student_id)
            for subject in SUBJECTS:
                for cat_name in category_manager.get_categories():
                    student.add_grade(subject, cat_name, round(random.uniform(55, 98), 1))
            cohort.add_student(student)
        cohorts_dict[cohort_name] = cohort

    return cohorts_dict, category_manager


if __name__ == "__main__":
    storage = Storage()

    seed_teachers(storage)

    print("\n[2/3] Seeding cohorts, students, and grades...")
    cohorts_dict, category_manager = build_cohorts()
    storage.save(cohorts_dict, category_manager)

    print("\n[3/3] Health check:")
    storage.backup()

    print("\n── LOGIN REFERENCE ─────────────────────────────────────────")
    print("  Head Teacher   →  password : admin123")
    for _, _, password, subject in TEACHERS:
        print(f"  {subject:<28} →  password : {password}")
    print("────────────────────────────────────────────────────────────")
    print("\nDone! Run python main.py to start.")
