# -*- coding: utf-8 -*-
#

import abstractRenderer
import codecs
import StringIO
import os

IN = 1
OUT = 2
JUSTOUT = 3

#
#   Simplest renderer. Ignores everything except ascii text.
#

class Renderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputDir, outputName, config):
        abstractRenderer.AbstractRenderer.__init__(self, inputDir, outputDir, outputName, config)
        # Data
        self.stringStream = StringIO.StringIO()
        self.rendered = u''
        # IO
        self.outputFilename = os.path.join(outputDir, outputName + '.md')
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
                    
    def render_text(self, token):    self.write(self.escape(token.value))

    def render_h(self, token):       self.book = token.getValue() ; self.write(u'\n\n\n\n')
    def render_mt(self, token):      self.write(u'\n\n' + token.value + u'\n' + (u'=' * len(token.value)) + u'\n')
    def render_mt2(self, token):     self.write(u'\n\n' + token.value + u'\n' + (u'-' * len(token.value)) + u'\n')
    def render_ms(self, token):      self.write(u'\n\n### ' + token.value + u' ###\n')
    def renderMS2(self, token):     self.write(u'\n\n#### ' + token.value + u' ####\n')
    def render_s1(self, token):       self.qStatus = OUT ; self.write(u'\n\n##### ' + token.value + u' #####\n\n')
    def render_s2(self, token):      self.qStatus = OUT ; self.write(u'\n\n###### ' + token.value + u' ######\n\n')
    def render_p(self, token):       self.qStatus = OUT ; self.write(u'\n\n')
    def render_b(self, token):       self.write(u'\n\n')
    def render_c(self, token):       self.currentC = token.value; self.write(u'\n\n [' + self.book + u' ' + self.currentC + u'] \n\n')
    def render_v(self, token):       self.write(u' [' + self.currentC + u':' + token.value + u'] ')
    def render_q(self, token):
        if self.qStatus == OUT: 
            self.write(u'\n\n')
            self.qStatus = IN
        self.write(u'\n|  ') 
    def render_q1(self, token):      self.render_q(token) 
    def render_q2(self, token):      self.write(u'\n|    ') 
    def render_q3(self, token):      self.write(u'\n|      ') 
    def render_nb(self, token):      self.write(u'\n|  ') 
    def render_li(self, token):      self.write(u'* ')
    def render_pbr(self, token):     self.write(u'\n')
    
    def render_f_s(self,token):       self.write(u'^[')
    def render_f_e(self,token):       self.write(u']')
    def render_fr(self, token):      self.write(self.escape(token.value))    
    def render_ft(self, token):      self.write(self.escape(token.value))    
    def render_fq(self, token):      self.write(self.escape(token.value))    

    def render_wj_s(self,token):       self.write(u' ')
    def render_wj_e(self,token):       self.write(u' ')

    def render_x_s(self,token):       self.write(u'^[')
    def render_x_e(self,token):       self.write(u']')
    def render_xo(self, token):      self.write(self.escape(token.value))
    def render_xt(self, token):      self.write(self.escape(token.value))
    
    def render_nd_s(self,token):      self.ndStatus = IN
    def render_nd_e(self,token):      self.ndStatus = JUSTOUT
            