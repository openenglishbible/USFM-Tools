# -*- coding: utf-8 -*-
#

import os
import parseUsfm
import books
import datetime

class CSVPrinter(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        self.cb = u''    # Current Book
        self.cc = u'001'    # Current Chapter
        self.cv = u'001'    # Currrent Verse  
        self.infootnote = False
        self.rendered = u''      
        
    #   SUPPORT
    #
    #
    def escape(self, s):
        if self.infootnote:
            t = u''
        else:
            t = s
        #t = t.replace(u'“', u'{@Char quotedblleft}').replace(u'”', u'{@Char quotedblright}').replace(u'—', u'{@Char emdash}').replace(u'‘', u'{@Char quoteleft}').replace(u'’', u'{@Char quoteright}').replace(u'"', u'{@Char quotedbl}')
        #t = t.replace(u'"', u'{@Char quotedbl}')
        #t = t.replace(u'’', u'{@Char quoteright}')
        return t
 
    def write(self, unicodeString):
        self.rendered = self.rendered + unicodeString
       
    def close(self):
        pass 
           
    #   TOKENS
    #
    #
    def renderID(self, token): 
        self.cb = books.bookKeyForIdValue(token.value)
    def renderIDE(self, token): pass
    def renderH(self, token):   pass
    def renderMT(self, token):  pass
    def renderMT2(self, token): pass
    def renderMT3(self, token): pass
    def renderMS(self, token):  pass
    def renderMS2(self, token): pass
    def renderP(self, token):   pass
    def renderS(self, token):   pass
    def renderS2(self, token):  pass
    def renderC(self, token):
        self.cc = token.value.zfill(3)
    def renderV(self, token):
        self.cv = token.value.zfill(3)
        self.write(u'\nOEB,' + str(int(self.cb)) + ',' + str(int(self.cc)) + ',' + self.cv   + ',')
    def renderWJS(self, token):     pass
    def renderWJE(self, token):     pass
    def renderTEXT(self, token):    self.write(self.escape(token.value) + ' ')
    def renderQ(self, token):       pass
    def renderQ1(self, token):      pass
    def renderQ2(self, token):      pass
    def renderQ3(self, token):      pass
    def renderNB(self, token):      pass
    def renderB(self, token):       pass
    def renderQTS(self, token):     pass
    def renderQTE(self, token):     pass
    def renderFS(self, token):      self.infootnote = True
    def renderFE(self, token):      self.infootnote = False
    def renderIS(self, token):      pass
    def renderIE(self, token):      pass
    def renderNDS(self, token):     pass
    def renderNDE(self, token):     pass
    def renderPBR(self, token):     pass
    def renderSCS(self, token):     pass
    def renderSCE(self, token):     pass
    def renderD(self, token):       pass
    def renderREM(self, token):     pass # This is for comments in the USFM
    def renderADDS(self, token):    pass
    def renderADDE(self, token):    pass

class TransformToCSV(object):
    outputDir = ''
    patchedDir = ''
    prefaceDir = ''

    def setupAndRun(self, patchedDir, outputDir, buildName):
        self.patchedDir = patchedDir
        self.outputDir = outputDir
        self.booksUsfm = books.loadBooks(patchedDir)
        self.printer = CSVPrinter(self.outputDir)

        for bookName in books.silNames:
            if self.booksUsfm.has_key(bookName):
                tokens = parseUsfm.parseString(self.booksUsfm[bookName])
                for t in tokens: t.renderOn(self.printer)
                self.printer.close()
                print '      (' + bookName + ')'
        self.printer.close()

        f = open(self.outputDir + buildName, 'w')
        f.write(self.printer.rendered.encode('utf-8'))
        f.close()
        
