#!/usr/bin/env python3
"""
writes initial files for file storage
"""
from modules.urls.helpers import url_is_new
import datetime
import random

# FILES
FILE_HASH = str(random.random()).split('.')[1]
TEMP_EMAIL_OUTPUT_FILE = './file_storage/temp_emails_' + FILE_HASH
TEMP_SOCIAL_OUTPUT_FILE = './file_storage/temp_social_media_' + FILE_HASH
CHECKED_URLS = './file_storage/already_checked_urls_' + FILE_HASH

def read_file_add_to_queue(INPUT_FILE, all_links, links_to_scrape_q):
    """
    reads links from input file and adds them to a queue
    """
    with open(INPUT_FILE, "r", encoding="utf-8") as open_file:
        for i, line in enumerate(open_file):
            new_url = line.strip()
            if url_is_new(new_url, all_links):
                all_links.add(new_url)
                links_to_scrape_q.put(new_url)

def initial_files(file_list):
    """
    creates temp files to be appended to
    """
    FIRST_LINE = "TIME: {}\n".format(str(datetime.datetime.now()))
    for f in file_list:
        with open(f, "w", encoding="utf-8") as open_file:
            open_file.write(FIRST_LINE)

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

if __name__ == "__main__":
    """
    MAIN APP
    """
    print('usage: import this')
