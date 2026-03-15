from datetime import datetime

def calculate_age(birth_year):
    current_year = datetime.now().year
    age = current_year - birth_year
    return age

born_year = int(input("Enter your birth year: "))
age = calculate_age(born_year)
print(f"Age: {age}")