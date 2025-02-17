# importing the collections module
import collections

def distribute_array(total,number):
    dividend = int(total/number)
    array = [dividend for _ in range(number)]
    remainder = total - (number * dividend)

    for i in range(remainder):
       array[i] += 1

    return array

while True:
    total = int(input("Enter total"))
    number = int(input ("Enter number"))
    # getting the elements frequencies using Counter class
    elements_count = collections.Counter(distribute_array(total,number))
    # printing the element and the frequency
    for key, value in elements_count.items():
        print(f"{key}: {value}")


