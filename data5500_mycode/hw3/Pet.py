class Pet:
    average_lifespans = {
        "dog": 13,
        "cat": 15,
        "rabbit": 9,
        "parrot": 50
    }
    
    def __init__(self, name, age, species):
        self.name = name
        self.age = age
        self.species = species.lower()
    
    def age_in_human_years(self):
        """Convert pet's age to human equivalent based on species."""
        if self.species == "dog":
            return self.age * 7
        elif self.species == "cat":
            return self.age * 6
        elif self.species == "rabbit":
            return self.age * 8
        elif self.species == "parrot":
            return self.age * 5
        else:
            return self.age
    
    def get_average_lifespan(self):
        """Return average lifespan for this pet's species."""
        return Pet.average_lifespans.get(self.species, "Unknown lifespan")

pet1 = Pet("Buddy", 3, "Dog")
pet2 = Pet("Whiskers", 4, "Cat")
pet3 = Pet("Coco", 2, "Parrot")

for pet in [pet1, pet2, pet3]:
    print(f"{pet.name} the {pet.species.capitalize()} is {pet.age} years old.")
    print(f"In human years: {pet.age_in_human_years()}")
    print(f"Average lifespan of a {pet.species}: {pet.get_average_lifespan()} years")
    print("-" * 40)

#ChatGPT Conversations: How would I create a variable called species to store the species of a certain pet?