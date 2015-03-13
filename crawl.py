"""
crawl.py

Handles the recursion of crawling and the authentication logic.
"""

import requests
from page import Page, PageSet

session = None
page_set = None
custom_auth = None

"""
Authenticate a request, based on the custom_auth string.
"""
def perform_auth():
    global session
    global custom_auth

    # If custom_auth was used, set up the session.
    if custom_auth == "dvwa":
        session = auth_DVWA(session)
    elif custom_auth == "bodgeit":
        session = auth_BodgeIt(session)

"""
Authenticate a session on the DVWA website.
Params:
    session: a Requests.Session object to use
Returns:
    session: the modified Requests.Session object
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
Create a user and authenticate a session on the BodgeIt website.
Params:
    session: a Requests.Session object to use
Returns:
    session: the modified Requests.Session object
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

"""
Begin crawling, starting with the base URL, then the guessed URLs.
Then, print the Page Set and the session cookies.
Params:
    url: the base Url to begin crawling from
    guessed_urls: a list of additional Urls to crawl from
    in_custom_auth: the custom authentication string to determine login
    test: True when test is specified
    timeout: the Requests timeout, in seconds
"""
def crawl(url, guessed_urls, in_custom_auth, test, timeout):
    global session
    global page_set
    global custom_auth

    custom_auth = in_custom_auth

    page_set = PageSet(test, timeout)
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

"""
Recursively create/update pages.
Params:
    url: the Url to crawl from
"""
def recurse_crawl(url):
    global page_set
 
    new_page = page_set.create_or_update_page_by_url(url)
    if new_page is not None:
        print("Crawling: " + str(url))
        for link in new_page.links:
            recurse_crawl(link)
