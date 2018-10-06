#!/usr/bin/env python3

import getopt, sys, os

def start( args ):
"""
WIP
Idea is to use input arguments to execute the appropriate script
from modules

optlist:
--check=broken-links
--extract=name-from-email
--scrape=emais-socmedia
--scrape=emails_and_social_media_no_new_links

args:
some input file with links

usage:
$ python3 optlis_option arg
"""
	longopts = [ "check=", "extract=", "scrape=" ]

	optlist, args = getopt.getopt( args, '', longopts )

	opt = optlist[0]

	func = opt[0].replace( "--", "" ) + "_" + opt[1].replace( "-", "_" ) + ".py"

	path = os.path.join( os.path.dirname(os.path.abspath(__file__)), "modules", func )

	cmd = "python " + path + " " + args[0]

	os.system( cmd )

if __name__ == "__main__":

	start( sys.argv[1:] )
