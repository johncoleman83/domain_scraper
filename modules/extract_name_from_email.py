#!/usr/bin/env python3
"""
reads emails and extracts a username from them
"""
import queue
import sys
import os.path
import datetime
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

# REGEX
# EMAIL_PATH_PATTERN = re.compile('about|affiliations|board|departments|directory|governance|leadership|staff|team', re.IGNORECASE|re.DOTALL)
# INVALID_SOCIAL_MEDIA_PATTERN = re.compile('/home\?status|/intent/|share', re.IGNORECASE|re.DOTALL)
# VALID_SOCIAL_MEDIA_PATTERN = re.compile('twitter\.com|linkedin\.com|facebook\.com|github\.com', re.IGNORECASE|re.DOTALL)

def error_check_and_init_main_file():
    """
    checks errors
    """
    if len(sys.argv) != 2:
        print("Usage:", file=sys.stderr)
        print("$ ./modules/extract_name_from_email.py [FILE TO BE SCRAPED]", file=sys.stderr)
        sys.exit(1)
    INPUT_FILE = sys.argv[1]
    if not os.path.isfile(INPUT_FILE):
        print("please use a valid file", file=sys.stderr)
        sys.exit(1)
    return INPUT_FILE


def read_file_add_to_queue(INPUT_FILE):
    """
    reads emails from input file and adds them to a queue
    """
    with open(INPUT_FILE, "r", encoding="utf-8") as open_file:
        for i, line in enumerate(open_file):
            new_email = line.strip()
            emails_q.put(new_email)

def create_temp_files(file_list):
    """
    creates temp files to be appended to
    """
    FIRST_LINE = "TIME: {}\n".format(str(datetime.datetime.now()))
    for f in file_list:
        with open(f, "w", encoding="utf-8") as open_file:
            open_file.write(FIRST_LINE)

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


def main_app():
    """
    completes all tasks of the application
    """
    INPUT_FILE = error_check_and_init_main_file()
    read_file_add_to_queue(INPUT_FILE)
    create_temp_files([TEMP_EMAIL_OUTPUT_FILE])
    loop_all_emails()

if __name__ == "__main__":
    """
    MAIN APP
    """
    main_app()
