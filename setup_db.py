import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def setup_db():
    """Creates all required tables on Aiven if they don't exist yet."""

    host     = os.environ.get("DB_HOST")
    port     = os.environ.get("DB_PORT")
    user     = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")
    database = os.environ.get("DB_NAME")
    use_ssl  = os.environ.get("DB_SSL", "true").lower() == "true"

    try:
        connect_args = {
            "host": host, "port": int(port),
            "user": user, "password": password,
            "database": database,
        }
        if use_ssl:
            connect_args["ssl_disabled"]    = False
            connect_args["ssl_verify_cert"] = False

        conn   = mysql.connector.connect(**connect_args)
        cursor = conn.cursor()

        print("[DB] Connected to Aiven. Creating tables if they do not exist...")

        # Each student_id can exist in multiple cohorts, but not twice in the same one
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cohorts (
                id   INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                student_id  VARCHAR(50)  NOT NULL,
                full_name   VARCHAR(150) NOT NULL,
                cohort_name VARCHAR(100) NOT NULL,
                UNIQUE KEY unique_student_in_cohort (student_id, cohort_name)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id     INT AUTO_INCREMENT PRIMARY KEY,
                name   VARCHAR(100) NOT NULL UNIQUE,
                weight FLOAT NOT NULL
            )
        """)

        # UNIQUE KEY prevents duplicate grades — re-logging updates the score instead
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grades (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                student_id  VARCHAR(50)  NOT NULL,
                cohort_name VARCHAR(100) NOT NULL,
                subject     VARCHAR(100) NOT NULL,
                category    VARCHAR(100) NOT NULL,
                score       FLOAT        NOT NULL,
                UNIQUE KEY unique_grade (student_id, cohort_name, subject, category)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id        INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(150) NOT NULL,
                username  VARCHAR(50)  NOT NULL UNIQUE,
                password  VARCHAR(100) NOT NULL,
                subject   VARCHAR(100) NOT NULL
            )
        """)

        conn.commit()
        print("[DB] All tables created (or already existed). Setup complete.")

    except mysql.connector.Error as e:
        print(f"[DB ERROR] Could not set up the database: {e}")

    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    setup_db()
