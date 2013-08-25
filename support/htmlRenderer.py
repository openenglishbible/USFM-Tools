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
    
    def __init__(self, inputDir, outputDir, oebFlag=False):
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
        self.oebFlag = oebFlag
        
    def render(self):
        # Write index
        self.f = open(self.outputDir + u'/index.html', 'w')
        self.write(indexPage)
        self.close()
        self.f = DummyFile()
        # Write pages
        self.loadUSFM(self.inputDir)
        self.run()
        self.close()
        
    def writeLog(self, s):
        print s
        
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

    def renderID(self, token): 
        self.write(footer)
        self.close()
        self.cb = books.bookKeyForIdValue(token.value)
        self.openFile(self.cb)
        self.write(header)
        self.indentFlag = False
    def renderMT(self, token):      self.write(u'</p><h1>' + token.value + u'</h1><p>')
    def renderMT2(self, token):      self.write(u'</p><h2>' + token.value + u'</h2><p>')
    def renderMS(self, token):      self.write(u'</p><h4>' + token.value + u'</h4><p>')
    def renderMS2(self, token):     self.write(u'</p><h5>' + token.value + u'</h5><p>')
    def renderP(self, token):
        self.indentFlag = False
        self.write(u'<br /><br />')
        self.writeChapterMarker()
    def renderS(self, token):
        self.indentFlag = False
        if token.value == u'~':
            self.write(u'<p>&nbsp;</p><p>')
        else:
            self.write(u'</p><h6>' + token.value + u'</h6><p>')
    def renderS2(self, token):
        self.indentFlag = False
        self.write(u'</p><h7>' + token.value + u'</h7><p>')
    def renderC(self, token):
        self.cc = token.value.zfill(3)
        self.cachedChapterMarker = u'<span class="chapter">' + token.value + u'</span>'
        # if self.cb==u'019': self.write(u'<p><em>Psalm ' + token.value + u'</em></p>')
    def renderV(self, token):
        self.cv = token.value.zfill(3)
        if self.cv == u'001':
            pass
        else:
            self.write(u'\n<span class="verse" rel="v' + self.cb + self.cc + self.cv + u'">' + token.value + u'</span>\n')
    def renderWJS(self, token):     self.write(u'<span class="woc">')
    def renderWJE(self, token):     self.write(u'</span>')

    def renderNDS(self, token):     self.write(u'<span class="nd">')
    def renderNDE(self, token):     self.write(u'</span>')

    def renderTEXT(self, token):    self.write(u" " + token.value + u" ")
    def renderQ(self, token):       self.writeIndent(1)
    def renderQ1(self, token):      self.writeIndent(1)
    def renderQ2(self, token):      self.writeIndent(2)
    def renderQ3(self, token):      self.writeIndent(3)
    def renderNB(self, token):      self.writeIndent(0)
    def renderB(self, token):       self.write(u'<br />')
    def renderIS(self, token):      self.write(u'<i>')
    def renderIE(self, token):      self.write(u'</i>')
    def renderPBR(self, token):     self.write(u'<br />')
    
    def renderD(self, token):       self.writeChapterMarker()

    def render_is1(self, token):    self.renderS(token)
    def render_ip(self, token):     self.renderP(token)
    def render_iot(self, token):    self.renderQ(token)
    def render_io1(self, token):    self.renderQ2(token)
    
    def renderFS(self, token):      self.write(u'<span class="rightnotemarker">*</span><span class="rightnote">')
    def renderFE(self, token):      self.write(u'</span>')
    

#
#  Structure
#

