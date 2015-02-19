import requests
from bs4 import BeautifulSoup as bs
from utils import *

global visited
global good_links

def crawl(domain, url):
    global visited
    global good_links
    visited = set()
    good_links = set()
    recurse_crawl(domain, url)
    
    print("\n\n\nLink List (sorted):")
    for url in sorted(good_links):
        print(url);

def recurse_crawl(domain, url):
    global visited
    global good_links
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
    beautiful = bs(r.content)
    for link in beautiful.find_all('a'):
        linkContent = link.get('href')
        if linkContent is not None:
            links.add(to_absolute(domain, url, linkContent))
    links = filter_externals(domain, links)
    for link in links:
        if link not in visited:
            visited.add(link)
            recurse_crawl(domain, link)
