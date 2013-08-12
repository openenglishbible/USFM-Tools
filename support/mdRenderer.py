# -*- coding: utf-8 -*-
#

import abstractRenderer
import codecs

#
#   Simplest renderer. Ignores everything except ascii text.
#

class MarkdownRenderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputFilename):
        # Unset
        self.f = None  # output file stream
        # IO
        self.outputFilename = outputFilename
        self.inputDir = inputDir
        # Position
        self.currentC = 1
        self.book = u''
        
    def render(self):
        self.f = codecs.open(self.outputFilename, 'w', 'utf_8_sig')
        self.loadUSFM(self.inputDir)
        self.run()
        self.f.close()
        
    def writeLog(self, s):
        print s
        
    # Support    
        
    def escape(self, s):
        return s
                    
    def renderTEXT(self, token):    self.f.write(self.escape(token.value))

    def renderH(self, token):       self.book = token.getValue()
    def renderMT(self, token):      self.f.write(u'\n\n# ' + token.value.upper() + u'\n\n')
    def renderMT2(self, token):     self.f.write(u'\n\n## ' + token.value.upper() + u'\n\n')
    def renderMS(self, token):      self.f.write(u'\n\n' + token.value + u'\n' + (u'=' * len(token.value)) + u'\n\n')
    def renderMS2(self, token):     self.f.write(u'\n\n' + token.value + u'\n' + (u'-' * len(token.value)) + u'\n\n')
    def renderP(self, token):       self.f.write(u'\n\n')
    def renderB(self, token):       self.f.write(u'\n\n')
    def renderS(self, token):       self.f.write(u'\n\ \n')
    def renderS2(self, token):      self.f.write(u'\n\ \n')
    def renderC(self, token):       self.currentC = token.value; self.f.write(u'\n\n [' + self.book + u' ' + self.currentC + u' ] \n\n')
    def renderV(self, token):       self.f.write(u' [' + self.currentC + u':' + token.value + u'] ')
    def renderQ(self, token):       self.f.write(u'\n|  ') 
    def renderQ1(self, token):      self.f.write(u'\n|  ') 
    def renderQ2(self, token):      self.f.write(u'\n|    ') 
    def renderQ3(self, token):      self.f.write(u'\n|      ') 
    def renderNB(self, token):      self.f.write(u'\n|  ') 
    def renderLI(self, token):      self.f.write(u'* ')
    def renderPBR(self, token):     self.f.write(u'\n')
    
    def renderFS(self,token):       self.f.write(u'^[')
    def renderFE(self,token):       self.f.write(u']')
    def renderFR(self, token):      self.f.write(self.escape(token.value))    
    def renderFT(self, token):      self.f.write(self.escape(token.value))    
    def renderFQ(self, token):      self.f.write(self.escape(token.value))    

    def renderXS(self,token):       self.f.write(u'^[')
    def renderXE(self,token):       self.f.write(u']')
    def renderXO(self, token):      self.f.write(self.escape(token.value))
    def renderXT(self, token):      self.f.write(self.escape(token.value))
    
            