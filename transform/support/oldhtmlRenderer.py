# -*- coding: utf-8 -*-
#

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

class HTMLRenderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputDir):
        # Unset
        self.f = DummyFile()  # output file stream
        # IO
        self.outputDir = outputDir
        self.inputDir = inputDir
        # Position
        self.cb = ''    # Current Book
        self.cc = '001'    # Current Chapter
        self.cv = '001'    # Currrent Verse
        self.indentFlag = False
        
    def render(self):
        # Write index
        self.f = open(self.outputDir + '/index.html', 'w')
        self.write(indexPage)
        self.close()
        self.f = DummyFile()
        # Write pages
        self.loadUSFM(self.inputDir)
        self.run()
        self.f.close()
        
    # Support    
        
    def openFile(self, bookID):
        self.f = open(self.outputDir + '/b' + bookID + '.html', 'w')
        
    def close(self): 
        self.f.close()
 
    def write(self, unicodeString):
        self.f.write(unicodeString.encode('utf-8'))

    def writeIndent(self, level):
        if level == 0:
            self.indentFlag = False
            self.write('<br /><br />')
            return 
        if not self.indentFlag:
            self.indentFlag = True
            self.write('<br />')
        self.write('<br />')
        self.write('&nbsp;&nbsp;&nbsp;&nbsp;' * level)

    def render_id(self, token): 
        self.write(footer)
        self.close()
        self.cb = books.bookKeyForIdValue(token.value)
        self.openFile(self.cb)
        self.write(header)
        self.indentFlag = False
    def render_mt(self, token):      self.write('</p><h1>' + token.value + '</h1><p>')
    def render_mt2(self, token):      self.write('</p><h2>' + token.value + '</h2><p>')
    def render_ms(self, token):      self.write('</p><h4>' + token.value + '</h4><p><br />')
    def renderMS2(self, token):     self.write('</p><h5>' + token.value + '</h5><p><br />')
    def render_p(self, token):
        self.indentFlag = False
        self.write('<br /><br />')
    def render_s1(self, token):
        self.indentFlag = False
        self.write('</p><p align="center">_________________________</p><p>')
    def render_s2(self, token):
        self.indentFlag = False
        self.write('</p><p align="center">----</p><p>')
    def render_c(self, token):
        self.cc = token.value.zfill(3)
        self.write('<h2 class="c-num">' + token.value + '</h2><p>')
    def render_v(self, token):
        self.cv = token.value.zfill(3)
        if self.cv == '001':
            self.write('\n<span class="verse" rel="v' + self.cb + self.cc + self.cv + '"><span class="v-num-1">' + token.value + '&nbsp;</span>\n')
        else:
            self.write('</span>\n<span class="verse" rel="v' + self.cb + self.cc + self.cv + '"><span class="v-num">' + token.value + '&nbsp;</span>\n')
    def render_wj_s(self, token):     self.write('<span class="woc">')
    def render_wj_e(self, token):     self.write('</span>')
    def render_text(self, token):    self.write(" " + token.value + " ")
    def render_q(self, token):       self.writeIndent(1)
    def render_q1(self, token):      self.writeIndent(1)
    def render_q2(self, token):      self.writeIndent(2)
    def render_q3(self, token):      self.writeIndent(3)
    def render_nb(self, token):      self.writeIndent(0)
    def render_b(self, token):       self.write('<br /><br />')
    def render_i_s(self, token):      self.write('<i>')
    def render_i_e(self, token):      self.write('</i>')
    def render_pbr(self, token):     self.write('<br />')

#
#  Structure
#