header = ur"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <title>Open English Bible</title>
    <meta charset='utf-8'>
    <link href="normalize.css" rel="stylesheet">
    <script src="http://code.jquery.com/jquery-1.10.2.min.js"></script>
    <script>
    $( document ).ready(function() {
 
        $( "html" ).click(function( e ) {
            var container = $("div.navbar");
            if (!container.is(e.target)
                && container.has(e.target).length === 0) 
            {
                $("table").css( "left", "-9999px" ); 
            }           
         });
        
        $( "div.navbar" ).click(function( event ) {
           $("table").css( "left", "0px" );
        });
 
        $( "div.navbar" ).hover(
            function( e ) { $("table").css( "left", "0px"    ); },
            function( e ) { $("table").css( "left", "-999px" ); }
        );
    });
    </script>
    <style type="text/css">
    @media all {
        html {font-size: 19px;} 
        body {
            padding: 0rem 0em 0rem 0em;
            margin-left:auto;
            margin-right:auto;
            width:100%;
            max-width:800px;
            min-height: 100%;
            position: relative; 
        }
        body > * {
            font-size: 100%;
            line-height: 135%;
            text-rendering: optimizeLegibility;
            margin-left: 7rem; 
            margin-right: 7rem;
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
        .rightnotemarker{
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
        	font-family: 'Verdana', sans-serif;
        	font-size: 180%;
        	color: #202020;
        }
        h2{
        	font-family: 'Verdana', sans-serif;
        	font-size: 140%;
        	color: #202020;
        }
        h3{
        	font-family: 'Verdana', sans-serif;
        	font-size: 120%;
        	color: #202020;
        }
        h4{
        	font-family: 'Verdana', sans-serif;
        	font-size: 100%;
        	color: #202020;
            padding-top:2em;
        }
        h5{
        	font-family: 'Verdana', sans-serif;
        	font-size: 100%;
        	color: #202020;
            padding-top:2em;
        }
        h6{
        	font-family: 'Verdana', sans-serif;
        	font-size: 100%;
        	color: #202020;
            padding-top:0em;
        }
        h7{
        	font-family: 'Verdana', sans-serif;
        	font-size: 100%;
        	color: #202020;
            padding-top:0em;
        }
        p{
        	-webkit-hyphens: auto;
        	-moz-hyphens: auto;
        	-ms-hyphens: auto;
        	-o-hyphens: auto;
        	hyphens: auto;
        	font-family: 'Verdana', sans-serif;
        	color: #202020;
            -moz-font-feature-settings: "liga=1, dlig=1", "onum=1";
            -ms-font-feature-settings: "liga", "dlig","onum";
            -webkit-font-feature-settings: "liga", "dlig","onum";
            -o-font-feature-settings: "liga", "dlig","onum";
            font-feature-settings: "liga", "dlig","onum";
        }
        .navbar { 
            position:fixed; 
            margin-left:5px; 
            font-family: 'Verdana', sans-serif;
            background-color:white;
            z-index:999;
         }
        .navbar a { 
            color: green;  
            text-decoration: none; 
        }
        .navbar p { 
            color:green; 
        }
        .navbar table {
            position:absolute; 
            left:-999em; 
            background-color:#E6FAE6;
            border-top:solid green;
            font-size:80%;
        }
        .nd { /* Lord */
            font-variant:small-caps;
        }
        .vspacer{
            height:1em;
        }
    }
    @media all and (max-width:800px){html {font-size: 19px;}}
    @media all and (max-width:760px){html {font-size: 18px;}}
    @media all and (max-width:720px){html {font-size: 17px;}}
    @media all and (max-width:680px){html {font-size: 16px;}}
    @media all and (max-width:640px){html {font-size: 14px;}}
    @media all and (max-width:600px){html {font-size: 12px;}}
    
    /* iPhone 2 - 4 */
    @media only screen 
    and (min-device-width : 320px) 
    and (max-device-width : 480px) 
    and (orientation : portrait) {
        html {font-size: 58px;}
        body {
            margin:0;
            padding:0;
        } 
        body > * { margin-left:100px; margin-right:0px; width:100%; }
        .chapter{
        	position: absolute;
        	left: 20px;
        	width: 60px;
        	text-align: left;
        	font-size: 100%;
        	color: green;
        }
        .verse{
        	position: absolute;
        	left: 20px;
        	width: 60px;
        	text-align: left;
        	font-size: 80%;
        	color: green;
        }
        .navbar {
            position:relative;
        }
    }
    </style>
    </head>

    <body>
    <div class="navbar">
        <p>%navmarker%</p>
        <table>
            <tr><td colspan = "5" style="font-size:100%;">&nbsp;<br/>Old Testament</td></tr>
            <tr>
            <td><a href="b001.html">Genesis</a>&nbsp;</td>
            <td><a href="b002.html">Exodus</a>&nbsp;</td>
            <td><a href="b003.html">Leviticus</a>&nbsp;</td>
            <td><a href="b004.html">Numbers</a>&nbsp;</td>
            <td><a href="b005.html">Deuteronomy</a>&nbsp;</td>
            <td><a href="b006.html">Joshua</a>&nbsp;</td>
        </tr>
        <tr>
            <td><a href="b007.html">Judges</a>&nbsp;</td>
            <td><a href="b008.html">Ruth</a>&nbsp;</td>
            <td><a href="b009.html">1&nbsp;Samuel</a>&nbsp;</td>
            <td><a href="b010.html">2&nbsp;Samuel</a>&nbsp;</td>
            <td><a href="b011.html">1&nbsp;Kings</a>&nbsp;</td>
            <td><a href="b012.html">2&nbsp;Kings</a>&nbsp;</td>
        </tr>
        <tr>
            <td><a href="b013.html">1&nbsp;Chronicles</a>&nbsp;</td>
            <td><a href="b014.html">2&nbsp;Chronicles</a>&nbsp;</td>
            <td><a href="b015.html">Ezra</a>&nbsp;</td>
            <td><a href="b016.html">Nehemiah</a>&nbsp;</td>
            <td><a href="b017.html">Esther</a>&nbsp;</td>
            <td><a href="b018.html">Job</a>&nbsp;</td>
        </tr>
        <tr>
        <td><a href="b019.html">Psalms</a>&nbsp;</td>
        <td><a href="b020.html">Proverbs</a>&nbsp;</td>
        <td><a href="b021.html">Ecclesiastes</a>&nbsp;</td>
        <td><a href="b022.html">Song&nbsp;of&nbsp;Solomon</a>&nbsp;</td>
        <td><a href="b023.html">Isaiah</a>&nbsp;</td>
        <td><a href="b024.html">Jeremiah</a>&nbsp;</td>
    </tr>
    <tr>
        <td><a href="b025.html">Lamentations</a>&nbsp;</td>
        <td><a href="b026.html">Ezekiel</a>&nbsp;</td>
        <td><a href="b027.html">Daniel</a>&nbsp;</td>
        <td><a href="b028.html">Hosea</a>&nbsp;</td>
        <td><a href="b029.html">Joel</a>&nbsp;</td>
        <td><a href="b030.html">Amos</a>&nbsp;</td>
    </tr>
    <tr>
        <td><a href="b031.html">Obadiah</a>&nbsp;</td>
        <td><a href="b032.html">Jonah</a>&nbsp;</td>
        <td><a href="b033.html">Micah</a>&nbsp;</td>
        <td><a href="b034.html">Nahum</a>&nbsp;</td>
        <td><a href="b035.html">Habakkuk</a>&nbsp;</td>
        <td><a href="b036.html">Zephaniah</a>&nbsp;</td>
    </tr>
    <tr>
        <td><a href="b037.html">Haggai</a>&nbsp;</td>
        <td><a href="b038.html">Zechariah</a>&nbsp;</td>
        <td><a href="b039.html">Malachi</a>&nbsp;</td>
    </tr>
    <tr><td colspan = "5" style="font-size:100%;">&nbsp;<br/>New Testament</td></tr>
    <tr>
        <td><a href="b040.html">Matthew</a>&nbsp;</td>
        <td><a href="b041.html">Mark</a>&nbsp;</td>
        <td><a href="b042.html">Luke</a>&nbsp;</td>
        <td><a href="b043.html">John</a>&nbsp;</td>
        <td><a href="b044.html">Acts</a>&nbsp;</td>
        <td><a href="b045.html">Romans</a>&nbsp;</td>
    </tr>
    <tr>
        <td><a href="b046.html">1&nbsp;Corinthians</a>&nbsp;</td>
        <td><a href="b047.html">2&nbsp;Corinthians</a>&nbsp;</td>
        <td><a href="b048.html">Galatians</a>&nbsp;</td>
        <td><a href="b049.html">Ephesians</a>&nbsp;</td>
        <td><a href="b050.html">Philippians</a>&nbsp;</td>
        <td><a href="b051.html">Colossians</a>&nbsp;</td>
    </tr>
    <tr>
        <td><a href="b052.html">1&nbsp;Thessalonians</a>&nbsp;</td>
        <td><a href="b053.html">2&nbsp;Thessalonians</a>&nbsp;</td>
        <td><a href="b054.html">1&nbsp;Timothy</a>&nbsp;</td>
        <td><a href="b055.html">2&nbsp;Timothy</a>&nbsp;</td>
        <td><a href="b056.html">Titus</a>&nbsp;</td>
        <td><a href="b057.html">Philemon</a>&nbsp;</td>
    </tr>
    <tr>
        <td><a href="b058.html">Hebrews</a>&nbsp;</td>
        <td><a href="b059.html">James</a>&nbsp;</td>
        <td><a href="b060.html">1&nbsp;Peter</a>&nbsp;</td>
        <td><a href="b061.html">2&nbsp;Peter</a>&nbsp;</td>
        <td><a href="b062.html">1&nbsp;John</a>&nbsp;</td>
        <td><a href="b063.html">2&nbsp;John</a>&nbsp;</td>
    </tr>
    <tr>
        <td><a href="b064.html">3&nbsp;John</a>&nbsp;</td>
        <td><a href="b065.html">Jude</a>&nbsp;</td>
        <td><a href="b066.html">Revelation</a>&nbsp;</td>
        </tr>
        <tr><td>&nbsp;</td></tr>
        %linkToWebsite%
    </table>
    </div>
        """

footer = ur"""
        </p></body>   
        """

indexPage = header + ur"""<h1>Bible</h1>""" + footer

