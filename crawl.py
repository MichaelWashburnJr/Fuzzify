import requests
from bs4 import BeautifulSoup as bs
from url import Url, filter_externals

global visited
global good_links

class InputField:
    def __init__(self, field_element, url):
        self.name = field_element.get('name')
        self.id = field_element.get('id')
        self.type = field_element.get('type')
        self.from_url = url
    def __str__(self):
        return "name: {!s:<15} id: {!s:<15} type: {!s:<15}".format(self.name, self.id, self.type)

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

def crawl(domain, url, guessed_urls, custom_auth):
    global visited
    global good_links

    visited = set()
    good_links = set()
    session = requests.Session()

    # If custom_auth was used, set up the session.
    if custom_auth == "dvwa":
        session = auth_DVWA(session)
    elif custom_auth == "bodgeit":
        session = auth_BodgeIt(session)

    recurse_crawl(session, domain, url)

    # Guess URLs.
    print("\nTesting guessed URLs...\n")
    for url_to_test in guessed_urls:
        recurse_crawl(session, domain, url_to_test)
    

    print("\n\n\n{:=^76}\n".format(" OUTPUT "))

    print("\nPages found:")
    for url in sorted(good_links, key=lambda u: u.url):
        print(url.url);
        if len(url.inputs) > 0:
            print("    Variable(s) found:")
            for input_variable in url.inputs:
                print("      - " + input_variable)
        if len(url.input_fields) > 0:
            print("    Input field(s) found:")
            for input_variable in url.input_fields:
                print("      - " + str(input_variable))

    print("\n\nSession Cookie List:")
    for cookie in session.cookies:
        print(cookie);

def update_inputs(url_set, url):
    for u1 in url_set:
        if (u1.get_absolute() == url.get_absolute()):
            for inp in url.inputs:
                if inp not in u1.inputs:
                    u1.inputs.append(inp)

def recurse_crawl(session, domain, url):
    global visited
    global good_links

    print("Crawling: " + str(url))
    links = []
    try:
        r = session.get(url.url)
    except requests.exceptions.ConnectionError:
        print("  ConnectionError")
        return links
    if r.status_code != 200:
        print("  Status code: " + str(r.status_code))
        return links

    good_links.add(url)

    beautiful = bs(r.content)

    # Find all inputs
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
            recurse_crawl(session, domain, link)
        else:
            update_inputs(good_links, link)
