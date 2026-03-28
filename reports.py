W = 68  # default separator width


class ReportGenerator:

    def __init__(self):
        pass

    def show_report_menu(self, student, category_manager, calculator):
        """Interactive report menu — loops until the user goes back."""
        categories = category_manager.get_categories()

        # Continuous Assessment = everything except Exam and Midterm
        ca_cats   = {n: c for n, c in categories.items() if n not in ("Exam", "Midterm")}
        midterm_c = categories.get("Midterm")
        exam_c    = categories.get("Exam")
        ca_weight = sum(c.weight for c in ca_cats.values())
        ca_label  = ", ".join(ca_cats.keys()) if ca_cats else ""
        grades    = student.get_grades()

        while True:
            print("\n" + "═" * W)
            print(f"  GRADE REPORT  ·  {student.full_name}  ({student.student_id})".center(W))
            print("═" * W)
            print("  What would you like to view?\n")

            if ca_cats:
                print(f"  1.  Continuous Assessment  [{ca_label}]  ({ca_weight:.0f}%)")
            if midterm_c:
                print(f"  2.  Midterm  ({midterm_c.weight:.0f}%)")
            if exam_c:
                print(f"  3.  Exam  ({exam_c.weight:.0f}%)")
            print("  4.  Full Combined Report")
            print("  5.  Back")
            print("─" * W)

            choice = input("  Choose (1-5): ").strip()

            if choice == "1" and ca_cats:
                self._print_ca_detail(student, ca_cats, ca_weight, calculator)
            elif choice == "2" and midterm_c:
                self._print_single_category(student, "Midterm", midterm_c, calculator, grades)
            elif choice == "3" and exam_c:
                self._print_single_category(student, "Exam", exam_c, calculator, grades)
            elif choice == "4":
                self._print_full_report(student, category_manager, calculator,
                                        ca_cats, ca_weight, midterm_c, exam_c)
            elif choice == "5":
                return
            else:
                print("  [!] Invalid choice.")

    def _print_ca_detail(self, student, ca_cats, ca_weight, calculator):
        grades = student.get_grades()
        if not grades:
            print("\n  No grades recorded yet.")
            return

        cat_names = list(ca_cats.keys())
        subj_w    = max(max(len(s) for s in grades), 18)
        col_w     = 9

        print("\n" + "═" * W)
        print(f"  CONTINUOUS ASSESSMENT  ·  {student.full_name}")
        print("  Categories: " + "  ·  ".join(
            f"{n} ({ca_cats[n].weight:.0f}%)" for n in cat_names))
        print("─" * W)

        header = f"  {'Subject':<{subj_w}}"
        for n in cat_names:
            header += f"  {n[:col_w-1]:^{col_w}}"
        header += f"  {'CA Avg':>7}"
        print(header)
        print("  " + "─" * (W - 2))

        subject_ca_avgs = []
        for subject, cat_scores in grades.items():
            row = f"  {subject:<{subj_w}}"
            scores_for_avg = {}
            for n in cat_names:
                score = cat_scores.get(n)
                if score is not None:
                    row += f"  {score:^{col_w}.1f}"
                    scores_for_avg[n] = score
                else:
                    row += f"  {'—':^{col_w}}"
            ca_avg = self._group_weighted_avg(scores_for_avg, ca_cats, ca_weight)
            subject_ca_avgs.append(ca_avg)
            row += f"  {ca_avg:>7.2f}"
            print(row)

        print("  " + "─" * (W - 2))
        overall = sum(subject_ca_avgs) / len(subject_ca_avgs) if subject_ca_avgs else 0
        print(f"\n  Continuous Assessment Average : {overall:.2f} / 100")
        print("═" * W + "\n")

    def _print_single_category(self, student, cat_name, cat_obj, calculator, grades):
        if not grades:
            print("\n  No grades recorded yet.")
            return

        subj_w = max(max(len(s) for s in grades), 18)

        print("\n" + "═" * W)
        print(f"  {cat_name.upper()} REPORT  ·  {student.full_name}  ({student.student_id})")
        print(f"  Category weight : {cat_obj.weight:.0f}%")
        print("─" * W)
        print(f"  {'Subject':<{subj_w}}  {'Score':>8}   {'/ 100':>6}   Letter")
        print("  " + "─" * (W - 2))

        scores = []
        for subject, cat_scores in grades.items():
            score = cat_scores.get(cat_name)
            if score is not None:
                letter = calculator.get_letter_grade(score)
                print(f"  {subject:<{subj_w}}  {score:>8.1f}   {'/ 100':>6}   {letter}")
                scores.append(score)
            else:
                print(f"  {subject:<{subj_w}}  {'—':>8}   {'/ 100':>6}   —")

        print("  " + "─" * (W - 2))
        if scores:
            avg = sum(scores) / len(scores)
            print(f"\n  {cat_name} Average : {avg:.2f} / 100   ({calculator.get_letter_grade(avg)})")
        else:
            print(f"\n  No {cat_name} scores recorded yet.")
        print("═" * W + "\n")

    def _print_full_report(self, student, category_manager, calculator,
                           ca_cats, ca_weight, midterm_c, exam_c):
        grades = student.get_grades()
        if not grades:
            print("\n  No grades recorded yet.")
            return

        subj_w = max(max(len(s) for s in grades), 18)
        col_w  = 12

        cols = []
        if ca_cats:   cols.append(("Cont. Assess.", f"({ca_weight:.0f}%)"))
        if midterm_c: cols.append(("Midterm",        f"({midterm_c.weight:.0f}%)"))
        if exam_c:    cols.append(("Exam",            f"({exam_c.weight:.0f}%)"))
        cols.append(("Final Avg", ""))
        cols.append(("Grade", ""))

        total_w = subj_w + 4 + col_w * len(cols)
        sep     = "═" * total_w

        print("\n" + sep)
        print(f"  FULL COMBINED REPORT  ·  {student.full_name}  ({student.student_id})")
        print("─" * total_w)

        hdr1 = f"  {'Subject':<{subj_w}}"
        hdr2 = f"  {'':<{subj_w}}"
        for label, wlabel in cols:
            hdr1 += f"  {label:^{col_w-2}}"
            hdr2 += f"  {wlabel:^{col_w-2}}"
        print(hdr1)
        print(hdr2)
        print("─" * total_w)

        ca_vals, midterm_vals, exam_vals = [], [], []

        for subject, cat_scores in grades.items():
            row = f"  {subject:<{subj_w}}"

            if ca_cats:
                ca_scores_here = {n: cat_scores[n] for n in ca_cats if n in cat_scores}
                ca_avg = self._group_weighted_avg(ca_scores_here, ca_cats, ca_weight)
                ca_vals.append(ca_avg)
                row += f"  {ca_avg:^{col_w-2}.2f}"

            if midterm_c:
                m = cat_scores.get("Midterm")
                midterm_vals.append(m) if m is not None else None
                row += f"  {m:^{col_w-2}.1f}" if m is not None else f"  {'—':^{col_w-2}}"

            if exam_c:
                e = cat_scores.get("Exam")
                exam_vals.append(e) if e is not None else None
                row += f"  {e:^{col_w-2}.1f}" if e is not None else f"  {'—':^{col_w-2}}"

            subj_avg = calculator.get_subject_average(cat_scores, category_manager)
            row += f"  {subj_avg:^{col_w-2}.2f}"
            row += f"  {calculator.get_letter_grade(subj_avg):^{col_w-2}}"
            print(row)

        print("─" * total_w)
        avg_row = f"  {'AVERAGE':<{subj_w}}"
        if ca_cats:    avg_row += f"  {sum(ca_vals)/len(ca_vals) if ca_vals else 0:^{col_w-2}.2f}"
        if midterm_c:  avg_row += f"  {sum(midterm_vals)/len(midterm_vals) if midterm_vals else 0:^{col_w-2}.2f}"
        if exam_c:     avg_row += f"  {sum(exam_vals)/len(exam_vals) if exam_vals else 0:^{col_w-2}.2f}"

        overall_avg = calculator.calculate_weighted_average(grades, category_manager)
        overall_let = calculator.get_letter_grade(overall_avg)
        avg_row += f"  {overall_avg:^{col_w-2}.2f}  {overall_let:^{col_w-2}}"
        print(avg_row)

        print(sep)
        print(f"  Overall Weighted Average : {overall_avg:.2f} / 100")
        print(f"  Letter Grade             : {overall_let}")
        print(f"  GPA                      : {calculator.get_gpa(overall_avg):.1f} / 4.0")
        print(sep + "\n")

    def _group_weighted_avg(self, score_dict, cat_dict, group_total_weight):
        """Weighted average within a category group, normalised to 0-100."""
        if not score_dict or group_total_weight == 0:
            return 0.0
        used = sum(cat_dict[n].weight for n in score_dict)
        return sum(score_dict[n] * cat_dict[n].weight for n in score_dict) / used if used else 0.0

    def print_class_overview(self, cohort, category_manager, calculator,
                             subject_filter=None):
        """
        Spreadsheet overview — rows = students, columns = subjects.
        subject_filter restricts columns to one subject (subject teacher view).
        """
        all_students = cohort.get_all_students()
        if not all_students:
            print("\n  [!] No students in this cohort yet.")
            return

        subjects_ordered = []
        seen = set()
        for student in all_students:
            for subj in student.get_subjects():
                if subj not in seen and (subject_filter is None or subj == subject_filter):
                    seen.add(subj)
                    subjects_ordered.append(subj)

        if not subjects_ordered:
            print(f"\n  [!] No grades recorded for '{subject_filter}' in this cohort yet.")
            return

        name_w  = min(max(max(len(s.full_name) for s in all_students), 18), 22)
        id_w    = min(max(max(len(s.student_id) for s in all_students), 6), 12)
        sc_w    = 11
        total_w = max(name_w + 2 + id_w + 3 + len(subjects_ordered) * (sc_w + 1) + 13, 60)

        def shorten(s, w):
            return s if len(s) <= w else s[:w - 1] + "."

        title = f"CLASS OVERVIEW  —  {cohort.cohort_name}"
        if subject_filter:
            title += f"  |  {subject_filter}"

        sep = "═" * total_w
        div = f"  {'─'*name_w}  {'─'*id_w}  " + "".join(f"{'─'*sc_w}┼" for _ in subjects_ordered)
        if not subject_filter:
            div += f"{'─'*9}  {'─'*4}"

        print("\n" + sep)
        print(f"  {title}".center(total_w))
        print(sep)

        hdr = f"  {'Name':<{name_w}}  {'ID':<{id_w}}  "
        for subj in subjects_ordered:
            hdr += f" {shorten(subj, sc_w):^{sc_w}}│"
        if not subject_filter:
            hdr += f" {'Overall':^7}  {'GPA':^4}"
        print(hdr)
        print(div)

        subject_score_lists = {s: [] for s in subjects_ordered}
        overall_scores      = []

        for student in all_students:
            grades = student.get_grades()
            row    = f"  {student.full_name[:name_w]:<{name_w}}  {student.student_id:<{id_w}}  "

            for subj in subjects_ordered:
                cat_scores = grades.get(subj)
                if cat_scores:
                    avg    = calculator.get_subject_average(cat_scores, category_manager)
                    letter = calculator.get_letter_grade(avg)
                    subject_score_lists[subj].append(avg)
                    row += f" {avg:>5.1f} {letter:^{sc_w - 7}}│"
                else:
                    row += f" {'—':^{sc_w}}│"

            if not subject_filter:
                overall = calculator.calculate_weighted_average(grades, category_manager)
                overall_scores.append(overall)
                row += f"  {overall:>5.2f}    {calculator.get_gpa(overall):>3.1f}"
            print(row)

        print(div)
        avg_row = f"  {'CLASS AVERAGE':<{name_w}}  {'':^{id_w}}  "
        lowest_subj, lowest_val = None, float("inf")

        for subj in subjects_ordered:
            vals = subject_score_lists[subj]
            if vals:
                class_avg = sum(vals) / len(vals)
                letter    = calculator.get_letter_grade(class_avg)
                if class_avg < lowest_val:
                    lowest_val, lowest_subj = class_avg, subj
                avg_row += f" {class_avg:>5.1f} {letter:^{sc_w - 7}}│"
            else:
                avg_row += f" {'—':^{sc_w}}│"

        if not subject_filter:
            oc = sum(overall_scores) / len(overall_scores) if overall_scores else 0
            avg_row += f"  {oc:>5.2f}    {calculator.get_gpa(oc):>3.1f}"
        print(avg_row)

        print(sep)
        if lowest_subj:
            print(f"  ⚠  Lowest subject average: {lowest_subj}  ({lowest_val:.2f} / 100)")
        print(f"  Total students: {len(all_students)}")
        print(sep + "\n")

    def export_report_to_file(self, student, category_manager, calculator):
        """Saves the student's grade report to a .txt file."""
        filename = f"{student.student_id}_report.txt"
        grades   = student.get_grades()
        try:
            with open(filename, "w") as f:
                f.write(f"GRADE REPORT — {student.full_name} ({student.student_id})\n")
                f.write("=" * 60 + "\n\n")
                if not grades:
                    f.write("No grades recorded yet.\n")
                else:
                    for subject, cat_scores in grades.items():
                        f.write(f"Subject: {subject}\n")
                        for cat_name, score in cat_scores.items():
                            f.write(f"  {cat_name:<20} {score:.1f} / 100\n")
                        subj_avg = calculator.get_subject_average(cat_scores, category_manager)
                        f.write(f"  {'Subject Average':<20} {subj_avg:.2f} / 100\n\n")

                    overall_avg = calculator.calculate_weighted_average(grades, category_manager)
                    letter      = calculator.get_letter_grade(overall_avg)
                    gpa         = calculator.get_gpa(overall_avg)
                    f.write("=" * 60 + "\n")
                    f.write(f"Overall Average : {overall_avg:.2f} / 100\n")
                    f.write(f"Letter Grade    : {letter}\n")
                    f.write(f"GPA             : {gpa:.1f} / 4.0\n")
                    f.write("=" * 60 + "\n")
            print(f"\n  [✓] Report exported to: {filename}")
        except Exception as e:
            print(f"\n  [✗] Could not save report: {e}")

    def print_student_report(self, student, category_manager, calculator):
        """Legacy entry point — delegates to the menu viewer."""
        self.show_report_menu(student, category_manager, calculator)