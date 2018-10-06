#!/usr/bin/env python3
"""
checks for errors from the command execution and input args
"""
import sys
import os.path

def check_argv(this_file, resource):
    """
    checks errors
    """
    if len(sys.argv) != 2:
        print("Usage:", file=sys.stderr)
        print("$ ./modules/{} resources/{}".format(this_file, resource), file=sys.stderr)
        sys.exit(1)
    INPUT_FILE = sys.argv[1]
    if not os.path.isfile(INPUT_FILE):
        print("please use a valid file", file=sys.stderr)
        sys.exit(1)
    return INPUT_FILE

if __name__ == "__main__":
    """
    MAIN APP
    """
    print('usage: import error_check')
