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