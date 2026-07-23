# -*- coding: utf-8 -*-
#

import os
import shutil
import glob
import html
import re

import abstractRenderer
import books

# render_text pads every token with spaces, which strands punctuation after
# closing inline tags ("Lord </span> ,"); this rejoins it to the preceding
# word. The ’ branch covers split possessives and contractions
# ("Lord </span> 's") without touching opening quotes (always ‘).
punctuationGap = re.compile(
    r'[ \t\n]+((?:</(?:span|i|b|em)>)*(?:[,;.:!?]|’(?=(?:s|t|ll|ve|re|d|m)\b)))')


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
        # Chapters rendered in this book, in order
        self.chaptersSeen = []
        # Footnotes rendered in this book (for unique toggle ids)
        self.noteCount = 0

    def render(self):
        # Load
        self.loadUSFM(self.inputDir)
        # Write pages
        self.run()
        self.close()
        for f in glob.glob(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/*'):
            if os.path.isdir(f):
                shutil.copytree(f, self.outputDir + '/' + f.split('/')[-1])
            else:
                shutil.copy(f, self.outputDir + '/')
        shutil.copy(self.config.get('HTML','frontlogo'), self.outputDir + '/')
        self.generateIndexFile()
        
    # File handling    
    
    def generateIndexFile(self):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/htmlsupport/index.html') as f:
            c = f.read()
        c = c.replace('{{{ot}}}', self.bookList(1, 39))
        c = c.replace('{{{nt}}}', self.bookList(40, 66))
        if 'FRT' in self.booksUsfm:
            c = c.replace('{{{frontmatter}}}', '<a href="b000.html">About this translation</a>')
        else:
            c = c.replace('{{{frontmatter}}}', '')
        c = c.replace(r'{{{translationname}}}',self.config.get('General','name'))
        c = c.replace(r'{{{pathtologo}}}',self.config.get('HTML','frontlogo').split('/')[-1])  # copy logo into place
        with open(self.outputDir + '/index.html', 'w') as f:
            f.write(c)

    def bookList(self, s, f):
        h = ''
        for b in range(s, f + 1):
            if books.silNames[b] in self.booksUsfm:
                h = h + '\n<a href="b' + str(b).zfill(3) + '.html">' + books.bookNames[b - 1].replace(' ', '&nbsp;') + '</a><br>'
            else:
                h = h + '\n' + books.bookNames[b - 1] + '<br>'
        return h
                
    def openFile(self, bookID):
        self.f = open(self.outputDir + '/b' + bookID + '.html', 'w')
        self.ft = []
        
    def close(self):
        if self.cb:
            self.write(self.bookNav())
        self.write(footer)
        t = ''.join(self.ft)
        t = t.replace(r'{{{chapternav}}}', self.chapterNav())
        self.f.write(self.cleanHTML(t))
        self.f.close()
        self.ft = []
 
    def write(self, unicodeString):
        self.ft.append(unicodeString)
        
    def cleanHTML(self, t):
        c = t
        c = c.replace(r'~', '&nbsp;')
        # Repeat until stable: a gap like "word </span> ," needs one pass for
        # the space before the comma and another for the one before the tag.
        while True:
            c2 = punctuationGap.sub(r'\1', c)
            if c2 == c:
                break
            c = c2

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
        h = h.replace(r'{{{ book name }}}', self.bookTitle())
        return h

    def bookTitle(self):
        if self.cb == '000':
            return 'About'
        return books.fullName(int(self.cb))

    def chapterNav(self):
        if len(self.chaptersSeen) < 2:
            return ''
        h = '\n<div class="chapternav">Chapters: '
        for c in self.chaptersSeen:
            h = h + '<a href="#' + c.zfill(3) + '001">' + c + '</a> '
        return h + '</div>\n'

    def bookNav(self):
        contents = '<span><a href="index.html">Contents</a></span>'
        if self.cb == '000':
            return '\n<div class="booknav"><span></span>' + contents + '<span></span></div>\n'
        b = int(self.cb)
        prev = ''
        for i in range(b - 1, 0, -1):
            if books.silNames[i] in self.booksUsfm:
                prev = '<a href="b' + str(i).zfill(3) + '.html">&#8592;&nbsp;' + books.bookNames[i - 1] + '</a>'
                break
        nxt = ''
        for i in range(b + 1, 67):
            if books.silNames[i] in self.booksUsfm:
                nxt = '<a href="b' + str(i).zfill(3) + '.html">' + books.bookNames[i - 1] + '&nbsp;&#8594;</a>'
                break
        return ('\n<div class="booknav"><span>' + prev + '</span>'
                + contents + '<span>' + nxt + '</span></div>\n')

    def writeChapterMarker(self):
        self.write(self.cachedChapterMarker)
        self.cachedChapterMarker = ''

    def writeIndent(self, level):
        self.write('\n<p class="indent' + str(level) + '">')
        self.writeChapterMarker()

    def writeHeader(self, level, token, cssClass=''):
        self.afterHeader = True
        attr = ' class="' + cssClass + '"' if cssClass else ''
        self.write('\n<h' + str(level) + attr + '>' + html.escape(token.value, quote=False) + '</h' + str(level) + '>')

    def render_id(self, token):
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
        self.writeHeader(6, token, 's2')
    def render_c(self, token):
        self.cc = token.value.zfill(3)
        self.chaptersSeen.append(token.value)
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
        text = html.escape(token.value, quote=False)
        if self.firstParagraphInBook:
            v = text.lstrip() or text
            self.write('<span class="dropcap">' + v[0] + '</span>' + v[1:] + ' ')
        else:
            self.write(" " + text + " ")
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
        self.write('<em>' + html.escape(token.value, quote=False) + '</em>')

    def render_is1(self, token):    self.render_s1(token)
    def render_ip(self, token):     self.render_p(token)
    def render_iot(self, token):    self.render_q(token)
    def render_io1(self, token):    self.render_q2(token)
    
    def render_f_s(self, token):
        # Marker is a label tied to a hidden checkbox: on narrow screens
        # :checked reveals the note inline (see style.css); on wide screens
        # the note is always visible in the right margin.
        self.noteCount += 1
        n = 'note-' + str(self.noteCount)
        self.write('<label class="rightnotemarker" for="' + n + '">*</label>'
                   + '<input type="checkbox" class="notetoggle" id="' + n + '" />'
                   + '<span class="rightnote">')
    def render_f_e(self, token):      self.write('</span>')
    

#
#  Structure
#

header_header = r"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <title>{{{translationname}}} | {{{ book name }}}</title>
    <meta charset='utf-8'>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="color-scheme" content="light dark">
    <script>try{var t=localStorage.getItem('theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}</script>
    <script src="jquery-3.4.1.min.js"></script>
    <link href="normalize.css" rel="stylesheet">
    <link href="style.css" rel="stylesheet">
    <script src="jump.js"></script>
    <script src="theme.js" defer></script>
    </head>

    <body>
<button id="themetoggle" title="Switch between light, dark and automatic colours">&#9680; Auto</button>
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
{{{chapternav}}}
"""

footer = r"""
</body>
</html>
"""

