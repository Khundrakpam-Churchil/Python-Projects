import sys
import math


print("Python version:", sys.version)

x, y = 3, 4
print("Addition:", x + y)
print("Subtraction:", x - y)
print("Multiplication:", x * y)
print("Modulus:", x % y)
print("Division:", x / y)
print("Exponential:", x ** y)
print("Floor division:", x // y)

first_name = "YourName"
last_name = "YourFamilyName"
country = "YourCountry"

print(first_name)
print(last_name)
print(country)
print("I am enjoying 30 days of python")

values = [10, 9.8, 3.14, 4 - 4j, ["Churchil", "Khundrakpam", "India"], first_name, last_name, country]
for value in values:
    print(value, "type:", type(value))


integer_example = 7
float_example = 3.14
complex_example = 4 - 4j
string_example = "Hello, 30 days of Python!"
boolean_example = True
list_example = ["Churchil", "Khundrakpam", "India"]
tuple_example = (2, 3, 5)
set_example = {1, 2, 3}
dictionary_example = {"name": "Churchil", "language": "Python", "country": "India"}

print("\nPython data type examples:")
print("Integer:", integer_example, type(integer_example))
print("Float:", float_example, type(float_example))
print("Complex:", complex_example, type(complex_example))
print("String:", string_example, type(string_example))
print("Boolean:", boolean_example, type(boolean_example))
print("List:", list_example, type(list_example))
print("Tuple:", tuple_example, type(tuple_example))
print("Set:", set_example, type(set_example))
print("Dictionary:", dictionary_example, type(dictionary_example))

p1 = (2, 3)
p2 = (10, 8)
distance = math.dist(p1, p2)
print(f"\nEuclidean distance between {p1} and {p2}: {distance}")
