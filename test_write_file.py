from functions.write_file import write_file

r1 = write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum")
print(r1)

r2 = write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet")
print(r2)

r3 = write_file("calculator", "/tmp/temp.txt", "this should not be allowed")
print(r3)

