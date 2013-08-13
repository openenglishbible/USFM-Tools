# -*- coding: utf-8 -*-
#

import abstractRenderer
import codecs
import datetime
import books

#
#   Simplest renderer. Ignores everything except ascii text.
#

class SingleHTMLRenderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputFilename):
        # Unset
        self.f = None  # output file stream
        # IO
        self.outputFilename = outputFilename
        self.inputDir = inputDir
        # Position
        self.cb = u''    # Current Book
        self.cc = u'001'    # Current Chapter
        self.cv = u'001'    # Currrent Verse
        self.indentFlag = False
        self.bookName = u''
        
    def render(self):
        self.f = codecs.open(self.outputFilename, 'w', 'utf_8_sig')
        self.f.write(u"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta http-equiv="content-type" content="text/html; charset=utf-8" />
            <title>Bible</title>
        </head>
        <body>
        """.encode('utf-8'))
        self.f.write('<p>Draft built ' + datetime.date.today().strftime("%A, %d %B %Y") + '</p>\n\n')
        self.loadUSFM(self.inputDir)
        self.run()
        self.f.write('</body></html>')
        self.f.close()
        
    def writeLog(self, s):
        print s
        
    def write(self, unicodeString):
        self.f.write(unicodeString)
        
    def writeIndent(self, level):
        self.write(u'\n\n')
        if level == 0:
            self.indentFlag = False
            self.write(u'<p class="indent-0">')
            return 
        if not self.indentFlag:
            self.indentFlag = True
            self.write(u'<p>')
        self.write(u'<p class="indent-' + str(level) + u'">')

    def renderID(self, token): 
        self.cb = books.bookKeyForIdValue(token.value)
        self.indentFlag = False
    def renderH(self, token):       self.bookname = token.value 
    def renderMT(self, token):      self.write(u'\n\n<h1>' + token.value + u'</h1>')
    def renderMT2(self, token):     self.write(u'\n\n<h2>' + token.value + u'</h2>')
    def renderMS(self, token):      self.write(u'\n\n<h3>' + token.value + u'</h3>')
    def renderMS2(self, token):     self.write(u'\n\n<h4>' + token.value + u'</h4>')
    def renderP(self, token):
        self.indentFlag = False
        self.write(u'\n\n<p>')
    def renderS(self, token):
        self.indentFlag = False
        self.write(u'\n\n<h5>' + token.getValue() + u'</h5>')
    def renderS2(self, token):
        self.indentFlag = False
        self.write(u'\n\n<p align="center">----</p>')
    def renderC(self, token):
        self.cc = token.value.zfill(3)
        self.write(u'\n\n<p class="c-num">' + token.value + u'</p>')
    def renderV(self, token):
        self.cv = token.value.zfill(3)
        self.write(u' <span class="v-num">' + token.value + u'</span> ')
    def renderWJS(self, token):     self.write(u'<span class="woc">')
    def renderWJE(self, token):     self.write(u'</span>')
    def renderTEXT(self, token):    self.write(u" " + token.value + u" ")
    def renderQ(self, token):       self.writeIndent(1)
    def renderQ1(self, token):      self.writeIndent(1)
    def renderQ2(self, token):      self.writeIndent(2)
    def renderQ3(self, token):      self.writeIndent(3)
    def renderNB(self, token):      self.writeIndent(0)
    def renderB(self, token):       self.write(u'\n\n<p class="indent-0">&nbsp;</p>')
    def renderIS(self, token):      self.write(u'<i>')
    def renderIE(self, token):      self.write(u'</i>')
    def renderNDS(self, token):     self.write(u'<span class="tetragrammaton">')
    def renderNDE(self, token):     self.write(u'</span>')
    def renderPBR(self, token):     self.write(u'<br />')
    def renderSCS(self, token):     self.write(u'<b>')
    def renderSCE(self, token):     self.write(u'</b>')
