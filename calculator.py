# =============================================================================
# FILE: calculator.py
# PURPOSE:
#   Handles all grade-related calculations:
#     - Weighted averages (overall and per subject)
#     - Letter grade conversion (A–F)
#     - GPA conversion (4.0 scale)
# =============================================================================


class GradeCalculator:
    """Utility class for grade calculations (stateless)."""

    def __init__(self):
        pass  # No internal state required

    # -------------------------------------------------------------------------
    # Overall Weighted Average
    # -------------------------------------------------------------------------
    def calculate_weighted_average(self, grades_dict, category_manager):
        """
        Computes weighted average across all subjects.

        Args:
            grades_dict (dict): student grades per subject
            category_manager: provides category weights

        Returns:
            float: overall average (0–100)
        """

        categories = category_manager.get_categories()
        weighted_total = 0.0
        weight_used = 0.0

        for _, category_scores in grades_dict.items():
            for category_name, score in category_scores.items():
                if category_name in categories:
                    weight = categories[category_name].weight / 100
                    weighted_total += score * weight
                    weight_used += weight

        # Avoid division by zero if no valid grades exist
        return weighted_total / weight_used if weight_used else 0.0

    # -------------------------------------------------------------------------
    # Single Subject Average
    # -------------------------------------------------------------------------
    def get_subject_average(self, subject_grades, category_manager):
        """
        Computes weighted average for a single subject.

        Args:
            subject_grades (dict): category scores for one subject
            category_manager: provides category weights

        Returns:
            float: subject average (0–100)
        """

        categories = category_manager.get_categories()
        weighted_total = 0.0
        weight_used = 0.0

        for category_name, score in subject_grades.items():
            if category_name in categories:
                weight = categories[category_name].weight / 100
                weighted_total += score * weight
                weight_used += weight

        return weighted_total / weight_used if weight_used else 0.0

    # -------------------------------------------------------------------------
    # Letter Grade Conversion
    # -------------------------------------------------------------------------
    def get_letter_grade(self, average):
        """
        Converts numeric score to letter grade.
        """

        if average >= 90:
            return "A"
        elif average >= 80:
            return "B"
        elif average >= 70:
            return "C"
        elif average >= 60:
            return "D"
        return "F"

    # -------------------------------------------------------------------------
    # GPA Conversion (4.0 Scale)
    # -------------------------------------------------------------------------
    def get_gpa(self, average):
        """
        Converts numeric score to GPA.
        """

        if average >= 90:
            return 4.0
        elif average >= 80:
            return 3.0
        elif average >= 70:
            return 2.0
        elif average >= 60:
            return 1.0
        return 0.0