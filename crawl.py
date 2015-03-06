import requests
from bs4 import BeautifulSoup as bs
from url import Url, filter_externals
from page import Page

global visited
global good_links
global session
global custom_auth

def perform_auth():
    global session
    global custom_auth

    # If custom_auth was used, set up the session.
    if custom_auth == "dvwa":
        session = auth_DVWA(session)
    elif custom_auth == "bodgeit":
        session = auth_BodgeIt(session)

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


def crawl(domain, url, guessed_urls, in_custom_auth):
    global visited
    global good_links
    global session
    global custom_auth

    visited = set()
    good_links = set()
    session = requests.Session()
    custom_auth = in_custom_auth

    perform_auth()

    recurse_crawl(domain, url)

    # Guess URLs.
    print("\nTesting guessed URLs...\n")
    for url_to_test in guessed_urls:
        recurse_crawl(domain, url_to_test)
    

    print("\n\n\n{:=^76}\n".format(" OUTPUT "))

    print("\nPages found:")
    for url in sorted(good_links, key=lambda u: u.url):
        print(url.url)
        if len(url.params) > 0:
            print("    Variable(s) found:")
            for input_variable in url.params:
                print("      - " + input_variable)
        if len(url.input_fields) > 0:
            print("    Input field(s) found:")
            for input_variable in url.input_fields:
                print("      - " + str(input_variable))

    print("\n\nSession Cookie List:")
    for cookie in session.cookies:
        print("  " + str(cookie))

def update_params(url_set, url):
    for u1 in url_set:
        if (u1.get_absolute() == url.get_absolute()):
            for inp in url.params:
                if inp not in u1.params:
                    u1.params.append(inp)

def recurse_crawl(domain, url):
    global visited
    global good_links
    global session

    print("Crawling: " + str(url))
    links = []
    try:
        r = session.get(url.url)
    except requests.exceptions.ConnectionError:
        print("  ConnectionError")
        return links
    if r.status_code != 200:
        print("  Status code: " + str(r.status_code))
        if r.status_code == 403:
            print("  Attempting re-auth...")
            perform_auth()
            try:
                r = session.get(url.url)
            except requests.exceptions.ConnectionError:
                print("    ConnectionError")
                return links
            if r.status_code != 200:
                print("    Status code: " + str(r.status_code))
                return links
        return links

    good_links.add(url)

    beautiful = bs(r.content)

    # Find all input fields
    for input_field in beautiful.find_all('input'):
        url.input_fields.add(InputField(input_field, url))

    # Find all links
    for link in beautiful.find_all('a'):
        linkContent = link.get('href')
        if linkContent is not None:
            links.append(Url(linkContent, source=r.url, domain=url.domain))
    links = filter_externals(domain, links)
    for link in links:
        if link not in visited:
            visited.add(link)
            recurse_crawl(domain, link)
        else:
            update_params(good_links, link)

    for link in links:
        if PageSet.create_or_update_page_by_url(link):
            recurse_crawl(link)