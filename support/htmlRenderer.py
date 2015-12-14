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
    
    def __init__(self, inputDir, outputDir, outputName):
        abstractRenderer.AbstractRenderer.__init__(self, inputDir, outputDir, outputName)
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
        # Write pages
        self.loadUSFM(self.inputDir)
        self.run()
        self.close()
        shutil.copy(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/normalize.css', self.outputDir + u'/')
        shutil.copy(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/style.css', self.outputDir + u'/')
        shutil.copy(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/jump.js', self.outputDir + u'/')
        shutil.copy(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/index-dev.html', self.outputDir + u'/index.html')
        shutil.copy(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/header.png', self.outputDir + u'/')
        
    # File handling    
        
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
            c = c.replace(ur'%navmarker%', u'OEB')
            c = c.replace(ur'%linkToWebsite%',u'<tr><td colspan = "2"><a href="http://openenglishbible.org">OpenEnglishBible.org</a></td></tr>')
        else:
            c = c.replace(ur'%navmarker%', u'<div style="font-size:200%;color:green;">✝</div>')
            c = c.replace(ur'%linkToWebsite%',u'')
        return c
        
    # Support
        
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
        self.write(header_dev)
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
        <p id="navoeb">OEB</p>
        <div id="navtable">
        <table>
        <tr><td colspan = "5" style="font-size:100%;">
            <form id="navform">
                <input type="text" style="font-size: 140%;" id="txtSearch"/> (eg Ps 23)
            </form>
        </td></tr>
"""

header_nt = ur"""
    <tr><td colspan = "5" style="font-size:100%;">&nbsp;<br/>New Testament</td></tr>
        <tr><td>
            <a href="b040.html">Matthew</a>&nbsp;<br>
            <a href="b041.html">Mark</a>&nbsp;<br>
            <a href="b042.html">Luke</a>&nbsp;<br>
            <a href="b043.html">John</a>&nbsp;<br>
            <a href="b044.html">Acts</a>&nbsp;<br>
        </td>
        <td>
            <a href="b045.html">Romans</a>
            <a href="b046.html">1&nbsp;Corinthians</a>&nbsp;<br>
            <a href="b047.html">2&nbsp;Corinthians</a>&nbsp;<br>
            <a href="b048.html">Galatians</a>&nbsp;<br>
            <a href="b049.html">Ephesians</a>&nbsp;<br>
        </td>
        <td>
            <a href="b050.html">Philippians</a>&nbsp;<br>
            <a href="b051.html">Colossians</a>
            <a href="b052.html">1&nbsp;Thessalonians</a>&nbsp;<br>
            <a href="b053.html">2&nbsp;Thessalonians</a>&nbsp;<br>
        </td>
        <td>
            <a href="b054.html">1&nbsp;Timothy</a>&nbsp;<br>
            <a href="b055.html">2&nbsp;Timothy</a>&nbsp;<br>
            <a href="b056.html">Titus</a>&nbsp;<br>
            <a href="b057.html">Philemon</a>
            <a href="b058.html">Hebrews</a>&nbsp;<br>
            <a href="b059.html">James</a>&nbsp;<br>
        </td>
        <td>
            <a href="b060.html">1&nbsp;Peter</a>&nbsp;<br>
            <a href="b061.html">2&nbsp;Peter</a>&nbsp;<br>
            <a href="b062.html">1&nbsp;John</a>&nbsp;<br>
            <a href="b063.html">2&nbsp;John</a>
            <a href="b064.html">3&nbsp;John</a>&nbsp;<br>
        </td>
        <td>
            <a href="b065.html">Jude</a>&nbsp;<br>
            <a href="b066.html">Revelation</a>
        </td></tr>
        <tr><td colspan = "2"><a href="http://openenglishbible.org">OpenEnglishBible.org</a></td></tr>
    </table>
    </div>
    </div>
"""

header_release = header_header + ur"""
        <tr><td colspan = "5" style="font-size:100%;">&nbsp;<br/>Old Testament</td></tr>
        <tr>
            <td>
            <a href="b008.html">Ruth</a>&nbsp;<br>
            <a href="b017.html">Esther</a>&nbsp;<br>
            <a href="b019.html">Psalms</a>
            </td>
        </tr>
""" + header_nt

header_dev = header_header + ur"""
        <tr><td colspan = "5" style="font-size:100%;">&nbsp;<br/>Old Testament</td></tr>
            <td>
            <a href="b001.html">Genesis</a>&nbsp;<br>
            Exodus&nbsp;<br>
            Leviticu&nbsp;<br>
            Numbers&nbsp;<br>
            Deuteronomy&nbsp;<br>
            Joshua&nbsp;<br>
            Judges
            </td>
            <td>
            <a href="b008.html">Ruth</a>&nbsp;<br>
            1&nbsp;Samuel&nbsp;<br>
            2&nbsp;Samuel&nbsp;<br>
            1&nbsp;Kings&nbsp;<br>
            2&nbsp;Kings<br>
            1&nbsp;Chronicles&nbsp;<br>
            2&nbsp;Chronicles&nbsp;
            </td>
            <td>
            Ezra&nbsp;<br>
            Nehemiah&nbsp;<br>
            <a href="b017.html">Esther</a>&nbsp;<br>
            Job&nbsp;<br>
            <a href="b019.html">Psalms</a>&nbsp;<br>
            <a href="b020.html">Proverbs</a>&nbsp;<br>
            Ecclesiastes&nbsp;<br>
            </td>
            <td>
            Song&nbsp;of&nbsp;Solomon&nbsp;<br>
            Isaiah&nbsp;<br>
            Jeremiah<br>
            Lamentations&nbsp;<br>
            Ezekiel&nbsp;<br>
            <a href="b027.html">Daniel</a>&nbsp;<br>
            Hosea&nbsp;<br>
            </td>
            <td>
            <a href="b029.html">Joel</a>&nbsp;<br>
            <a href="b030.html">Amos</a>
            <a href="b031.html">Obadiah</a>&nbsp;<br>
            <a href="b032.html">Jonah</a>&nbsp;<br>
            <a href="b033.html">Micah</a>&nbsp;<br>
            <a href="b034.html">Nahum</a>&nbsp;<br>
            <a href="b035.html">Habakkuk</a>&nbsp;<br>
            </td>
            <td>
            <a href="b036.html">Zephaniah</a>
            <a href="b037.html">Haggai</a>&nbsp;<br>
            <a href="b038.html">Zechariah</a>&nbsp;<br>
            <a href="b039.html">Malachi</a>
            </td>
        </tr>
""" + header_nt

footer = ur"""
        </p></body>   
        """

indexPage = header_dev + ur"""<h1>Open English Bible</h1>""" + footer

