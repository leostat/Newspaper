#
#!/usr/bin/env python3
#
##
import optparse
import pprint
import urllib.request, urllib.parse, urllib.error
import hashlib
import sys
import sqlite3
import os.path
import signal
import json
import feedparser
from sumy.parsers.html import HtmlParser
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer


import pdfWriter
import shortLink
import fileUpload
import helpers

# Requires
# Also
# pip install numpy
# NLTK tokenizers are missing. Download them by following command: python -c "import nltk; nltk.download('punkt')"

#########################################################################
# Gooooooooooooood Reading Good Reading Good Reading Good reading
#           And Welcome to newsPaper
#########################################################################
#########################################################################
# Copyright: lololol
#########################################################################
__version__ = "1.0.1"
__prog__ = "Newspaper"
__authors__ = ["Senni"]

#########################################################################
## Fixes:
##   * Go back over the database and find things which do not conform and retry the get - If nothing blat them after two attempts?
## Pipeline:
##   * Make the handling of the sources more sane
## Future:
#########################################################################

#########################################################################
# Configuration
#########################################################################

EXIT_CODES = {
        "ok"      : 0,
        "generic" : 1,
        "invalid" : 3,
        "missing" : 5,
        "limit"   : 7,
}

#########################################################################
# Main program
#########################################################################

def pushreMarkable(filename):
    """ Push PDF to remarkable device """
    helpers.debug("Call to push paper")
    # This should be set via more options!
    if not filename:
        helpers.debug("No filename so making one up")
        filename = (str(x.timestamp()) + '.pdf', 'F')
    paperKid = fileUpload.paperKid(filename)
    bike = paperKid.getAuth(options.tokenValue)
    if bike:
        paperKid.yeetPaper()

def procURL(url):
    """ Process Weird URL's IE Youtube, PDF, MS, Oracle """
    # if youtube
    # elif youtube playlist
    # elif ..
    # else
    # warn(shouldnt hapen)
    pass

def writeContent(contentList,conn):
    """Write New Articles to the DB """
    helpers.debug("    I: INSERT INTO History values (NULL,?,?,?,?,?,NULL,?,?,?,?,NULL,?)")
    cur = conn.cursor()
    # As its a list use many

    cur.executemany("INSERT OR IGNORE INTO History(\
    'newsID','Source','Author','Title','URL','permURL','published','datePublished','weight','summary','borked','sourceID') \
    values(NULL,:Source,:Author,:Title,:URL,:permURL,0,:datePublished,:weight,:summary,NULL,:sourceID)"\
    ,contentList)
    try:
        conn.commit()
    except Exception as e:
        # TODO: Try to write indevidual things at this point incase its one corrupt thing 
        helpers.debug("write failed  : "+str(e))

def enrichContent(contentList):

    import nltk
    nltk.download('punkt')
    """ Take in list of dict meta object and spit out minified content """
    i = 0
    cur = conn.cursor()
    # This should be stored in the database XXX
    #differntUrl = ['youtube.com','rnetsecs_q4_2018_information_security_hiring','the_rnetsec_monthly_discussion_thread','github.com']

    # If comes from reddit see if we are able to grab meta author from the site, only use the HTML 5 or authortags
    for item in contentList:
        url = item['URL']
        #helpers.debug(str(item['datePublished']))
        if item['URL']:
            # This block is to reduce network traffic by checking if we allready have the content form the block we are returning
            cur.execute('SELECT summary FROM history where URL = :URL', (item['URL'],))
            source = cur.fetchall()
            if len(source) < 1:
                url = item['URL']
                # hack to skip a video in netsec, who posts a MP4!?!! :'( 
                if ".mp4" in url:
                    url = ''
                try:
                    parser = HtmlParser.from_url(url,Tokenizer('english'))
                    """ python3 -m sumy lsa --url 'https://a.b.com/d' Arrays cannot be empty """
                    # This is the error when the LSA fails
                    stemmer = Stemmer('english')
                    summarizer = Summarizer(stemmer)
                    value = summarizer(parser.document, 20)
                    textSum = ""
                    for line in value:
                        textSum += str(line)
                    contentList[i]['summary'] = str(textSum)
                except Exception as e:
                    contentList[i]['summary'] = "Error" + str(e)
                    helpers.warn(str(e))

            else: # Else for if source
                helpers.debug('Not running Stemmer as we already seem to have the summary')
                contentList[i]['summary'] = str(source)
        else: # else for if item['URL']
            contentList[i]['summary'] = "Page did not return URL "

        i += 1
    return contentList

