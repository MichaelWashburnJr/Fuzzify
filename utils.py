"""
util.py

Holds helper and general utility functions
"""

global debug_flag
debug_flag = False

"""
Handle debug printing.
"""
def debug(text):
    global debug_flag
    if debug_flag:
        print(text)


"""
Reads in each line from a text file and returns a list of the words found.
params:
    filename: path to the file to open
returns:
    An array-list of words found
"""
def load_common_words(filename):
    words = []
    for line in open(filename):
        words.append(line.strip())
    return words
