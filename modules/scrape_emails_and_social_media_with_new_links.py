#!/usr/bin/env python3
"""
Scrapes links from argv 1 file for email addresses & social media
looks for new links
"""
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from errors.input import check_argv
import queue
import re
import os
import requests
import datetime
import random

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

# FILES
FILE_HASH = str(random.random()).split('.')[1]
ALL_OUTPUT_FILE = './file_storage/email_social_links_' + FILE_HASH
TEMP_EMAIL_OUTPUT_FILE = './file_storage/temp_emails_' + FILE_HASH
TEMP_SOCIAL_OUTPUT_FILE = './file_storage/temp_social_media_' + FILE_HASH
NEWLY_FOUND_URLS = './file_storage/newly_found_urls_' + FILE_HASH
CHECKED_URLS = './file_storage/already_checked_urls_' + FILE_HASH

# REGEX
EMAIL_PATH_PATTERN = re.compile('about|affiliations|board|departments|directory|governance|leadership|staff|team', re.IGNORECASE|re.DOTALL)
INVALID_SOCIAL_MEDIA_PATTERN = re.compile('/home\?status|/intent/|share', re.IGNORECASE|re.DOTALL)
VALID_SOCIAL_MEDIA_PATTERN = re.compile('twitter\.com|linkedin\.com|facebook\.com|github\.com', re.IGNORECASE|re.DOTALL)

def read_file_add_to_queue(INPUT_FILE):
    """
    reads links from input file and adds them to a queue
    """
    with open(INPUT_FILE, "r", encoding="utf-8") as open_file:
        for i, line in enumerate(open_file):
            new_url = line.strip()
            if url_is_new(new_url, all_links):
                all_links.add(new_url)
                links_to_scrape_q.put(new_url)

def create_temp_files(file_list):
    """
    creates temp files to be appended to
    """
    FIRST_LINE = "TIME: {}\n".format(str(datetime.datetime.now()))
    for f in file_list:
        with open(f, "w", encoding="utf-8") as open_file:
            open_file.write(FIRST_LINE)

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

def url_is_image_or_css_link(url):
    """
    checks if url has image link in it
    """
    IMAGE_EXTENSIONS = [
        '.png', '.jpg', '@md.x', '.pdf', '.calendar.google.com'
    ]
    for ext in IMAGE_EXTENSIONS:
        if ext in url: return True
    return False

def url_is_valid(url):
    """
    checks if url is valid
    """
    if url[:7] == 'mailto:':           return False
    if url[-5:] == '.aspx':            return False
    if url_is_image_or_css_link(url):  return False
    if not url_is_new(url, all_links): return False
    return True

def url_could_contain_email_link(original_domain, parsed_url_object, url):
    """
    checks if input url could contian a link with emails
    """
    if not original_domain or original_domain not in url:    return False
    if url_could_be_social_media(url):                       return False
    query = parsed_url_object.query
    if query.__class__.__name__ == 'str' and len(query) > 0: return False
    path = parsed_url_object.path
    if path.__class__.__name__ != 'str' or len(path) < 4:    return False
    path = path.lower()
    m = re.search(EMAIL_PATH_PATTERN, path)
    return m is not None

def url_is_valid_social_media(social_url):
    """
    checks if input url could contian a social media link
    """
    m = re.search(INVALID_SOCIAL_MEDIA_PATTERN, social_url)
    return m is None

def url_could_be_social_media(potential_social_url):
    """
    checks if input url could contian a social media link
    """
    m = re.search(VALID_SOCIAL_MEDIA_PATTERN, potential_social_url)
    return m is not None

def do_social_media_checks(url_lowered):
    """
    runs all checks on social media
    """
    return (
        url_could_be_social_media(url_lowered) and
        url_is_valid_social_media(url_lowered) and
        url_is_new(url_lowered, all_social_links)
    )

def get_original_domain_from_url(parsed_url_object):
    """
    gets the original domain
    """
    original_domain = parsed_url_object.netloc
    if original_domain.__class__.__name__ != 'str' or len(original_domain) == 0:
        return None
    return original_domain

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

def parse_response(original_domain, r):
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
        parsed_url_object = urlparse(url_lowered)
        m = re.search(pattern, new_url)
        if m is None or not url_is_valid(url_lowered):
            continue
        if do_social_media_checks(url_lowered):
            social_links.add(new_url)
            all_social_links.add(url_lowered)
        if url_could_contain_email_link(original_domain, parsed_url_object, url_lowered):
            with open(NEWLY_FOUND_URLS, "a", encoding="utf-8") as open_file:
                open_file.write("{}\n".format(new_url))
            all_links.add(new_url)
            links_to_scrape_q.put(new_url)
    emails = parse_response_for_emails(r)
    return emails, social_links

def temp_write_updates_to_files(url, emails, social_links):
    """
    writes the temporary findings in case of crash
    """
    with open(CHECKED_URLS, "a", encoding="utf-8") as open_file:
        open_file.write("{}\n".format(url))
    if len(emails) + len(social_links) == 0:
        del emails
        del social_links
        return
    if len(emails) > 0:
        with open(TEMP_EMAIL_OUTPUT_FILE, "a", encoding="utf-8") as open_file:
            lines = ""
            for e in emails:
                lines += "{}\n".format(e)
            open_file.write(lines)
    if len(social_links) > 0:
        with open(TEMP_SOCIAL_OUTPUT_FILE, "a", encoding="utf-8") as open_file:
            lines = ""
            for s in social_links:
                lines += "{}\n".format(s)
            open_file.write(lines)
    del emails
    del social_links

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
    parsed_original_url_object = urlparse(url)
    original_domain = get_original_domain_from_url(parsed_original_url_object)
    emails, social_links = parse_response(original_domain, r)
    temp_write_updates_to_files(url, emails, social_links)

def loop_all_links():
    """
    loops through and makes request for all queue'd url's
    """
    while links_to_scrape_q.empty() is False:
        url = links_to_scrape_q.get()
        scrape_url(url)


def write_results_to_file():
    """
    final writing of results
    """
    FIRST_LINE = "TIME: {}\n".format(str(datetime.datetime.now()))
    with open(ALL_OUTPUT_FILE, "w", encoding="utf-8") as open_file:
        open_file.write(FIRST_LINE)
        for url, meta in all_links.items():
            if meta.__class__.__name__ == 'dict':
                line = "url: {}\n".format(url)
                if len(meta.get('emails', 0)) > 0:
                    line += "emails: {}\n".format(meta.get('emails', 0))
                if len(meta.get('social_media', 0)) > 0:
                    line += "social_media: {}\n".format(meta.get('social_media', 0))
                open_file.write(line)

def main_app():
    """
    completes all tasks of the application
    """
    INPUT_FILE = check_argv(
        os.path.basename(__file__), '[FILE TO BE SCRAPED]'
    )
    read_file_add_to_queue(INPUT_FILE)
    create_temp_files([
        TEMP_EMAIL_OUTPUT_FILE, TEMP_SOCIAL_OUTPUT_FILE, CHECKED_URLS, NEWLY_FOUND_URLS
    ])
    loop_all_links()
    # No need anymore for this
    # write_results_to_file()

if __name__ == "__main__":
    """
    MAIN APP
    """
    main_app()
