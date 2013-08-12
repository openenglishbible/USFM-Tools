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
        
    def render(self):
        self.f = codecs.open(self.outputFilename, 'w', 'utf_8_sig')
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
        self.f.write(u'\n' + str(int(self.cb)) + ',' + str(int(self.cc)) + ',' + self.cv   + ',')
    def renderTEXT(self, token):    self.f.write(self.escape(token.value) + ' ')
    def renderFS(self, token):      self.infootnote = True
    def renderFE(self, token):      self.infootnote = False
