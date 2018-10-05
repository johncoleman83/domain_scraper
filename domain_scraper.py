#!/usr/bin/env python3

import getopt, sys, os

def start( args ):

	longopts = [ "check=", "extract=", "scrape=" ]

	optlist, args = getopt.getopt( args, '', longopts )

	opt = optlist[0]

	func = opt[0].replace( "--", "" ) + "_" + opt[1].replace( "-", "_" ) + ".py"

	path = os.path.join( os.path.dirname(os.path.abspath(__file__)), "modules", func )

	cmd = "python " + path + " " + args[0]

	os.system( cmd )

if __name__ == "__main__":

	start( sys.argv[1:] )