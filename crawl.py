import requests
from bs4 import BeautifulSoup as bs
from utils import *

global visited
global good_links
global cookies
global inputs

class InputField:
    def __init__(self, field_element, url):
        self.name = field_element.get('name')
        self.id = field_element.get('id')
        self.type = field_element.get('type')
        self.from_url = url
    def __str__(self):
        return "InputField { name:%s id:%s type:%s from_url:%s }" % (self.name, self.id, self.type, self.from_url)


def crawl(domain, url):
    global visited
    global good_links
    global cookies
    global inputs

    visited = set()
    good_links = set()
    cookies = set()
    inputs = set()

    recurse_crawl(domain, url)
    
    print("\n\n\nLink List (sorted):")
    for url in sorted(good_links):
        print(url);

    print("\n\n\nCookie List:")
    for cookie in cookies:
        print(cookie);

    print("\n\n\nInput List:")
    for input_item in inputs:
        print(input_item);


def recurse_crawl(domain, url):
    global visited
    global good_links
    global cookies
    global inputs

    print("Crawling: " + url)
    links = set()
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print("ConnectionError")
        return links
    if r.status_code != 200:
        print("Status code: " + str(r.status_code))
        return links

    good_links.add(url)
    for cookie in r.cookies:
        if cookie not in cookies:
            cookies.add(cookie)

    beautiful = bs(r.content)

    # Find all inputs
    for input_field in beautiful.find_all('input'):
        inputs.add(InputField(input_field, url))

    # Find all links
    for link in beautiful.find_all('a'):
        linkContent = link.get('href')
        if linkContent is not None:
            links.add(to_absolute(domain, url, linkContent))
    links = filter_externals(domain, links)
    for link in links:
        if link not in visited:
            visited.add(link)
            recurse_crawl(domain, link)
