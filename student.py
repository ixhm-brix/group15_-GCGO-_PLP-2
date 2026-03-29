class Student:
    def __init__(self, full_name, student_id):
        self.full_name = full_name
        self.student_id = student_id
        self.grades = {}

    def add_grade(self, subject, category, score):
        if subject not in self.grades:
            self.grades[subject] = {}
        self.grades[subject][category] = score

    def get_grades(self):
        return self.grades

    def get_subjects(self):
        return list(self.grades.keys())

    @staticmethod
    def validate_id(student_id):
        if not student_id.strip() or " " in student_id:
            return False
        return True

    def __str__(self):
        return f"Student: {self.full_name} (ID: {self.student_id})"
