import re
import os
import parseUsfm
import books


class PlainPrinter(object):
    def __init__(self):
        self.currentC = 1
        self.li = False
        self.narrower = False
        self.d = False

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
                    
    def renderID(self, token):      return u''
    def renderIDE(self, token):     return u''
    def renderH(self, token):       return u'\n\n\n\n' + (u'=' * len(token.value)) + u'\n' + token.value + u'\n' + (u'=' * len(token.value))
    def renderMT(self, token):      return self.stopNarrower() + u'\n\n' + (u'-' * len(token.value)) + u'\n' + token.value + u'\n' + (u'-' * len(token.value)) + u'\n\n'
    def renderMS(self, token):      return self.stopNarrower() + u'\n\n' + token.value + u'\n' + (u'=' * len(token.value)) + u'\n\n'
    def renderMS2(self, token):     return self.stopNarrower() + u'\n\n' + token.value + u'\n' + (u'-' * len(token.value)) + u'\n\n'
    def renderP(self, token):       return self.stopD() + self.stopNarrower() + u'\n\n    '
    def renderB(self, token):       return self.stopD() + self.stopNarrower() + u'\n\n    '
    def renderS(self, token):       return self.stopD() + self.stopNarrower() + u'\n\n----\n\n    '
    def renderS2(self, token):       return self.stopD() + self.stopNarrower() + u'\n\n----\n\n    '
    def renderC(self, token):       self.currentC = token.value; return u''
    def renderV(self, token):       return u' [' + self.currentC + u':' + token.value + u'] '
    def renderWJS(self, token):     return u""
    def renderWJE(self, token):     return u""
    def renderTEXT(self, token):    return token.value
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
    def renderLI(self, token):      return u'* '
    def renderD(self, token):       return self.startD()
    def renderSP(self, token):      return self.startD()
    def renderNDS(self, token):     return u''
    def renderNDE(self, token):     return u' '
    def renderPBR(self, token):     return u'\n'
    
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

    def saveAll(self, allBooks):

        f = open(self.outputDir + '/Bible.txt', 'w')
        f.write(allBooks.encode('utf-8'))
        f.close()

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
                  
        bookTex = u''

        for bookName in books.silNames:
            if self.booksUsfm.has_key(bookName):
                bookTex = bookTex + self.translateBook(self.booksUsfm[bookName])
                print '      (' + bookName + ')'
        self.saveAll(bookTex)