indexPage = r"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta http-equiv="content-type" content="text/html; charset=utf-8" />
            <title>Bible</title>
        </head>
		<style media="all" type="text/css">
		h2.c-num { position:absolute; margin-left:-30px; color: #AAAAAA; }
		span.v-num-1 { display : none; }
		span.v-num { color: #AAAAAA; font-size: small}
		a { color:green; text-decoration:none;}
		p { font-family: Verdana, Helvetica, Arial, Sans-Serif;}
		li { font-family: Verdana, Helvetica, Arial, Sans-Serif;}
		h1 { font-family: Verdana, Helvetica, Arial, Sans-Serif; }
		h2 { font-family: Verdana, Helvetica, Arial, Sans-Serif; }
		h3 { font-family: Verdana, Helvetica, Arial, Sans-Serif; }
		h4 { font-family: Verdana, Helvetica, Arial, Sans-Serif; }
		</style>
        <body>
        <div style="position:absolute; margin-left:5; width:190px; background-color:#E6FAE6;">
		<h2>Bible</h2>

        <p><b>Old Testament</b></p>
        <ul>
        <li><a href="b001.html">Genesis</li>
        <li><a href="b002.html">Exodus</li>
        <li><a href="b003.html">Leviticus</li>
        <li><a href="b004.html">Numbers</li>
        <li><a href="b005.html">Deuteronomy</li>
        <li><a href="b006.html">Joshua</li>
        <li><a href="b007.html">Judges</li>
        <li><a href="b008.html">Ruth</a></li>
        <li><a href="b009.html">1 Samuel</li>
        <li><a href="b010.html">2 Samuel</li>
        <li><a href="b011.html">1 Kings</li>
        <li><a href="b012.html">2 Kings</li>
        <li><a href="b013.html">1 Chronicles</li>
        <li><a href="b014.html">2 Chronicles</li>
        <li><a href="b015.html">Ezra</li>
        <li><a href="b016.html">Nehemiah</li>
        <li><a href="b017.html">Esther</a></li>
        <li><a href="b018.html">Job</li>
        <li><a href="b019.html">Psalms</a></li>
        <li><a href="b020.html">Proverbs</li>
        <li><a href="b021.html">Ecclesiastes</li>
        <li><a href="b022.html">Song of Solomon</li>
        <li><a href="b023.html">Isaiah</a></li>
        <li><a href="b024.html">Jeremiah</li>
        <li><a href="b025.html">Lamentations</li>
        <li><a href="b026.html">Ezekiel</li>
        <li><a href="b027.html">Daniel</a></li>
        <li><a href="b028.html">Hosea</li>
        <li><a href="b029.html">Joel</a></li>
        <li><a href="b030.html">Amos</li>
        <li><a href="b031.html">Obadiah</a></li>
        <li><a href="b032.html">Jonah</a></li>
        <li><a href="b033.html">Micah</li>
        <li><a href="b034.html">Nahum</a></li>
        <li><a href="b035.html">Habakkuk</a></li>
        <li><a href="b036.html">Zephaniah</a></li>
        <li><a href="b037.html">Haggai</a></li>
        <li><a href="b038.html">Zechariah</li>
        <li><a href="b039.html">Malachi</li>
        </ul>            

        <p><b>New Testament</b></p>
        <ul>
        <li><a href="b040.html">Matthew</a></li>
        <li><a href="b041.html">Mark</a></li>
        <li><a href="b042.html">Luke</a></li>
        <li><a href="b043.html">John</a></li>
        <li><a href="b044.html">Acts</a></li>
        <li><a href="b045.html">Romans</a></li>
        <li><a href="b046.html">1 Corinthians</a></li>
        <li><a href="b047.html">2 Corinthians</a></li>
        <li><a href="b048.html">Galatians</a></li>
        <li><a href="b049.html">Ephesians</a></li>
        <li><a href="b050.html">Philippians</a></li>
        <li><a href="b051.html">Colossians</a></li>
        <li><a href="b052.html">1 Thessalonians</a></li>
        <li><a href="b053.html">2 Thessalonians</a></li>
        <li><a href="b054.html">1 Timothy</a></li>
        <li><a href="b055.html">2 Timothy</a></li>
        <li><a href="b056.html">Titus</a></li>
        <li><a href="b057.html">Philemon</a></li>
        <li><a href="b058.html">Hebrews</a></li>
        <li><a href="b059.html">James</a></li>
        <li><a href="b060.html">1 Peter</a></li>
        <li><a href="b061.html">2 Peter</a></li>
        <li><a href="b062.html">1 John</a></li>
        <li><a href="b063.html">2 John</a></li>
        <li><a href="b064.html">3 John</a></li>
        <li><a href="b065.html">Jude</a></li>
        <li><a href="b066.html">Revelation</a></li>
        </ul>
        </div>
        <div style="margin-left:230px; margin-right:80px">
        </div>
        </body>
        </html>
"""

header = r"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta http-equiv="content-type" content="text/html; charset=utf-8" />
            <title>Bible</title>
        </head>
		<style media="all" type="text/css">
		h2.c-num { position:absolute; margin-left:-30px; color: #AAAAAA; }
		span.v-num-1 { display : none; }
		span.v-num { color: #AAAAAA; font-size: small}
		a { color:green; text-decoration:none;}
		p { font-family: Verdana, Helvetica, Arial, Sans-Serif;}
		li { font-family: Verdana, Helvetica, Arial, Sans-Serif;}
		h1 { font-family: Verdana, Helvetica, Arial, Sans-Serif; }
		h2 { font-family: Verdana, Helvetica, Arial, Sans-Serif; }
		h3 { font-family: Verdana, Helvetica, Arial, Sans-Serif; }
		h4 { font-family: Verdana, Helvetica, Arial, Sans-Serif; }
		</style>
        <body>
        <div style="position:absolute; margin-left:5; width:190px; background-color:#E6FAE6;">
		<h2>Bible</h2>

        <p><b>Old Testament</b></p>
        <ul>
        <li><a href="b001.html">Genesis</li>
        <li><a href="b002.html">Exodus</li>
        <li><a href="b003.html">Leviticus</li>
        <li><a href="b004.html">Numbers</li>
        <li><a href="b005.html">Deuteronomy</li>
        <li><a href="b006.html">Joshua</li>
        <li><a href="b007.html">Judges</li>
        <li><a href="b008.html">Ruth</a></li>
        <li><a href="b009.html">1 Samuel</li>
        <li><a href="b010.html">2 Samuel</li>
        <li><a href="b011.html">1 Kings</li>
        <li><a href="b012.html">2 Kings</li>
        <li><a href="b013.html">1 Chronicles</li>
        <li><a href="b014.html">2 Chronicles</li>
        <li><a href="b015.html">Ezra</li>
        <li><a href="b016.html">Nehemiah</li>
        <li><a href="b017.html">Esther</a></li>
        <li><a href="b018.html">Job</li>
        <li><a href="b019.html">Psalms</a></li>
        <li><a href="b020.html">Proverbs</li>
        <li><a href="b021.html">Ecclesiastes</li>
        <li><a href="b022.html">Song of Solomon</li>
        <li><a href="b023.html">Isaiah</a></li>
        <li><a href="b024.html">Jeremiah</li>
        <li><a href="b025.html">Lamentations</li>
        <li><a href="b026.html">Ezekiel</li>
        <li><a href="b027.html">Daniel</a></li>
        <li><a href="b028.html">Hosea</li>
        <li><a href="b029.html">Joel</a></li>
        <li><a href="b030.html">Amos</li>
        <li><a href="b031.html">Obadiah</a></li>
        <li><a href="b032.html">Jonah</a></li>
        <li><a href="b033.html">Micah</li>
        <li><a href="b034.html">Nahum</a></li>
        <li><a href="b035.html">Habakkuk</a></li>
        <li><a href="b036.html">Zephaniah</a></li>
        <li><a href="b037.html">Haggai</a></li>
        <li><a href="b038.html">Zechariah</li>
        <li><a href="b039.html">Malachi</li>
        </ul>            

        <p><b>New Testament</b></p>
        <ul>
        <li><a href="b040.html">Matthew</a></li>
        <li><a href="b041.html">Mark</a></li>
        <li><a href="b042.html">Luke</a></li>
        <li><a href="b043.html">John</a></li>
        <li><a href="b044.html">Acts</a></li>
        <li><a href="b045.html">Romans</a></li>
        <li><a href="b046.html">1 Corinthians</a></li>
        <li><a href="b047.html">2 Corinthians</a></li>
        <li><a href="b048.html">Galatians</a></li>
        <li><a href="b049.html">Ephesians</a></li>
        <li><a href="b050.html">Philippians</a></li>
        <li><a href="b051.html">Colossians</a></li>
        <li><a href="b052.html">1 Thessalonians</a></li>
        <li><a href="b053.html">2 Thessalonians</a></li>
        <li><a href="b054.html">1 Timothy</a></li>
        <li><a href="b055.html">2 Timothy</a></li>
        <li><a href="b056.html">Titus</a></li>
        <li><a href="b057.html">Philemon</a></li>
        <li><a href="b058.html">Hebrews</a></li>
        <li><a href="b059.html">James</a></li>
        <li><a href="b060.html">1 Peter</a></li>
        <li><a href="b061.html">2 Peter</a></li>
        <li><a href="b062.html">1 John</a></li>
        <li><a href="b063.html">2 John</a></li>
        <li><a href="b064.html">3 John</a></li>
        <li><a href="b065.html">Jude</a></li>
        <li><a href="b066.html">Revelation</a></li>
        </ul>
        </div>
        <div style="margin-left:230px; margin-right:80px">
        """

footer = r"""
        </p></div></body>   
        """