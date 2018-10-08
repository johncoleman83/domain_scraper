#!/usr/bin/env python3
"""
Scrapes argv 1 input file for broken links
"""
from modules.errors import insert
from modules.file_io import io
import re
import requests
import datetime
import random
import queue
import os

all_links = set()
broken_links = {}
domain_links_q = queue.Queue()
TIMEOUT = (3, 10)
OUTPUT_FILE = './file_storage/broken_links_' + str(random.random()).split('.')[1]
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

def check_url_and_add_to_lists(url):
    """
    scrapes url that is from main domain website
    """
    try:
        r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=TIMEOUT)
    except Exception as e:
        print("ERROR with requests to {}".format(url))
        print(e)
        return 500
    status = r.status_code
    if status >= 300:
        print('error with URL: {} STATUS: {}'.format(url, status))
        if status == 302:
            status = r.url
    else:
        status = None
    return status


def domain_links_loop():
    """
    loops through and makes request for all queue'd url's
    """
    while domain_links_q.empty() is False:
        url = domain_links_q.get()
        status = check_url_and_add_to_lists(url)
        if status is not None:
            broken_links[url] = status

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


def main_app(INPUT_FILE):
    """
    completes all tasks of the application
    """
    io.read_file_add_to_queue(INPUT_FILE, all_links, domain_links_q)
    domain_links_loop()
    write_results_to_file()

if __name__ == "__main__":
    """
    MAIN APP
    """
    print('usage: import this')
