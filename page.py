"""
page.py

Handles Page Sets, Pages, and Input Fields.
"""

# External modules
import requests
from bs4 import BeautifulSoup as bs

# Standard
import itertools

# Other files in project
from url import Url, filter_externals
import crawl
import html

"""
Represents an HTML input field on a page.
"""
class InputField:

    def __init__(self, field_element, url):
        self.name = field_element.get('name')
        self.id = field_element.get('id')
        self.type = field_element.get('type')
        self.from_url = url

    def __str__(self):
        return "name: {!s:<17} id: {!s:<17} type: {!s:<15}".format(self.name, self.id, self.type)

"""
Represents a Page, including links, input fields, and URL.
"""
class Page:
    __slots__ = ('base_url', 'domain', 'params', 'input_fields',
                 'links', 'status_code', 'test', 'is_sanitary')

    def __init__(self, url, test, req_timeout):

        self.params = set()
        self.input_fields = list()
        self.links = list()
        self.test = test
        self.status_code = -1 # Assume the page will time out. 
        self.is_sanitary = True

        self.base_url = url.get_absolute()
        self.params.update(url.params)
        self.domain = url.domain


        r = None
        try:
            r = crawl.session.get(url.url, timeout=req_timeout)
        except requests.exceptions.Timeout:
            print("  Timeout exceeded.")

        # Attempt reauthentication
        if r != None and r.status_code == 403:
            print("  Attempting re-auth.")
            crawl.perform_auth()
            try:
                r = crawl.session.get(url.url, timeout=req_timeout)
            except requests.exceptions.Timeout:
                print("  Timeout exceeded.")

        # If the request is valid and not timed out 
        if r != None:
            self.status_code = r.status_code
            #self.base_url = Url(r.url).get_absolute()

            beautiful = bs(r.content)

            # Find all input fields
            for input_field in beautiful.find_all('input'):
                self.input_fields.append(InputField(input_field, url))

            # Find all links
            for link in beautiful.find_all('a'):
                link_href = link.get('href')
                if link_href is not None:
                    self.links.append(Url(link_href, source=r.url, domain=url.domain))

            self.links = filter_externals(self.domain, self.links)

            if self.test:
                # Do the additional test actions (sensitive data leaks)
            
                # TODO: this would make a nice helper funtion that we could run
                #       all responses through to check for data leaks
                # for sensiword in sensitive_words:
                #     if (sensiword in r.content):
                #         print("You done goofed!")
                pass

    def __str__(self):
        return_str = ""

        return_str += "URL: {0}\n".format(self.base_url)
        if len(self.params) > 0:
            return_str += "    Variable(s) found:\n"
            for input_variable in self.params:
                return_str += "      - {0}\n".format(str(input_variable))
        if len(self.input_fields) > 0:
            return_str += "    Input field(s) found:\n"
            for input_field in self.input_fields:
                return_str += "      - {0}\n".format(str(input_field))

        return return_str.rstrip() # Strip the last newline character.

    """
    Test that the page sanitizes its inputs.
    Params:
        req_timeout: the Requests timeout, in seconds
        vectors: a list of inputs to try in forms
    """
    def test_sanitization(self, req_timeout, vectors):
        # Only try if there are inputs for this page
        print("Testing: " + self.base_url)
        if len(self.input_fields) > 0:
            for vector in vectors: # For each vector 
                try:

                    # If the vector has characters that should be escaped in it, test
                    if vector != html.escape(vector, quote=False):
                        #first reload the page
                        r = crawl.session.get(self.base_url, timeout=req_timeout)

                        # Gather inputs and values for the form
                        payload = dict()
                        beautiful = bs(r.content)
                        for input_field in beautiful.find_all('input'):                            
                            # If the type is "submit" or "hidden," dont use the vector
                            value = vector
                            if "type" in input_field and input_field["type"] in ("submit", "hidden"):
                                value = input_field["value"]
                            # Add the input to the payload
                            if "name" in input_field:
                                payload[input_field["name"]] = value

                        # Make the post request
                        r = crawl.session.post(self.base_url, data=payload)
                        if vector in r.text:
                            print("  Code not sanitized: " + vector)
                            self.is_sanitary = False;
                            # No need to continue once we no this page isn't sanitary...
                            break;

                # Catch the timeout exception only
                except requests.exceptions.Timeout:
                    print("  Timeout exceeded.")

    """
    Update the set of parameters with the parameters from the given URL.
    Params:
        url: the Url to get parameters from
    """
    def add_params_from_url(self, url):
        self.params.update(url.params)

    """
    Check if this Page's base Url matches the given Url.
    Params:
        url: the Url to match against
    Returns:
        True if this Page's base URL matches the given URL.
    """
    def matches_url(self, url):
        return self.base_url == url.get_absolute()

    """
    Get this Page's Url.
    Returns:
        A Url object representing this Page's base URL.
    """
    def get_url(self):
        return Url(self.base_url)

