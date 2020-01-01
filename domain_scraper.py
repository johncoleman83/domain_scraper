#!/usr/bin/env python3

import getopt, sys, os
import argparse
import random
from modules import *

def parse_and_handle_args(args):
	"""
	Handles arguments extracted from the user inputs
	#Set input var and build url path to input (points to working directory)
	"""
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
		INPUT_URL = args.url[0]
		INPUT_FILE = None
	if args.url:
		print('executing: {}'.format(url_input))
		url_input.execute(INPUT_URL)
	elif args.check:
		print('executing: {}'.format(check))
		check.execute(INPUT_FILE)
	elif args.check_json:
		print('executing: {}'.format(check_json))
		check_json.execute(INPUT_FILE)
	elif args.extract:
		print('executing: {}'.format(extract))
		extract.execute(INPUT_FILE)
	elif args.scrape:
		print('executing: {}'.format(scrape))
		scrape.execute(INPUT_FILE)
	elif args.scrape_n:
		print('executing: {}'.format(scrape_n))
		scrape_n.execute(INPUT_FILE)

def init_parser():
	"""
	sets up parser with expected arguments
	"""
	parser = argparse.ArgumentParser(
		prog='domain_scraper',
		description='''Scrapes domains from one input URL or 
		from a file list of domains for broken links, 
		valid emails, and valid social media links.''',
	)
	parser.add_argument(
		'input_file',
		help='Indicate the input file to scrape.  Files must be formated like the files in the examples directory.',
		type=str,
		nargs='*'
	)
	parser.add_argument(
		'--url',
		help='Indicate the url to scrape.',
		type=str,
		nargs='*'
	)
	parser.add_argument(
		'--check',
		help='Find broken links from urls in input file.',
		const=True, default=False,
		type=bool,
		nargs='?'
	)
	parser.add_argument(
		'--check-json',
		help='Find broken links from urls in input json.',
		const=True,
		default=False,
		type=bool,
		nargs='?'
	)
	parser.add_argument(
		'--extract',
		help='Extract name from emails in input file.',
		const=True,
		default=False,
		type=bool,
		nargs='?'
	)
	parser.add_argument(
		'--scrape',
		help='Scrape emails and social media urls from urls in file.',
		const=True,
		default=False,
		type=bool,
		nargs='?'
	)
	parser.add_argument(
		'--scrape-n',
		help='Scrape emails and social media urls from urls in file while adding new urls to the queue to scrape.',
		const=True,
		default=False,
		type=bool,
		nargs='?'
	)
	return parser

def execute():
	"""
	MAIN APP
	"""
	parser = init_parser()
	parsed_args = parser.parse_args()
	parse_and_handle_args(parsed_args)

if __name__ == "__main__":
	if len(sys.argv) <= 2 and '--help' not in sys.argv:
		print('Usage:\n$ ./domain_scraper.py --help', file=sys.stderr)
		sys.exit(1)
	execute()