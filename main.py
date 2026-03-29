from dotenv import load_dotenv
load_dotenv()  # Load .env credentials before anything else runs

from student import Student
from grade import GradeCategory, CategoryManager
from calculator import GradeCalculator
from cohort import Cohort
from auth import Auth
from reports import ReportGenerator
from storage import Storage
from setup_db import setup_db  # Creates tables on Aiven if they do not exist yet


class GradeTracker:

    def __init__(self):
        self.cohorts          = {}
        self.current_cohort   = None
        self.category_manager = CategoryManager()
        self.calculator       = GradeCalculator()
        self.report_generator = ReportGenerator()
        self.storage          = Storage()
        self.auth             = Auth()

    # STARTUP
    def run(self):
        setup_db()   # Create all DB tables if they don't exist yet
        loaded_cohorts, custom_categories = self.storage.load()
        self.cohorts = loaded_cohorts

        if custom_categories:
            self.category_manager.categories = {}
            for cat_name, cat_weight in custom_categories:
                self.category_manager.add_category(cat_name, cat_weight)

        self._print_banner()

        while True:
            print("\n" + "=" * 44)
            print("  Who are you?")
            print("=" * 44)
            print("  1.  Head Teacher")
            print("  2.  Subject Teacher")
            print("  3.  Student  (view my grades)")
            print("  4.  Exit")
            print("-" * 44)

            choice = input("  Enter choice (1-4): ").strip()

            if choice == "1":
                if self.auth.login_head_teacher():
                    self._head_teacher_flow()

            elif choice == "2":
                teacher = self.auth.login_subject_teacher(self.storage)
                if teacher is not None:
                    self._subject_teacher_flow(teacher)

            elif choice == "3":
                self._student_login_flow()

            elif choice == "4":
                print("\n  Goodbye!\n")
                break

            else:
                print("\n  [!] Please enter 1, 2, 3 or 4.")

    # HEAD TEACHER FLOW  — full access
    def _head_teacher_flow(self):
        """
        Head teacher selects or creates a cohort, then enters the full menu.
        They can also manage teachers without selecting a cohort.
        """
        while True:
            print("\n" + "=" * 44)
            print("  HEAD TEACHER PANEL")
            print("=" * 44)
            print("  1.  Select / Create cohort")
            print("  2.  Manage subject teachers")
            print("  3.  Manage grade categories")
            print("  4.  Save all data")
            print("  5.  Back to role selection")
            print("-" * 44)

            choice = input("  Enter choice (1-5): ").strip()

            if choice == "1":
                self._select_or_create_cohort(can_create=True)
                if self.current_cohort is not None:
                    self._head_teacher_cohort_menu()

            elif choice == "2":
                self._manage_teachers()

            elif choice == "3":
                self._manage_categories()

            elif choice == "4":
                self.storage.save(self.cohorts, self.category_manager)

            elif choice == "5":
                self.current_cohort = None
                return

            else:
                print("\n  [!] Please enter a number between 1 and 5.")

    def _head_teacher_cohort_menu(self):
        """Full menu once a cohort is selected — head teacher has no restrictions."""
        while True:
            print("\n" + "=" * 44)
            print(f"  HEAD TEACHER MENU")
            print(f"  Cohort  : {self.current_cohort.cohort_name}")
            print(f"  Students: {self.current_cohort.get_student_count()}")
            print("=" * 44)
            print("  1.  Add students")
            print("  2.  Log a grade  (any subject)")
            print("  3.  View student report")
            print("  4.  Class overview")
            print("  5.  Switch cohort")
            print("  6.  Save & go back")
            print("-" * 44)

            choice = input("  Enter choice (1-6): ").strip()

            if choice == "1":
                self._add_student()
            elif choice == "2":
                self._log_grade(fixed_subject=None)   # no subject restriction
            elif choice == "3":
                self._view_student_report()
            elif choice == "4":
                # Head teacher picks which cohort to view — not locked to current one
                cohort = self._pick_cohort_for_overview()
                if cohort is not None:
                    self.report_generator.print_class_overview(
                        cohort, self.category_manager, self.calculator)
            elif choice == "5":
                self._select_or_create_cohort(can_create=True)
                if self.current_cohort is None:
                    return
            elif choice == "6":
                self.storage.save(self.cohorts, self.category_manager)
                print("\n  Returning to Head Teacher panel...\n")
                return
            else:
                print("\n  [!] Please enter a number between 1 and 6.")

    # SUBJECT TEACHER FLOW  — restricted to their subject
    def _subject_teacher_flow(self, teacher):
        """
        Subject teacher picks an existing cohort (cannot create one),
        then works only within their assigned subject.
        """
        subject = teacher["subject"]

        # Must pick a cohort first
        self._select_or_create_cohort(can_create=False)
        if self.current_cohort is None:
            return

        while True:
            print("\n" + "=" * 44)
            print(f"  TEACHER MENU")
            print(f"  Teacher : {teacher['full_name']}")
            print(f"  Subject : {subject}")
            print(f"  Cohort  : {self.current_cohort.cohort_name}")
            print(f"  Students: {self.current_cohort.get_student_count()}")
            print("=" * 44)
            print("  1.  Add students")
            print(f"  2.  Log grades  ({subject})")
            print("  3.  View student report")
            print("  4.  Class overview")
            print("  5.  Switch cohort")
            print("  6.  Save & exit")
            print("-" * 44)

            choice = input("  Enter choice (1-6): ").strip()

            if choice == "1":
                self._add_student()
            elif choice == "2":
                self._log_grade(fixed_subject=subject)   # locked to their subject
            elif choice == "3":
                self._view_student_report()
            elif choice == "4":
                self.report_generator.print_class_overview(
                    self.current_cohort, self.category_manager, self.calculator,
                    subject_filter=subject)   # only show this teacher's subject
            elif choice == "5":
                self._select_or_create_cohort(can_create=False)
                if self.current_cohort is None:
                    return
            elif choice == "6":
                self.storage.save(self.cohorts, self.category_manager)
                print("\n  Returning to role selection...\n")
                return
            else:
                print("\n  [!] Please enter a number between 1 and 6.")

    # STUDENT SELF-VIEW FLOW
    def _student_login_flow(self):
        student_id = input("\n  Enter your Student ID: ").strip()
        found = None
        for cohort in self.cohorts.values():
            result = cohort.get_student(student_id)
            if result is not None:
                found = result
                break

        if found is not None:
            print(f"\n  Welcome, {found.full_name}!")
            print("  Use the menu below to explore your grades (read-only).\n")
            self.report_generator.show_report_menu(found, self.category_manager, self.calculator)
        else:
            print(f"\n  [!] No student found with ID '{student_id}'.")
            print("      Please check your ID and try again.")

    # COHORT PICKER FOR OVERVIEW  — head teacher chooses any cohort to inspect
    def _pick_cohort_for_overview(self):
        """Shows all cohorts and returns the one the head teacher picks, or None."""
        if not self.cohorts:
            print("\n  [!] No cohorts exist yet.")
            return None

        print("\n" + "=" * 44)
        print("  SELECT COHORT TO VIEW")
        print("=" * 44)
        cohort_names = list(self.cohorts.keys())
        for i, name in enumerate(cohort_names, start=1):
            count = self.cohorts[name].get_student_count()
            print(f"  {i}.  {name}  ({count} students)")
        print("  B.  Cancel")
        print("-" * 44)

        choice = input("  Enter choice: ").strip().upper()
        if choice == "B":
            return None
        try:
            index = int(choice) - 1
            if 0 <= index < len(cohort_names):
                return self.cohorts[cohort_names[index]]
            print("  [!] Number out of range.")
        except ValueError:
            print("  [!] Invalid input.")
        return None

    # COHORT SELECTION  (can_create=True for head teacher, False for subject teacher)
    def _select_or_create_cohort(self, can_create=True):
        while True:
            print("\n" + "=" * 44)
            print("  COHORT SELECTION")
            print("=" * 44)

            if self.cohorts:
                print("  Existing cohorts:")
                cohort_names = list(self.cohorts.keys())
                for i, name in enumerate(cohort_names, start=1):
                    count = self.cohorts[name].get_student_count()
                    print(f"    {i}.  {name}  ({count} students)")
            else:
                print("  No cohorts created yet.")

            if can_create:
                print("\n  N.  Create a new cohort")
            print("  B.  Go back")
            print("-" * 44)

            choice = input("  Enter choice: ").strip().upper()

            if choice == "B":
                self.current_cohort = None
                return

            if choice == "N" and can_create:
                cohort_name = input("  New cohort name: ").strip()
                if not cohort_name:
                    print("  [!] Cohort name cannot be empty.")
                    continue
                if cohort_name in self.cohorts:
                    print(f"  [!] A cohort named '{cohort_name}' already exists.")
                    continue
                self.cohorts[cohort_name] = Cohort(cohort_name)
                self.current_cohort = self.cohorts[cohort_name]
                print(f"\n  [✓] Cohort '{cohort_name}' created and selected.")
                return

            try:
                index = int(choice) - 1
                if 0 <= index < len(self.cohorts):
                    name = list(self.cohorts.keys())[index]
                    self.current_cohort = self.cohorts[name]
                    print(f"\n  [✓] Selected cohort: '{name}'")
                    return
                else:
                    print("  [!] Number out of range.")
            except ValueError:
                print("  [!] Invalid input.")

    # ADD STUDENT  (loop until 'done')
    def _add_student(self):
        print("\n  --- ADD STUDENTS ---")
        print("  Type 'done' as the name when you are finished adding students.")
        print("-" * 40)

        added_count = 0

        while True:
            while True:
                full_name = input("\n  Full name (or 'done' to finish): ").strip()
                if full_name.lower() == "done":
                    print(f"\n  [✓] Done. {added_count} student{'s' if added_count != 1 else ''} added.")
                    return
                if not full_name:
                    print("  [!] Name cannot be empty.")
                else:
                    break

            while True:
                student_id = input("  Student ID (e.g. STU001): ").strip()
                if not Student.validate_id(student_id):
                    print("  [!] Invalid ID. Must not be empty or contain spaces.")
                    continue
                if self.current_cohort.student_exists(student_id):
                    print(f"  [!] ID '{student_id}' already exists in this cohort.")
                    continue
                break

            self.current_cohort.add_student(Student(full_name, student_id))
            added_count += 1
            print(f"  [✓] Added: {full_name} (ID: {student_id})  —  {added_count} added so far.")

    # LOG GRADE
    # fixed_subject=None  → head teacher picks any subject
    # fixed_subject="X"   → subject teacher locked to subject X
    def _log_grade(self, fixed_subject=None):
        print("\n  --- LOG GRADES ---")

        if self.current_cohort.get_student_count() == 0:
            print("  [!] No students in this cohort yet. Add students first.")
            return

        # Subject selection
        if fixed_subject is not None:
            # Subject teacher — no choice, their subject is fixed
            subject = fixed_subject
            print(f"  Subject (fixed): {subject}")
        else:
            # Head teacher — show existing subjects + option to enter a new one
            existing_subjects = set()
            for student in self.current_cohort.get_all_students():
                for subj in student.get_subjects():
                    existing_subjects.add(subj)

            if existing_subjects:
                print(f"\n  Subjects already in use: {', '.join(sorted(existing_subjects))}")
                print("  (Use the same spelling to add to an existing subject.)")

            subject = input("\n  Subject / Course name: ").strip()
            if not subject:
                print("  [!] Subject name cannot be empty.")
                return

        # Category selection
        print("\n  Available grade categories:")
        self.category_manager.display_categories()

        category_names = list(self.category_manager.get_categories().keys())
        print("\n  Choose a category:")
        for i, name in enumerate(category_names, start=1):
            print(f"    {i}.  {name}")

        cat_input = input("\n  Enter category number or name: ").strip()
        category  = None

        try:
            cat_index = int(cat_input) - 1
            if 0 <= cat_index < len(category_names):
                category = category_names[cat_index]
            else:
                print("  [!] Number out of range.")
                return
        except ValueError:
            if cat_input in category_names:
                category = cat_input
            else:
                print(f"  [!] '{cat_input}' is not a valid category.")
                return

        # Enter scores
        print(f"\n  Subject  : {subject}")
        print(f"  Category : {category}")
        print(f"  Students : {self.current_cohort.get_student_count()}")
        print()
        print("  Type a score (0-100) for each student, or press Enter to skip.")
        print("-" * 45)

        all_students  = self.current_cohort.get_all_students()
        graded_count  = 0
        skipped_count = 0

        for pos, student in enumerate(all_students, start=1):
            print(f"\n  [{pos}/{len(all_students)}]  {student.full_name}  (ID: {student.student_id})")

            existing = student.get_grades().get(subject, {}).get(category)
            if existing is not None:
                print(f"          Current score: {existing}  (will be overwritten if you enter a new score)")

            while True:
                score_input = input("          Score: ").strip()
                if score_input == "":
                    print("          → Skipped.")
                    skipped_count += 1
                    break
                try:
                    score = float(score_input)
                    if not 0 <= score <= 100:
                        print("          [!] Score must be 0-100.")
                        continue
                    student.add_grade(subject, category, score)
                    graded_count += 1
                    print(f"          → Saved: {score}")
                    break
                except ValueError:
                    print("          [!] Please enter a number or press Enter to skip.")

        print("\n" + "=" * 45)
        print(f"  Subject  : {subject}  |  Category : {category}")
        print(f"  Graded   : {graded_count}   Skipped: {skipped_count}")
        print("=" * 45)

    # VIEW STUDENT REPORT
    def _view_student_report(self):
        print("\n  --- VIEW STUDENT REPORT ---")
        student_id = input("  Enter student ID: ").strip()
        student    = self.current_cohort.get_student(student_id)

        if student is None:
            print(f"  [!] No student with ID '{student_id}' in this cohort.")
            return

        self.report_generator.show_report_menu(
            student, self.category_manager, self.calculator)

        if input("  Export full report to a .txt file? (y/n): ").strip().lower() == "y":
            self.report_generator.export_report_to_file(
                student, self.category_manager, self.calculator)

    # MANAGE SUBJECT TEACHERS  (head teacher only)
    def _manage_teachers(self):
        while True:
            print("\n" + "=" * 44)
            print("  MANAGE SUBJECT TEACHERS")
            print("=" * 44)

            teachers = self.storage.get_all_teachers()
            if teachers:
                print(f"  {'Name':<22} {'Username':<15} Subject")
                print("  " + "-" * 42)
                for t in teachers:
                    print(f"  {t['full_name']:<22} {t['username']:<15} {t['subject']}")
            else:
                print("  No subject teachers registered yet.")

            print("\n  1.  Add a subject teacher")
            print("  2.  Remove a subject teacher")
            print("  3.  Back")
            print("-" * 44)

            choice = input("  Enter choice (1-3): ").strip()

            if choice == "1":
                self._add_teacher()
            elif choice == "2":
                self._remove_teacher()
            elif choice == "3":
                return
            else:
                print("  [!] Please enter 1, 2 or 3.")

    def _add_teacher(self):
        print("\n  -- ADD SUBJECT TEACHER --")

        full_name = input("  Full name       : ").strip()
        if not full_name:
            print("  [!] Name cannot be empty.")
            return

        username = input("  Username        : ").strip()
        if not username or " " in username:
            print("  [!] Username must not be empty or contain spaces.")
            return

        import getpass
        password = getpass.getpass("  Password        : ")
        if not password.strip():
            print("  [!] Password cannot be empty.")
            return

        subject = input("  Subject teaches : ").strip()
        if not subject:
            print("  [!] Subject cannot be empty.")
            return

        success = self.storage.add_teacher(full_name, username, password, subject)
        if success:
            print(f"\n  [✓] Teacher '{full_name}' ({username}) added for subject: {subject}")
        else:
            print(f"\n  [✗] Username '{username}' already exists. Choose a different one.")

    def _remove_teacher(self):
        username = input("  Username to remove: ").strip()
        removed  = self.storage.remove_teacher(username)
        if removed:
            print(f"  [✓] Teacher '{username}' removed.")
        else:
            print(f"  [!] No teacher found with username '{username}'.")

    # MANAGE GRADE CATEGORIES  (head teacher only)
    def _manage_categories(self):
        while True:
            print("\n  --- MANAGE GRADE CATEGORIES ---")
            self.category_manager.display_categories()
            print("\n  1.  Add new category")
            print("  2.  Remove category")
            print("  3.  Validate weights (must total 100%)")
            print("  4.  Back")
            print("-" * 35)

            choice = input("  Enter choice (1-4): ").strip()

            if choice == "1":
                cat_name = input("  New category name: ").strip()
                if not cat_name:
                    print("  [!] Category name cannot be empty.")
                    continue
                try:
                    weight = float(input(f"  Weight for '{cat_name}' (%): ").strip())
                    if not 0 <= weight <= 100:
                        print("  [!] Weight must be 0-100.")
                        continue
                except ValueError:
                    print("  [!] Please enter a valid number.")
                    continue
                self.category_manager.add_category(cat_name, weight)
                print(f"  [✓] Category '{cat_name}' ({weight}%) added.")

            elif choice == "2":
                cat_name = input("  Category to remove: ").strip()
                if self.category_manager.remove_category(cat_name):
                    print(f"  [✓] Category '{cat_name}' removed.")
                else:
                    print(f"  [!] Category '{cat_name}' not found.")

            elif choice == "3":
                try:
                    self.category_manager.validate_weights()
                    print("  [✓] Weights are valid — they total 100%.")
                except ValueError as e:
                    print(f"  [!] {e}")

            elif choice == "4":
                return

            else:
                print("  [!] Please enter 1, 2, 3 or 4.")

    # =========================================================================
    # BANNER
    # =========================================================================

    def _print_banner(self):
        print("\n")
        print("  ╔══════════════════════════════════════════╗")
        print("  ║        STUDENT GRADE TRACKER             ║")
        print("  ║   ALU Peer Learning Days — Python        ║")
        print("  ║           Group 15 (GCGO)                ║")
        print("  ╚══════════════════════════════════════════╝")
        print()


if __name__ == "__main__":
    tracker = GradeTracker()
    tracker.run()
