#!/usr/bin/env python3

import getopt, sys, os
import argparse
import random
from modules import *

def parse_and_handle_args(args):
	#Set input var and build url path to input (points to working directory)
	print('your selection:\n{}'.format(args))
	if not args.url:
		if args.input_file == []:
			print('Usage:\n$ ./domain_scraper.py --help', file=sys.stderr)
			sys.exit(1)
		input_file = args.input_file[0]
		if 'input_file=' in input_file:
			input_file = input_file.split('=')[1]
		INPUT_FILE = os.path.join( os.getcwd(), input_file)
	else:
		INPUT_URL = args.input_file[0]
	#Get args and pass input to modules
	if args.extract:
		extract.main_app(INPUT_FILE)
	elif args.check:
		check.main_app(INPUT_FILE)
	elif args.url:
		print('hi')
		url_input.main_app(INPUT_URL)
	elif args.scrape:
		scrape.main_app(INPUT_FILE)
	elif args.scrape_n:
		scrape_n.main_app(INPUT_FILE)
	elif args.all:
		extract.main_app(INPUT_FILE)
		check.main_app(INPUT_FILE)
		scrape.main_app(INPUT_FILE)
		scrape_n.main_app(INPUT_FILE)


def start( args ):
	parser = argparse.ArgumentParser(
		prog='domain_scraper',
		description='''Scrapes domains from one input URL or 
		from a file list of domains for broken links, 
		valid emails, and valid social media links.''',
	)
	parser.add_argument('input_file',
                        help='Indicate the input file to scrape.',
                        type=str,
						nargs='*')
	parser.add_argument('--url',
                        help='Indicate the url to scrape.',
                        type=str,
						nargs='*')
	parser.add_argument('--check',
						help='Find broken links from urls in file.',
						const=True,
						default=False,
						type=bool,
						nargs='?')
	parser.add_argument('--extract',
						help='Extract name from emails in file.',
						const=True,
						default=False,
						type=bool,
						nargs='?')
	parser.add_argument('--scrape',
						help='Scrape emails and social media urls from file.',
						const=True,
						default=False,
						type=bool,
						nargs='?')
	parser.add_argument('--scrape-n',
						help='Scrape emails and social media urls from file with new links.',
						const=True,
						default=False,
						type=bool,
						nargs='?')
	parser.add_argument('--all',
						help='Perform all actions on urls from file with links.',
						const=True,
						default=False,
						type=bool,
						nargs='?')

	args = parser.parse_args()
	parse_and_handle_args(args)

if __name__ == "__main__":
	if len(sys.argv) <= 2 and '--help' not in sys.argv:
		print('Usage:\n$ ./domain_scraper.py --help', file=sys.stderr)
		sys.exit(1)
	start( sys.argv[1:] )