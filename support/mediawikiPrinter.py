# -*- coding: utf-8 -*-
#

import os
import parseUsfm
import books

class DummyFile(object):
    def close(self):
        pass
    def write(self, str):
        pass

class MediaWikiPrinter(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        self.f = DummyFile()
        self.cb = u''       # Current Book
        self.cc = u'001'    # Current Chapter
        self.ccUnfil = u'1' # same, not padded.
        self.cv = u'001'    # Currrent Verse
        self.indentFlag   = False
        self.footnoteFlag = False

    def write(self, unicodeString):
        self.f.write(unicodeString.encode('utf-8'))

    def renderID(self, token):
        self.write(u'</p>')
        self.f.close()
        self.cb = books.bookKeys[token.value[:3]]
        self.f = open(self.outputDir + u'/c' + self.cb + u'001.html', 'w')
        self.write(u'\n<!-- \\id ' + self.cb + u' -->')
        self.indentFlag = False
    def renderIDE(self, token):     pass
    def renderTOC2(self, token):    self.write(u' Bible:' + token.value + u'_# ')
    def renderH(self, token):       self.write(u'\n<!-- \\h ' + token.value + u' -->')
    def renderMT(self, token):      self.write(u'\n<!-- \\mt1 ' + token.value + u' -->')
    def renderMS(self, token):      pass
    def renderMS2(self, token):     pass
    def renderP(self, token):
        self.indentFlag = False
        self.write(u'\n\n')
    def renderS(self, token):
        self.indentFlag = False
        self.write(u'\n=== ' + token.value + u' === ')
    def renderS2(self, token):
        self.indentFlag = False
        pass
    def renderR(self, token):       self.write('\n<span class="srefs">' + token.value + '</span>')
    def renderC(self, token):
        self.cc = token.value.zfill(3)
        self.ccUnfil = token.getValue()
        if self.cc == u'001':
            self.write(u'Bible:' + self.cb + u'_' + token.value + u' ')
        else:
            self.write(u'\n\n')
            self.f.close()
            self.f = open(self.outputDir + u'/c' + self.cb + self.cc + u'.html', 'w')
            self.write(u'Bible:' + self.cb + u'_' + token.value + u' ')
    def renderV(self, token):
        self.cv = token.value.zfill(3)
        if not self.cv == u'001': self.write(u'<\span>\n')
        self.write(u'<span id="' + self.ccUnfil + u'_' + token.getValue() + u'"><sup>' + token.getValue() + u'</sup>')

    def renderWJS(self, token):     pass
    def renderWJE(self, token):     pass
    def renderTEXT(self, token):
        if self.footnoteFlag:       self.footnoteFlag = False; self.write(u' -->')
        self.write(token.getValue())
    def renderQ(self, token):       self.write(u'\n:')
    def renderQ1(self, token):      self.write(u'\n::')
    def renderQ2(self, token):      pass
    def renderQ3(self, token):      pass
    def renderNB(self, token):      pass
    def renderQTS(self, token):     pass
    def renderQTE(self, token):     pass
    def renderFS(self, token):      self.write(u'<ref><!-- '); self.footnoteFlag = True
    def renderFT(self, token):      self.write(u'\\ft ' + token.getValue())
    def renderFK(self, token):      self.write(u'\\fk ' + token.getValue())
    def renderFE(self, token):
        if self.footnoteFlag:       self.footnoteFlag = False; self.write(u' -->')
        self.write(u'</ref>')
    def renderIS(self, token):      pass
    def renderIE(self, token):      pass
    def renderB(self, token):       pass
    def renderD(self, token):       pass
    def renderADDS(self, token):    pass
    def renderADDE(self, token):    pass
    def renderLI(self, token):      self.write(u'\n:<!-- \li -->')
    def renderSP(self, token):      pass
    def renderNDS(self, token):     pass
    def renderNDE(self, token):     pass
    def renderPBR(self, token):     pass
    def renderFR(self, token):      pass
    def renderFRE(self, token):     pass
    def renderXS(self, token):      pass
    def renderXE(self, token):      pass
    def renderXDCS(self, token):    pass
    def renderXDCE(self, token):    pass
    def renderXO(self, token):      pass
    def renderXT(self, token):      pass
    def renderM(self, token):       pass
    def renderMI(self, token):      pass
    def renderTLS(self, token):     pass
    def renderTLE(self, token):     pass
    def renderPI(self, token):      pass
    def renderSCS(self, token):     pass
    def renderSCE(self, token):     pass

class Transform(object):

    def stripUnicodeHeader(self, unicodeString):
        if unicodeString[0] == u'\ufeff':
            return unicodeString[1:]
        else:
            return unicodeString

    def translateBook(self, usfm):
         tokens = parseUsfm.parseString(usfm)
         tp = MediaWikiPrinter(self.outputDir)
         for t in tokens: t.renderOn(tp)

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

    def setupAndRun(self, patchedDir, outputDir):
        self.outputDir = outputDir
        self.booksUsfm = self.loadBooks(patchedDir)

        for bookName in books.silNames:
            if self.booksUsfm.has_key(bookName):
                print '     ' + bookName
                self.translateBook(self.booksUsfm[bookName])
