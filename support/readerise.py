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

class ReaderPrinter(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        self.f = DummyFile()
        self.cb = u''    # Current Book
        self.cc = u'001'    # Current Chapter
        self.cv = u'001'    # Currrent Verse
        self.indentFlag = False
        self.inSpanFlag = False
        self.inParaFlag = False
 
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
        if self.inSpanFlag:
                self.inSpanFlag = False
                self.write(u'</span>')
        if self.inParaFlag:
                self.inParaFlag = False
                self.write(u'\n</p>')
        self.write(u'\n</article>')
        self.f.close()
        self.cb = books.bookKeys[token.value[:3]]
        self.f = open(self.outputDir + u'/c' + self.cb + u'001.html', 'w')
        self.write(u'\n<!--\ntitle:  Matthew 1 (Open English Bible)\nauthor: http://www.biblewebapp.com/\ndate:   4/22/2010 3:34:43 PM\n-->\n<article class="chapter nt oeb" lang="en" dir="ltr" rel="c' + self.cb + u'001">')
        self.indentFlag = False

    def renderIDE(self, token):     pass
    def renderH(self, token):       self.write(u'\n<h1 class="bookname">' + token.value + u'</h1>')
    def renderMT(self, token):      self.write(u'\n<h3>' + token.value + u'</h3>')
    def renderMS(self, token):
        if self.inSpanFlag:
                self.inSpanFlag = False
                self.write(u'</span>')
        if self.inParaFlag:
                self.inParaFlag = False
                self.write(u'\n</p>')
        self.write(u'\n<h4>' + token.value + u'</h4>')
    def renderMS2(self, token):     self.write(u'\n<h5>' + token.value + u'</h5>')
    def renderP(self, token):
        if self.inSpanFlag:
                self.inSpanFlag = False
                self.write(u'</span>')
        self.indentFlag = False
        if self.inParaFlag:
                self.inParaFlag = False
                self.write(u'\n</p>')
        self.inParaFlag = True
        self.write(u'\n<p>')
    def renderS(self, token):
        self.indentFlag = False
    def renderS2(self, token):
        self.indentFlag = False
    def renderC(self, token):
        self.cc = token.value.zfill(3)
        if self.cc == u'001':
            self.write(u'\n<h2 class="c-num">' + token.value + u'</h2>\n<p>')
            self.inParaFlag = True  
        else:
            if self.inSpanFlag:
                    self.inSpanFlag = False
                    self.write(u'</span>')
            if self.inParaFlag:
                    self.inParaFlag = False
                    self.write(u'\n</p>')
            self.write(u'\n</article>')
            self.f.close()
            self.f = open(self.outputDir + u'/c' + self.cb + self.cc + u'.html', 'w')
            self.write(u'\n<!--\ntitle:  Matthew 1 (Open English Bible)\nauthor: http://www.biblewebapp.com/\ndate:   4/22/2010 3:34:43 PM\n-->')
            self.write(u'\n<article class="chapter nt oeb" lang="en" dir="ltr" rel="c' + self.cb + self.cc + u'">')
            self.write(u'\n<h2 class="c-num">' + token.value + u'</h2>\n<p>')      
            self.inParaFlag = True  
    def renderV(self, token):
        self.cv = token.value.zfill(3)
        if self.cv == u'001':
            if self.inSpanFlag:
                    self.inSpanFlag = False
                    self.write(u'</span>')
            self.inSpanFlag = True
            self.write(u'\n<span class="verse" rel="v' + self.cb + self.cc + self.cv + u'"><span class="v-num v-1">' + token.value + u'&nbsp;</span>')
        else:
            if self.inSpanFlag:
                    self.inSpanFlag = False
                    self.write(u'</span>')
            self.inSpanFlag = True
            self.write(u'\n<span class="verse" rel="v' + self.cb + self.cc + self.cv + u'"><span class="v-num">' + token.value + u'&nbsp;</span>')
 
    def renderWJS(self, token):     self.write(u'<span class="woc">')
    def renderWJE(self, token):     self.write(u'</span>')
    def renderTEXT(self, token):    self.write(token.value)
    def renderQ(self, token):       self.writeIndent(1)
    def renderQ1(self, token):      self.writeIndent(1)
    def renderQ2(self, token):      self.writeIndent(2)
    def renderQ3(self, token):      self.writeIndent(3)
    def renderNB(self, token):      self.writeIndent(0)
    def renderQTS(self, token):     pass
    def renderQTE(self, token):     pass
    def renderFS(self, token):      self.write(u'{')
    def renderFE(self, token):      self.write(u'}')
    def renderIS(self, token):      self.write(u'<i>')
    def renderIE(self, token):      self.write(u'</i>')
    def renderB(self, token):       self.write(u'<p />')
    def renderD(self, token):       self.write(u'<p />')
    def renderADDS(self, token):    self.write(u'<i>')
    def renderADDE(self, token):    self.write(u'</i>')
    def renderLI(self, token):      self.write(u'<p />')
    def renderSP(self, token):      self.write(u'<p />')
    def renderNDS(self, token):     return u''
    def renderNDE(self, token):     return u''
    def renderPBR(self, token):     self.write(u'<br />')
    
class TransformForReader(object):
    outputDir = ''
    patchedDir = ''
    prefaceDir = ''
    
    def stripUnicodeHeader(self, unicodeString):
        if unicodeString[0] == u'\ufeff':
            return unicodeString[1:]
        else:
            return unicodeString

    def translateBook(self, name):

        f = open(self.patchedDir + '/' + name + '.usfm')
        fc = self.stripUnicodeHeader(unicode(f.read(), 'utf-8'))
        f.close()

        print '        > ' + name
        tokens = parseUsfm.parseString(fc)

        for t in tokens: t.renderOn(self.printer)
 
    def setupAndRun(self, patchedDir, prefaceDir, outputDir):
        self.patchedDir = patchedDir
        self.prefaceDir = prefaceDir
        self.outputDir = outputDir
        self.printer = ReaderPrinter(self.outputDir)

        for book in books.books:
            self.translateBook(book)
 