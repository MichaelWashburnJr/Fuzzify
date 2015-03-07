import requests
from bs4 import BeautifulSoup as bs
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

    def __init__(self, url):

        self.params = set()
        self.input_fields = list()
        self.links = list()

        self.base_url = url.get_absolute()
        self.params.update(url.params)
        self.domain = url.domain

        try:
            r = crawl.session.get(url.url)
        except requests.exceptions.Timeout:
            print("  Timeout exceeded.")
        if r.status_code == 403:
            print("  Attempting re-auth.")
            crawl.perform_auth()
            try:
                r = crawl.session.get(url.url)
            except requests.exceptions.Timeout:
                print("  Timeout exceeded.")
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
        returnStr = ""

        returnStr += "URL: {0}\n".format(self.base_url)
        if len(self.params) > 0:
            returnStr += "    Variable(s) found:\n"
            for input_variable in self.params:
                returnStr += "      - {0}\n".format(str(input_variable))
        if len(self.input_fields) > 0:
            returnStr += "    Input field(s) found:\n"
            for input_field in self.input_fields:
                returnStr += "      - {0}\n".format(str(input_field))

        return returnStr

    def add_params_from_url(self, url):
        self.params.update(url.params)

    def matches_url(self, url):
        return self.base_url == url.get_absolute()

    def get_url(self):
        return Url(self.base_url)


class PageSet:
    __slots__ = ('pages')

    def __init__(self):
        self.pages = list()

    def __str__(self):
        returnStr = ""

        returnStr += "Pages found:\n"
        for page in self.pages:
            if page.status_code == 200:
                returnStr += str(page) + '\n'

        return returnStr

    """
    Returns true if the page was added.
    """
    def create_or_update_page_by_url(self, url):
        page = self.get_page_by_url(url)
        if page is None:
            new_page = Page(url)
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

    

