# -*- coding: utf-8 -*-
#

import abstractRenderer
import codecs
import books

#
#   UTF-8 CVS file
#

class CSVRenderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputFilename):
        # Unset
        self.f = None  # output file stream
        # IO
        self.outputFilename = outputFilename
        self.inputDir = inputDir
        # Flags
        self.cb = u''    # Current Book
        self.cc = u'001'    # Current Chapter
        self.cv = u'001'    # Currrent Verse  
        self.infootnote = False
        self.verseHadContent = True
        
    def render(self):
        self.f = codecs.open(self.outputFilename, 'w', 'macroman') # 'utf_8_sig macroman
        self.loadUSFM(self.inputDir)
        self.run()
        self.f.close()
        
    def writeLog(self, s):
        print s
                
    #   SUPPORT

    def escape(self, s):
        return u'' if self.infootnote else s
            
    #   TOKENS

    def renderID(self, token): 
        self.cb = books.bookKeyForIdValue(token.value)
    def renderC(self, token):
        self.cc = token.value.zfill(3)
    def renderV(self, token):
        self.cv = token.value.zfill(3)
        if not self.verseHadContent: self.f.write(u' ~')
        self.verseHadContent = False
        self.f.write(u'\n' + books.accordanceNameForBookKey(self.cb) + ' ' + str(int(self.cc)) + ':' + str(int(self.cv.split('-')[0]))   + ' ') # str(int(self.cb))
    def renderTEXT(self, token):    self.verseHadContent = True ; self.f.write(self.escape(token.value) + ' ')
    def renderFS(self, token):      self.infootnote = True
    def renderFE(self, token):      self.infootnote = False
