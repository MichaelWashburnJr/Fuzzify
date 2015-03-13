"""
util.py

Holds helper and general utility functions
"""

global debug_flag
debug_flag = False

"""
Handle debug printing.
Params:
    text: the string to print.
"""
def debug(text):
    global debug_flag
    if debug_flag:
        print(text)


"""
Reads in each line from a text file and returns a list of all lines.
Params:
    filename: path to the file to open
Returns:
    An array-list of lines found
"""
def load_lines_from_file(filename):
    lines = []
    for line in open(filename):
        lines.append(line.strip())
    return lines
