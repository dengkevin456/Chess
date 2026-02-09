import os
"""
A simple script of counting how many lines of code I have written in total for this project.
"""

directory_path = "."

def count_lines(filename):
    with open(filename, 'r') as f:
        line_count = sum(1 for line in f)
    return line_count

only_files = filter(lambda x: os.path.isfile(os.path.join(directory_path, x)), os.listdir(directory_path))

a = 0
for f in only_files:
    x = count_lines(f)
    print(f"{f}: {x}")
    a += x
print(a)


