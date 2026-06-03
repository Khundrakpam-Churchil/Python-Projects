#Day 2: 30 Days of Python Variables

import math

first_name = 'Churchil'
last_name = 'Khundrakpam'
full_name = first_name + ' ' + last_name
country = 'India'
city = 'Imphal'
age = 26
year = 2026
is_married = False
is_true = True
is_light_on = False



first_name_type = type(first_name)
last_name_type = type(last_name)
full_name_type = type(full_name)
country_type = type(country)
city_type = type(city)
age_type = type(age)
year_type = type(year)
is_married_type = type(is_married)
is_true_type = type(is_true)
is_light_on_type = type(is_light_on)


first_name_length = len(first_name)
last_name_length = len(last_name)
is_first_name_longer = first_name_length > last_name_length
is_last_name_longer = last_name_length > first_name_length
is_name_length_equal = first_name_length == last_name_length


num_one = 5
num_two = 4
total = num_one + num_two
diff = num_one - num_two
product = num_one * num_two
division = num_one / num_two
remainder = num_two % num_one
exp = num_one ** num_two
floor_division = num_one // num_two


radius = 30
area_of_circle = math.pi * radius ** 2
circum_of_circle = 2 * math.pi * radius


radius_input = float(input('Enter circle radius: '))
area_from_input = math.pi * radius_input ** 2

first_name = input('Enter your first name: ')
last_name = input('Enter your last name: ')
country = input('Enter your country: ')
age = input('Enter your age: ')


help('keywords')

a, b, c = 1, 2, 3
