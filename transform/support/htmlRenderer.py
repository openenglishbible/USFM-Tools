# -*- coding: utf-8 -*-
#

import os
import shutil

import abstractRenderer
import books


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
        self.identity = 'html renderer'
        self.outputDescription = os.path.join(outputDir, outputName + '_html')
        abstractRenderer.AbstractRenderer.__init__(self, inputDir, outputDir, outputName, config)
        # Unset
        self.f = DummyFile()  # output file stream
        self.ft = [] # array of text to write to file
        # IO
        self.outputDir = os.path.join(outputDir, outputName + '_html')
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)
        self.inputDir = inputDir
        # Reset
        self.resetBookStart()

    def resetBookStart(self):
        # Caches
        self.cachedChapterMarker = ''
        self.cachedBookname = ''
        # Position
        self.cb = ''    # Current Book
        self.cc = '001'    # Current Chapter
        self.cv = '001'    # Currrent Verse
        # Flags
        self.indentFlag = False
        self.firstParagraphInBook = True
        self.afterHeader = False

    def render(self):
        # Load
        self.loadUSFM(self.inputDir)
        # Write pages
        self.run()
        self.close()
        shutil.copy(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/jquery-3.2.1.min.js', self.outputDir + '/')
        shutil.copy(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/normalize.css', self.outputDir + '/')
        shutil.copy(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/style.css', self.outputDir + '/')
        shutil.copy(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/jump.js', self.outputDir + '/')
        shutil.copy(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/header.png', self.outputDir + '/')
        self.generateIndexFile()
        
    # File handling    
    
    def generateIndexFile(self):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/index.html') as f:
            c = f.read()
        c = c.replace('{{{ot}}}', self.bookList(1, 39))
        c = c.replace('{{{nt}}}', self.bookList(40, 67))
        c = c.replace(r'{{{translationname}}}',self.config.get('General','name'))
        c = c.replace(r'{{{pathtologo}}}',self.config.get('HTML','frontlogo'))
        with open(self.outputDir + '/index.html', 'w') as f:
            f.write(c)

    def bookList(self, s, f):
        h = ''
        for b in range(s, f):
            if books.silNames[b] in self.booksUsfm:
                h = h + '\n<a href="b' + str(b).zfill(3) + '.html">' + books.bookNames[b - 1].replace(' ', '&nbsp;') + '</a></br>'
            else:
                h = h + '\n' + books.bookNames[b - 1] + '</br>'
        return h
                
    def openFile(self, bookID):
        self.f = open(self.outputDir + '/b' + bookID + '.html', 'w')
        self.ft = []
        
    def close(self): 
        t = ''.join(self.ft)
        self.f.write(self.cleanHTML(t))
        self.f.close()
 
    def write(self, unicodeString):
        self.ft.append(unicodeString)
        
    def cleanHTML(self, t):
        c = t
        c = c.replace(r'~', '&nbsp;')
        c = c.replace(r'<span class="nd"> Lord </span> ,', r'<span class="nd"> Lord</span>,')
        c = c.replace(r'<span class="nd"> Lord </span> ;', r'<span class="nd"> Lord</span>;')
        c = c.replace(r'<span class="nd"> Lord </span> .', r'<span class="nd"> Lord</span>.')
        c = c.replace(r'<span class="nd"> Lord </span> :', r'<span class="nd"> Lord</span>:')
        c = c.replace(r'<span class="nd"> Lord </span> !', r'<span class="nd"> Lord</span>!')
        c = c.replace(r'<span class="nd"> Lord </span> ?', r'<span class="nd"> Lord</span>?')
        c = c.replace('<span class="nd"> Lord </span> \'', '<span class="nd"> Lord</span>\'')
        
        c = c.replace(r'{{{navmarker}}}', 'Go to...')
        c = c.replace('{{{translationname}}}', self.config.get('General','name'))
        c = c.replace(r'{{{websiteURL}}}',self.config.get('HTML','websiteURL'))
        c = c.replace(r'{{{websiteName}}}',self.config.get('HTML','websiteName'))

        return c
        
    # Support

    def headerGroup(self, start, finish):
        h = ''
        for b in range(start, finish + 1):
            if books.silNames[b] in self.booksUsfm:
                h = h + '\n<li class="label3"><a href="b' + str(b).zfill(3) + '.html">' + books.bookNames[b - 1].replace(' ', '&nbsp;') + '</a></li>'
            else:
                h = h + '\n<li class="label3">' + books.bookNames[b - 1] + '</li>'
        return h

    def header(self):
        h = '\n<ul>'
        h = h + '\n<li class="label1">Old Testament</li>'
        h = h + '\n<li class="label2">The Law</li>'
        h = h + self.headerGroup(1, 5)
        h = h + '\n<li class="label2">Histories</li>'
        h = h + self.headerGroup(6, 17)
        h = h + '\n<li class="label2">Wisdom</li>'
        h = h + self.headerGroup(18, 22)
        h = h + '\n<li class="label2">Major Prophets</li>'
        h = h + self.headerGroup(23, 27)
        h = h + '\n<li class="label2">Minor Prophets</li>'
        h = h + self.headerGroup(28, 39)
        h = h + '\n<li class="label1">New Testament</li>'
        h = h + '\n<li class="label2">Gospels</li>'
        h = h + self.headerGroup(40, 43)
        h = h + '\n<li class="label2">History</li>'
        h = h + self.headerGroup(44, 44)
        h = h + '\n<li class="label2">Pauline Epistles</li>'
        h = h + self.headerGroup(45, 58)
        h = h + '\n<li class="label2">Other Epistles</li>'
        h = h + self.headerGroup(59, 65)
        h = h + '\n<li class="label2">Revelation</li>'
        h = h + self.headerGroup(66, 66)
        h = h + '\n</ul>'
        #h = h + '\n</tr><tr><td colspan = "2"><br><a href="{{{websiteURL}}}">{{{websiteName}}}</a></td></tr></table></div></div>'
        h = header_header.replace(r'{{{ book list }}}', h)
        h = h.replace(r'{{{ book name }}}', books.fullName(int(self.cb)))
        return h

    def writeChapterMarker(self):
        self.write(self.cachedChapterMarker)
        self.cachedChapterMarker = ''

    def writeIndent(self, level):
        self.write('\n<p class="indent' + str(level) + '">')
        self.writeChapterMarker()

    def writeHeader(self, level, token):
        self.afterHeader = True
        self.write('\n<h' + str(level) + '>' + token.value + '</h' + str(level) + '>')

    def render_id(self, token): 
        self.write(footer)
        self.close()
        self.resetBookStart()
        self.cb = books.bookKeyForIdValue(token.value)
        self.openFile(self.cb)
        self.write(self.header())
        self.indentFlag = False
    def render_mt(self, token):     self.writeHeader(1, token)
    def render_mt2(self, token):    self.writeHeader(2, token)
    def render_ms(self, token):     self.writeHeader(4, token)
    def render_ms2(self, token):    self.writeHeader(5, token)
    def render_p(self, token):
        self.write('\n<!-- ' + self.cc + ' ' + self.cv + ' -->\n')
        self.indentFlag = False
        if self.cc == '001' and self.cv == '001' and self.firstParagraphInBook:
            self.write('\n\n<p class="smallcappara">')
        else:
            self.write('\n\n<p>')
        self.writeChapterMarker()
    def render_s1(self, token):
        self.indentFlag = False
        if token.value == '~':
            self.write('<p>&nbsp;<p>')
        else:
            self.writeHeader(6, token)
    def render_s2(self, token):
        self.indentFlag = False
        self.writeHeader(7, token)
    def render_c(self, token):
        self.cc = token.value.zfill(3)
        self.cachedChapterMarker = '<span class="chapter" id="' + self.cc + '001">' + token.value + '</span>'
    def render_v(self, token):
        self.cv = token.value.zfill(3)
        if self.cv == '001':
            self.writeChapterMarker()
        else:
            self.write('<span class="verse" rel="v' + self.cb + self.cc + self.cv + '" id="' + self.cc + self.cv + '" >' + token.value + '</span>\n')
    def render_wj_s(self, token):     self.write('<span class="woc">')
    def render_wj_e(self, token):     self.write('</span>')

    def render_nd_s(self, token):     self.write('<span class="nd">')
    def render_nd_e(self, token):     self.write('</span>')

    def render_text(self, token):
        if self.firstParagraphInBook:
            self.write('<span class="dropcap">' + token.value[0] + '</span>' + token.value[1:] + ' ')
        else:
            self.write(" " + token.value + " ")
        self.firstParagraphInBook = False

    def render_m(self, token):       self.render_p(token)
    def render_q(self, token):       self.writeIndent(1)
    def render_q1(self, token):      self.writeIndent(1)
    def render_q2(self, token):      self.writeIndent(2)
    def render_q3(self, token):      self.writeIndent(3)
    def render_nb(self, token):      self.writeIndent(0)
    def render_b(self, token):       self.write('<p>')
    def render_i_s(self, token):      self.write('<i>')
    def render_i_e(self, token):      self.write('</i>')
    def render_pbr(self, token):     self.write('<br />')
    
    def render_d(self, token):
        self.write('\n<p>')
        self.writeChapterMarker()
        self.write('<em>' + token.value + '</em>')

    def render_is1(self, token):    self.render_s1(token)
    def render_ip(self, token):     self.render_p(token)
    def render_iot(self, token):    self.render_q(token)
    def render_io1(self, token):    self.render_q2(token)
    
    def render_f_s(self, token):      self.write('<span class="rightnotemarker">*</span><span class="rightnote">')
    def render_f_e(self, token):      self.write('</span>')
    

#
#  Structure
#

header_header = r"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <title>{{{translationname}}} | {{{ book name }}}</title>
    <meta charset='utf-8'>
    <script src="jquery-3.2.1.min.js"></script>
    <link href="normalize.css" rel="stylesheet">
    <link href="style.css" rel="stylesheet">
    <link rel="stylesheet" href="fonts/crimsonpro/stylesheet.css" type="text/css" charset="utf-8" />
    <script src="jump.js"></script>
    </head>

    <body>
<div id="nav-menu">
    <input id="menubar" type="checkbox" name="menu" class="label" />
    <label for="menubar">{{{translationname}}} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {{{ book name }}} &#9660;</label>
    <div class="submenu">
        <form id="navform">
            <small><label for="txtSearch">Enter Reference (eg Ps 23)</label></small>
            <input type="text" id="txtSearch"/>
        </form>
        {{{ book list }}}
    </div>
</div>

<p>&nbsp;</p>
"""

footer = r"""
        </p></body>   
        """

