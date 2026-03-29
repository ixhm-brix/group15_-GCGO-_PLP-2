from student import Student

class Cohort:
    def __init__(self, cohort_name):
        self.cohort_name = cohort_name
        self.students = {}

    def add_student(self, student):
        if student.student_id in self.students:
         # Check if this student's ID is already used in the cohort.
        # student.student_id accesses the id attribute of the Student object.
            return False
        
        # If the ID is new then, safe to add
        #self.students["STU001"] = <Student object>
        self.students[student.student_id] = student

        return True 

    def get_student(self, student_id):
        # Finds and returns the Student object with the given ID.
        return self.students.get(student_id, None)

    def get_all_students(self):
        # Returns a list of ALL Student objects in this cohort.
        return list(self.students.values())
        # self.students.values() gives all the Student objects stored.
        # list() turns that into a regular Python list.

    def student_exists(self, student_id):
        # Checks whether a student with the given ID is in a cohort.
        return student_id in self.students

    def get_student_count(self):
        # Returns the total number of students in a cohort.
        return len(self.students)

    def __str__(self):
        # Returns a readable summary string for a cohort.
        # Call get_student_number() to get the number of students.
        # Use an f-string to retrieve both the cohort name and the count.
        number = self.get_student_number()
        return f"Cohort: {self.cohort_name} ({number} student{'s' if number != 1 else ''})"