# TODO : Processors need to be split into their own file now as there is more than use reddit
def procReddit(line,contentList,after):
    """ Process a JSON reddit feed, doesnt load the back end content only the meta """
    helpers.debug(line)
    helpers.debug(contentList)
    helpers.debug(after)
    rurl = line[7]+"?after="+after
    with urllib.request.urlopen(urllib.request.Request(rurl,headers={'User-Agent': 'Mozilla Newspaper'})) as url:
        try:
            feed = json.loads(url.read().decode())
        except:
            helpers.debug(" ! Connection error on : "+str(line[7]))
            return(contentList)

    for post in feed['data']['children']:
        content = {\
            'Source' : post['data']['subreddit'],\
            'Author' : post['data']['author'],\
            'Title':post['data']['title'].strip('\n'),\
            'URL':post['data']['url'],\
            'permURL':post['data']['permalink'],\
            'after':post['data']['name'],\
            'datePublished':int(post['data']['created_utc']),\
            'sourceID':line[0]}
        
        if post['data']['score'] > 200:
            content['weight'] =  line[5]
        elif post['data']['score'] > 100:
            content['weight'] =  line[5]/2
        elif post['data']['score'] > 50:
            content['weight'] =  line[5]/3
        elif post['data']['score'] > 25:
            content['weight'] =  line[5]/4
        elif post['data']['score'] < 25:
            content['weight'] =  line[5]/5
        else:
            content['weight'] =  1
        # TODO : Turn this into a function, post['data']['contentList'] would be a varible
        #if not any(d['main_color'] == 'red' for d in a):
        if not any(d['permURL'] == post['data']['permalink'] for d in contentList):
            contentList.append(content)
        else:
            pass
            #helpers.debug("Dupe post : "+post['data']['permalink'])
    return(contentList)


def procConf(line, conn, contentList):
    """ Generate and metadata Dicts to database, this way only a single insert 
    These lists should only contain the Meta, not the actuall content, 
    actual content is delt with in enrichContent
    content = {:author,:title,:url,:}
    """
    if line[3] == 'json':
        # TODO: each sub should use its own content list which then gets smuched at the end, else it is hella inefficient
        if line[4] == "reddit":
            helpers.debug("  - Its a reddit feed")
            contentList = procReddit(line,contentList,"")
            
            # TODO : Turn this into a process archive reddit
            # TODO : access older posts
           # counter = 0
           # while counter < 100:
           #     afterbefore = contentList[-1]['after']
           #     contentList = procReddit(line,contentList,contentList[-1]['after'])
           #     afterafter = contentList[-1]['after']
           #     counter += 1
           #     if afterafter == afterbefore:
           #         helpers.warn('Out Of posts?')
           #         break;
           #     helpers.debug(contentList[-1]['after'])
        elif line[4] == 'mwr':
            pass
        elif line[4] == 'ncc':
            pass
        elif line[4] == 'harmjoy':
            pass
        elif line[4] == 'foxglove':
            pass
        elif line[4] == 'adsecurity':
            pass
        elif line[4] == 'necurity-nsa':
            # This is the NSA threat mappings, uses necurity php api
            pass
        elif line[4] == 'necurity-attack':
            # Get the MITRE attack framework bits
            pass
        elif line[4] == 'necurity-french':
            # Maybe for french tibbits
            pass
        elif line[4] == 'necurity-chinese':
            # Maybe for chinese tibbits
            pass
        else:
            helpers.warn("  - Unknown Subtype : "+line[4])
    else:
        helpers.warn("  - Unknown Type : "+line[3])
    return contentList


