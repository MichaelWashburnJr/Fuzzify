from argparse import ArgumentParser
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
    A list of lines found
"""
def load_lines_from_file(filename):
    lines = []
    for line in open(filename):
        lines.append(line.strip())
    return lines

"""
Creates an argument parser for the program. Use it to parse the CL args
Putting this code here clears up main a bunch.
Returns:
    Parsed command line arguments
"""
def parse_args():
        # Initialize an argument parser
    parser = ArgumentParser(
        description="Discover vulnerabilities for web applications"
    )
    # Define 'help' strings up here to be cleaner
    command_desc = ("[ discover / test ] Whether to discover available pages"+
        " or test for vulnerabilities")
    url_desc = "The URL of the website to discover or test"
    common_desc = ("(discover only) Text file containing a list of common "+
        "words to try when searching for pages")
    auth_desc = "[ dvwa / bodgeit ] The custom authentication method to use"
    vect_desc = "A file containing common strings used to exploit web pages"
    sens_desc = ("A file containing data that is determined to be \"sensitive"+
        "\", i.e. users should not see it")
    rand_desc = ("When off, try each input to each page systematically."+
        " When on, choose a random page, then a random input field and test"+
        " all vectors. Default: false.")
    slow_desc = ("Number of milliseconds considered when a response is cons"+
        "idered \"slow\". Default is 500 milliseconds")


    # Add command line arguments to the parser
    parser.add_argument('command', metavar='command', type=str,
        help=command_desc)
    parser.add_argument('url', metavar='url', type=str, help=url_desc)
    parser.add_argument('--common-words', metavar='<file>', help=common_desc, 
        required=True)
    parser.add_argument('--custom-auth', metavar='string', help=auth_desc)
    parser.add_argument('--vectors', metavar='<file>', help=vect_desc)
    parser.add_argument('--sensitive', metavar='<file>', help=sens_desc)
    parser.add_argument('--random', metavar='[true/false]', help=rand_desc)
    parser.add_argument('--slow', metavar='<ms>', help=slow_desc)

    return parser.parse_args()
