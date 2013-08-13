# -*- coding: utf-8 -*-
#

import abstractRenderer
import codecs
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
        self.cb = u''    # Current Book
        self.cc = u'001'    # Current Chapter
        self.cv = u'001'    # Currrent Verse
        self.indentFlag = False
        
    def render(self):
        # Write index
        self.f = open(self.outputDir + u'/index.html', 'w')
        self.write(indexPage)
        self.close()
        self.f = DummyFile()
        # Write pages
        self.loadUSFM(self.inputDir)
        self.run()
        self.f.close()
        
    def writeLog(self, s):
        print s
        
    # Support    
        
    def openFile(self, bookID):
        self.f = open(self.outputDir + u'/b' + bookID + u'.html', 'w')
        
    def close(self): 
        self.f.close()
 
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

    def renderID(self, token): 
        self.write(footer)
        self.close()
        self.cb = books.bookKeyForIdValue(token.value)
        self.openFile(self.cb)
        self.write(header)
        self.indentFlag = False
    def renderMT(self, token):      self.write(u'</p><h1>' + token.value + u'</h1><p>')
    def renderMT2(self, token):      self.write(u'</p><h2>' + token.value + u'</h2><p>')
    def renderMS(self, token):      self.write(u'</p><h4>' + token.value + u'</h4><p><br />')
    def renderMS2(self, token):     self.write(u'</p><h5>' + token.value + u'</h5><p><br />')
    def renderP(self, token):
        self.indentFlag = False
        self.write(u'<br /><br />')
    def renderS(self, token):
        self.indentFlag = False
        self.write(u'</p><p align="center">_________________________</p><p>')
    def renderS2(self, token):
        self.indentFlag = False
        self.write(u'</p><p align="center">----</p><p>')
    def renderC(self, token):
        self.cc = token.value.zfill(3)
        self.write(u'<span class="chapter">' + token.value + u'</span>')
    def renderV(self, token):
        self.cv = token.value.zfill(3)
        if self.cv == u'001':
            pass
        else:
            self.write(u'\n<span class="verse" rel="v' + self.cb + self.cc + self.cv + u'">' + token.value + u'</span>\n')
    def renderWJS(self, token):     self.write(u'<span class="woc">')
    def renderWJE(self, token):     self.write(u'</span>')
    def renderTEXT(self, token):    self.write(u" " + token.value + u" ")
    def renderQ(self, token):       self.writeIndent(1)
    def renderQ1(self, token):      self.writeIndent(1)
    def renderQ2(self, token):      self.writeIndent(2)
    def renderQ3(self, token):      self.writeIndent(3)
    def renderNB(self, token):      self.writeIndent(0)
    def renderB(self, token):       self.write(u'<br /><br />')
    def renderIS(self, token):      self.write(u'<i>')
    def renderIE(self, token):      self.write(u'</i>')
    def renderPBR(self, token):     self.write(u'<br />')

#
#  Structure
#

