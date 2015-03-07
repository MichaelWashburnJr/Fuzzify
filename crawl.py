import requests
from bs4 import BeautifulSoup as bs
from url import Url, filter_externals
from page import Page, PageSet

session = None
page_set = None

def perform_auth(custom_auth):
    global session

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


def crawl(url, guessed_urls, custom_auth):
    global session
    global page_set

    page_set = PageSet()
    session = requests.Session()

    perform_auth(custom_auth)
    recurse_crawl(url)

    # Guess URLs.
    print("\nTesting guessed URLs...\n")
    for url_to_test in guessed_urls:
        recurse_crawl(url_to_test)
    
    print("\n\n\n{:=^76}\n".format(" OUTPUT "))

    print(str(page_set))

    print("\n\nSession Cookie List:")
    for cookie in session.cookies:
        print("  " + str(cookie))

def recurse_crawl(url):
    global page_set

    print("Crawling: " + str(url))
 
    if page_set.create_or_update_page_by_url(url):
        for link in page_set.get_page_by_url(url).links:
            recurse_crawl(link)