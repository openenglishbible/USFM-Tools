# -*- coding: utf-8 -*-
#

import abstractRenderer
import codecs
import books
import shutil
import os

#
#   Renders as set of web pages
#

class DummyFile(object):
    def close(self):
        pass
    def write(self, str):
        pass

class Renderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputDir, outputName, config):
        abstractRenderer.AbstractRenderer.__init__(self, inputDir, outputDir, outputName, config)
        # Unset
        self.f = DummyFile()  # output file stream
        self.ft = [] # array of text to write to file
        # IO
        self.outputDir = outputDir
        self.inputDir = inputDir
        # Caches
        self.cachedChapterMarker = u''
        self.cachedBookname = u''
        # Position
        self.cb = u''    # Current Book
        self.cc = u'001'    # Current Chapter
        self.cv = u'001'    # Currrent Verse
        # Flags
        self.indentFlag = False

    def render(self):
        # Load
        self.loadUSFM(self.inputDir)
        # Write pages
        self.run()
        self.close()
        shutil.copy(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/normalize.css', self.outputDir + u'/')
        shutil.copy(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/style.css', self.outputDir + u'/')
        shutil.copy(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/jump.js', self.outputDir + u'/')
        shutil.copy(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/header.png', self.outputDir + u'/')
        self.generateIndexFile()
        
    # File handling    
    
    def generateIndexFile(self):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/index.html') as f:
            c = f.read()
        c = c.replace('{{{ot}}}', self.bookList(1, 39))
        c = c.replace('{{{nt}}}', self.bookList(40, 66))
        with open(self.outputDir + u'/index.html', 'w') as f:
            f.write(c)

    def bookList(self, s, f):
        h = ''
        for b in range(s, f):
            if self.booksUsfm.has_key(books.silNames[b]):
                h = h + '\n<a href="b' + str(b).zfill(3) + '.html">' + books.bookNames[b-1].replace(' ', '&nbsp;') + '</a></br>'
            else:
                h = h + '\n' + books.bookNames[b-1] + '</br>'
        return h
                
    def openFile(self, bookID):
        self.f = open(self.outputDir + u'/b' + bookID + u'.html', 'w')
        self.ft = []
        
    def close(self): 
        t = u''.join(self.ft)
        self.f.write(self.cleanHTML(t).encode('utf-8'))
        self.f.close()
 
    def write(self, unicodeString):
        self.ft.append(unicodeString)
        
    def cleanHTML(self, t):
        c = t
        c = t.replace(u'<p><br /><br />', u'<p>')
        c = c.replace(ur'~', u'&nbsp;')
        c = c.replace(ur'<span class="nd"> Lord </span> ,', ur'<span class="nd"> Lord</span>,')
        c = c.replace(ur'<span class="nd"> Lord </span> ;', ur'<span class="nd"> Lord</span>;')
        c = c.replace(ur'<span class="nd"> Lord </span> .', ur'<span class="nd"> Lord</span>.')
        c = c.replace(ur'<span class="nd"> Lord </span> :', ur'<span class="nd"> Lord</span>:')
        c = c.replace(ur'<span class="nd"> Lord </span> !', ur'<span class="nd"> Lord</span>!')
        c = c.replace(ur'<span class="nd"> Lord </span> ?', ur'<span class="nd"> Lord</span>?')
        c = c.replace(u'<span class="nd"> Lord </span> \'', u'<span class="nd"> Lord</span>\'')
        if self.oebFlag:
            c = c.replace(ur'{{{navmarker}}}', u'Go to...')
            c = c.replace(ur'{{{linkToWebsite}}}',u'<a href="http://openenglishbible.org">OpenEnglishBible.org</a>')
        else:
            c = c.replace(ur'{{{navmarker}}}', u'<div style="font-size:200%;color:green;">✝</div>')
            c = c.replace(ur'{{{linkToWebsite}}}',u'Go to...')
        return c
        
    # Support
    
    def header(self):
        h = header_header
        h = h + '<tr><td colspan = "5" style="font-size:100%;">&nbsp;<br/>Old Testament</td></tr><tr>'
        for b in range(1, 39):
            if self.booksUsfm.has_key(books.silNames[b]):
                h = h + '\n<td><a href="b' + str(b).zfill(3) + '.html">' + books.bookNames[b-1].replace(' ', '&nbsp;') + '</a></td>'
            else:
                h = h + '\n<td>' + books.bookNames[b-1] + '</td>'
            if b % 5 == 0: h = h + '</tr><tr>'
        h = h + '\n</tr><tr><td colspan = "5" style="font-size:100%;">&nbsp;<br/>New Testament</td></tr><tr>'
        for b in range(40, 66):
            if self.booksUsfm.has_key(books.silNames[b]):
                h = h + '\n<td><a href="b' + str(b).zfill(3) + '.html">' + books.bookNames[b-1].replace(' ', '&nbsp;') + '</a></td>'
            else:
                h = h + '\n<td>' + books.bookNames[b-1] + '</td>'
            if b % 5 == 4: h = h + '</tr><tr>'
        h = h + '\n</tr><tr><td colspan = "2">{{{linkToWebsite}}}</td></tr></table></div></div>'
        return h
        
    def writeChapterMarker(self):
        self.write(self.cachedChapterMarker)
        self.cachedChapterMarker = u''

    def writeIndent(self, level):
        if level == 0:
            self.indentFlag = False
            self.write(u'<br /><br />')
            return 
        if not self.indentFlag:
            self.indentFlag = True
            self.write(u'<br />')
        self.write(u'<br />')
        self.write(u'&nbsp;&nbsp;' * level)
        self.writeChapterMarker()

    def render_id(self, token): 
        self.write(footer)
        self.close()
        self.cb = books.bookKeyForIdValue(token.value)
        self.openFile(self.cb)
        self.write(self.header())
        self.indentFlag = False
    def render_mt(self, token):      self.write(u'</p><h1>' + token.value + u'</h1><p>')
    def render_mt2(self, token):      self.write(u'</p><h2>' + token.value + u'</h2><p>')
    def render_ms(self, token):      self.write(u'</p><h4>' + token.value + u'</h4><p>')
    def renderMS2(self, token):     self.write(u'</p><h5>' + token.value + u'</h5><p>')
    def render_p(self, token):
        self.indentFlag = False
        self.write(u'<br /><br />')
        self.writeChapterMarker()
    def render_s1(self, token):
        self.indentFlag = False
        if token.value == u'~':
            self.write(u'<p>&nbsp;</p><p>')
        else:
            self.write(u'</p><h6>' + token.value + u'</h6><p>')
    def render_s2(self, token):
        self.indentFlag = False
        self.write(u'</p><h7>' + token.value + u'</h7><p>')
    def render_c(self, token):
        self.cc = token.value.zfill(3)
        self.cachedChapterMarker = u'<span class="chapter" id="' + self.cc + u'001">' + token.value + u'</span>'
        # if self.cb==u'019': self.write(u'<p><em>Psalm ' + token.value + u'</em></p>')
    def render_v(self, token):
        self.cv = token.value.zfill(3)
        if self.cv == u'001':
            self.writeChapterMarker()
        else:
            self.write(u'\n<span class="verse" rel="v' + self.cb + self.cc + self.cv + u'" id="' + self.cc + self.cv + u'" >' + token.value + u'</span>\n')
    def render_wj_s(self, token):     self.write(u'<span class="woc">')
    def render_wj_e(self, token):     self.write(u'</span>')

    def render_nd_s(self, token):     self.write(u'<span class="nd">')
    def render_nd_e(self, token):     self.write(u'</span>')

    def render_text(self, token):    self.write(u" " + token.value + u" ")
    def render_q(self, token):       self.writeIndent(1)
    def render_q1(self, token):      self.writeIndent(1)
    def render_q2(self, token):      self.writeIndent(2)
    def render_q3(self, token):      self.writeIndent(3)
    def render_nb(self, token):      self.writeIndent(0)
    def render_b(self, token):       self.write(u'<br />')
    def render_i_s(self, token):      self.write(u'<i>')
    def render_i_e(self, token):      self.write(u'</i>')
    def render_pbr(self, token):     self.write(u'<br />')
    
    def render_d(self, token):       self.writeChapterMarker()

    def render_is1(self, token):    self.render_s1(token)
    def render_ip(self, token):     self.render_p(token)
    def render_iot(self, token):    self.render_q(token)
    def render_io1(self, token):    self.render_q2(token)
    
    def render_f_s(self, token):      self.write(u'<span class="rightnotemarker">*</span><span class="rightnote">')
    def render_f_e(self, token):      self.write(u'</span>')
    

#
#  Structure
#

header_header = ur"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <title>Open English Bible</title>
    <meta charset='utf-8'>
    <script src="//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
    <link href="//cdnjs.cloudflare.com/ajax/libs/normalize/3.0.1/normalize.min.css" rel="stylesheet">
    <link href="style.css" rel="stylesheet">
    <script src="jump.js"></script>
    </head>

    <body>
    <div id="navbar">
        <p id="navoeb">{{{navmarker}}}</p>
        <div id="navtable">
        <table>
        <tr><td colspan = "5" style="font-size:100%;">
            <form id="navform">
                <input type="text" style="font-size: 140%;" id="txtSearch"/> (eg Ps 23)
            </form>
        </td></tr>
"""

footer = ur"""
        </p></body>   
        """

