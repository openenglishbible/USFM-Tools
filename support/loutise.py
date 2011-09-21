# -*- coding: utf-8 -*-
#

import os
import parseUsfm
import books
import datetime

class LoutPrinter(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        self.cb = u''    # Current Book
        self.cc = u'001'    # Current Chapter
        self.cv = u'001'    # Currrent Verse
        self.indentFlag = False
        self.rendered = u''
        self.bookName = u''
        self.inChapter = False
        self.inSections = False
        self.inSection = False
        self.startTextType = 'drop' # Or nomal or smallcaps
        self.inDropCap = False
        self.inPoetry = False
        
        
    #   SUPPORT
    #
    #
    def escape(self, s):
        return s.replace(u'“', u'{@Char quotedblleft }').replace(u'”', u'{@Char quotedblright }').replace(u'—', u'{@Char emdash }').replace(u'‘', u'{@Char quoteleft }').replace(u'’', u'{@Char quoteright }')
 
    def write(self, unicodeString):
        self.rendered = self.rendered + unicodeString
        
    def close(self):
        self.closeChapter()
    
    def closeChapter(self):
        self.closeSections()
        if self.inChapter:          # We need to close previous chapter (ie Book)
            self.inChapter = False
            self.write(u'\n@End @Chapter\n')   
            
    def closeSections(self):
        self.closeSection()
        if self.inSections:          # We need to close previous section 
            self.inSections = False
            self.write(u'\n@EndSections\n')   
            
    def closeSection(self):
        self.closeDropCap()
        if self.inSection:          # We need to close previous section 
            self.inSection = False
            self.write(u'\n@End @Section\n')  

    def closeDropCap(self):
        if self.inDropCap:          # We need to close previous section 
            self.inDropCap = False
            self.write(u'}')            

    def writeIndent(self, level):
        self.closeDropCap()
        if not self.inPoetry:
            self.write(u'\n@DP ') 
            self.inPoetry = True
        else:
            self.write(u'\n@LLP ') 
        self.write(u'~ ~ ~ ~' * level)   
        
    def formatText(self, text):
        t = text
        if len(t) < 60: self.startTextType = 'normal'  # Don't do funky things with short first lines.
        if self.startTextType == 'drop':
            self.inDropCap = True
            self.write(t[0] + u' @DropCapTwo {')
            self.write(self.escape(self.smallCapText(t[1:])))
        elif self.startTextType == 'smallcaps':
            self.write(self.escape(self.smallCapText(t)))
        else:
            self.write(self.escape(self.addNextText(t)))
        self.write(u'\n')
        self.startTextType = 'normal'
        
    def addNextText(self, text):
        t = text
        if not self.registerForNextText == u'':
            try:
                i = t.index(u' ')
                t = t[:i] + self.registerForNextText + u' ' + t[i+1:]
            except Exception:
                t = self.registerForNextText + t                
            self.registerForNextText = u''
        return t        

    def smallCapText(self, s):
         i = 0
         while i < len(s):
             if i < 60:  #we are early, look for comma
                 if s[i] == u',' or s[i] == u';' or s[i] == u'.' or s[i] == u'—':
                     return u'{@S {' + self.addNextText(s[:i+1]) + u'}} ' + s[i+1:]
                 i = i + 1
             else: # look for space
                 if s[i] == ' ':
                     return u'{@S {' + self.addNextText(s[:i]) + u'}}' + s[i:]
                 i = i + 1
         return self.addNextText(s)     
         
    def newPara(self, indent = True):
        self.closeDropCap()
        if self.inPoetry:
            self.write(u'\n\n@DP\n')
            self.inPoetry = False
        else:
            if indent:
                self.write(u'\n\n@PP\n')
            else:
                self.write(u'\n\n@LP\n')
            
    #   TOKENS
    #
    #
    def renderID(self, token): 
        self.cb = books.bookKeys[token.value]
        self.indentFlag = False
        self.closeChapter()
    def renderIDE(self, token):     pass
    def renderH(self, token):       
        self.bookname = token.value
        self.write(u'\n@Chapter @Title {' + self.escape(token.value) + u'} @Begin\n')
        self.inChapter = True
        self.startTextType = 'drop'
    def renderMT(self, token):      self.write(u'\n@Display @Heading {' + self.escape(token.value) + u'}\n')
    def renderMS(self, token):
        self.closeSection()
        if not self.inSections: self.write(u'@BeginSections '); self.inSections = True
        self.write(u'\n@Section @Title {' + self.escape(token.value) + u'} @Begin @LP\n')
        self.inSection = True
        if self.startTextType == 'normal': self.startTextType = 'smallcaps'
    def renderMS2(self, token):     self.write(u'\n@Display @Heading {' + self.escape(token.value) + u'}\n')
    def renderP(self, token):       self.newPara()
    def renderS(self, token):       self.inPoetry = False; self.closeDropCap(); self.write(u'\n\n@DP @LP\n')
    def renderS2(self, token):      self.closeDropCap(); self.write(u'\n\n@DP\n')
    def renderC(self, token):
        self.cc = token.value.zfill(3)
        self.registerForNextText = u'{@OuterNote { 10.5p @Font {@B ' + token.value + u'}}}'
    def renderV(self, token):
        self.cv = token.value.zfill(3)
        if not self.cv == u'001':   self.registerForNextText = u'{@OuterNote { 8p @Font {' + token.value + u'}}}'
    def renderWJS(self, token):     pass
    def renderWJE(self, token):     pass
    def renderTEXT(self, token):    self.formatText(token.value)
    def renderQ(self, token):       self.writeIndent(1)
    def renderQ1(self, token):      self.writeIndent(1)
    def renderQ2(self, token):      self.writeIndent(2)
    def renderQ3(self, token):      self.writeIndent(3)
    def renderNB(self, token):      self.newPara(indent = False)
    def renderB(self, token):       self.newPara()
    def renderQTS(self, token):     pass
    def renderQTE(self, token):     pass
    def renderFS(self, token):      self.write(u'@FootNote { ')
    def renderFE(self, token):      self.write(u' }')
    def renderIS(self, token):      self.write(u'{@I {')
    def renderIE(self, token):      self.write(u'}}')
    def renderNDS(self, token):     pass
    def renderNDE(self, token):     pass
    def renderPBR(self, token):     self.write(u'@LLP ')
    def renderSCS(self, token):     self.write(u'{@B {')
    def renderSCE(self, token):     self.write(u'}}')

class TransformToLout(object):
    outputDir = ''
    patchedDir = ''
    prefaceDir = ''

    def loadBooks(self, path):
        books = {}
        dirList=os.listdir(path)
        for fname in dirList:
          if fname[-5:] == '.usfm':
              f = open(path + '/' + fname)
              usfm = unicode(f.read(), 'utf-8')
              books[self.bookID(usfm)] = usfm
              f.close()
        return books

    def bookID(self, usfm):
        return books.bookID(usfm)

    def setupAndRun(self, patchedDir, outputDir, buildName):
        self.patchedDir = patchedDir
        self.outputDir = outputDir
        self.booksUsfm = self.loadBooks(patchedDir)
        self.printer = LoutPrinter(self.outputDir)

        for bookName in books.silNames:
            if self.booksUsfm.has_key(bookName):
                tokens = parseUsfm.parseString(self.booksUsfm[bookName])
                for t in tokens: t.renderOn(self.printer)
                print '      (' + bookName + ')'
        self.printer.close()

        f = open(self.outputDir + buildName, 'w')
        f.write(ur"""
        @Include { oebbook } 
        @Book
            @Title {}
            @Author {}
            @Edition {}
            @Publisher {}
            @BeforeTitlePage {}
            @OnTitlePage {}
            @AfterTitlePage {}
            @AtEnd {}
            @InitialFont { Palatino Base 10.5p } 
            @InitialBreak { adjust 1.2fx hyphen } 
            @InitialSpace { lout } 
            @InitialLanguage { English } 
            @PageOrientation { Portrait } 
            @PageHeaders { Titles } 
            @ColumnNumber { 1 } 
            @FirstPageNumber { 1 } 
            @IntroFirstPageNumber { 1 } 
            @OptimizePages { No } 
            @GlossaryText { @Null } 
            @IndexText { @Null }
            @IndexAText { @Null }
            @IndexBText { @Null } 
        //

        @Preface
        @Title { Preface }
        @Begin
        @PP
        This is the preface to the Open English Bible.
        @End @Preface
        """.encode('utf-8'))
        f.write(self.printer.rendered.encode('utf-8'))
        f.close()
        
