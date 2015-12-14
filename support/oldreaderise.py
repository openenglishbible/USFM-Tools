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
        
class TokenStream(object):
    def __init__(self, array):
        self.tokens = array
        self.i = 0
        
    def copy(self):
        t = TokenStream(self.tokens)
        t.i = self.i
        return t
        
    def next(self, n=1):
        self.i = self.i + n
        return self.tokens[self.i -1]
        
    def previous(self, n=1):
        self.i = self.i - n
        return self.tokens[self.i -1]    

    def peek(self):
        return self.tokens[self.i -1]
        
    def atEnd(self):
        return self.i == len(self.tokens) - 1
        
    def moveTo(self, p):
        self.i = p
        
    def position(self):
        return self.i
            
class ReaderPrinter(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        self.f = DummyFile()
        self.cb = u'001'    # Current Book
        self.cc = u'001'    # Current Chapter
        self.cv = u'001'    # Currrent Verse
        self.indentFlag = False
        self.inSpanFlag = False
        self.inParaFlag = False
        self.tokenStream = None
        
    def renderStream(self, ts):
        self.tokenStream = ts
        while not self.tokenStream.atEnd():
            self.tokenStream.next().renderOn(self)
        self.close()
        
    def close(self):
        self.writeFooter()
        self.f.close() # Close final file
        
    def writeHeader(self, v=u''):
        self.write(u'<!--\nname: Open English Bible\ncontent: %(book)s %(chapter)s (OEB)\nauthor: Russell Allen\ndate:   4/6/2012 3:34:43 PM\n-->' % {"book": books.fullName(self.cb), "chapter": str(int(self.cc))})
        self.write(u'\n<!DOCTYPE html>')
        self.write(u'\n<html lang="en" dir="ltr">')
        self.write(u'\n<head>')
        self.write(u'\n\t<meta charset="utf-8" /> ')
        self.write(u'\n\t<title>%(book)s %(chapter)s (OEB)</title>' % {"book": books.fullName(self.cb), "chapter": str(int(self.cc))})
        self.write(u'\n\t<meta name="viewport" content="width=device-width, initial-scale=1" />')
        self.write(u'\n\t<script src="../../../js/mobile.js"></script>')
        self.write(u'\n\t<link href="../../../css/mobile.css" rel="stylesheet" />')
        self.write(u'\n</head>')
        self.write(u'\n<body>')
        self.write(u'\n<div data-role="page">')
        self.write(u'\n\t<div data-role="header">')
        self.write(u'\n\t\t<a href="%(book)s.%(chapter)s.html" data-icon="arrow-l">%(fullbook)s %(chapter)s</a>' % {"fullbook": books.fullName(self.previousChapter()[0]), "book": books.readerName(self.previousChapter()[0]), "chapter": str(self.previousChapter()[1])})
        self.write(u'\n\t\t<h1>%(book)s %(chapter)s (OEB)</h1>' % {"book": books.fullName(self.cb), "chapter": str(int(self.cc))})
        self.write(u'\n\t\t<a href="%(book)s.%(chapter)s.html" data-icon="arrow-r">%(fullbook)s %(chapter)s</a>' % {"fullbook": books.fullName(self.nextChapter()[0]), "book": books.readerName(self.nextChapter()[0]), "chapter": str(self.nextChapter()[1])})
        self.write(u'\n\t</div>')
        self.write(u'\n\t<div data-role="content">')
        self.write(u'\n<div class="chapter OEB nt %(book)s_%(chapter)s" data-osis="%(book)s.%(chapter)s" lang="en" dir="ltr">' % {"book": books.readerName(self.cb), "chapter": str(int(self.cc))})
        self.write(u'\n<h2 class="chapter-num">' + v + u'</h2>\n<p>')   
        
    def writeFooter(self):
        self.write(u'\n</div>')   
        self.write(u'\n')   
        self.write(u'\n\t</div>')   
        self.write(u'\n\t<div data-role="footer">	')   
        self.write(u'\n\t\t<div data-role="navbar">')   
        self.write(u'\n\t\t\t<ul>')   
        self.write(u'\n\t\t\t\t<li><a href="%(book)s.%(chapter)s.html" data-icon="arrow-l">%(fullbook)s %(chapter)s</a></li>' % {"fullbook": books.fullName(self.previousChapter()[0]), "book": books.readerName(self.previousChapter()[0]), "chapter": str(self.previousChapter()[1])})
        self.write(u'\n\t\t\t\t<li><a href="index.html" data-icon="home">Books</a></li>')   
        self.write(u'\n\t\t\t\t<li><a href="%(book)s.%(chapter)s.html" data-icon="arrow-r">%(fullbook)s %(chapter)s</a></li>' % {"fullbook": books.fullName(self.nextChapter()[0]), "book": books.readerName(self.nextChapter()[0]), "chapter": str(self.nextChapter()[1])})
        self.write(u'\n\t\t\t</ul>')   
        self.write(u'\n\t\t</div>')   
        self.write(u'\n\t</div>')   
        self.write(u'\n</div>')   
        self.write(u'\n</body>')   
        self.write(u'\n</html>')   
        
    def previousChapter(self):
        t = self.tokenStream.copy()
        c = 1
        b = self.cb
        p = t.position() 
        if t.peek().isC(): t.previous(1)
        while t.position() > 0:
            n = t.previous()
            if n.isC(): 
                c = n.value
                break
        if int(c) > int(self.cc):
            b = str(int(self.cb)-1)
        return (b, c)
        
    def nextChapter(self):
        t = self.tokenStream.copy()
        c = self.cc
        b = self.cb    
        while not t.atEnd():
            n = t.next()
            if n.isC(): 
                c = n.value
                break
        if int(c) < int(self.cc): # We must have started new book
            b = str(int(self.cb)+1)
        return (b,c)
        
    def openNextFile(self):
        self.f = open(self.outputDir + u'/' + books.readerName(self.cb) + u'.' + str(int(self.cc)) + u'.html', 'w')

    def incrementChapter(self, chapter):
        self.cc = chapter
 
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

    def render_id(self, token): 
        if self.inSpanFlag:
                self.inSpanFlag = False
                self.write(u'</span>')
        if self.inParaFlag:
                self.inParaFlag = False
                self.write(u'\n</p>')
        self.write(u'\n</div>')
        self.tokenStream.previous(2) # Go back to end of last chapter
        self.writeFooter()
        self.f.close()
        self.tokenStream.next(2) # Go forward again to start of this chapter.
        self.cb = books.bookKeyForIdValue(token.value)
        self.incrementChapter(1)
        self.openNextFile()
        self.writeHeader()
        self.indentFlag = False

    def render_id_e(self, token):     pass
    def render_h(self, token):       self.write(u'\n<h1 class="book-name">' + token.value + u'</h1>')
    def render_mt(self, token):      self.write(u'\n<h3>' + token.value + u'</h3>')
    def render_mt2(self, token):      self.write(u'\n<h3>' + token.value + u'</h3>')
    def render_ms(self, token):
        if self.inSpanFlag:
                self.inSpanFlag = False
                self.write(u'</span>')
        if self.inParaFlag:
                self.inParaFlag = False
                self.write(u'\n</p>')
        self.write(u'\n<h4>' + token.value + u'</h4>')
    def renderMS2(self, token):     self.write(u'\n<h5>' + token.value + u'</h5>')
    def render_p(self, token):
        if self.inSpanFlag:
                self.inSpanFlag = False
                self.write(u'</span>')
        self.indentFlag = False
        if self.inParaFlag:
                self.inParaFlag = False
                self.write(u'\n</p>')
        self.inParaFlag = True
        self.write(u'\n<p>')
    def render_s1(self, token):
        self.indentFlag = False
    def render_s2(self, token):
        self.indentFlag = False
    def render_c(self, token):
        if token.value.zfill(3) == u'001':
            self.incrementChapter(token.value.zfill(3))
            self.write(u'\n<h2 class="chapter-num">' + token.value + u'</h2>\n<p>')
            self.inParaFlag = True  
        else:
            if self.inSpanFlag:
                    self.inSpanFlag = False
                    self.write(u'</span>')
            if self.inParaFlag:
                    self.inParaFlag = False
                    self.write(u'\n</p>')
            self.tokenStream.previous(2) # Go back to end of last chapter
            self.writeFooter()
            self.f.close()
            self.tokenStream.next(2) # Go forward again to start of this chapter.
            self.incrementChapter(token.value.zfill(3))
            self.openNextFile()
            self.writeHeader(token.value)
            self.inParaFlag = True  
    def render_v(self, token):
        if u'-' in token.value: # Complex, eg 42-43
            self.cv = token.value[:token.value.index(u'-')].zfill(3)
        else:
            self.cv = token.value.zfill(3)
        if self.cv == u'001':
            if self.inSpanFlag:
                    self.inSpanFlag = False
                    self.write(u'</span>')
            self.inSpanFlag = True
            self.write(u'\n<span class="verse ' + books.readerName(self.cb) + u"_" + str(int(self.cc)) + u"_" + str(int(self.cv)) + u'" data-osis="' + books.readerName(self.cb) + u'.' + str(int(self.cc)) + u"." + str(int(self.cv)) + u'"><span class="verse-num v-1">' + token.value + u'&nbsp;</span>')
        else:
            if self.inSpanFlag:
                    self.inSpanFlag = False
                    self.write(u'</span>')
            self.inSpanFlag = True
            self.write(u'\n<span class="verse ' + books.readerName(self.cb) + u"_" + str(int(self.cc)) + u"_" + str(int(self.cv)) + u'" data-osis="' + books.readerName(self.cb) + u'.' + str(int(self.cc)) + u"." + str(int(self.cv)) + u'"><span class="verse-num v-' + str(int(self.cv)) + u'">' + token.value + u'&nbsp;</span>')
 
    def render_wj_s(self, token):     self.write(u'<span class="woc">')
    def render_wj_e(self, token):     self.write(u'</span>')
    def render_text(self, token):    self.write(token.value)
    def render_q(self, token):       self.writeIndent(1)
    def render_q1(self, token):      self.writeIndent(1)
    def render_q2(self, token):      self.writeIndent(2)
    def render_q3(self, token):      self.writeIndent(3)
    def render_nb(self, token):      self.writeIndent(0)
    def render_qt_s(self, token):     pass
    def render_qt_e(self, token):     pass
    def render_f_s(self, token):      self.write(u'{')
    def render_f_e(self, token):      self.write(u'}')
    def render_i_s(self, token):      self.write(u'<i>')
    def render_i_e(self, token):      self.write(u'</i>')
    def render_b(self, token):       self.write(u'<p />')
    def render_d(self, token):       self.write(u'<p />')
    def render_add_s(self, token):    self.write(u'<i>')
    def render_add_e(self, token):    self.write(u'</i>')
    def render_li(self, token):      self.write(u'<p />')
    def render_sp(self, token):      self.write(u'<p />')
    def render_nd_s(self, token):     self.write(u' ')
    def render_nd_e(self, token):     self.write(u' ')
    def render_pbr(self, token):     self.write(u'<br />')
    def render_d(self, token):       pass # For now
    def render_rem(self, token):     pass # This is for comments in the USFM
    
    
class TransformForReader(object):
    outputDir = ''
    patchedDir = ''
    prefaceDir = ''
    
    def stripUnicodeHeader(self, unicodeString):
        if unicodeString[0] == u'\ufeff':
            return unicodeString[1:]
        else:
            return unicodeString

    def setupAndRun(self, patchedDir, outputDir):
        self.patchedDir = patchedDir
        self.outputDir = outputDir
        self.booksUsfm = books.loadBooks(patchedDir)
        self.printer = ReaderPrinter(self.outputDir)

        tokens = []
        print "    ** Parsing"
        for bookName in books.silNames:
            if self.booksUsfm.has_key(bookName):
                tokens = tokens + parseUsfm.parseString(self.booksUsfm[bookName])
        self.tokenStream = TokenStream(tokens)
        
        print "    ** Rendering"
        self.printer.renderStream(self.tokenStream)
        
