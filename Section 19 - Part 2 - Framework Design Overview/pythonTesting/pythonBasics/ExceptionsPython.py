

ItemsInCart = 0
#2 items will be added to cart

if ItemsInCart != 2: #raise Exception("Products Cart count not matching")
    pass

assert(ItemsInCart == 0)

#try , catch

try:
    with open('test.txt', 'r') as reader:
        reader.read()

except:
    print("SOme how i reached this block because there is failure in try block")


try:
    with open('test.txt', 'r') as reader:
        reader.read()

except Exception as e:
    print(e)

finally:
    print("cleaning up records")








