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
        
    def render(self, order="normal"):
        self.f = codecs.open(self.outputFilename, 'w', 'utf_8_sig')
        self.f.write(u"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta http-equiv="content-type" content="text/html; charset=utf-8" />
            <title>Bible</title>
            <style media="all" type="text/css">
            .indent-0 {
                margin-left:0em;
                margin-bottom:0em;
                margin-top:0em;
            }
            .indent-1 {
                margin-left:0em;
                margin-bottom:0em;
                margin-top:0em;
            }
            .indent-2 {
                margin-left:1em;
                margin-bottom:0em;
                margin-top:0em;
            }
            .indent-3 {
                margin-left:2em;
                margin-bottom:0em;
                margin-top:0em;
            }
            .c-num {
                color:gray;
            }
            .v-num {
                color:gray;
            }
            .tetragrammaton {
                font-variant: small-caps;
            }
            </style>
            
        </head>
        <body>
        <h1>Table of Contents</h1>
        <p><b>Old Testament</b></p>
        <p class="indent-1"><a href="#019">Psalms</a></p>
        <p><b>New Testament</b></p>
        <p class="indent-1"><a href="#040">Matthew</a></p>
        <p class="indent-1"><a href="#041">Mark</a></p>
        <p class="indent-1"><a href="#042">Luke</a></p>
        <p class="indent-1"><a href="#043">John</a></p>
        <p class="indent-1"><a href="#044">Acts</a></p>
        <p class="indent-1"><a href="#045">Romans</a></p>
        <p class="indent-1"><a href="#046">1 Corinthians</a></p>
        <p class="indent-1"><a href="#047">2 Corinthians</a></p>
        <p class="indent-1"><a href="#048">Galatians</a></p>
        <p class="indent-1"><a href="#049">Ephesians</a></p>
        <p class="indent-1"><a href="#050">Philippians</a></p>
        <p class="indent-1"><a href="#051">Colossians</a></p>
        <p class="indent-1"><a href="#052">1 Thessalonians</a></p>
        <p class="indent-1"><a href="#053">2 Thessalonians</a></p>
        <p class="indent-1"><a href="#054">1 Timothy</a></p>
        <p class="indent-1"><a href="#055">2 Timothy</a></p>
        <p class="indent-1"><a href="#056">Titus</a></p>
        <p class="indent-1"><a href="#057">Philemon</a></p>
        <p class="indent-1"><a href="#058">Hebrews</a></p>
        <p class="indent-1"><a href="#059">James</a></p>
        <p class="indent-1"><a href="#060">1 Peter</a></p>
        <p class="indent-1"><a href="#061">2 Peter</a></p>
        <p class="indent-1"><a href="#062">1 John</a></p>
        <p class="indent-1"><a href="#063">2 John</a></p>
        <p class="indent-1"><a href="#064">3 John</a></p>
        <p class="indent-1"><a href="#065">Jude</a></p>
        <p class="indent-1"><a href="#066">Revelation</a></p>
        
        """.encode('utf-8'))
        self.f.write('<p>Draft built ' + datetime.date.today().strftime("%A, %d %B %Y") + '</p>\n\n')
        self.loadUSFM(self.inputDir)
        self.run(order)
        self.f.write('</body></html>')
        self.f.close()
        
    def escape(self, s):
        return s.replace(u'~',u'&nbsp;')

    def writeLog(self, s):
        print s
        
    def write(self, unicodeString):
        self.f.write(unicodeString.replace(u'~', u' '))
        
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
        self.write(u'\n\n<h1 id="' + self.cb + u'"></h1>\n')
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
        self.write(u'\n\n<p class="c-num">[' + self.bookname + u' ' + token.value + u']</p>')
    def renderV(self, token):
        self.cv = token.value.zfill(3)
        self.write(u' <span class="v-num">[' + token.value + u']</span> ')
    def renderWJS(self, token):     self.write(u'<span class="woc">')
    def renderWJE(self, token):     self.write(u'</span>')
    def renderTEXT(self, token):    self.write(u" " + self.escape(token.value) + u" ")
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
    def renderFS(self, token):     self.write(u'[Note: ')
    def renderFE(self, token):     self.write(u' ]')
