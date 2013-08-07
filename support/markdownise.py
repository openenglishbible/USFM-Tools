# -*- coding: utf-8 -*-
#

import re
import os
import parseUsfm
import books
import codecs


class PlainPrinter(object):
    def __init__(self):
        self.currentC = 1
        self.li = False
        self.narrower = False
        self.d = False
        self.book = u''

    def startNarrower(self, n):
        s = u'\n'
        if not self.narrower: s = s + u'\n'
        self.narrower = True
        return s + u'    ' * n

    def stopNarrower(self):
        self.narrower = False
        return u''

    def startD(self):
        self.d = True
        return u''

    def stopD(self):
        self.d = False
        return u''
        
    def escape(self, s):
        return s
                    
    def renderID(self, token):      return u''
    def renderIDE(self, token):     return u''
    def renderH(self, token):       self.book = token.getValue(); return u''
    def renderMT(self, token):      return self.stopNarrower() + u'\n\n# ' + token.value.upper() + u'\n\n'
    def renderMT2(self, token):     return self.stopNarrower() + u'\n\n## ' + token.value.upper() + u'\n\n'
    def renderMS(self, token):      return self.stopNarrower() + u'\n\n' + token.value + u'\n' + (u'=' * len(token.value)) + u'\n\n'
    def renderMS2(self, token):     return self.stopNarrower() + u'\n\n' + token.value + u'\n' + (u'-' * len(token.value)) + u'\n\n'
    def renderP(self, token):       return self.stopD() + self.stopNarrower() + u'\n\n'
    def renderB(self, token):       return self.stopD() + self.stopNarrower() + u'\n\n'
    def renderS(self, token):       return self.stopD() + self.stopNarrower() + u'\n\n----\n\n'
    def renderS2(self, token):       return self.stopD() + self.stopNarrower() + u'\n\n----\n\n'
    def renderC(self, token):       self.currentC = token.value; return u'\n\n[' + self.book + u' ' + self.currentC + u' ]\n\n'
    def renderV(self, token):       return u' [' + self.currentC + u':' + token.value + u'] '
    def renderWJS(self, token):     return u""
    def renderWJE(self, token):     return u""
    def renderTEXT(self, token):    return self.escape(token.value)
    def renderQ(self, token):       return self.stopD() + self.startNarrower(1)
    def renderQ1(self, token):      return self.stopD() + self.startNarrower(1)
    def renderQ2(self, token):      return self.stopD() + self.startNarrower(2)
    def renderQ3(self, token):      return self.stopD() + self.startNarrower(3)
    def renderNB(self, token):      return self.stopD() + self.stopNarrower() + u"\n\n"
    def renderQTS(self, token):     return u''
    def renderQTE(self, token):     return u''
    def renderFS(self, token):      return u'[ footnote: '
    def renderFE(self, token):      return u']'
    def renderIS(self, token):      return u''
    def renderIE(self, token):      return u''
    def renderADDS(self, token):    return u''
    def renderADDE(self, token):    return u''
    def renderPI(self, token):      return u''
    def renderLI(self, token):      return u'* '
    def renderD(self, token):       return self.startD()
    def renderSP(self, token):      return self.startD()
    def renderNDS(self, token):     return u''
    def renderNDE(self, token):     return u' '
    def renderPBR(self, token):     return u'\n'
    def renderD(self, token):       return u'' # For now
    def renderREM(self, token):     return u'' # This is for comments in the USFM
    
class TransformToMarkdown(object):

    def translateBook(self, usfm):

        tokens = parseUsfm.parseString(usfm)
        s = u''
        tp = PlainPrinter()
        for t in tokens: s = s + t.renderOn(tp)
        return s
        
    def stripUnicodeHeader(self, unicodeString):
        if unicodeString[0] == u'\ufeff':
            return unicodeString[1:]
        else:
            return unicodeString

    def saveAll(self, allBooks, buildName):
        f = codecs.open(self.outputDir + buildName, 'w', 'utf-8-sig')
        f.write(allBooks)
        f.close()

    def setupAndRun(self, patchedDir, outputDir, buildName):
        self.outputDir = outputDir
        self.booksUsfm = books.loadBooks(patchedDir)
                  
        r = u"""Open English Bible
Version:""" + buildName + """

"""
        for book in books.orderFor(self.booksUsfm):
            r = r + self.translateBook(book)
                
        # Clean up a bit
        r = r.replace(u'\n [', u'\n[')
        r = r.replace(u'\n\n\n', u'\n\n')
        self.saveAll(r, buildName)