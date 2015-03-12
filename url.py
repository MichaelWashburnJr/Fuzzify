from utils import debug

"""
url.py
File to abstract URL parsing logic
"""

class Url():
    __slots__ = ('domain', 'url', 'params')

    def __init__(self, url, source="", domain=""):
        if '#' in url: #chop off anchors
            url = url[:url.index("#")]
        # If URL empty string, make things a little easier
        if (url == "" or url.startswith("mailto:") or url.startswith("javascript:")):
            self.url = source
            self.domain = domain
            self.params = []
            return
        debug("URL: %s" % url)
        debug("Source: %s" % source)
        debug("Domain: %s" % domain)
        self.url = to_absolute(domain, source, url)
        debug("Absolute URL: %s" % self.url)
        self.domain = get_domain(self.url) # Cover all cases
        debug("Interpreted domain: %s" % self.domain)
        # Now, we need the parts of the URL after the domain.
        # The domain IS a part of the URL at this point, guaranteed.
        d = self.domain # alias
        debug("Constructing URL. domain: %s" % d)
        path = self.url[self.url.index(d) + len(d):]
        debug("Path: %s" % path)
        path = path.strip("/")
        debug("Stripped to: %s" % path)
        parts = path.split("/")
        debug("Split to %r" % parts)
        canonical_parts = []
        self.params = []
        debug("Iterating through parts")
        for part in parts:
            if (part == ""):
                continue
            debug("Found part: %s" % part)

            if ('?' in part):
                self.params += parse_query_string(part.split('?')[1])
                debug("Inputs: %s " % self.params)
                part = part.split("?")[0]

            if (part == ".."): # Need to remove the previous part
                if (len(canonical_parts) is not 0):
                    debug("Found '..', removing %s" % canonical_parts.pop())

            elif (part == "."):
                continue

            else:
                canonical_parts.append(part)
        debug("Final parts: %r" % canonical_parts)
        

        final_url = "http://" + self.domain
        for p in canonical_parts:
            final_url += "/" + p
        debug("Final URL: %s" % final_url)
        self.url = final_url

    def get_absolute(self):
        return self.url

    def __str__(self):
        return self.get_absolute()

    def __eq__(self, other):
        return self.get_absolute() == other.get_absolute()

    def __hash__(self):
        return hash(self.get_absolute())

"""
Returns a list of parameters gathered from the "Query String" found at
the end of some URLs. Query strings are of the form:
    ?[param]=[value]&[param2]=[value2]$...
Params:
    string: The query string (first question mark removed)
Returns:
    A list of parameters parsed from the query string.
"""
def parse_query_string(string):
    params = []
    parts = string.split("&")
    for part in parts:
        input_field = part.split("=")[0]
        params.append(input_field)
    return params

"""
Determine if a url is an absolute URL (it contains a protocol specifier)
Params:
    url: The url to check for absoluteness
Returns:
    true if the URL is absolute, false otherwise
"""
def is_absolute(url):
    return "://" in url

"""
Converts a URL to absolute from if it is not already in absolute form.
Params:
    base: the base domain
    source: the URL we came from
    url: The URL to convert to an absolute URL
Returns:
    An absolute URL referring to the given path.
"""
def to_absolute(base, source, url):
    try:
        source = source[:source.index("#")]
    except ValueError:
        pass

    try:
        source = source[:source.index("?")]
    except ValueError:
        pass

    if '/' in source:
        # Use everything up to and including the last slash as the base
        # reverse the source
        new_source = source[::-1]
        # Grab everything from the first slash on
        new_source = new_source[new_source.index('/'):]
        # reverse it again
        source = new_source[::-1]

    # if URL already absolute, just return it
    if is_absolute(url):
        return url

    if url[0] == "/": # e.g. /info/about.html
        return "http://" + base + url

    else: # e.g. projects/medialist
        url = url.rstrip("#")
        return source + "/" + url

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
        if domain_matches(base, str(url)):
            filtered_urls.append(url)
    return filtered_urls