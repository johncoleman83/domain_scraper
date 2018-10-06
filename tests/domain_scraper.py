import os

"""
--check=broken-links
--extract=name-from-email
--scrape=emais-socmedia
--scrape=emails_and_social_media_no_new_links
"""

domain_scraper = os.path.dirname( os.path.dirname(os.path.abspath(__file__)) ) + os.path.sep + "domain_scraper.py"
test_file = os.path.join( os.path.dirname(os.path.abspath(__file__)), "resources", "example_file.txt" )
cmd = "python " + domain_scraper + " --check=broken-links " + test_file

os.system( cmd )