#!/usr/bin/env python3
"""
Scrapes argv 1 input domain for broken links
"""
from bs4 import BeautifulSoup
import datetime
import queue
import re
import requests
import sys
import random

all_links = {}
domain_links_q = queue.Queue()
external_and_image_links_q = queue.Queue()
TIMEOUT = (3, 10)
OUTPUT_FILE = './broken_links_' + str(random.random()).split('.')[1]
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

def error_check_and_init_main_domain(INPUT_URL):
    """
    checks errors and saves original_domain
    """
    global original_domain
    if len(INPUT_URL) != 2:
        print("Usage:", file=sys.stderr)
        print("$ ./module/find_broken_links_from_input_url.py resources/[URL TO BE SCAPED]", file=sys.stderr)
        sys.exit(1)
    url = INPUT_URL
    if 'http' or '://' not in url:
        print("please use a valid HTTP URL", file=sys.stderr)
        sys.exit(1)
    url = add_terminating_slash_to_url(url)
    pattern = re.compile("(\.{1}.*\.{1}.*\/.*)")
    m = re.search(pattern, url)
    if m is None:
        pattern = re.compile("(:\/\/.*\.{1}.*\/.*)")
        m = re.search(pattern, url)
        if m is None:
            print("please use a valid HTTP URL", file=sys.stderr)
            sys.exit(1)
        original_domain = m.groups()[0][3:-1]
    else:
        original_domain = m.groups()[0][1:-1]
    return url


def add_terminating_slash_to_url(url):
    """
    adds terminating slash if necessary to main input URL
    """
    if url[-1] != '/':
        url += '/'
    return url

def url_is_new(url, object_store):
    """
    checks if URL exists in reviewed storage of URLs
    """
    if url in object_store:                                return False
    if url.replace('www.', '') in object_store:            return False
    if url.replace('://', '://www.') in object_store:      return False
    if url.replace('http://', 'https://') in object_store: return False
    if url.replace('https://', 'http://') in object_store: return False
    if url + '/' in object_store:                          return False
    if url[:-1] in object_store:                           return False
    return True

def parse_response_for_new_links(r):
    """
    parses response text for new links to add to queue
    """
    soup = BeautifulSoup(r.text, 'html.parser')
    pattern = re.compile("(http.*\:\/\/.*\.+.*\/.*)")
    for link in soup.find_all('a'):
        new_url = link.get('href', None)
        if new_url is None: continue
        m = re.search(pattern, new_url)
        if m is None or not url_is_new(new_url, all_links):
            continue
        all_links[new_url] = None
        if original_domain in new_url:
            domain_links_q.put(new_url)
        else:
            external_and_image_links_q.put(new_url)
    for link in soup.find_all('img'):
        new_url = link.get('src')
        m = re.search(pattern, new_url)
        if m is None or not url_is_new(new_url, all_links):
            continue
        all_links[new_url] = None
        external_and_image_links_q.put(new_url)

def scrape_url_from_original_domain_links(url):
    """
    scrapes url that is from main domain website
    """
    try:
        r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=TIMEOUT)
    except Exception as e:
        all_links[url] = 500
        return
    status_code = r.status_code
    all_links[url] = status_code
    if (r.headers['Content-Type'] != 'text/html; charset=UTF-8' or status_code >= 300):
        return
    parse_response_for_new_links(r)


def domain_links_loop():
    """
    loops through and makes request for all queue'd url's
    """
    while domain_links_q.empty() is False:
        url = domain_links_q.get()
        scrape_url_from_original_domain_links(url)

def external_and_image_head_request(url):
    """
    makes head request for external and image URL inputs
    """
    try:
        r = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=TIMEOUT)
    except Exception as e:
        all_links[url] = 500
        return
    all_links[url] = r.status_code

def external_and_image_links_loop():
    """
    loops and makes head request to all queue'd URL's
    """
    while external_and_image_links_q.empty() is False:
        url = external_and_image_links_q.get()
        external_and_image_head_request(url)


def write_results_to_file():
    """
    final writing of results
    """
    FIRST_LINE = """TIME: {}
        link                  -                   status
""".format(str(datetime.datetime.now()))
    with open(OUTPUT_FILE, "w", encoding="utf-8") as open_file:
        open_file.write(FIRST_LINE)
        for l, s in all_links.items():
            if s >= 300:
                line = "{} - {}\n".format(l, s)
                open_file.write(line)

def main_app(INPUT_URL):
    """
    completes all tasks of the application
    """
    url = error_check_and_init_main_domain(INPUT_URL)
    all_links[url] = None
    domain_links_q.put(url)
    domain_links_loop()
    external_and_image_links_loop()
    write_results_to_file()

if __name__ == "__main__":
    """
    MAIN APP
    """
    main_app()