header = ur"""
    <html lang="en">
    <head>
    <title>Bible</title>
    <meta charset='utf-8'>
    <link href="normalize.css" rel="stylesheet">
    <link href='http://fonts.googleapis.com/css?family=GFS+Didot' rel='stylesheet' type='text/css'>
    <style type="text/css">
    @media all {html {font-size: 24px;}}
    @media all and (max-width:1000px){html {font-size: 24px;}}
    @media all and (max-width:960px){html {font-size: 23px;}}
    @media all and (max-width:920px){html {font-size: 22px;}}
    @media all and (max-width:880px){html {font-size: 21px;}}
    @media all and (max-width:840px){html {font-size: 20px;}}
    @media all and (max-width:800px){html {font-size: 19px;}}
    @media all and (max-width:760px){html {font-size: 18px;}}
    @media all and (max-width:720px){html {font-size: 17px;}}
    @media all and (max-width:680px){html {font-size: 16px;}}
    @media all and (max-width:640px){html {font-size: 15px;}}
    @media all and (max-width:600px){html {font-size: 14px;}}
    @media all and (max-width:560px){html {font-size: 13px;}}
    @media all and (max-width:520px){html {font-size: 12px;}}
    body {
    padding: 0rem 0em 0rem 0em;
    margin-left:auto;
    margin-right:auto;
    width:100%;
    max-width:1000px;
    min-width:520px;
    min-height: 100%;
    position: relative;
 
    }
    body > * {
    font-size: 100%;
    line-height: 125%;
    margin-left: 7rem;
    margin-right: 7rem;
    text-rendering: optimizeLegibility;
    }
    .chapter{
    	position: absolute;
    	left: 0rem;
    	width: 6rem;
    	text-align: right;
    	font-size: 120%;
    	color: #202020;
    }
    .verse{
    	position: absolute;
    	left: 0rem;
    	width: 6rem;
    	text-align: right;
    	font-size: 80%;
    	color: gray;
    }
    .rightnote{
    	position: absolute;
    	right: 0rem;
    	width: 6rem;
    	text-align: left;	
    	color: gray;
    	font-size: 80%;
    }
    h1{
    	font-family: 'Helvetica', serif;
    	font-size: 180%;
    	color: #202020;
    }
    p{
    	-webkit-hyphens: auto;
    	-moz-hyphens: auto;
    	-ms-hyphens: auto;
    	-o-hyphens: auto;
    	hyphens: auto;
    	font-family: 'GFS Didot', 'Palatino', serif;
    	color: #202020;
        -moz-font-feature-settings: "liga=1, dlig=1", "onum=1";
        -ms-font-feature-settings: "liga", "dlig","onum";
        -webkit-font-feature-settings: "liga", "dlig","onum";
        -o-font-feature-settings: "liga", "dlig","onum";
        font-feature-settings: "liga", "dlig","onum";

    }
    .navbar { position:absolute; margin-left:5px; font-size: 60% ; font-family: 'Helvetica', sans; }
    .navbar a { color: darkred;  text-decoration: none; }
    </style>
    </head>

    <body>
        <div class="navbar">
		<p><b>Bible</b></p>

        <p><b>Old Testament</b><br />
        <a href="b001.html">Genesis</a><br />
        <a href="b002.html">Exodus</a><br />
        <a href="b003.html">Leviticus</a><br />
        <a href="b004.html">Numbers</a><br />
        <a href="b005.html">Deuteronomy</a><br />
        <a href="b006.html">Joshua</a><br />
        <a href="b007.html">Judges</a><br />
        <a href="b008.html">Ruth</a><br />
        <a href="b009.html">1 Samuel</a><br />
        <a href="b010.html">2 Samuel</a><br />
        <a href="b011.html">1 Kings</a><br />
        <a href="b012.html">2 Kings</a><br />
        <a href="b013.html">1 Chronicles</a><br />
        <a href="b014.html">2 Chronicles</a><br />
        <a href="b015.html">Ezra</a><br />
        <a href="b016.html">Nehemiah</a><br />
        <a href="b017.html">Esther</a><br />
        <a href="b018.html">Job</a><br />
        <a href="b019.html">Psalms</a><br />
        <a href="b020.html">Proverbs</a><br />
        <a href="b021.html">Ecclesiastes</a><br />
        <a href="b022.html">Song of Solomon</a><br />
        <a href="b023.html">Isaiah</a><br />
        <a href="b024.html">Jeremiah</a><br />
        <a href="b025.html">Lamentations</a><br />
        <a href="b026.html">Ezekiel</a><br />
        <a href="b027.html">Daniel</a><br />
        <a href="b028.html">Hosea</a><br />
        <a href="b029.html">Joel</a><br />
        <a href="b030.html">Amos</a><br />
        <a href="b031.html">Obadiah</a><br />
        <a href="b032.html">Jonah</a><br />
        <a href="b033.html">Micah</a><br />
        <a href="b034.html">Nahum</a><br />
        <a href="b035.html">Habakkuk</a><br />
        <a href="b036.html">Zephaniah</a><br />
        <a href="b037.html">Haggai</a><br />
        <a href="b038.html">Zechariah</a><br />
        <a href="b039.html">Malachi</a><br />
        </p>

        <p><b>New Testament</b><br />
        <a href="b040.html">Matthew</a><br />
        <a href="b041.html">Mark</a><br />
        <a href="b042.html">Luke</a><br />
        <a href="b043.html">John</a><br />
        <a href="b044.html">Acts</a><br />
        <a href="b045.html">Romans</a><br />
        <a href="b046.html">1 Corinthians</a><br />
        <a href="b047.html">2 Corinthians</a><br />
        <a href="b048.html">Galatians</a><br />
        <a href="b049.html">Ephesians</a><br />
        <a href="b050.html">Philippians</a><br />
        <a href="b051.html">Colossians</a><br />
        <a href="b052.html">1 Thessalonians</a><br />
        <a href="b053.html">2 Thessalonians</a><br />
        <a href="b054.html">1 Timothy</a><br />
        <a href="b055.html">2 Timothy</a><br />
        <a href="b056.html">Titus</a><br />
        <a href="b057.html">Philemon</a><br />
        <a href="b058.html">Hebrews</a><br />
        <a href="b059.html">James</a><br />
        <a href="b060.html">1 Peter</a><br />
        <a href="b061.html">2 Peter</a><br />
        <a href="b062.html">1 John</a><br />
        <a href="b063.html">2 John</a><br />
        <a href="b064.html">3 John</a><br />
        <a href="b065.html">Jude</a><br />
        <a href="b066.html">Revelation</a><br />
        </div>
        """

footer = ur"""
        </p></body>   
        """

indexPage = header + ur"""<p>Index page""" + footer

