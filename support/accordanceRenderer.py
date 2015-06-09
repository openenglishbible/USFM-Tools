# -*- coding: utf-8 -*-
#

import abstractRenderer
import codecs
import books
import os

#
#   Renderer for Accordance - accordancebible.com
#

IN = 1
OUT = 2
JUSTOUT = 3

class Renderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputDir, outputName):
        abstractRenderer.AbstractRenderer.__init__(self, inputDir, outputDir, outputName)
        # Unset
        self.f = None  # output file stream
        # IO
        self.outputFilename = os.path.join(outputDir, outputName + '.accordance.txt')
        self.inputDir = inputDir
        # Flags
        self.cb = u''    # Current Book
        self.cc = u'001'    # Current Chapter
        self.cv = u'001'    # Currrent Verse  
        self.infootnote = False
        self.verseHadContent = True
        self.atStart = True
        self.ndStatus = OUT
        self.beforeFirstVerse = True
        
    def render(self):
        self.f = codecs.open(self.outputFilename, 'w', 'utf_8') # 'utf_8_sig macroman
        self.loadUSFM(self.inputDir)
        self.run()
        self.f.close()
        
    #   SUPPORT

    def escape(self, s):
        if self.ndStatus == IN: return s.strip()
        if self.ndStatus == JUSTOUT: self.ndStatus = OUT ; return ' ' + s if s[0].isalnum() else s
        return u'' if self.infootnote else s
        
    def write(self, s):
        if self.beforeFirstVerse:
            self.beforeFirstVerse = False
        else:
            self.f.write(s)
            
    #   TOKENS

    def render_id(self, token): 
        self.cb = books.bookKeyForIdValue(token.value)
    def renderC(self, token):
        self.cc = token.value.zfill(3)
    def renderV(self, token):
        self.cv = token.value.zfill(3)
        if not self.verseHadContent: self.write(u' ~')
        self.verseHadContent = False
        if self.atStart:
            self.atStart = False
        else:
            self.f.write(u'\n')
        self.f.write(books.accordanceNameForBookKey(self.cb) + ' ' + str(int(self.cc)) + ':' + str(int(self.cv.split('-')[0]))   + ' ') # str(int(self.cb))
    def renderTEXT(self, token):    self.verseHadContent = True ; self.write(self.escape(token.value + ' '))
    def renderFS(self, token):      self.infootnote = True
    def renderFE(self, token):      self.infootnote = False
    def renderP(self, token):       self.write(u' ¶ ')
    def render_nd_s(self,token):    self.ndStatus = IN; self.write(u'<c>')
    def render_nd_e(self,token):    self.ndStatus = JUSTOUT; self.write(u'</c>')
    def render_q1(self, token):     self.write(u'<br>\t')
    def render_q2(self, token):     self.write(u'<br>\t\t') 
    def render_q3(self, token):     self.write(u'<br>\t\t\t') 
    
