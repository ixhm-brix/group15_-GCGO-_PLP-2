
class GradeCategory:


    def __init__(self, name, weight):  
        self.name = name
        self.weight = weight

    def __str__(self):

        return f"{self.name} ({self.weight}%)"

class CategoryManager:


    def __init__(self):

        self.categories = {}
        self.add_category("Exam", 40)
        self.add_category("Midterm", 25)
        self.add_category("Quiz", 20)
        self.add_category("Exercise", 10)
        self.add_category("Assignment", 5)


    def add_category(self, name, weight):

        self.categories[name] = GradeCategory(name, weight)

    def remove_category(self, name):
 
        if name in self.categories:
            del self.categories[name]
            return True
        else:
            return False

    def get_categories(self):

        return self.categories

    def validate_weights(self):
        total = 0

        for category in self.categories.values():
            total += category.weight

        if total != 100:

            raise ValueError(
                f"Category weights must add up to 100%. "
                f"Current total is {total}%. "
                f"Please adjust your categories."
            )

        return True

    def display_categories(self):
        print("=" * 35)
        print("  GRADE CATEGORIES".center(35))
        print("=" * 35)
        print(f"  {'Category':<20} {'Weight':>8}")
        print("-" * 35)

        for name, category in self.categories.items():
            print(f"  {name:<20} {category.weight:>7}%")

        print("=" * 35)
        total = sum(c.weight for c in self.categories.values())
        print(f"  {'TOTAL':<20} {total:>7}%")
        print("=" * 35)
