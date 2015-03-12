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


class InputField:
    def __init__(self, field_element, url):
        self.name = field_element.get('name')
        self.id = field_element.get('id')
        self.type = field_element.get('type')
        self.from_url = url
    def __str__(self):
        return "name: {!s:<17} id: {!s:<17} type: {!s:<15}".format(self.name, self.id, self.type)

class Page:
    __slots__ = ('base_url', 'domain', 'params', 'input_fields', 'links', 'status_code')

    def __init__(self, url, req_timeout):

        self.params = set()
        self.input_fields = list()
        self.links = list()

        self.base_url = url.get_absolute()
        self.params.update(url.params)
        self.domain = url.domain
        self.status_code = -1 # Assume the page will time out. 

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

        return return_str.rstrip()

    def add_params_from_url(self, url):
        self.params.update(url.params)

    def matches_url(self, url):
        return self.base_url == url.get_absolute()

    def get_url(self):
        return Url(self.base_url)


class PageSet:
    __slots__ = ('pages', 'timeout')

    def __init__(self, timeout):
        self.pages = list()
        self.timeout = timeout

    def __str__(self):
        return_str = "\"OK\" Pages found:\n"
        not_ok_or_404_pages = list()
        timeout_pages = list()

        for page in self.pages:
            if page.status_code == 200:
                return_str += str(page) + '\n'
            elif page.status_code != 404:
                not_ok_or_404_pages.append(page)

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

        return return_str.rstrip()

    """
    Returns true if the page was added.
    """
    def create_or_update_page_by_url(self, url):
        page = self.get_page_by_url(url)
        if page is None:
            new_page = Page(url, self.timeout)
            self.add_page(new_page)
            return new_page
        else:
            page.add_params_from_url(url)
            return None

    def get_page_by_url(self, url):
        for page in self.pages:
            if page.matches_url(url):
                return page
        return None

    def add_page(self, page):
        self.pages.append(page)
