#!/usr/bin/env python3
"""
Scrapes argv 1 input file for broken links

WIP WORK IN PROGRESS

"""
import re
import requests
import sys
import os.path
import datetime
import random
import queue

broken_links = {}
domain_links_q = queue.Queue()
TIMEOUT = (3, 10)
OUTPUT_FILE = './broken_links_' + str(random.random()).split('.')[1]


def error_check_and_init_main_file():
    """
    checks errors and saves original_domain
    """
    global original_domain
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
                domain_links_q.put(new_link)


def url_is_new(url):
    """
    checks if URL exists in reviewed storage of URLs
    """
    if 'www.' in url:
        i = url.index('www.')
        new = "{}{}".format(url[:i], url[i + 4:])
        if new in broken_links:     return False
    else:
        i = url.index('://')
        new = "{}www.{}".format(url[:i + 3], url[i + 3:])
        if new in broken_links:     return False
    if url in broken_links:         return False
    elif url + '/' in broken_links: return False
    elif url[:-1] in broken_links:  return False
    else:                        return True

def check_url_and_add_to_lists(url):
    """
    scrapes url that is from main domain website
    """
    try:
        r = requests.get(url, allow_redirects=True, timeout=TIMEOUT)
    except Exception as e:
        print("ERROR with requests to {}".format(url))
        print(e)
        return
    status_code = r.status_code
    if r.status_code > 302:
        print('error with URL: {} STATUS: {}'.format(url, status_code))
        broken_links[url] = status_code
    if r.status_code == 302:
        broken_links[url] = r.url
    return


def domain_links_loop():
    """
    loops through and makes request for all queue'd url's
    """
    while domain_links_q.empty() is False:
        url = domain_links_q.get()
        check_url_and_add_to_lists(url)


def write_results_to_file():
    """
    final writing of results
    """
    FIRST_LINE = """TIME: {}
        link                  -                   status
""".format(str(datetime.datetime.now()))
    with open(OUTPUT_FILE, "w", encoding="utf-8") as open_file:
        open_file.write(FIRST_LINE)
        for l, s in broken_links.items():
            line = "{} - {}\n".format(l, s)
            open_file.write(line)


def main_app():
    """
    completes all tasks of the application
    """
    INPUT_FILE = error_check_and_init_main_file()
    # all_links[url] = None
    # domain_links_q.put(url)
    read_file_add_to_queue(INPUT_FILE)
    domain_links_loop()
    write_results_to_file()

if __name__ == "__main__":
    """
    MAIN APP
    """
    main_app()
