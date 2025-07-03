file = open('test.txt')
#with open('test.txt') as reader:
    # print(file.read()) read all the cntent in file  (3) characters

    # print(file.readline(6))   read one single line at a time
    # print(file.readline(3))
    # for i in range(1, 5):
     #     print(file.readline())

line = file.readline()
while line!= "":
    print(line)
    line = file.readline()


# for line in reader.readlines():
    #     print(line)


file.close()

with open('test.txt', 'r') as reader:
    dog_breeds = reader.readlines()
    with open('test.txt', 'w') as writer:


        for breed in reversed(dog_breeds):
            writer.write(breed)
