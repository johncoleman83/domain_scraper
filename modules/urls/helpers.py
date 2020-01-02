#!/usr/bin/env python3
"""
url helpers
"""
import re
import requests

INVALID_SOCIAL_MEDIA_PATTERN = re.compile('/home\?status|/intent/|share', re.IGNORECASE|re.DOTALL)
VALID_SOCIAL_MEDIA_PATTERN = re.compile('twitter\.com|linkedin\.com|facebook\.com|github\.com', re.IGNORECASE|re.DOTALL)
TIMEOUT = (3, 10)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

def make_request_for(url):
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

def do_social_media_checks(url_lowered, all_social_links):
    """
    runs all checks on social media
    """
    return (
        url_could_be_social_media(url_lowered) and
        url_is_valid_social_media(url_lowered) and
        url_is_new(url_lowered, all_social_links)
    )

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

def url_is_valid(url, all_links):
    """
    checks if url is valid
    """
    if url[:7] == 'mailto:':           return False
    if url[-5:] == '.aspx':            return False
    if url_is_image_or_css_link(url):  return False
    if not url_is_new(url, all_links): return False
    return True

if __name__ == "__main__":
    """
    MAIN APP
    """
    print('usage: import this')
