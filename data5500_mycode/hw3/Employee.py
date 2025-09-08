class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
    
    def increase_salary(self, percentage):
        self.salary += self.salary * (percentage / 100)

emp = Employee("John", 5000)

emp.increase_salary(10)

# Print updated salary
print(f"Updated salary of {emp.name}: {emp.salary}")
#Chat GPT: How would I create a class called employee with attributes name and salary? Also, how would I implement a method within the class that increases the salary of the employee by a given percentage?