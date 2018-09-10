#!/usr/bin/env python3
"""
Scrapes links from argv 1 file for email addresses
"""
from bs4 import BeautifulSoup
import queue
import re
import requests
import sys


all_links = {}
domain_links_q = queue.Queue()
external_and_image_links_q = queue.Queue()
TIMEOUT = (3, 10)
OUTPUT_FILE = './broken_links_' + str(random.random()).split('.')[1]


def error_check_and_init_main_file():
    """
    checks errors
    """
    if len(sys.argv) != 2:
        print("Usage:", file=sys.stderr)
        print("$ ./scrape_url.py [FILE TO BE SCRAPED]", file=sys.stderr)
        sys.exit(1)
    INPUT_FILE = sys.argv[1]
    if not os.path.isfile(INPUT_FILE):
        print("please use a valid file", file=sys.stderr)
        sys.exit(1)
    return INPUT_FILE


def read_file_add_to_queue(INPUT_FILE):
    """
    reads links from input file and adds them to a queue
    """
    with open(INPUT_FILE, "r", encoding="utf-8") as open_file:
        for i, line in enumerate(open_file):
            new_link = line.strip()
            if url_is_new(new_link):
                all_links[new_url] = None
                domain_links_q.put(new_link)

def url_is_new(url):
    """
    checks if URL exists in reviewed storage of URLs
    """
    if url in all_links:         return False
    if 'www.' in url:
        i = url.index('www.')
        new = "{}{}".format(url[:i], url[i + 4:])
        if new in all_links:     return False
    else:
        i = url.index('://')
        new = "{}www.{}".format(url[:i + 3], url[i + 3:])
        if new in all_links:     return False
    if url + '/' in all_links:   return False
    elif url[:-1] in all_links:  return False
    return True

def url_could_contain_email_link(url):
    """
    checks if input url could contian a link with emails
    """
    LINKS_COULD_CONTAIN_EMAILS = [
        'contact',
        'about',
        'staff',
        'directory',
        'leadership',
        'team'
    ]
    url = url.lower()
    for word in LINKS_COULD_CONTAIN_EMAILS:
        if word in url: return True
    return False

def add_terminating_slash_to_url(url):
    """
    adds terminating slash if necessary to main input URL
    """
    if url[-1] != '/':
        url += '/'
    return url

def get_original_domain_from_url(url):
    """
    gets the original domain
    """
    pattern = re.compile("(\.{1}.*\.{1}.*\/.*)")
    m = re.search(pattern, url)
    if m is None:
        pattern = re.compile("(:\/\/.*\.{1}.*\/.*)")
        m = re.search(pattern, url)
        if m is None:
            print("could not find a valid HTTP URL", file=sys.stderr)
            return None
        return m.groups()[0][3:-1]
    else:
        return m.groups()[0][1:-1]

def parse_response_for_new_emails(url, r):
    """
    parses response text for new links to add to queue
    """
    soup = BeautifulSoup(r.text, 'html.parser')
    pattern = re.compile("(http.*\:\/\/.*\.+.*\/.*)")
    for link in soup.find_all('a'):
        new_url = link.get('href', None)
        if new_url is None: continue
        m = re.search(pattern, new_url)
        if m is None or not url_is_new(new_url):
            continue
        url = add_terminating_slash_to_url(url)
        original_domain = get_original_domain_from_url(url)
        if url_could_contain_email_link(new_url) and original_domain in new_url:
            all_links[new_url] = None
            domain_links_q.put(new_url)
    # should check for social media links and store social media links for this URL
    # Should check for emails and store email object for this URL



def scrape_emails_from_url(url):
    """
    scrapes for emails that is from main domain website
    """
    try:
        r = requests.get(url, allow_redirects=True, timeout=TIMEOUT)
    except Exception as e:
        return
    status_code = r.status_code
    if (r.headers['Content-Type'] != 'text/html; charset=UTF-8' or status_code >= 300):
        return
    parse_response_for_new_emails(url, r)


def loop_all_links():
    """
    loops through and makes request for all queue'd url's
    """
    while domain_links_q.empty() is False:
        url = domain_links_q.get()
        scrape_emails_from_url(url)


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

def main_app():
    """
    completes all tasks of the application
    """
    INPUT_FILE = error_check_and_init_main_file()
    read_file_add_to_queue(INPUT_FILE)
    loop_all_links()
    external_and_image_links_loop()
    write_results_to_file()

if __name__ == "__main__":
    """
    MAIN APP
    """
    main_app()
