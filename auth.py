import os
import getpass
from dotenv import load_dotenv

load_dotenv()

MAX_ATTEMPTS = 3


class Auth:

    def __init__(self):
        self._admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")

    # =========================================================================
    # HEAD TEACHER LOGIN
    # =========================================================================

    def login_head_teacher(self):
        """Password-only login for the head teacher."""
        print("\n  --- HEAD TEACHER LOGIN ---")

        for attempt in range(1, MAX_ATTEMPTS + 1):
            remaining = MAX_ATTEMPTS - attempt + 1
            password  = getpass.getpass(
                f"\n  Password ({remaining} attempt{'s' if remaining != 1 else ''} left): "
            )

            if password == self._admin_password:
                print("\n  [✓] Welcome, Head Teacher!")
                return True

            left = MAX_ATTEMPTS - attempt
            if left > 0:
                print(f"  [✗] Wrong password. {left} attempt{'s' if left != 1 else ''} remaining.")
            else:
                print("  [!] Too many failed attempts. Returning to main menu.")

        return False

    # =========================================================================
    # SUBJECT TEACHER LOGIN
    # =========================================================================

    def login_subject_teacher(self, storage):
        """
        Password-only login for subject teachers.
        Looks up the password in the teachers table and returns the matching
        teacher dict {full_name, username, subject}, or None on failure.
        """
        print("\n  --- SUBJECT TEACHER LOGIN ---")

        for attempt in range(1, MAX_ATTEMPTS + 1):
            remaining = MAX_ATTEMPTS - attempt + 1
            password  = getpass.getpass(
                f"\n  Password ({remaining} attempt{'s' if remaining != 1 else ''} left): "
            )

            teacher = storage.get_teacher_by_password(password)

            if teacher is not None:
                print(f"\n  [✓] Welcome, {teacher['full_name']}!")
                print(f"      Subject : {teacher['subject']}")
                return teacher

            left = MAX_ATTEMPTS - attempt
            if left > 0:
                print(f"  [✗] Wrong password. {left} attempt{'s' if left != 1 else ''} remaining.")
            else:
                print("  [!] Too many failed attempts. Returning to main menu.")

        return None
