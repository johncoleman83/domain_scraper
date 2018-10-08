# domain_scraper

Scrapes domains from one input URL or from a file list of domains for broken links,
valid emails and valid social media links.

## Usage

*  Check URL's from text file to scrape for emails and social media links. This also
  checks common paths found from the input domain such as contact and team pages to add
  to the queue to new URL's to scrape for emails and social media links. This
  does not store broken links, but does output them to STDOUT during runtime. This
  does save to a file all valid & unique emails addresses and social media links
  during runtime so data is stored in the event of an error.

```shell
$ python domain_scraper.py [INPUT FILE] --scrape-n
```

*  Same as above, but do not check for new links to add to the queue

```shell
$ python domain_scraper.py [INPUT FILE] --scrape
```

*  To check all URLS from the same domain based off of one main input URL

```shell
$ python domain_scraper.py --url [URL TO SCRAPE]
```

*  Check URL's for broken links from text file

```shell
$ python domain_scraper.py [INPUT FILE] --check
```

*  extract name associations from email list

```shell
$ python domain_scraper.py [INPUT FILE] --extract
```

## Data storage

Data is written to a file during runtime of the email and social media scraper.  Data is only
written to files at program completion for the broken link checkers.

TODO: The broken link checkers should output results to a file during runtime and not wait until
the end of the program

## Example file & file cleanup

__how to cleanup a .csv file__

```shell
$ cat example_file_bad_format.txt
https://google.com/^Mhttps://cecinestpasun.site/^Mhttps://google.com/^Mhttp://www.davidjohncoleman.com/wp-content/uploads/2017/06/headshot-retro.png

# replace ^M character after copying from .csv file
$ tr '\r' '\n' < example_file_bad_format.txt > example_file.txt

# remove repeat links
$ awk '!seen[$0]++' example_file.txt > example_file_no_repeats.txt

$ cat example_file.txt
https://google.com/
https://cecinestpasun.site/
http://www.davidjohncoleman.com/wp-content/uploads/2017/06/headshot-retro.png
```

## Author

*  David John Coleman II, [davidjohncoleman.com](http://www.davidjohncoleman.com/)
| [@djohncoleman](https://twitter.com/djohncoleman)

## Contributors

*  edikxl, [@edikxl](https://github.com/edikxl)
*  mrvnmchm, [@mrvnmchm](https://github.com/mrvnmchm)
## License

MIT License
