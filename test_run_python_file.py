from functions.run_python_file import run_python_file

r1 = run_python_file("calculator", "main.py")
print(r1)

r2 = run_python_file("calculator", "main.py", ["3 + 5"]) 
print(r2)

r3 = run_python_file("calculator", "tests.py")
print(r3)

r4 = run_python_file("calculator", "../main.py")
print(r4)

r5 = run_python_file("calculator", "nonexistent.py")
print(r5)

r6 = run_python_file("calculator", "lorem.txt")
print(r6)
