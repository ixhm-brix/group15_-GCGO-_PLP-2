import os
import sys
import mysql.connector
from dotenv import load_dotenv
from student import Student
from cohort import Cohort

load_dotenv()


class Storage:

    def __init__(self):
        self.host     = os.environ.get("DB_HOST")
        self.port     = os.environ.get("DB_PORT")
        self.user     = os.environ.get("DB_USER")
        self.password = os.environ.get("DB_PASSWORD")
        self.database = os.environ.get("DB_NAME")
        self.use_ssl  = os.environ.get("DB_SSL", "true").lower() == "true"

        try:
            conn = self.get_connection()
            conn.close()
            print("[DB] Connected to Aiven MySQL successfully.")
        except mysql.connector.Error as e:
            print(f"[DB ERROR] Cannot connect to the database: {e}")
            sys.exit(1)

    def get_connection(self):
        args = {
            "host": self.host, "port": int(self.port),
            "user": self.user, "password": self.password,
            "database": self.database,
        }
        if self.use_ssl:
            args["ssl_disabled"]    = False
            args["ssl_verify_cert"] = False
        return mysql.connector.connect(**args)

    # SAVE
    def save(self, cohorts_dict, category_manager):
        conn   = self.get_connection()
        cursor = conn.cursor()
        try:
            # Cohorts — skip if already exists
            for cohort_name in cohorts_dict:
                cursor.execute(
                    "INSERT IGNORE INTO cohorts (name) VALUES (%s)", (cohort_name,))

            # Students — skip duplicates
            for cohort_name, cohort in cohorts_dict.items():
                for student in cohort.get_all_students():
                    cursor.execute(
                        "INSERT IGNORE INTO students (student_id, full_name, cohort_name) "
                        "VALUES (%s, %s, %s)",
                        (student.student_id, student.full_name, cohort_name))

            # Categories — replace entirely so deletions are reflected
            cursor.execute("DELETE FROM categories")
            for cat_name, cat_obj in category_manager.get_categories().items():
                cursor.execute(
                    "INSERT INTO categories (name, weight) VALUES (%s, %s)",
                    (cat_name, cat_obj.weight))

            # Grades — insert or update score if already exists
            for cohort_name, cohort in cohorts_dict.items():
                for student in cohort.get_all_students():
                    for subject, categories in student.get_grades().items():
                        for category, score in categories.items():
                            cursor.execute(
                                "INSERT INTO grades "
                                "(student_id, cohort_name, subject, category, score) "
                                "VALUES (%s, %s, %s, %s, %s) "
                                "ON DUPLICATE KEY UPDATE score = VALUES(score)",
                                (student.student_id, cohort_name, subject, category, score))

            conn.commit()
            print("[DB] Data saved to Aiven MySQL successfully.")

        except mysql.connector.Error as e:
            conn.rollback()
            print(f"[DB ERROR] Save failed: {e}")

        finally:
            cursor.close()
            conn.close()

    # LOAD
    def load(self):
        """Returns (cohorts_dict, custom_categories_list)."""
        conn   = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name, weight FROM categories")
            custom_categories = [(r[0], r[1]) for r in cursor.fetchall()]

            cursor.execute("SELECT name FROM cohorts")
            cohorts_dict = {name: Cohort(name) for (name,) in cursor.fetchall()}

            cursor.execute("SELECT student_id, full_name, cohort_name FROM students")
            for student_id, full_name, cohort_name in cursor.fetchall():
                if cohort_name in cohorts_dict:
                    cohorts_dict[cohort_name].add_student(Student(full_name, student_id))

            cursor.execute(
                "SELECT student_id, cohort_name, subject, category, score FROM grades")
            for student_id, cohort_name, subject, category, score in cursor.fetchall():
                if cohort_name in cohorts_dict:
                    student = cohorts_dict[cohort_name].get_student(student_id)
                    if student:
                        student.add_grade(subject, category, score)

            if not cohorts_dict:
                print("[DB] No existing data found. Starting fresh.")
                return {}, []

            print(f"[DB] Loaded {len(cohorts_dict)} cohort(s) from Aiven MySQL.")
            return cohorts_dict, custom_categories

        except mysql.connector.Error as e:
            print(f"[DB ERROR] Load failed: {e}")
            return {}, []

        finally:
            cursor.close()
            conn.close()

    # TEACHER MANAGEMENT
    def get_teacher_by_password(self, password):
        conn   = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT full_name, username, subject FROM teachers WHERE password = %s",
                (password,))
            row = cursor.fetchone()
            return {"full_name": row[0], "username": row[1], "subject": row[2]} if row else None
        except mysql.connector.Error as e:
            print(f"[DB ERROR] Teacher login check failed: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_all_teachers(self):
        conn   = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT full_name, username, subject FROM teachers ORDER BY subject, full_name")
            return [{"full_name": r[0], "username": r[1], "subject": r[2]}
                    for r in cursor.fetchall()]
        except mysql.connector.Error as e:
            print(f"[DB ERROR] Could not load teachers: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def add_teacher(self, full_name, username, password, subject):
        """Returns True on success, False if username already exists."""
        conn   = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO teachers (full_name, username, password, subject) "
                "VALUES (%s, %s, %s, %s)",
                (full_name, username, password, subject))
            conn.commit()
            return True
        except mysql.connector.IntegrityError:
            return False
        except mysql.connector.Error as e:
            print(f"[DB ERROR] Could not add teacher: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def remove_teacher(self, username):
        conn   = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM teachers WHERE username = %s", (username,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as e:
            print(f"[DB ERROR] Could not remove teacher: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    # BACKUP / HEALTH CHECK
    def backup(self):
        conn   = self.get_connection()
        cursor = conn.cursor()
        try:
            print("\n[DB] === DATABASE HEALTH CHECK ===")
            for table in ["cohorts", "students", "categories", "grades"]:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                (count,) = cursor.fetchone()
                print(f"  {table:<15} : {count} record(s)")
            print("[DB] === END OF HEALTH CHECK ===\n")
        except mysql.connector.Error as e:
            print(f"[DB ERROR] Health check failed: {e}")
        finally:
            cursor.close()
            conn.close()
