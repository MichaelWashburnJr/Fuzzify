import requests
from bs4 import BeautifulSoup as bs
from url import Url, filter_externals
from page import Page, PageSet

session = None
page_set = None
custom_auth = None

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

    return session


def crawl(url, guessed_urls, in_custom_auth, timeout):
    global session
    global page_set
    global custom_auth

    custom_auth = in_custom_auth

    page_set = PageSet(timeout)
    session = requests.Session()

    perform_auth()
    recurse_crawl(url)

    # Guess URLs.
    print("\nTesting guessed URLs...\n")
    for url_to_test in guessed_urls:
        recurse_crawl(url_to_test)
    
    print("\n\n\n{:=^76}\n".format(" OUTPUT "))

    print(str(page_set))

    print("\nSession Cookie List:")
    for cookie in session.cookies:
        print("  " + str(cookie))

def recurse_crawl(url):
    global page_set
 
    new_page = page_set.create_or_update_page_by_url(url)
    if new_page is not None:
        print("Crawling: " + str(url))
        for link in new_page.links:
            recurse_crawl(link)
