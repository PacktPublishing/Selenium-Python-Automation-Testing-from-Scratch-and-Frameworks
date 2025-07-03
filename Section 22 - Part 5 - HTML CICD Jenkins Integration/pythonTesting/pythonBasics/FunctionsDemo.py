#In Python, function is a group of related statements that perform a specific task.
#Function Declaration


def GreetMe(name):
    print("Good Morning"+name)
    #Function Call


def AddIntegers(a, b):
    return a+b
dic = {"a": 2, 4:"bcd", "c": "Hello world"}

# GreetMe("Rahul Shetty")
#
# print(AddIntegers(2, 3))


itemsInCart = 0
#some operation
if itemsInCart != 2:#    raise Exception("x should not exceed 7 ")
    pass

#assert(itemsInCart == 2)


try:
    with open('file.log') as file:
        read_data = file.read()
except:

    print('Could not open file.log')


try:
    with open('test.txt', 'w') as file:
        read_data = file.write("hello")
except Exception as e:

    print(e)

finally:
    print('Cleaning up, irrespective of any exceptions.')














