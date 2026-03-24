# print("Hello, World!")
# print(10 + 5)         # prints 15
# print("Name:", "Charitra")  # prints: Name: Charitra

# name = "Charitra"
# age = 21
# height = 5.9
# is_developer = True

# print(type(42))       # <class 'int'>
# print(type("hello"))  # <class 'str'>

# x = "10"
# y = int(x)       # string → int → 10
# z = float(x)     # string → float → 10.0
# a = str(100)     # int → string → "100"
# b = bool(0)      # 0 → False, anything else → True

# x = 10
# y = 3

# print(x + y)   # 13  — addition
# print(x - y)   # 7   — subtraction
# print(x * y)   # 30  — multiplication
# print(x / y)   # 3.333 — division (always float)
# print(x // y)  # 3   — floor division (drops decimal)
# print(x % y)   # 1   — modulo (remainder)
# print(x ** y)  # 1000 — power (10 to the 3)


# print(10 == 10)  # True
# print(10 != 5)   # True
# print(10 > 5)    # True
# print(10 < 5)    # False
# print(10 >= 10)  # True
# print(10 <= 9)   # False

# print(True and False)  # False — both must be True
# print(True or False)   # True  — at least one True
# print(not True)        # False — reverses


# x = 10
# x += 5   # x = x + 5 → 15
# x -= 3   # x = x - 3 → 12
# x *= 2   # x = x * 2 → 24
# x /= 4   # x = x / 4 → 6.0
# x //= 2  # x = x // 2 → 3.0
# x **= 3  # x = x ** 3 → 27.0


# s = "Python"
# print(s[0])     # P  — first character
# print(s[-1])    # n  — last character
# print(s[0:3])   # Pyt — index 0 to 2
# print(s[::2])   # Pto — every 2nd character
# print(s[::-1])  # nohtyP — reversed

# name = "Charitra"
# age = 21
# print(f"My name is {name} and I am {age} years old.")
# # My name is Charitra and I am 21 years old.

# s = "  Hello World  "

# print(s.upper())       # "  HELLO WORLD  "
# print(s.lower())       # "  hello world  "
# print(s.strip())       # "Hello World"  — removes spaces
# print(s.replace("World", "Python"))  # "  Hello Python  "
# print(s.split())       # ['Hello', 'World']
# print(s.startswith("  H"))  # True
# print(s.endswith("  "))     # True
# print(len(s))          # 15
# print("hello".capitalize())  # Hello
# print("hello world".title()) # Hello World
# print("hello".find("l"))     # 2 — index of first match


# x = 10
# if x > 0:
#     if x > 5:
#         print("Greater than 5")
#     else:
#         print("Between 1 and 5")


# status = "Adult" if age >= 18 else "Minor"

# for i in range(5):
#     print(i)       # 0 1 2 3 4

# for i in range(1, 6):
#     print(i)       # 1 2 3 4 5

# for i in range(0, 10, 2):
#     print(i)       # 0 2 4 6 8

# for char in "Python":
#     print(char)    # P y t h o n

# fruits = ["apple", "banana", "cherry"]

# print(fruits[0])    # apple
# print(fruits[-1])   # cherry
# print(fruits[1:3])  # ['banana', 'cherry']

# matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
# print(matrix[1][2])  # 6


# # 9. Tuples
# # Ordered, immutable (cannot change after creation).
# pythoncoords = (10, 20)
# print(coords[0])   # 10


# # Unpacking
# x, y = coords
# print(x, y)        # 10 20
# pythonRED = (255, 0, 0)
# pythont = (5,)   # tuple
# t = (5)    # just an int, NOT a tuple


# person = {
#     "name": "Charitra",
#     "age": 21,
#     "city": "Kathmandu"
# }

# print(person["name"])         # Charitra
# print(person.get("age"))      # 21
# print(person.get("phone", "N/A"))  # N/A — default if not found


# users = {
#     "user1": {"name": "Ram", "age": 20},
#     "user2": {"name": "Sita", "age": 22}
# }
# print(users["user1"]["name"])  # Ram

# s = {1, 2, 3, 3, 2}
# print(s)   # {1, 2, 3} — duplicates removed automatically


# a = {1, 2, 3, 4}
# b = {3, 4, 5, 6}

# print(a | b)   # {1,2,3,4,5,6} — union (all)
# print(a & b)   # {3, 4}        — intersection (common)
# print(a - b)   # {1, 2}        — difference (in a not b)
# print(a ^ b)   # {1,2,5,6}     — symmetric difference

# # 12. List Comprehensions
# # A shorter way to create lists.
# # Normal way:
# pythonsquares = []
# for x in range(10):
#     squares.append(x**2)
# # With comprehension:
# pythonsquares = [x**2 for x in range(10)]
# # With condition:
# pythonevens = [x for x in range(20) if x % 2 == 0]
# pythonmatrix = [[i * j for j in range(1, 4)] for i in range(1, 4)]




# # 13. Functions
# # Reusable block of code.
# # python
# def greet(name):
#     return f"Hello, {name}!"

# print(greet("Charitra"))   # Hello, Charitra!
# # Default arguments:
# # python
# def greet(name, greeting="Hello"):
#     return f"{greeting}, {name}!"

# print(greet("Ram"))            # Hello, Ram!
# print(greet("Ram", "Namaste")) # Namaste, Ram!
# def info(name, age):
#     print(f"{name} is {age}")

# info(age=21, name="Charitra")  # order doesn't matter
# def min_max(nums):
#     return min(nums), max(nums)

# low, high = min_max([3, 1, 9, 5])

# 14. *args and **kwargs
# *args — accepts any number of positional arguments as a tuple:
# pythondef total(*args):
#     return sum(args)

# print(total(1, 2, 3, 4, 5))  # 15
# **kwargs — accepts any number of keyword arguments as a dict:
# pythondef show_info(**kwargs):
#     for key, value in kwargs.items():
#         print(f"{key}: {value}")

# show_info(name="Charitra", age=21, city="Kathmandu")


# class Dog:
#     def __init__(self, name, age):  # constructor
#         self.name = name            # instance attribute
#         self.age = age

#     def bark(self):
#         print(f"{self.name} says Woof!")

# # Creating objects
# dog1 = Dog("Bruno", 3)
# dog2 = Dog("Max", 5)

# dog1.bark()          # Bruno says Woof!
# print(dog2.name)     # Max


# class Vector:
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y

#     def __str__(self):           # called by print()
#         return f"Vector({self.x}, {self.y})"

#     def __add__(self, other):    # called by +
#         return Vector(self.x + other.x, self.y + other.y)

#     def __len__(self):           # called by len()
#         return 2

# v1 = Vector(1, 2)
# v2 = Vector(3, 4)
# print(v1)          # Vector(1, 2)
# print(v1 + v2)     # Vector(4, 6)
# print(len(v1))     # 2
