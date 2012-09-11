# -*- coding: utf-8 -*-
#

import os
import parseUsfm
import books
import datetime

header = ur"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta http-equiv="content-type" content="text/html; charset=utf-8" />
            <title>Open English Bible</title>
        </head>
		<style media="all" type="text/css">
		h2.c-num { position:absolute; margin-left:-30px; color: #AAAAAA; }
		span.v-num-1 { display : none; }
		span.v-num { color: #AAAAAA; font-size: small}
		a { color:green; text-decoration:none;}
		p { font-family: Verdana, Helvetica, Arial, Sans-Serif;}
		li { font-family: Verdana, Helvetica, Arial, Sans-Serif;}
		h1 { font-family: Verdana, Helvetica, Arial, Sans-Serif; }
		h2 { font-family: Verdana, Helvetica, Arial, Sans-Serif; }
		h3 { font-family: Verdana, Helvetica, Arial, Sans-Serif; }
		h4 { font-family: Verdana, Helvetica, Arial, Sans-Serif; }
		</style>
        <body>
        <div style="position:absolute; margin-left:5; width:190px; background-color:#E6FAE6;">
		<h2><a href="http://openenglishbible.org">Open<br>English<br>Bible</a></h2>

        <p><b>Old Testament</b></p>
        <ul>
        <li>Genesis</li>
        <li>Exodus</li>
        <li>Leviticus</li>
        <li>Numbers</li>
        <li>Deuteronomy</li>
        <li>Joshua</li>
        <li>Judges</li>
        <li><a href="b008.html">Ruth</a></li>
        <li>1 Samuel</li>
        <li>2 Samuel</li>
        <li>1 Kings</li>
        <li>2 Kings</li>
        <li>1 Chronicles</li>
        <li>2 Chronicles</li>
        <li>Ezra</li>
        <li>Nehemiah</li>
        <li><a href="b017.html">Esther</a></li>
        <li>Job</li>
        <li><a href="b019.html">Psalms</a></li>
        <li>Proverbs</li>
        <li>Ecclesiastes</li>
        <li>Song of Solomon</li>
        <li><a href="b023.html">Isaiah</a></li>
        <li>Jeremiah</li>
        <li>Lamentations</li>
        <li>Ezekiel</li>
        <li><a href="b027.html">Daniel</a></li>
        <li>Hosea</li>
        <li><a href="b029.html">Joel</a></li>
        <li>Amos</li>
        <li><a href="b031.html">Obadiah</a></li>
        <li><a href="b032.html">Jonah</a></li>
        <li>Micah</li>
        <li><a href="b034.html">Nahum</a></li>
        <li><a href="b035.html">Habakkuk</a></li>
        <li><a href="b036.html">Zephaniah</a></li>
        <li><a href="b037.html">Haggai</a></li>
        <li>Zechariah</li>
        <li>Malachi</li>
        </ul>            

        <p><b>New Testament</b></p>
        <ul>
        <li><a href="b040.html">Matthew</a></li>
        <li><a href="b041.html">Mark</a></li>
        <li><a href="b042.html">Luke</a></li>
        <li><a href="b043.html">John</a></li>
        <li><a href="b044.html">Acts</a></li>
        <li><a href="b045.html">Romans</a></li>
        <li><a href="b046.html">1 Corinthians</a></li>
        <li><a href="b047.html">2 Corinthians</a></li>
        <li><a href="b048.html">Galatians</a></li>
        <li><a href="b049.html">Ephesians</a></li>
        <li><a href="b050.html">Philippians</a></li>
        <li><a href="b051.html">Colossians</a></li>
        <li><a href="b052.html">1 Thessalonians</a></li>
        <li><a href="b053.html">2 Thessalonians</a></li>
        <li><a href="b054.html">1 Timothy</a></li>
        <li><a href="b055.html">2 Timothy</a></li>
        <li><a href="b056.html">Titus</a></li>
        <li><a href="b057.html">Philemon</a></li>
        <li><a href="b058.html">Hebrews</a></li>
        <li><a href="b059.html">James</a></li>
        <li><a href="b060.html">1 Peter</a></li>
        <li><a href="b061.html">2 Peter</a></li>
        <li><a href="b062.html">1 John</a></li>
        <li><a href="b063.html">2 John</a></li>
        <li><a href="b064.html">3 John</a></li>
        <li><a href="b065.html">Jude</a></li>
        <li><a href="b066.html">Revelation</a></li>
        </ul>
        </div>
        <div style="margin-left:230px; margin-right:80px">
        """

class DummyFile(object):
    def close(self):
        pass
    def write(self, str):
        pass

class ReaderPrinter(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        self.f = DummyFile()
        self.cb = u''    # Current Book
        self.cc = u'001'    # Current Chapter
        self.cv = u'001'    # Currrent Verse
        self.indentFlag = False
        
    def close(self): pass # Dummy
 
    def write(self, unicodeString):
        self.f.write(unicodeString.encode('utf-8'))

    def writeIndent(self, level):
        if level == 0:
            self.indentFlag = False
            self.write(u'<br /><br />')
            return 
        if not self.indentFlag:
            self.indentFlag = True
            self.write(u'<br />')
        self.write(u'<br />')
        self.write(u'&nbsp;&nbsp;&nbsp;&nbsp;' * level)

    def renderID(self, token): 
        self.write(u'</p></div></body>')
        self.f.close()
        self.cb = books.bookKeyForIdValue(token.value)
        self.f = open(self.outputDir + u'/b' + self.cb + u'.html', 'w')
        self.write(header)
        self.indentFlag = False
    def renderIDE(self, token):     pass
    def renderH(self, token):       pass # self.write(u'</p><h1 class="bookname">' + token.value + u'</h1><p>')
    def renderMT(self, token):      self.write(u'</p><h1>' + token.value + u'</h1><p>')
    def renderMT2(self, token):      self.write(u'</p><h2>' + token.value + u'</h2><p>')
    def renderMS(self, token):      self.write(u'</p><h4>' + token.value + u'</h4><p><br />')
    def renderMS2(self, token):     self.write(u'</p><h5>' + token.value + u'</h5><p><br />')
    def renderP(self, token):
        self.indentFlag = False
        self.write(u'<br /><br />')
    def renderS(self, token):
        self.indentFlag = False
        self.write(u'</p><p align="center">_________________________</p><p>')
    def renderS2(self, token):
        self.indentFlag = False
        self.write(u'</p><p align="center">----</p><p>')
    def renderC(self, token):
        self.cc = token.value.zfill(3)
        self.write(u'<h2 class="c-num">' + token.value + u'</h2><p>')
    def renderV(self, token):
        self.cv = token.value.zfill(3)
        if self.cv == u'001':
            self.write(u'\n<span class="verse" rel="v' + self.cb + self.cc + self.cv + u'"><span class="v-num-1">' + token.value + u'&nbsp;</span>\n')
        else:
            self.write(u'</span>\n<span class="verse" rel="v' + self.cb + self.cc + self.cv + u'"><span class="v-num">' + token.value + u'&nbsp;</span>\n')
    def renderWJS(self, token):     self.write(u'<span class="woc">')
    def renderWJE(self, token):     self.write(u'</span>')
    def renderTEXT(self, token):    self.write(u" " + token.value + u" ")
    def renderQ(self, token):       self.writeIndent(1)
    def renderQ1(self, token):      self.writeIndent(1)
    def renderQ2(self, token):      self.writeIndent(2)
    def renderQ3(self, token):      self.writeIndent(3)
    def renderNB(self, token):      self.writeIndent(0)
    def renderB(self, token):       self.write(u'<br /><br />')
    def renderQTS(self, token):     pass
    def renderQTE(self, token):     pass
    def renderFS(self, token):      pass
    def renderFE(self, token):      pass
    def renderIS(self, token):      self.write(u'<i>')
    def renderIE(self, token):      self.write(u'</i>')
    def renderNDS(self, token):     pass
    def renderNDE(self, token):     pass
    def renderPBR(self, token):     self.write(u'<br />')
    def renderD(self, token):       pass # For now
    def renderREM(self, token):     pass # This is for comments in the USFM

class TransformToHTML(object):
    outputDir = ''
    patchedDir = ''
    prefaceDir = ''
 
    def setupAndRun(self, patchedDir, prefaceDir, outputDir):
        self.patchedDir = patchedDir
        self.prefaceDir = prefaceDir
        self.outputDir = outputDir

        self.booksUsfm = books.loadBooks(patchedDir)
        self.printer = ReaderPrinter(self.outputDir)

        for bookName in books.silNames:
            if self.booksUsfm.has_key(bookName):
                tokens = parseUsfm.parseString(self.booksUsfm[bookName])
                for t in tokens: t.renderOn(self.printer)
                self.printer.close()
                print '      (' + bookName + ')'
        self.printer.close()

        index = header + ur"""
            <h1>Open English Bible</h1>
            <p>Release of """ + datetime.date.today().strftime("%A %d. %B %Y") + u"""</p>
            </div>
            </body>
            </html>
            """
    
        f = open(self.outputDir + u'/index.html', 'w')
        f.write(index.encode('utf-8'))
        f.close()
        
