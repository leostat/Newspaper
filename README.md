# Newspaper
Create and push a morning paper to the remarkable eReader based on stuff from reddit.

## Example / quickstart

You can just run newspaper.py and it will put a paper in ./papers/ 
```
newspaper.py
```

You can set other options to do other things

### Pushing to the remarkable API
There is a problem with the rmapy project where on line 120 of api.py its missing. https://github.com/subutux/rmapy/issues/1
```
body=body
```

As such you need to fix this first before being able to talk to remarkable.

First time we run we need to have a remarkable token. Get this by registering a new device on my.remarkable.com
```
newspaper.py -t tokenval -m 10 -u
PS C:\Users\i91\Dropbox\GIT\Newspaper> python.exe .\newspaper.py -u -m 30
[OK]: Starting
[OK]: Making paper
[WARNING]: Long Thing will look ugly
[OK]: Pushing File
[OK]: Done so exiting, Have a nice day :-)

```

Once we do this once, we can just push to the DB
```
newspaper.py -m 10 -u
PS C:\Users\i91\Dropbox\GIT\Newspaper> python.exe .\newspaper.py -u -m 30
[OK]: Starting
[OK]: Making paper
[WARNING]: Long Thing will look ugly
[OK]: Pushing File
[OK]: Done so exiting, Have a nice day :-)
```



If something goes wrong, add -d for *lots* of debugging. Hopefully you wont need it
```
newspaper.py -d -m 10 -u
[OK]: Starting
[DEBUG]: Debugging requested
[DEBUG]: SELECT * FROM Sources;
[DEBUG]: Start w
[DEBUG]: Processing : (1, 'RedditNetSecNew', 'Unkown Reddit User', 'json', 'reddit', 0.7, 15, 'https://reddit.com/r/netsec/new/.json', 0, 0)
[DEBUG]: (1, 'RedditNetSecNew', 'Unkown Reddit User', 'json', 'reddit', 0.7, 15, 'https://reddit.com/r/netsec/new/.json', 0, 0)
[DEBUG]:   - Its a reddit feed
[DEBUG]: (1, 'RedditNetSecNew', 'Unkown Reddit User', 'json', 'reddit', 0.7, 15, 'https://reddit.com/r/netsec/new/.json', 0, 0)
[DEBUG]: []
[DEBUG]:
```

Its currently not possible to control what sources are used or add source. This is planned

###


### Short links
This project drops short links onto the page using a simple link shortner i wrote, source for this is available at 
https://github.com/leostat/simpleshortlink. I fully expect this to break as its SQLITE.



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

