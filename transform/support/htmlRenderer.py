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
        self.outputDescription = os.path.join(outputDir, outputName + '.epub')
        abstractRenderer.AbstractRenderer.__init__(self, inputDir, outputDir, outputName, config)
        # Unset
        self.f = DummyFile()  # output file stream
        self.ft = [] # array of text to write to file
        # IO
        self.outputDir = os.path.join(outputDir, outputName + '_html')
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)
        self.inputDir = inputDir
        # Caches
        self.cachedChapterMarker = ''
        self.cachedBookname = ''
        # Position
        self.cb = ''    # Current Book
        self.cc = '001'    # Current Chapter
        self.cv = '001'    # Currrent Verse
        # Flags
        self.indentFlag = False

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
        c = c.replace('{{{nt}}}', self.bookList(40, 66))
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
        c = t.replace('<p><br /><br />', '<p>')
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
    
    def header(self):
        h = header_header
        h = h + '<tr><td colspan = "5" style="font-size:100%;">&nbsp;<br/><b>Old Testament</b></td></tr><tr>'
        for b in range(1, 39):
            if books.silNames[b] in self.booksUsfm:
                h = h + '\n<td><a href="b' + str(b).zfill(3) + '.html">' + books.bookNames[b - 1].replace(' ', '&nbsp;') + '</a></td>'
            else:
                h = h + '\n<td>' + books.bookNames[b - 1] + '</td>'
            if b % 5 == 0: h = h + '</tr><tr>'
        h = h + '\n</tr><tr><td colspan = "5" style="font-size:100%;">&nbsp;<br/><b>New Testament</b></td></tr><tr>'
        for b in range(40, 66):
            if books.silNames[b] in self.booksUsfm:
                h = h + '\n<td><a href="b' + str(b).zfill(3) + '.html">' + books.bookNames[b - 1].replace(' ', '&nbsp;') + '</a></td>'
            else:
                h = h + '\n<td>' + books.bookNames[b - 1] + '</td>'
            if b % 5 == 4: h = h + '</tr><tr>'
        h = h + '\n</tr><tr><td colspan = "2"><br><a href="{{{websiteURL}}}">{{{websiteName}}}</a></td></tr></table></div></div>'
        return h
        
    def writeChapterMarker(self):
        self.write(self.cachedChapterMarker)
        self.cachedChapterMarker = ''

    def writeIndent(self, level):
        if level == 0:
            self.indentFlag = False
            self.write('<br /><br />')
            return 
        if not self.indentFlag:
            self.indentFlag = True
            self.write('<br />')
        self.write('<br />')
        self.write('&nbsp;&nbsp;' * level)
        self.writeChapterMarker()

    def render_id(self, token): 
        self.write(footer)
        self.close()
        self.cb = books.bookKeyForIdValue(token.value)
        self.openFile(self.cb)
        self.write(self.header())
        self.indentFlag = False
    def render_mt(self, token):      self.write('</p><h1>' + token.value + '</h1><p>')
    def render_mt2(self, token):      self.write('</p><h2>' + token.value + '</h2><p>')
    def render_ms(self, token):      self.write('</p><h4>' + token.value + '</h4><p>')
    def renderMS2(self, token):     self.write('</p><h5>' + token.value + '</h5><p>')
    def render_p(self, token):
        self.indentFlag = False
        self.write('<br /><br />')
        self.writeChapterMarker()
    def render_s1(self, token):
        self.indentFlag = False
        if token.value == '~':
            self.write('<p>&nbsp;</p><p>')
        else:
            self.write('</p><h6>' + token.value + '</h6><p>')
    def render_s2(self, token):
        self.indentFlag = False
        self.write('</p><h7>' + token.value + '</h7><p>')
    def render_c(self, token):
        self.cc = token.value.zfill(3)
        self.cachedChapterMarker = '<span class="chapter" id="' + self.cc + '001">' + token.value + '</span>'
        # if self.cb==u'019': self.write(u'<p><em>Psalm ' + token.value + u'</em></p>')
    def render_v(self, token):
        self.cv = token.value.zfill(3)
        if self.cv == '001':
            self.writeChapterMarker()
        else:
            self.write('\n<span class="verse" rel="v' + self.cb + self.cc + self.cv + '" id="' + self.cc + self.cv + '" >' + token.value + '</span>\n')
    def render_wj_s(self, token):     self.write('<span class="woc">')
    def render_wj_e(self, token):     self.write('</span>')

    def render_nd_s(self, token):     self.write('<span class="nd">')
    def render_nd_e(self, token):     self.write('</span>')

    def render_text(self, token):    self.write(" " + token.value + " ")
    def render_q(self, token):       self.writeIndent(1)
    def render_q1(self, token):      self.writeIndent(1)
    def render_q2(self, token):      self.writeIndent(2)
    def render_q3(self, token):      self.writeIndent(3)
    def render_nb(self, token):      self.writeIndent(0)
    def render_b(self, token):       self.write('<br />')
    def render_i_s(self, token):      self.write('<i>')
    def render_i_e(self, token):      self.write('</i>')
    def render_pbr(self, token):     self.write('<br />')
    
    def render_d(self, token):       self.writeChapterMarker()

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
    <title>{{{translationname}}} | Read</title>
    <meta charset='utf-8'>
    <script src="jquery-3.2.1.min.js"></script>
    <link href="normalize.css" rel="stylesheet">
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

footer = r"""
        </p></body>   
        """

