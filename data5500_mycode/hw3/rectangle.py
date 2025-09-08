class Rectangle:
    def __init__(self, length, width):
        self.length = length
        self.width = width
    
    def area(self):
        return self.length * self.width

rect = Rectangle(5, 3)

print("Area of rectangle:", rect.area())
#Chat GPT: How would I create a class called rectangle with attributes length and width in python? Also, how would I calculate the area of that rectangle?