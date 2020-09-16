# Newspaper
Create and push a morning paper to the remarkable eReader based on stuff from reddit.

## Example
```
# First time we run we need to have a remarkable token
newspaper.py -t diwubde -m 10 -p

# After this we can just push to the DB
newspaper.py -m 10 -p
```

Its currently not possible to control what sources are used or add source. This is planned

### Short links
This project drops short links onto the page using a simple link shortner i wrote, source for this is available at 
github.com/leostat/simpleshortlinks. I fully expect this to break as its SQLITE.



### Help
```
> python.exe .\newspaper.py -h
Usage: newspaper.py [OPTIONS]

Daily Newspaper Maker

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -m MAXPAGES, --max-pages=MAXPAGES
                        Max pages to generate
  -a SOURCELINE, --add-source=SOURCELINE
                        Add a source to the database
  -n, --no-new-content  Do not try to add new content, Create PDF only.
  -c, --no-create-pdf   Do not create a PDF, Update sources only
  -i, --ignore-pub      Allow Repost
  -u, --upload          Upload file to API's
  -t TOKENVALUE, --token=TOKENVALUE
                        remarkable token
  -d, --debug           Display verbose processing details (default: False)

Example: newspaper.py -m 10 -p
```

