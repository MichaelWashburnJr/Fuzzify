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

"""
Parses the domain name from a URL. If no protocol is specified, it is assumed
that the path is a relative path, and so no domain can be found.
params:
    url: the url to parse
returns:
    the domain name from the given url
"""
def get_domain(url):
    try:
        index = url.index("://")
        url = url[index + 3:]
    except ValueError:
        return ""
    try:
        index = url.index("/")
        url = url[:index]
    except ValueError:
        pass

    return url

"""
Determine if the domain for a given URL matches the base domain.
(This way we can ignore URLs to external sites)
params:
    base: The base domain (the one specified in command line args)
    url_test: The url to check against the base domain
returns:
    true if the url is a relative path or the domain of the URL matches
        the base domain.
"""
def domain_matches(base, url_test):
    test = get_domain(url_test).strip()
    # check for relative paths
    if (test == ""):
        return True
    return base.lower() == test.lower()

"""
Given a list of URLs, and a base domain, return a list with all URLs given
that are a part of the base domain.
params:
    base: The base domain (the one specified in command line args)
    urls: A list of URLs to check against the base domain and filter
returns
    A list of URLs that match the given domain
"""
def filter_externals(base, urls):
    filtered_urls = []
    for url in urls:
        if (domain_matches(base, url)):
            filtered_urls.append(url)
    return filtered_urls