"""
Represents the set of Pages that are encountered in the crawl.
"""
class PageSet:
    __slots__ = ('pages', 'test', 'timeout', 'vectors')

    def __init__(self, test, timeout, vectors):
        self.pages = list()
        self.test = test
        self.timeout = timeout
        self.vectors = vectors

    def __str__(self):
        return_str = "\"OK\" Pages found:\n"
        not_ok_or_404_pages = list()
        timeout_pages = list()
        not_sanitary_pages = list()

        for page in self.pages:
            if page.status_code == 200:
                return_str += str(page) + '\n'
            elif page.status_code != 404:
                not_ok_or_404_pages.append(page)
            # Build list of unsanitized pages
            if not page.is_sanitary:
                not_sanitary_pages.append(page)


        if (len(not_ok_or_404_pages) > 0):
            return_str += "\nOther Status Pages Found:\n"

            not_ok_or_404_pages.sort(key=lambda p: p.status_code)
            other_statuses = [list(g) for k, g in itertools.groupby(not_ok_or_404_pages, lambda p: p.status_code)]

            for code in other_statuses:
                status_code = code[0].status_code
                if status_code == -1:
                    timeout_pages = code
                    continue

                return_str += "Status {0}:\n".format(str(status_code))
                for page in code:
                    return_str += str(page) + '\n'

        if (len(timeout_pages) > 0):
            return_str += "\nTimeout Pages Found:\n"
                
            for page in timeout_pages:
                return_str += str(page) + '\n'


        if(len(not_sanitary_pages) > 0):
            return_str += "\nPages with Sanitization Errors:\n"

            for page in not_sanitary_pages:
                return_str += str(page) + '\n'

        return return_str.rstrip() # Strip the last newline character.

    """
    Run sanitization tests on all pages.
    """
    def test_sanitization(self):
        print("\nTesting Sanitization...\n")
        for page in self.pages:
            page.test_sanitization(self.timeout, self.vectors)

    """
    If a Page exists that matches the given URL, 
        update the Page with the parameters from the URL and return None.
    Else, create and return a new Page based on the given URL.
    Params:
        url: the Url to check against
    Returns:
        Page if a Page was created.
        None if a Page was updated.
    """
    def create_or_update_page_by_url(self, url):
        page = self.get_page_by_url(url)
        if page is None:
            new_page = Page(url, self.test, self.timeout)
            self.add_page(new_page)
            return new_page
        else:
            page.add_params_from_url(url)
            return None

    """
    Get the Page that contains the given URL.
    Params:
        url: the Url to use for lookup
    Returns:
        Page if there is a matching Page.
        None if there isn't a matching Page.
    """
    def get_page_by_url(self, url):
        for page in self.pages:
            if page.matches_url(url):
                return page
        return None

    """
    Add the given Page to this PageSet.
    Params:
        page: the Page to add to this PageSet.
    """
    def add_page(self, page):
        self.pages.append(page)
