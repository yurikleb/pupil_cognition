import csv

b = [1,2,3,4,5,6,7,8,9,10,11,"lol","hello"]
c = enumerate(b)

print(c)

with open("output.csv", "w", newline='') as myFile:
    print("Writing CSV")
    writer = csv.writer(myFile)
    writer.writerows(c)

print(c)