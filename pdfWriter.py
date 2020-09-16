from fpdf import FPDF
import helpers
import time
from unidecode import unidecode
import math
import shortLink
from os import sep

class paperWriter(object):
    linesPerPage = 35
    charsPerLine1 = 51
    charsPerLine2 = 101
    charsPerLine3 = 152
    charsPerLine4 = 203
    defaultCellWidth = 82

    def __init__(self,conn):
        self.cur = conn.cursor()
        self.conn = conn

    def selectNews(self,publishAll):
        helpers.debug("SELECT sourceID,cMax from Sources")
        self.cur.execute("SELECT sourceID,cMax from Sources")
        sources = self.cur.fetchall()
        helpers.debug("Returned :"+str(sources))
        # Get a list of the active sources
        # Get ID and max, 
        # ForEach of these
        chosenNews = {}
        esql=""
        if not publishAll:
            esql = " and published = 0 "
        for newsSource in sources:
            sql = 'SELECT * from HISTORY where datePublished > "' + (str(time.time()-(86400*3))) + \
                '" AND sourceID = '+str(newsSource[0])+ esql + ' AND summary not like "%PDF-%" and summary not like ""\
                ORDER BY RANDOM() LIMIT '+str((newsSource[1]+80))
            helpers.debug(str(sql))
            self.cur.execute(sql)
            chosenNews[newsSource[0]] = self.cur.fetchall()
        # Mark the content as used
        # TODO this needs moving to when the content is used as there is a chance the article wont make it to the paper
        #for i in chosenNews:
        #    for j in chosenNews[i]:
        #        helpers.debug("UPDATE HISTORY SET PUBLISHED = 1 where newsID =" + str([j][0][0]))
        #        sql = "UPDATE HISTORY SET PUBLISHED = 1 where newsID =" + str([j][0][0])
        #        self.cur.execute(sql)
        #        self.conn.commit()
        return chosenNews

    def createNewsList(self,chosenNews):
        nItem = []
        nItems = []
        for source in chosenNews:
            for article in chosenNews[source]:
                nItem = list(article)
                nItem.append(str(unidecode(str(nItem[9]))).replace('\n', ' ').replace('\r', ''))
                nItem.append(len(nItem[14]))
                nItem.append(unidecode(nItem[3]).replace('\n', ' ').replace('\r', ''))
                nItem.append(len(nItem[16]))
                newLines = 0
                newLines = nItem[14].count('\n')

                # This section assigns the width of the Cells
                lineCount = int(math.ceil((nItem[15] / self.charsPerLine1) + newLines))
                if lineCount > self.linesPerPage:
                    lineCount = math.ceil((nItem[15] / self.charsPerLine2) + newLines)
                    if lineCount > self.linesPerPage:
                        lineCount = math.ceil((nItem[15] / self.charsPerLine3) + newLines)
                        if lineCount > self.linesPerPage:
                            helpers.warn("Long Thing will look ugly")
                            nItem.append(4)
                            nItem.append(lineCount)
                        else:
                            nItem.append(3)
                            nItem.append(lineCount)
                    else:
                        nItem.append(2)
                        nItem.append(lineCount)
                else:
                    nItem.append(1)
                    nItem.append(lineCount)
                nItem.append(False)
                nItems.append(nItem)# = nItem
        return nItems

    def createPaper(self,conn,nItems,options):
        # page 1 / 2 will be blank for now
        pdf = FPDF('L','mm', 'Legal')
        #pdf.add_font('paper','','/usr/share/fonts/truetype/anonymous-pro/Anonymous Pro.ttf',True)
        #pdf.add_font('paper2','','/usr/share/fonts/truetype/anonymous-pro/Anonymous Pro B.ttf',True)
        pdf.add_page()
        pages = 1
        pdf.set_font('Times','',9)
        added = False
        linesLeft = self.linesPerPage
        prevWidth = -1
        index = 0
        rows = 4
        bump = 0
        x = 10
        y = 10

        nItems = shortLink.getShortlink(nItems)

        from random import shuffle
        shuffle(nItems) # Is this working as expected?

        # TODO : Use a fecking Dict rather than a list, the below is insanity
        while len(nItems):
            linesLeft = self.linesPerPage
            nItemsCopy = nItems
            for item in nItemsCopy:
                helpers.debug(str(item[18])+" : "+str(item[19])+":"+str(len(nItems)))
                if (prevWidth == -1) or (prevWidth == item[18]) or (linesLeft == self.linesPerPage): # we could do == or >= in the prev width check here
                    helpers.debug("item new size or smaller, we are on rows : "+str(rows))
                    if linesLeft < self.linesPerPage:
                    # TODO XXX : Make this more effecient Its the same code block twice
                        if (linesLeft - (item[19]+4) > 0) or (linesLeft == self.linesPerPage):
                                helpers.debug("Item being used")
                                pdf.set_xy(x,y)
                                pdf.set_font('Times','BIU',12)
                                pdf.multi_cell((self.defaultCellWidth*(item[18])), 4,item[14]+" ",0,1,'C')
                                y = (pdf.get_y())
                                pdf.set_xy(x,y)
                                pdf.set_font('Times', '', 12)
                                pdf.multi_cell((self.defaultCellWidth*(item[18])), 4,item[16],0,1,'L')
                                try:
                                    # If we have a short link place it on the page
                                    y = (pdf.get_y())
                                    pdf.set_xy(x,y)
                                    pdf.set_font('Times', '', 8)
                                    from datetime import datetime
                                    pdf.multi_cell((self.defaultCellWidth*(item[18])), 4,str(item[21]+" "+str(datetime.fromtimestamp(item[7]))),0,1,'L')
                                except Exception as e:
                                    helpers.warn("Unable to add shortlink to page " + str(e))

                                if not added:
                                    prevWidth = item[18]
                                added = True
                                linesLeft = (linesLeft - (item[19]+3))
                                item[18] = True
                                nItems.pop(index)
                                y = (pdf.get_y()+1)
                                if linesLeft < 4:
                                    linesLeft = 0
                                    helpers.debug("Broke out of for, less than 4 lines left")
                                    break
                                else:
                                    pass
                        else:
                            pass
                            helpers.debug("   Too Long to fit on page")
                    else:
                        if (((linesLeft == self.linesPerPage) and (rows - item[18]) >= 0)): #or ((linesLeft == self.linesPerPage) and (rows > 0)) and rows > 0 :
                            if (linesLeft - (item[19]+4) > 0) or (linesLeft == self.linesPerPage):
                                helpers.debug("Item being used")
                                pdf.set_xy(x,y)
                                pdf.set_font('Times','BIU',12)
                                pdf.multi_cell((self.defaultCellWidth*(item[18])), 4,item[16]+" ",0,1,'C')
                                y = (pdf.get_y())
                                pdf.set_xy(x,(y+2))
                                if item[18] == 4:
                                    pdf.set_font('Times', '', 8)
                                else:
                                    pdf.set_font('Times', '', 12)
                                pdf.multi_cell((self.defaultCellWidth*(item[18])), 4,(item[14]+'\n'),0,1,'L')
                                try:
                                    from datetime import datetime
                                    # If we have a short link place it on the pahe
                                    y = (pdf.get_y())
                                    pdf.set_xy(x,y)
                                    pdf.set_font('Times', '', 8)
                                    pdf.multi_cell((self.defaultCellWidth*(item[18])), 4,str(item[21]+" "+str(datetime.fromtimestamp(item[7]))),0,1,'L')
                                except Exception as e:
                                    helpers.warn("Unable to add shortlink to page " + str(e))
                                if not added:
                                    prevWidth = item[18]
                                added = True
                                linesLeft = (linesLeft - (item[19]+3))
                                item[20] = True
                                nItems.pop(index)
                                y = (pdf.get_y()+1)
                                if linesLeft < 4:
                                    linesLeft = 0
                                    helpers.debug("Broke out of for, less than 4 lines left")

                                    break
                                else:
                                    pass
                            else:
                                helpers.debug("   Too Long to fit on page")
                            helpers.debug("  Would overflow rows")
                else:
                    helpers.debug(" Wider than above content")
                index += 1
            # set new Row details
            helpers.debug("Now Out of For, added something to the list so marking for deletion")
            bump = bump + prevWidth
            helpers.debug("moving over by "+str(bump))
            rowsleft = 5-rows
            total = self.defaultCellWidth * ((rowsleft +0.2)+4)
            helpers.debug("Total is "+str(total))
            x = 15 + total
            if bump == 1:
                x = (self.defaultCellWidth*(bump+0.1)+2) #+ 25)
            elif bump == 2:
                x = (self.defaultCellWidth*(bump+0.1)+2) #+ 30)
            elif bump == 3:
                x = (self.defaultCellWidth*(bump+0.1)+2) #+ 30)
            else:
                x = (self.defaultCellWidth*(bump+0.1)+2) #+ 45)
            helpers.debug("Total x is "+str(x))
            y = 10
            rows -= prevWidth
            index = 0
            prevWidth = -1
            if not added or rows < 0:
                # Nothing new added at all
                pages += 1
                if pages <= int(options.maxPages):
                    helpers.debug("New Page on page " + str(pages))
                    rows = 4
                    bump = 0
                    x = 10
                    y = 10
                    pdf.add_page()
                    pdf.set_xy(x,y)
                else:
                    helpers.debug("Maximum pages met we are at " + str(pages))
                    break
            else:
                helpers.debug("No New page added")
            added = False

        import datetime
        x = datetime.datetime.now()

        filename = ("."+sep+"papers"+sep+str(x.timestamp()) + '.pdf')
        pdf.output(str(filename), 'F')
        return(str(filename))