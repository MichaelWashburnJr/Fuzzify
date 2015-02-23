import module_check
from utils import Url

#do all imports if the required packages were found
if module_check.all_found:
    from utils import get_domain, load_common_words
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
    command_desc = ("[ discover / test ] Whether to discover available pages" +
        " or test for vulnerabilities")
    url_desc = "The URL of the website to discover or test"
    common_desc = ("(discover only) Text file containing a list of common " +
        "words to try when searching for pages")

    # add command line arguments to the parser
    parser.add_argument('command', metavar='command', type=str,
        help=command_desc)
    parser.add_argument('url', metavar='url', type=str,
        help=url_desc)
    parser.add_argument('--common-words', metavar='file', help=common_desc)

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

    words = []
    url = Url(args.url)
    domain = url.domain # parse the domain name from the given URL

    if (args.common_words):
        words=load_common_words(args.common_words)
    extensions = load_common_words("extensions.txt")

    # This is where stuff starts to happen
    crawl(domain, url)
    return

if __name__ == "__main__" and module_check.all_found:
    main()