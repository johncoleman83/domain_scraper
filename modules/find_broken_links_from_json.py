#!/usr/bin/env python3
"""
Scrapes json file for broken links
"""
from modules.errors import insert
from modules.urls import helpers
from modules.file_io import io
import re
import datetime
import random
import queue
import os

all_links = set()
domain_links_q = queue.Queue()
OUTPUT_FILE = './file_storage/broken_links_' + str(random.random()).split('.')[1]

def domain_links_loop():
    """
    loops through and makes request for all queue'd url's
    """
    while domain_links_q.empty() is False:
        url = domain_links_q.get()
        status = helpers.make_request_for(url)
        if status is not None:
            io.write_one_link_result_to(OUTPUT_FILE, url, status)


def execute(INPUT_FILE):
    """
    completes all tasks of the application
    """
    io.read_json_and_add_to_queue(INPUT_FILE, all_links, domain_links_q)
    io.init_file_with_datetime(OUTPUT_FILE)
    domain_links_loop()

if __name__ == "__main__":
    """
    MAIN APP
    """
    print('usage: import this')
