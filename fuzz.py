from utils import *
from sys import argv

""" The main function """
def main():
	# TODO Parsing arguments
	words = load_common_words("words.txt")
	extensions = load_common_words("extensions.txt")
	print(words)

if __name__ == "__main__":
	main()