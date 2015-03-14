"""
fuzz.py

SWEN-331 Fuzzer Project.
See the included README.md file.

Main entrance point for the fuzzer.
"""

import module_check

# Do all imports if the required packages were found
if module_check.all_found:
    from url import Url
    from utils import load_lines_from_file, parse_args
    from crawl import crawl
    from sys import argv

VALID_COMMANDS = ['discover', 'test']

""" 
The main function.
Parses command line arguments and call crawl.
"""
def main():

    # Parse the arguments
    args = parse_args()

    # Validate arguments
    if (args.command.lower() not in VALID_COMMANDS):
        print("invalid command %s." % args.command)
        parser.print_help()
        exit()

    # Discover setup

    # Validate custom auth argument
    auth = ""
    valid_custom_auth = ["dvwa", "bodgeit"]
    if (args.custom_auth and args.custom_auth.lower() in valid_custom_auth):
        auth = args.custom_auth.lower()

    words = list()
    url = Url(args.url)

    if (args.common_words):
        words = load_lines_from_file(args.common_words)

    extensions = load_lines_from_file("extensions.txt")

    # Build the page guessing Urls.
    guessed_urls = list()
    for word in words:
        for extension in extensions:
            guessed_urls.append(Url(url.url + '/' + word + '.' + extension))

    if (args.slow == None): # If the argument was excluded, set default
        timeout = .5 # 500ms is the default timeout for requests
    else: # If the argument was set, parse timeout
        try:
            timeout = int(args.slow)/1000 # Convert from MS to seconds
        except:
            print("Invalid value for argument 'slow': %s", args.slow)
            exit()

    # Test setup
    test = False
    vectors = list()
    sensitive = list()
    if (args.command.lower() == "test"):
        # Set up to do the testing version
        test = True

        # Set up the additional testing parts here (sensitive data leaked, lack of sanitization)
        if args.vectors:
            vectors = load_lines_from_file(args.vectors)

        if args.sensitive:
            sensitive = load_lines_from_file(args.sensitive)


    crawl(url, guessed_urls, auth, test, timeout, vectors, sensitive)

    return

if __name__ == "__main__" and module_check.all_found:
    main()
