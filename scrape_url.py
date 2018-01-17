#!/usr/bin/env python3
"""
Scrapes argv 1 input domain for broken links
"""
from bs4 import BeautifulSoup
import queue
import re
import requests
import sys
import urllib.request


all_links = {}
domain_links_q = queue.Queue()
external_and_image_links_q = queue.Queue()
TIMEOUT = (3, 10)

def add_terminating_slash_to_url(url):
    """
    """
    if url[-1] != '/':
        url += '/'
    return url

def url_has_been_reviewed(url):
    """
    """
    if 'www.' in url:
        i = url.index('www.')
        new = "{}{}".format(url[:i], url[i + 4:])
        if new in all_links:     return True
    else:
        i = url.index('://')
        new = "{}www.{}".format(url[:i + 3], url[i + 3:])
        if new in all_links:     return True
    if url in all_links:         return True
    elif url + '/' in all_links: return True
    elif url[:-1] in all_links:  return True
    else:                        return False

def scrape_url_from_original_domain(url):
    """
    """
    try:
        r = requests.get(url, allow_redirects=True, timeout=TIMEOUT)
    except Exception as e:
        print(e)
        return
    all_links[url] = r.status_code
    if (r.headers['Content-Type'] != 'text/html; charset=UTF-8'
        or all_links[url] >= 400):
        return
    soup = BeautifulSoup(r.text, 'html.parser')
    pattern = re.compile("(http.*\:\/\/.*\.+.*\/.*)")
    for link in soup.find_all('a'):
        new_url = link.get('href', None)
        if new_url is None: continue
        m = re.search(pattern, new_url)
        if m is None or url_has_been_reviewed(new_url):
            continue
        all_links[new_url] = None
        if original_domain in new_url:
            domain_links_q.put(new_url)
        else:
            external_and_image_links_q.put(new_url)
    for link in soup.find_all('img'):
        new_url = link.get('src')
        m = re.search(pattern, new_url)
        if m is None or url_has_been_reviewed(new_url):
            continue
        all_links[new_url] = None
        external_and_image_links_q.put(new_url)


def domain_links_loop():
    """
    """
    while domain_links_q.empty() is False:
        url = domain_links_q.get()
        scrape_url_from_original_domain(url)

def external_and_image_head_request(url):
    """
    """
    try:
        r = requests.head(url, allow_redirects=True, timeout=TIMEOUT)
    except Exception as e:
        print(e)
        return
    all_links[url] = r.status_code

def external_and_image_links_loop():
    """
    """
    while external_and_image_links_q.empty() is False:
        url = external_and_image_links_q.get()
        external_and_image_head_request(url)


def print_results():
    """
    """
    for l, s in all_links.items():
        if s >= 400:
            print(l, s)

def main_app():
    """
    """
    global original_domain
    if len(sys.argv) != 2:
        print("Usage:", file=sys.stderr)
        print("$ ./scrape_url.py [URL TO BE SCAPED]", file=sys.stderr)
        sys.exit(1)
    url = sys.argv[1]
    if 'http' not in url or '://' not in url:
        print("please use a valid HTTP", file=sys.stderr)
        sys.exit(1)
    url = add_terminating_slash_to_url(url)
    pattern = re.compile("(\.{1}.*\.{1}.*\/.*)")
    m = re.search(pattern, url)
    if m is None:
        pattern = re.compile("(:\/\/.*\.{1}.*\/.*)")
        m = re.search(pattern, url)
        original_domain = m.groups()[0][3:-1]
    else:
        original_domain = m.groups()[0][1:-1]
    all_links[url] = None
    domain_links_q.put(url)
    domain_links_loop()
    external_and_image_links_loop()
    print_results()

if __name__ == "__main__":
    """
    MAIN APP
    """
    main_app()
