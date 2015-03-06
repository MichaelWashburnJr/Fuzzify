import requests
from bs4 import BeautifulSoup as bs
from url import Url, filter_externals

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
        global session

        self.params = set()
        self.input_fields = list()
        self.links = list()

        self.base_url = url.get_absolute()
        self.params.update(url.params)
        self.domain = url.domain

        try:
            r = session.get(url.url)
        except requests.exceptions.Timeout:
            print("  Timeout exceeded.")
        self.status_code = r.status_code

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

    def add_params_from_url(self, url):
        self.params.update(url.params)

    def matches_url(self, url):
        return self.base_url == url.get_absolute()





class PageSet:
    __slots__ = ('pages')

    """
    Returns true if the page was added.
    """
    def create_or_update_page_by_url(self, url):
        page = self.get_page_by_url(url)
        if page is None:
            self.add_page(Page(url))
            return True
        else:
            page.add_params_from_url(url)
            return False

    def get_page_by_url(self, url):
        for page in self.pages:
            if page.matches_url(url):
                return page
        return None

    def add_page(self, page):
        self.pages.append(page)

    

