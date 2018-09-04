# broken_link_checker

Scrapes a domain to check status of all links or checks status of all links from
an input file

## Usage

* To check all URLS from the same domain based off of one main input URL

```
$ ./scrape_url.py [URL_TO_CHECK]
```

* Check URL's from text file (a file with 2258 links took about 1 hour to
  complete on MacBook Pro 2017)

```
$ ./scrape_file.py [FILE_WITH_URLS]
```

## Example file & file cleanup

```
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

* David John Coleman II, [davidjohncoleman.com](http://www.davidjohncoleman.com/)
| [@djohncoleman](https://twitter.com/djohncoleman)

## License

MIT License
