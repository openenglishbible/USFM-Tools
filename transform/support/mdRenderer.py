# -*- coding: utf-8 -*-
#

import codecs
import io
import os

import abstractRenderer

IN = 1
OUT = 2
JUSTOUT = 3

#
#   Markdown renderer. Renders markdown in UTF8
#

class Renderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputDir, outputName, config):
        self.identity = 'markdown renderer'
        self.outputDescription = os.path.join(outputDir, outputName + '.md')
        abstractRenderer.AbstractRenderer.__init__(self, inputDir, outputDir, outputName, config)
        # Data
        self.stringStream = io.StringIO()
        self.rendered = ''
        # IO
        self.outputFilename = os.path.join(outputDir, outputName + '.md')
        self.inputDir = inputDir
        # Position
        self.currentC = '1'
        self.book = ''
        # Flags
        self.ndStatus = OUT
        self.qStatus = OUT
        
    def render(self, order="normal"):
        self.loadUSFM(self.inputDir)
        self.run(order)
        self.rendered = self.stringStream.getvalue()
        self.adjustRendered()
        f = open(self.outputFilename, 'w')
        self.writeHeader()
        f.write(self.rendered)
        f.close()
        
    def write(self, s):
        self.stringStream.write(s)
        
    def adjustRendered(self):
        self.rendered = self.rendered.replace('\n\n\n\n', '\n\n')
        self.rendered = self.rendered.replace('\n\n\n', '\n\n')
        self.rendered = self.rendered.replace('##### ~ #####', '')
        self.rendered = self.rendered.replace('LORD ,', 'LORD,')
        self.rendered = self.rendered.replace('LORD \'', 'LORD\'')
    
    def writeHeader(self):
        self.rendered = self.rendered + r'% ' + self.config.get('General', 'name') + '\n\n'
        
    # Support    
        
    def escape(self, s):
        if self.ndStatus == IN: return s.upper()
        if self.ndStatus == JUSTOUT: self.ndStatus = OUT ; return ' ' + s if not s[0] == "'" else s
        return s
                    
    def render_text(self, token):    self.write(self.escape(token.value))

    def render_h(self, token):       self.book = token.getValue() ; self.write('\n\n\n\n')
    def render_mt1(self, token):     self.write('\n\n' + token.value + '\n' + ('=' * len(token.value)) + '\n')
    def render_mt2(self, token):     self.write('\n\n' + token.value + '\n' + ('-' * len(token.value)) + '\n')
    def render_mt3(self, token):     self.write('\n\n### ' + token.value + ' ###\n')
    def render_ms(self, token):      self.write('\n\n### ' + token.value + ' ###\n')
    def render_ms2(self, token):     self.write('\n\n#### ' + token.value + ' ####\n')
    def render_s1(self, token):      self.qStatus = OUT ; self.write('\n\n##### ' + token.value + ' #####\n\n')
    def render_s2(self, token):      self.qStatus = OUT ; self.write('\n\n###### ' + token.value + ' ######\n\n')
    def render_p(self, token):       self.qStatus = OUT ; self.write('\n\n')
    def render_pi(self, token):      self.qStatus = OUT ; self.write('\n\n  ')
    def render_m(self, token):       self.qStatus = OUT; self.write('\n\n')
    def render_b(self, token):       self.write('\n\n')
    def render_c(self, token):       self.currentC = token.value; self.write('\n\n[' + self.book + ' ' + self.currentC + ']\n\n')
    def render_v(self, token):       self.write(' [' + self.currentC + ':' + token.value + '] ')
    def render_q(self, token):
        if self.qStatus == OUT: 
            self.write('\n\n')
            self.qStatus = IN
        self.write('\n|  ') 
    def render_q1(self, token):      self.render_q(token) 
    def render_q2(self, token):      self.write('\n|    ') 
    def render_q3(self, token):      self.write('\n|      ') 
    def render_nb(self, token):      self.write('\n|  ') 
    def render_li(self, token):      self.write('* ')
    def render_pbr(self, token):     self.write('\n')
    
    def render_f_s(self,token):       self.write('^[')
    def render_f_e(self,token):       self.write(']')
    def render_fr(self, token):      self.write(self.escape(token.value))    
    def render_ft(self, token):      self.write(self.escape(token.value))    
    def render_fq(self, token):      self.write(self.escape(token.value))    

    def render_wj_s(self,token):       self.write(' ')
    def render_wj_e(self,token):       self.write(' ')

    def render_x_s(self,token):       self.write('^[')
    def render_x_e(self,token):       self.write(']')
    def render_xo(self, token):      self.write(self.escape(token.value))
    def render_xt(self, token):      self.write(self.escape(token.value))
    
    def render_nd_s(self,token):      self.ndStatus = IN
    def render_nd_e(self,token):      self.ndStatus = JUSTOUT

    def render_em_s(self, token):     self.write('*')
    def render_em_e(self, token):     self.write('*')

    def render_d(self, token):        self.write('\n' + token.value + '\n')

    def render_qs_s(self, token):     self.write('*')
    def render_qs_e(self, token):     self.write('*')

    def render_periph(self, token):   pass
    def render_pb(self, token):       pass
