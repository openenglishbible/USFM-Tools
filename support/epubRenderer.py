# -*- coding: utf-8 -*-
#

import abstractRenderer
import codecs
import datetime
import books
import os
import tempfile
import subprocess
import StringIO

#
#   Requires Calibre ebook tools installed.
#
STANDARD_SUFFIX = '.epub'

class Renderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputDir, outputName, config):
        abstractRenderer.AbstractRenderer.__init__(self, inputDir, outputDir, outputName, config)
        # Unset
        self.f = None  # output file stream
        # IO
        self.outputFilename = os.path.join(outputDir, outputName)
        self.inputDir = inputDir
        # Position
        self.cb = u''    # Current Book
        self.cc = u'001'    # Current Chapter
        self.cv = u'001'    # Currrent Verse
        self.indentFlag = False
        self.bookName = u''
        # Footnotes
        self.footnoteBuffer = StringIO.StringIO()
        self.footnoteFlag = False
        self.footnoteID = 0
        
    def render(self, order="normal"):
        self.loadUSFM(self.inputDir)
        self.f =  tempfile.NamedTemporaryFile(suffix=".html")
        self.fName = self.f.name
        self.f.close()
        self.f = codecs.open(self.fName, 'w', 'utf_8_sig')
        h = u"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta http-equiv="content-type" content="text/html; charset=utf-8" />
            <title>Bible</title>
            <style media="all" type="text/css">
            p {
                margin-top: 0em;
                margin-bottom: 0em;
                text-indent: 2em;
            }
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
                font-size:60%;
            }
            .v-num {
                color:gray;
                font-size:60%;
            }
            .tetragrammaton {
                font-variant: small-caps;
            }
            .mt1 {
                font-size:180%;
                text-indent: 0em;
                margin-top:1em;
                margin-bottom: 1em;
            }
            .mt2 {
                font-size:140%;
                text-indent: 0em;
                margin-top:1em;
                margin-bottom: 1em;
            }
            .mt3 {
                font-size:120%;
                text-indent: 0em;
                margin-top:1em;
                margin-bottom: 1em;
            }
            .ms1 {
                font-size:140%;
                text-indent: 0em;
                margin-top:1em;
                margin-bottom: 1em;
            }
            .ms2 {
                font-size:120%;
                text-indent: 0em;
                margin-top:1em;
                margin-bottom: 1em;
            }
            .s1 {
                font-size:120%;
                text-indent: 0em;
                margin-top:1em;
                margin-bottom: 1em;
            }
            </style>
            
        </head>
        <body>
        <h1 id="toc">Table of Contents</h1>
        <p><b>Old Testament</b></p>
        {{{otlinks}}}
        <p><b>New Testament</b></p>
        
        {{{ntlinks}}}
        
        """
        h = h.replace('{{{otlinks}}}', self.bookList(1, 39))
        h = h.replace('{{{ntlinks}}}', self.bookList(40, 66))
        self.f.write(h.encode('utf-8'))
        self.f.write('<p>Draft built ' + datetime.date.today().strftime("%A, %d %B %Y") + '</p>\n\n')
        self.run(order)
        
        self.f.write('<h1 class="chapter" id="fn">Footnotes</h1>')
        self.f.write(self.footnoteBuffer.getvalue())
        self.footnoteBuffer.close()
        
        self.f.write('</body></html>')
        self.f.close()
        
        self.convert()
        
    def suffix(self):
        return STANDARD_SUFFIX
                
    def convert(self):
        suffix = self.suffix()
        calibre = os.path.join(self.config.get('ePub','calibre'),'ebook-convert')
        self.logger.info('Converting to ' + suffix + ' using: ' + calibre)
        
        run = calibre + ' "' + self.fName + '" "' + self.outputFilename + suffix + '" --cover="' + self.config.get('ePub', 'cover') + '" --title="' + self.config.get('ePub', 'title') + '" --authors="' + self.config.get('ePub', 'authors') + '"'
        subprocess.call(run, shell=True)
        
        
    def bookList(self, s, f):
        h = ''
        for b in range(s, f):
            if self.booksUsfm.has_key(books.silNames[b]):
                h = h + '\n<p class="indent-1"><a href="#' + str(b).zfill(3) + '">' + books.bookNames[b-1].replace(' ', '&nbsp;') + '</a></p>'
            else:
                h = h + '\n<p class="indent-1">' + books.bookNames[b-1] + '</p>'
        return h
        
    def escape(self, s):
        return s.replace(u'~',u'&nbsp;')

    def write(self, unicodeString):
        if self.footnoteFlag:
            self.footnoteBuffer.write(unicodeString.replace(u'~', u' '))
        else:
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

    def render_id(self, token): 
        self.cb = books.bookKeyForIdValue(token.value)
        self.indentFlag = False
        self.write(u'<p class="chapter" id="' + self.cb + '">' + books.Books().bookForNumber(self.cb).full + u'</p>\n')
        self.write(u'<p><a href="#toc">Table of Contents</a></p><p>')
        for i in range(0, books.Books().bookForNumber(self.cb).chapters):
            self.write(u'<a href="#' + self.cb + '-' + str(i +1) + '">' + str(i +1) + '</a> ')
        self.write(u'</p>')
    def render_h(self, token):       self.bookname = token.value 
    def render_mt1(self, token):      self.write(u'\n\n<p class="mt1">' + token.value + u'</p>')
    def render_mt2(self, token):     self.write(u'\n\n<p class="mt2">' + token.value + u'</p>')
    def render_mt3(self, token):     self.write(u'\n\n<p class="mt3">' + token.value + u'</p>')
    def render_ms1(self, token):      self.write(u'\n\n<p class="ms1">' + token.value + u'</p>')
    def render_ms2(self, token):     self.write(u'\n\n<p class="ms2">' + token.value + u'</p>')
    def render_p(self, token):
        self.indentFlag = False
        self.write(u'\n\n<p>')
    def render_pi(self, token):
        self.indentFlag = False
        self.write(u'\n\n<p class"indent-2">')
    def render_m(self, token):
        self.indentFlag = False
        self.write(u'\n\n<p>')
    def render_s1(self, token):
        self.indentFlag = False
        self.write(u'\n\n<p class="s1">' + token.getValue() + u'</p>')
    def render_s2(self, token):
        self.indentFlag = False
        self.write(u'\n\n<p align="center">----</p>')
    def render_c(self, token):
        self.cc = token.value
        self.write(u'<a id="' + self.cb + '-' + self.cc + '"></a>')
    def render_v(self, token):
        self.cv = token.value
        if self.cv == '1':
            self.write(u' <span class="c-num">[<a href="#' + self.cb + '">' + self.bookname + u'</a> ' + self.cc + u']</span>')
        else:
            self.write(u' <span class="v-num">[' + self.cv + u']</span> ')
    def render_wj_s(self, token):     self.write(u'<span class="woc">')
    def render_wj_e(self, token):     self.write(u'</span>')
    def render_text(self, token):    self.write(u" " + self.escape(token.value) + u" ")
    def render_q(self, token):       self.writeIndent(1)
    def render_q1(self, token):      self.writeIndent(1)
    def render_q2(self, token):      self.writeIndent(2)
    def render_q3(self, token):      self.writeIndent(3)
    def render_nb(self, token):      self.writeIndent(0)
    def render_b(self, token):       self.write(u'\n\n<p class="indent-0">&nbsp;</p>')
    def render_i_s(self, token):      self.write(u'<i>')
    def render_i_e(self, token):      self.write(u'</i>')
    def render_nd_s(self, token):     self.write(u'<span class="tetragrammaton">')
    def render_nd_e(self, token):     self.write(u'</span>')
    def render_pbr(self, token):     self.write(u'<br />')
    def render_sc_s(self, token):     self.write(u'<b>')
    def render_sc_e(self, token):     self.write(u'</b>')
    def render_qs_s(self, token):     self.write(u'<i>')
    def render_qs_e(self, token):     self.write(u'</i>')
    def render_em_s(self, token):     self.write(u'<i>')
    def render_em_e(self, token):     self.write(u'</i>')
    def render_d(self, token):
        self.indentFlag = False
        self.write(u'\n\n<p>' + token.value + '</p>')
        
    def render_pb(self, token):     pass
    def render_periph(self, token):  pass

    def render_f_s(self, token):
        self.footnoteID = self.footnoteID + 1
        self.write(u'<a id="fa' + str(self.footnoteID) + '"></a><a href="#fn' + str(self.footnoteID) + '">[*]</a>')
        self.footnoteFlag = True
        self.write('\n<p><a id="fn' + str(self.footnoteID) + '"></a><b>' + books.Books().bookForNumber(self.cb).full + ' ' + self.cc + ':' + self.cv + '</b> ')
    def render_f_e(self, token):
        self.write('<a id="fn' + str(self.footnoteID) + '"></a><a href="#fa' + str(self.footnoteID) + '">Back to text</a></p>' )
        self.footnoteFlag = False
        
