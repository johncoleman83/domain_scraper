#!/usr/bin/env python3
"""
reads emails and extracts a username from them
"""
from modules.errors import insert
from modules.file_io import write
import os
import queue
import random

# Storage
emails_q = queue.Queue()

# FILES
FILE_HASH = str(random.random()).split('.')[1]
TEMP_EMAIL_OUTPUT_FILE = './file_storage/email_name_associations_' + FILE_HASH

# SUPPORT
NAME_DIVIDERS = [ '.', '-', '_' ]
GENERIC_NAMES = set([
    'admin',
    'contact',
    'contactus',
    'hello',
    'help',
    'info',
    'infor',
    'inforequest',
    'information',
    'office',
    'program',
    'staff',
    'support',
    'youth'
])

def read_file_add_to_queue(INPUT_FILE):
    """
    reads emails from input file and adds them to a queue
    """
    with open(INPUT_FILE, "r", encoding="utf-8") as open_file:
        for i, line in enumerate(open_file):
            new_email = line.strip()
            emails_q.put(new_email)

def temp_write_new_name_to_file(name_association):
    """
    writes the temporary findings in case of crash
    """
    with open(TEMP_EMAIL_OUTPUT_FILE, "a", encoding="utf-8") as open_file:
        line = "{}\n".format(name_association)
        open_file.write(line)

def find_name_association(email):
    """
    finds the name association for the given input email
    """
    at_count = email.count('@')
    if  at_count == 0 or at_count > 1:
        print('ERROR with email: {}'.format(email))
        return email
    name_association = email.split('@')[0]
    if len(name_association) == 2 or len(name_association) == 3:
        return name_association.upper()
    for divider in NAME_DIVIDERS:
        if name_association.count(divider) > 0:
            names = name_association.split(divider)
            for i, n in enumerate(names):
                names[i] = n.capitalize()
            return ' '.join(names)
    if name_association.lower() in GENERIC_NAMES:
        return email.split('@')[1].capitalize()
    if name_association == name_association.capitalize():
        return name_association
    if sum(1 for c in name_association if c.isupper()) == 2:
        name_association = [c for c in name_association]
        name_association[0] = name_association[0].lower()
        new_index = 0
        for i, c in enumerate(name_association):
            if c.upper() == c:
                new_index = i
        name_association.insert(new_index, ' ')
        name_association[0] = name_association[0].upper()
        return ''.join(name_association)
    if name_association[0].lower() == name_association[1].lower():
        name_association = [ c for c in name_association]
        name_association.insert(1, ' ')
        name_association[0] = name_association[0].upper()
        name_association[2] = name_association[2].upper()
        return ''.join(name_association)
    print(name_association.capitalize())
    return name_association.capitalize()

def loop_all_emails():
    """
    loops through email to extract name association
    """
    while emails_q.empty() is False:
        email = emails_q.get()
        name_association = find_name_association(email)
        temp_write_new_name_to_file(name_association.strip())


def main_app(INPUT_FILE):
    """
    completes all tasks of the application
    """
    read_file_add_to_queue(INPUT_FILE)
    write.initial_files([TEMP_EMAIL_OUTPUT_FILE])
    loop_all_emails()

if __name__ == "__main__":
    """
    MAIN APP
    """
    print('usage: import this')
