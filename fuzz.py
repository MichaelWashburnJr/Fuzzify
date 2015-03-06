import module_check

#do all imports if the required packages were found
if module_check.all_found:
    from url import Url
    from utils import load_common_words
    from crawl import crawl
    from sys import argv
    from argparse import ArgumentParser

VALID_COMMANDS = ['discover', 'test']

""" The main function """
def main():
    # initialize an argument parser
    parser = ArgumentParser(
        description="Discover vulnerabilities for web applications"
    )
    # define 'help' strings up here to be cleaner
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


    # add command line arguments to the parser
    parser.add_argument('command', metavar='command', type=str,
        help=command_desc)
    parser.add_argument('url', metavar='url', type=str,
        help=url_desc)
    parser.add_argument('--common-words', metavar='<file>', help=common_desc, required=True)
    parser.add_argument('--custom-auth', metavar='string', help=auth_desc)
    parser.add_argument('--vectors', metavar='<file>', help=vect_desc)
    parser.add_argument('--sensitive', metavar='<file>', help=sens_desc)
    parser.add_argument('--random', metavar='[true/false]', help=rand_desc)
    parser.add_argument('--slow', metavar='<ms>', help=slow_desc)

    # parse the arguments
    args = parser.parse_args()

    # validate arguments
    if (args.command.lower() not in VALID_COMMANDS):
        print("invalid command %s." % args.command)
        parser.print_help()
        exit()
    if (args.command.lower() == "test"):
        print("test not implemented yet")
        exit()

    #validate custom auth arg
    auth = ""
    valid_custom_auth = ["dvwa", "bodgeit"]
    if (args.custom_auth and args.custom_auth.lower() in valid_custom_auth):
        auth = args.custom_auth.lower()

    words = []
    url = Url(args.url)
    domain = url.domain # parse the domain name from the given URL

    if (args.common_words):
        words = load_common_words(args.common_words)

    extensions = load_common_words("extensions.txt")

    # This is where stuff starts to happen

    # Build the page guessing Urls.
    guessed_urls = []
    for word in words:
        for extension in extensions:
            guessed_urls.append(Url(url.url + '/' + word + '.' + extension))

    crawl(domain, url, guessed_urls, auth)

    return

if __name__ == "__main__" and module_check.all_found:
    main()