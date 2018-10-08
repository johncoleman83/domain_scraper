#!/usr/bin/env python3
"""
Scrapes links from argv 1 file for email addresses and social media
does not look for new links
"""
from bs4 import BeautifulSoup
from modules.errors import insert
from modules.file_io import io
from modules.urls import helpers
import queue
import re
import os
import requests

# url helpers
url_is_new = helpers.url_is_new
url_is_image_or_css_link = helpers.url_is_image_or_css_link
do_social_media_checks = helpers.do_social_media_checks

# Storage
all_links = set()
all_social_links = set()
all_emails = set()
links_to_scrape_q = queue.Queue()

# Requests
TIMEOUT = (3, 10)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

def parse_response_for_emails(r):
    """
    looks for emails in response
    """
    emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", r.text, re.I)) - all_emails
    valid_emails = set()
    for e in emails:
        if not url_is_image_or_css_link(e):
            valid_emails.add(e)
    if len(valid_emails) > 0:
        all_emails.update(valid_emails)
    return valid_emails

def parse_response(r):
    """
    parses response text for new links to add to queue
    """
    soup = BeautifulSoup(r.text, 'html.parser')
    pattern = re.compile('(http.*\:\/\/.*\.+.*\/.*)', re.IGNORECASE)
    social_links = set()
    for link in soup.find_all('a'):
        new_url = link.get('href', None)
        if new_url.__class__.__name__ != 'str' or len(new_url) == 0: continue
        url_lowered = new_url.lower()
        m = re.search(pattern, new_url)
        if m is None:
            continue
        if do_social_media_checks(url_lowered, all_social_links):
            social_links.add(new_url)
            all_social_links.add(url_lowered)
    emails = parse_response_for_emails(r)
    return emails, social_links

def scrape_url(url):
    """
    makes request to input url and passes the response to be scraped and parsed
    if it is not an error code response
    """
    try:
        r = requests.get(url, allow_redirects=True, timeout=TIMEOUT)
    except Exception as e:
        print('ERROR with URL: {}'.format(url))
        return
    status_code = r.status_code
    if r and r.headers:
        content_type = r.headers.get('Content-Type', 'None')
    else:
        return
    if (status_code >= 300 or content_type.__class__.__name__ != 'str' or 'text/html' not in content_type.lower()):
        print('ERROR with URL: {}, status: {}, content-type: {}'.format(url, status_code, content_type))
        return
    emails, social_links = parse_response(r)
    io.temp_write_updates_to_files(url, emails, social_links)

def loop_all_links():
    """
    loops through and makes request for all queue'd url's
    """
    while links_to_scrape_q.empty() is False:
        url = links_to_scrape_q.get()
        scrape_url(url)


def main_app(INPUT_FILE):
    """
    completes all tasks of the application
    """
    io.read_file_add_to_queue(INPUT_FILE, all_links, links_to_scrape_q)
    io.initial_files([
        io.TEMP_EMAIL_OUTPUT_FILE, io.TEMP_SOCIAL_OUTPUT_FILE, io.CHECKED_URLS
    ])
    loop_all_links()

if __name__ == "__main__":
    """
    MAIN APP
    """
    print('usage: import this')
