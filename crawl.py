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

"""
Authorize a session on the DVWA website
"""
def auth_DVWA(session):
    r = session.post("http://127.0.0.1/dvwa/login.php?",
        data={
            "username" : "admin",
            "password" : "password",
            "Login"    : "Login"
        })
    return session

"""
Create a user and authorize a session on the BodgeIt website
"""
def auth_BodgeIt(session):
    username = "test@test.test"
    password = "password"

    # Create the user. This will fail gracefully if already created.
    session.post("http://127.0.0.1:8080/bodgeit/register.jsp?",
        data={
            "username"  : username,
            "password1" : password,
            "password2" : password
        })

    # Force a login of the user. This will fail gracefully if already logged in.
    session.post("http://127.0.0.1:8080/bodgeit/login.jsp?",
        data={
            "username" : username,
            "password" : password
        })

    #session.auth = (username, password)

    return session

def crawl(domain, url):
    global visited
    global good_links
    global cookies
    global inputs

    visited = set()
    good_links = set()
    cookies = set()
    inputs = set()
    session = requests.Session()

    #provided authentication for dvwa
    if "/dvwa" in url.url:
        session = auth_DVWA(session)
    elif "/bodgeit" in url.url:
        session = auth_BodgeIt(session)

    recurse_crawl(session, domain, url)
    
    print("\n\n\nLink List (sorted):")
    for url in sorted(good_links, key=lambda u: u.url):
        print(url.url);

    print("\n\n\nCookie List:")
    for cookie in cookies:
        print(cookie);

    print("\n\n\nInput List:")
    for input_item in inputs:
        print(input_item);


def recurse_crawl(session, domain, url):
    global visited
    global good_links
    global cookies
    global inputs

    print("Crawling: " + str(url))
    links = set()
    try:
        r = session.get(url.url)
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
            links.add(Url(linkContent, source=url.url, domain=url.domain))
    links = filter_externals(domain, links)
    for link in links:
        if link not in visited:
            visited.add(link)
            recurse_crawl(session, domain, link)
