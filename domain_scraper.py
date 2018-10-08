#!/usr/bin/env python3

import getopt, sys, os
import argparse
import random
from modules import *

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

	# Parse arguments

	#Set input var and build url path to input (points to working directory)  
	INPUT_FILE = os.path.join( os.getcwd(), str(args.input_file[0]))
	
	#Get args and pass input to modules
	if args.extract:
		extract.main_app(INPUT_FILE)
	elif args.check:
		check.main_app(INPUT_FILE)
	elif args.scrape:
		scrape.main_app(INPUT_FILE)
	elif args.scrape_n:
		scrape_n.main_app(INPUT_FILE)
	elif args.all:
		extract.main_app(INPUT_FILE)
		check.main_app(INPUT_FILE)
		scrape.main_app(INPUT_FILE)
		scrape_n.main_app(INPUT_FILE)

if __name__ == "__main__":
	#print('This is a WIP entrypoint for all scripts')
	#print('please use this execuation command\n')
	#print('Usage:\n$ ./modules/[SCRIPT_TO_RUN] resources/[FILE_OR_URL_TO_SCRAPE]')
	start( sys.argv[1:] )