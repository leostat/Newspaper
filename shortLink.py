import helpers
import urllib.request, urllib.parse, urllib.error

def getShortlink(contentList):
    """ ask for new shortlink """
    i = 0
    cc = contentList
    for item in cc:
        try:
            a = urllib.request.urlopen("https://lg.lc/3/index.php?url="+str(item[4]))
            shortLink = a.read().decode("utf-8")
            item.append("https://lg.lc/3/index.php?url=>"+shortLink)
            contentList[i] = item
            helpers.debug("Shortlink ID : "+str(shortLink))
            i += 1
        except:
            helpers.debug('Unable To connect to Chosen Shortlinker')
    return contentList
