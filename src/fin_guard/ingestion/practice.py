import random

#

## Exercise 1
# On the line below, create a variable named on_mars_right_now and assign it the boolean value of False
on_mars_right_now = False
assert on_mars_right_now == False
print('exercise1 is complete')

fruits =['Apple','Banana','kiwi','strawb']
numbers = [1,2,9,4,3,5,6,7,-8]

new_fruits = [fruit for fruit in fruits if sum(1 for char in fruit if char.lower() in 'aeiou') >=2]

print(new_fruits)




even_numbers =[num for num in numbers if num%2 !=0 ]
print(even_numbers)

negative_numbers = [num for num in numbers if num <0]
print(negative_numbers)


#programme to write febbonaic series 
# 1 1 2 3 5 8 13 
a =1 
b=1 
for i in range(5):
    print(a)
    a, b = b,a+b

vegetables = ["eggplant", "broccoli", "carrot", "cauliflower", "zucchini"]
assert vegetables == ["eggplant", "broccoli", "carrot", "cauliflower", "zucchini"]
print('exercise 3 is complete')

numbers = [1,2,9,4,3,5,6,7,-8]
numbers.sort()
print(numbers)
#numbers.reverse()

print(numbers[::-1])
vegetables = ["eggplant", "broccoli", "carrot", "cauliflower", "zucchini"]
vegetables.sort(reverse=False)
print(vegetables)

fruits_n_veggies = fruits+vegetables
print(fruits_n_veggies)


positive_even_number = random.randrange(2, 101, 2)
negative_even_number = random.randrange(-100, -1, 2)

positive_odd_number = random.randrange(1, 100, 2)
negative_odd_number = random.randrange(-101, 0, 2)
print("We now have some random numbers available for future exercises.")
print("The random positive even number is", positive_even_number)
print("The random positive odd nubmer is", positive_odd_number)
print("The random negative even number", negative_even_number)
print("The random negative odd number", negative_odd_number)

def say_hello(name):
    print(f'Hello {name} please check your inputs'  )
    return f'Hello {name} please check your inputs' 
#say_hello('pavani')
assert say_hello('pavani') =='Hello pavani please check your inputs' 
print('check complete')


def add_one(number):
    return number+1 

assert add_one(5) ==6
print('complete')

def is_positive(number):
   if number >0:
       return True
   elif number ==0:
       return 'zero'
   else:
       return False

print(is_positive(0))
print(is_positive(-1))
print(is_positive(7))

def is_positive_odd(number):
    if number >0 and number %2 !=0:
        return True
    else:
        return False

print(is_positive_odd(7))

def rev_sign(number):
   return number * -1

print(rev_sign(-4))

print(rev_sign(4))

def suare_of_number(number):
    return number**2

print(suare_of_number(5))

def change(x, y=2):
    x += y
    return x

x = 5
print(change(x))
print(x)