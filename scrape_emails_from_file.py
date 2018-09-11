#!/usr/bin/env python3
"""
Scrapes links from argv 1 file for email addresses
"""
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import queue
import re
import requests
import sys
import os.path
import datetime
import random


all_links = {}
all_social_links = set()
all_emails = set()
links_to_scrape_q = queue.Queue()
TIMEOUT = (3, 10)
FILE_HASH = str(random.random()).split('.')[1]
ALL_OUTPUT_FILE = './crh/email_social_links_' + FILE_HASH
TEMP_EMAIL_OUTPUT_FILE = './crh/temp_emails_' + FILE_HASH
TEMP_SOCIAL_OUTPUT_FILE = './crh/temp_social_media_' + FILE_HASH
CHECKED_URLS = './crh/already_checked_urls_' + FILE_HASH
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}


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
            new_url = line.strip()
            if url_is_new(new_url):
                all_links[new_url] = None
                links_to_scrape_q.put(new_url)

def create_temp_files():
    """
    creates temp files to be appended to
    """
    FIRST_LINE = "TIME: {}\n".format(str(datetime.datetime.now()))
    with open(TEMP_EMAIL_OUTPUT_FILE, "w", encoding="utf-8") as open_file:
        open_file.write(FIRST_LINE)
    with open(TEMP_SOCIAL_OUTPUT_FILE, "w", encoding="utf-8") as open_file:
        open_file.write(FIRST_LINE)
    with open(CHECKED_URLS, "w", encoding="utf-8") as open_file:
        open_file.write(FIRST_LINE)

def url_is_new(url):
    """
    checks if URL exists in reviewed storage of URLs
    """
    if url in all_links:         return False
    if 'www.' in url:
        new = url.replace('www.', '')
        if new in all_links:     return False
    else:
        new = url.replace('://', '://www.')
        if new in all_links:     return False
    if 'http://' in url:
        new = url.replace('http://', 'https://')
        if new in all_links:     return False
    else:
        new = url.replace('https://', 'http://')
        if new in all_links:     return False
    if url + '/' in all_links:   return False
    elif url[:-1] in all_links:  return False
    return True

def url_is_image_or_css_link(url):
    """
    checks if url has image link in it
    """
    IMAGE_EXTENSIONS = [
        '.png', '.jpg', '@md.x'
    ]
    for ext in IMAGE_EXTENSIONS:
        if ext in url: return True
    return False


def url_is_valid(url):
    """
    checks if url is valid
    """
    if not url_is_new(url):           return False
    if url[:7] == 'mailto:':          return False
    if url[-5:] == '.aspx':           return False
    if url_is_image_or_css_link(url): return False
    return True

def url_is_new_social_link(url):
    """
    checks if URL exists in reviewed storage of social links URLs
    """
    if url in all_social_links:         return False
    if 'www.' in url:
        new = url.replace('www.', '')
        if new in all_social_links:     return False
    else:
        new = url.replace('://', '://www.')
        if new in all_social_links:     return False
    if 'http://' in url:
        new = url.replace('http://', 'https://')
        if new in all_social_links:     return False
    else:
        new = url.replace('https://', 'http://')
        if new in all_social_links:     return False
    if url + '/' in all_social_links:   return False
    elif url[:-1] in all_social_links:  return False
    return True

def url_could_contain_email_link(original_domain, parsed_url_object, url):
    """
    checks if input url could contian a link with emails
    """
    LINKS_COULD_CONTAIN_EMAILS = [
        'leadership',
        'about',
        'affiliations',
        'departments',
        'governance',
        'about',
        'staff',
        'directory',
        'leadership',
        'team'
    ]
    if original_domain not in url:                        return False
    if url_could_be_social_media(url):                    return False
    path = (parsed_url_object.path).lower()
    if path.__class__.__name__ != 'str' or len(path) < 4: return False
    for word in LINKS_COULD_CONTAIN_EMAILS:
        if word in path: return True
    return False

def url_is_valid_social_media(potential_social_url):
    """
    checks if input url could contian a social media link
    """
    INVALID_SOCIAL_LINKS = [
        '/intent/',
        'shareArticle',
        'sharer',
        'share.php',
        'share',
    ]
    for invalid_word in INVALID_SOCIAL_LINKS:
        if invalid_word in potential_social_url:
            return False
    return True

def url_could_be_social_media(url):
    """
    checks if input url could contian a social media link
    """
    LINKS_COULD_BE_SOCIAL_MEDIA = [
        'http://linkedin.com',
        'http://twitter.com',
        'http://facebook.com',
        'http://github.com',
        'http://www.linkedin.com',
        'http://www.twitter.com',
        'http://www.facebook.com',
        'http://www.github.com',
        'https://linkedin.com',
        'https://twitter.com',
        'https://facebook.com',
        'https://github.com',
        'https://www.linkedin.com',
        'https://www.twitter.com',
        'https://www.facebook.com',
        'https://www.github.com',
    ]
    for social_link in LINKS_COULD_BE_SOCIAL_MEDIA:
        if social_link in url:
            return True
    return False

def add_terminating_slash_to_url(url):
    """
    adds terminating slash if necessary to main input URL
    """
    if url[-1] != '/':
        url += '/'
    return url

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

def parse_response(original_domain, url, r):
    """
    parses response text for new links to add to queue
    """
    soup = BeautifulSoup(r.text, 'html.parser')
    pattern = re.compile("(http.*\:\/\/.*\.+.*\/.*)")
    social_links = set()
    for link in soup.find_all('a'):
        new_url = link.get('href', None)
        if new_url.__class__.__name__ != 'str' or len(new_url) == 0: continue
        url_lowered = new_url.lower()
        parsed_url_object = urlparse(url_lowered)
        m = re.search(pattern, new_url)
        if m is None or not url_is_valid(url_lowered):
            continue
        if url_could_be_social_media(url_lowered) and url_is_valid_social_media(url_lowered) and url_is_new_social_link(url_lowered):
            social_links.add(new_url)
            all_social_links.add(url_lowered)
        if url_could_contain_email_link(original_domain, parsed_url_object, url_lowered):
            all_links[new_url] = None
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
    all_links[url] = {
        'emails': emails,
        'social_media': social_links
    }

def scrape_emails_from_url(url):
    """
    scrapes for emails that is from main domain website
    """
    try:
        r = requests.get(url, allow_redirects=True, timeout=TIMEOUT)
    except Exception as e:
        print('ERROR with URL: {}'.format(url))
        return
    status_code = r.status_code
    if r and r.headers:
        content_type = r.headers.get('Content-Type', None)
    else:
        return
    if (status_code >= 300 or content_type.__class__.__name__ != 'str' or 'text/html' not in content_type.lower()):
        print('ERROR with URL: {}, status: {}, content-type: {}'.format(url, status_code, content_type))
        return
    parsed_original_url_object = urlparse(url)
    original_domain = get_original_domain_from_url(parsed_original_url_object)
    emails, social_links = parse_response(
        original_domain, url, r
    )
    temp_write_updates_to_files(url, emails, social_links)

def loop_all_links():
    """
    loops through and makes request for all queue'd url's
    """
    while links_to_scrape_q.empty() is False:
        url = links_to_scrape_q.get()
        scrape_emails_from_url(url)


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
    INPUT_FILE = error_check_and_init_main_file()
    read_file_add_to_queue(INPUT_FILE)
    create_temp_files()
    loop_all_links()
    write_results_to_file()

if __name__ == "__main__":
    """
    MAIN APP
    """
    main_app()
