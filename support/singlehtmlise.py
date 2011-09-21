# -*- coding: utf-8 -*-
#

import os
import parseUsfm
import books
import datetime

class ReaderPrinter(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        self.cb = u''    # Current Book
        self.cc = u'001'    # Current Chapter
        self.cv = u'001'    # Currrent Verse
        self.indentFlag = False
        self.rendered = u''
        self.bookName = u''
 
    def write(self, unicodeString):
        self.rendered = self.rendered + unicodeString
        
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
        self.cb = books.bookKeys[token.value]
        self.indentFlag = False
    def renderIDE(self, token):     pass
    def renderH(self, token):       self.bookname = token.value; self.write(u'</p><h1 class="bookname">' + token.value + u'</h1><p>')
    def renderMT(self, token):      self.write(u'</p><h3>' + token.value + u'</h3><p>')
    def renderMS(self, token):      self.write(u'</p><h4>' + token.value + u'</h4><p><br />')
    def renderMS2(self, token):     self.write(u'</p><h5>' + token.value + u'</h5><p><br />')
    def renderP(self, token):
        self.indentFlag = False
        self.write(u'<br /><br />')
    def renderS(self, token):
        self.indentFlag = False
        self.write(u'</p><p><h2 align="center">' + token.getValue() + u'</h2><p><p>')
    def renderS2(self, token):
        self.indentFlag = False
        self.write(u'</p><p align="center">----</p><p>')
    def renderC(self, token):
        self.cc = token.value.zfill(3)
        self.write(u'\n<span class="c-num">[' + self.bookname + ' ' + token.value + u']</span>\n')
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
    def renderSCS(self, token):     self.write(u'<b>')
    def renderSCE(self, token):     self.write(u'</b>')

class TransformToHTML(object):
    outputDir = ''
    patchedDir = ''
    prefaceDir = ''

    def loadBooks(self, path):
        books = {}
        dirList=os.listdir(path)
        for fname in dirList:
          if fname[-5:] == '.usfm':
              f = open(path + '/' + fname)
              usfm = unicode(f.read(), 'utf-8')
              books[self.bookID(usfm)] = usfm
              f.close()
        return books

    def bookID(self, usfm):
        return books.bookID(usfm)

    def translateBook(self, usfm):
        tokens = parseUsfm.parseString(usfm)
        for t in tokens: t.renderOn(self.printer)
 
    def setupAndRun(self, patchedDir, prefaceDir, outputDir, buildName):
        self.patchedDir = patchedDir
        self.prefaceDir = prefaceDir
        self.outputDir = outputDir
        self.booksUsfm = self.loadBooks(patchedDir)
        self.printer = ReaderPrinter(self.outputDir)

        bookTex = u''

        for bookName in books.silNames:
            if self.booksUsfm.has_key(bookName):
                self.translateBook(self.booksUsfm[bookName])
                print '      (' + bookName + ')'

        f = open(self.outputDir + buildName, 'w')
        f.write(u"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta http-equiv="content-type" content="text/html; charset=utf-8" />
            <title>Open English Bible</title>
        </head>
		<style media="all" type="text/css">
		span.c-num { color: #AAAAAA; }
		span.v-num-1 { display : none; }
		span.v-num { color: #AAAAAA; font-size: small}
		</style>
        <body>
        <h1>Open English Bible</h1>
        """.encode('utf-8'))
        f.write('<p><i>Draft built ' + datetime.date.today().strftime("%A, %d %B %Y") + '</i><br />Version ' + buildName + '</p>\n\n<p><p>')
        f.write(self.printer.rendered.encode('utf-8'))
        f.write('</body></html>')
        f.close()
        