def run():
    helpers.ok("Starting")
    if options.debugging:
        helpers.debug("Debugging requested")
    else:
        # Overwride the debug function
        helpers.debug = helpers.fakedebug

    helpers.debug('SELECT * FROM Sources;')
    sql = 'SELECT * FROM Sources'
    cur = conn.cursor()
    cur.execute(sql)
    source = cur.fetchall()
    contentList = []
    if not options.noNewContent:
        helpers.debug("Start getting content")
        for line in source:
            helpers.debug("Processing : "+str(line))
            contentList  = procConf(line,conn,contentList)
            if contentList == 0:
                helpers.warn(" !! Total Failure of source SQL !! : "+str(source))

        #XXX : We need to move all other functions to seperate files 
        contentList = enrichContent(contentList)
        # Store the content in the database
        writeContent(contentList,conn)
    else:
            helpers.debug("User has Requested No new content")

    if not options.noNewPDF:
        helpers.ok("Making paper")
        paperPress = pdfWriter.paperWriter(conn)
        chosenNews = paperPress.selectNews(options.publishAll)
        nItems = paperPress.createNewsList(chosenNews)
        # TODO : Dont pass all of options, only pass what we need
        filename = paperPress.createPaper(conn,nItems,options)
    else: 
        helpers.debug("User has requested no new PDF")

    if options.uploadFile:
        helpers.ok("Pushing File")
        pushreMarkable(filename)
    else:
        helpers.debug("File not being pushed")

    helpers.ok("Done so exiting, Have a nice day :-) ")
    return 0


#########################################################################
# Starting point
#########################################################################
if __name__ == "__main__":
        if os.path.exists(os.path.dirname(os.path.realpath(sys.argv[0]))+'/History.db'):
                conn = sqlite3.connect(os.path.dirname(os.path.realpath(sys.argv[0]))+'/History.db')
                conn.text_factory = str
        else:
                try:
                        helpers.warn("Cant access the DB, creating a new one in the run path")
                        conn = sqlite3.connect(os.path.dirname(os.path.realpath(sys.argv[0]))+os.sep+'History.db')
                        conn.text_factory = str
                        cur = conn.cursor()
                        f = open(os.path.dirname(os.path.realpath(sys.argv[0]))+os.sep+'clean.sql','r')
                        sql_db = f.read()
                        cur.executescript(sql_db)
                except Exception as e:
                        helpers.debug(e)
                        helpers.err("Can not access a DB and can not create the file, giving up :'( ")
        cur = conn.cursor()
      
        parser = optparse.OptionParser(\
                usage="Usage: %prog [OPTIONS]",
                version="%s: v%s (%s) " % (__prog__, __version__, \
                        ','.join(__authors__), ),
                description="Daily Newspaper Maker",
                epilog="Example: newspaper.py -m 10 -u")

        parser.add_option("-m", "--max-pages", action="store", dest="maxPages",\
            help="Max pages to generate")

        parser.add_option("-a", "--add-source", action="store", dest="sourceLine",\
            help="Add a source to the database")

#        parser.add_option("-s", "--source", action="store", dest="sourceOnly",\
#            help="ID's of sources we want to use") Future flag

        parser.add_option("-n", "--no-new-content", action="store_true", dest="noNewContent",\
            help="Do not try to add new content, Create PDF only.")

        parser.add_option("-c", "--no-create-pdf", action="store_true", dest="noNewPDF",\
            help="Do not create a PDF, Update sources only")

        parser.add_option("-i", "--ignore-pub", action="store_true", dest="publishAll",\
            help="Allow Repost")

        parser.add_option("-u","--upload",action="store_true",dest="uploadFile",help="Upload file to API's")

        parser.add_option("-t","--token",action="store",dest="tokenValue",help="remarkable token")

        parser.add_option('-d', '--debug', action='store_true', dest="debugging",\
            help='Display verbose processing details (default: False)')

        (options, args) = parser.parse_args()
        run()