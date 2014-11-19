# -*- coding: utf-8 -*-
#

import abstractRenderer
import codecs
import StringIO

IN = 1
OUT = 2
JUSTOUT = 3

#
#   Simplest renderer. Ignores everything except ascii text.
#

class MarkdownRenderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputFilename):
        # Data
        self.stringStream = StringIO.StringIO()
        self.rendered = u''
        # IO
        self.outputFilename = outputFilename
        self.inputDir = inputDir
        # Position
        self.currentC = 1
        self.book = u''
        # Flags
        self.ndStatus = OUT
        self.qStatus = OUT
        
    def render(self, order="normal"):
        self.loadUSFM(self.inputDir)
        self.run(order)
        self.rendered = self.stringStream.getvalue()
        self.adjustRendered()
        f = codecs.open(self.outputFilename, 'w', 'utf_8_sig')
        self.writeHeader()
        f.write(self.rendered)
        f.close()
        
    def writeLog(self, s):
        print s
        
    def write(self, s):
        self.stringStream.write(s)
        
    def adjustRendered(self):
        self.rendered = self.rendered.replace(u'\n\n\n\n', u'\n\n')
        self.rendered = self.rendered.replace(u'\n\n\n', u'\n\n')
        self.rendered = self.rendered.replace(u'##### ~ #####', u'')
        self.rendered = self.rendered.replace(u'LORD ,', u'LORD,')
        self.rendered = self.rendered.replace(u'LORD \'', u'LORD\'')
    
    def writeHeader(self):
        self.rendered = self.rendered + ur'% Open English Bible\n\n'
        
    # Support    
        
    def escape(self, s):
        if self.ndStatus == IN: return s.upper()
        if self.ndStatus == JUSTOUT: self.ndStatus = OUT ; return ' ' + s if not s[0] == "'" else s
        return s
                    
    def renderTEXT(self, token):    self.write(self.escape(token.value))

    def renderH(self, token):       self.book = token.getValue() ; self.write(u'\n\n\n\n')
    def renderMT(self, token):      self.write(u'\n\n' + token.value + u'\n' + (u'=' * len(token.value)) + u'\n')
    def renderMT2(self, token):     self.write(u'\n\n' + token.value + u'\n' + (u'-' * len(token.value)) + u'\n')
    def renderMS(self, token):      self.write(u'\n\n### ' + token.value + u' ###\n')
    def renderMS2(self, token):     self.write(u'\n\n#### ' + token.value + u' ####\n')
    def renderS(self, token):       self.qStatus = OUT ; self.write(u'\n\n##### ' + token.value + u' #####\n\n')
    def renderS2(self, token):      self.qStatus = OUT ; self.write(u'\n\n###### ' + token.value + u' ######\n\n')
    def renderP(self, token):       self.qStatus = OUT ; self.write(u'\n\n')
    def renderB(self, token):       self.write(u'\n\n')
    def renderC(self, token):       self.currentC = token.value; self.write(u'\n\n [' + self.book + u' ' + self.currentC + u'] \n\n')
    def renderV(self, token):       self.write(u' [' + self.currentC + u':' + token.value + u'] ')
    def renderQ(self, token):
        if self.qStatus == OUT: 
            self.write(u'\n\n')
            self.qStatus = IN
        self.write(u'\n|  ') 
    def renderQ1(self, token):      self.renderQ(token) 
    def renderQ2(self, token):      self.write(u'\n|    ') 
    def renderQ3(self, token):      self.write(u'\n|      ') 
    def renderNB(self, token):      self.write(u'\n|  ') 
    def renderLI(self, token):      self.write(u'* ')
    def renderPBR(self, token):     self.write(u'\n')
    
    def renderFS(self,token):       self.write(u'^[')
    def renderFE(self,token):       self.write(u']')
    def renderFR(self, token):      self.write(self.escape(token.value))    
    def renderFT(self, token):      self.write(self.escape(token.value))    
    def renderFQ(self, token):      self.write(self.escape(token.value))    

    def renderWJS(self,token):       self.write(u' ')
    def renderWJE(self,token):       self.write(u' ')

    def renderXS(self,token):       self.write(u'^[')
    def renderXE(self,token):       self.write(u']')
    def renderXO(self, token):      self.write(self.escape(token.value))
    def renderXT(self, token):      self.write(self.escape(token.value))
    
    def renderNDS(self,token):      self.ndStatus = IN
    def renderNDE(self,token):      self.ndStatus = JUSTOUT
            