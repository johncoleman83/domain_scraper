#!/usr/bin/env python3
"""
writes initial files for file storage
"""
import datetime

def initial_files(file_list):
    """
    creates temp files to be appended to
    """
    FIRST_LINE = "TIME: {}\n".format(str(datetime.datetime.now()))
    for f in file_list:
        with open(f, "w", encoding="utf-8") as open_file:
            open_file.write(FIRST_LINE)

if __name__ == "__main__":
    """
    MAIN APP
    """
    print('usage: import initial_files from file_io.write')
