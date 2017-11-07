# -*- coding: utf-8 -*-
#

import codecs
import io
import os
import textwrap

import abstractRenderer


#
#   Simplest renderer. Ignores everything except ascii text.
#

class Renderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputDir, outputName, config):
        abstractRenderer.AbstractRenderer.__init__(self, inputDir, outputDir, outputName, config)
        # Unset
        self.f = None  # output file stream
        # IO
        self.outputFilename = os.path.join(outputDir, outputName + '.txt')
        self.inputDir = inputDir
        # Flags
        self.d = False
        self.narrower = False
        self.inFootnote = False
        self.inX = False
        self.inND = False
        
    def render(self):
        self.f = io.StringIO()
        self.loadUSFM(self.inputDir)
        self.run()
        v = self.f.getvalue()
        self.f.close()
        if self.config.get('Plain Text','encoding') == 'ascii':
            self.logger.info('Converting to ascii')
            v = self.clean(v)
        if self.config.get('Plain Text','wrap'):
            self.logger.info('Wrapping')
            v = self.wrap(v)
        o = codecs.open(self.outputFilename, 'w', self.config.get('Plain Text','encoding'))
        o.write(v)
        o.close()
        
    # Support
    
    def wrap(self, t):
        nl = ''
        for i in t.split('\n'):
            nl = nl + textwrap.fill(i, width=80) + '\n'
        return nl
        
    def clean(self, text):
        t = text.replace('‘', "'")
        t = t.replace('’', "'")
        t = t.replace('“', '"')
        t = t.replace('”', '"')
        t = t.replace('—', '--')
        t = t.encode('ascii', 'ignore')
        return t
    
    def startNarrower(self, n):
        s = '\n'
        if not self.narrower: s = s + '\n'
        self.narrower = True
        return s + '    ' * n

    def stopNarrower(self):
        self.narrower = False
        return ''

    def startD(self):
        self.d = True
        return ''

    def stopD(self):
        self.d = False
        return ''
        
    def escape(self, text):
        t = text
        if self.inX or self.inFootnote:
            return ''
        t = t.upper() if self.inND else t
        return t
        
    def box(self, text):
        t = (80 * '#') + '\n'
        t = t + '#' + (78 * ' ') + '#\n'
        t = t + '#' + (((78 - int(len(text)) / 2) * ' ')) + text + (((78 - int(len(text))) / 2) * ' ') + '#\n'
        t = t + '#' + (78 * ' ') + '#\n'
        t = t + (80 * '#') + '\n'
        return t
        
    def center(self, text):
        return (((80 - int(len(text))) / 2) * ' ') + text + (((80 - int(len(text))) / 2) * ' ')
        
    # Tokens
                    
    def render_h(self, token):       self.f.write('\n\n\n' + self.box(token.value) + '\n\n')

    def render_mt1(self, token):     self.f.write(self.center(token.value.upper()) + '\n')
    def render_mt2(self, token):     self.f.write(self.center(token.value.upper()) + '\n')
    def render_mt3(self, token):     self.f.write(self.center(token.value.upper()) + '\n')

    def render_ms1(self, token):     self.f.write('\n\n' + self.center('[' + token.value + ']') + '\n\n')
    def render_ms2(self, token):     self.f.write('\n\n' + self.center('[' + token.value + ']') + '\n\n')

    def render_m(self, token):       self.f.write(self.stopD() + self.stopNarrower() + '\n')
    def render_p(self, token):       self.f.write(self.stopD() + self.stopNarrower() + '\n    ')
    def render_b(self, token):       self.f.write(self.stopD() + self.stopNarrower() + '\n    ')

    def render_s1(self, token):      self.f.write(self.stopD() + self.stopNarrower() + '\n\n*' + token.value + '*\n    ')
    def render_s2(self, token):      self.f.write(self.stopD() + self.stopNarrower() + '\n\n*' + token.value + '*\n    ')

    def render_c(self, token):       self.f.write(' ' )
    def render_v(self, token):       self.f.write(' ' )
    def render_text(self, token):    self.f.write(self.escape(token.value))
    def render_q(self, token):       self.f.write(self.stopD() + self.startNarrower(1))
    def render_q1(self, token):      self.f.write(self.stopD() + self.startNarrower(1))
    def render_q2(self, token):      self.f.write(self.stopD() + self.startNarrower(2))
    def render_q3(self, token):      self.f.write(self.stopD() + self.startNarrower(3))
    def render_nb(self, token):      self.f.write(self.stopD() + self.stopNarrower() + "\n\n")
    def render_li(self, token):      self.f.write(' ')
    def render_d(self, token):       self.f.write(self.startD())
    def render_sp(self, token):      self.f.write(self.startD())
    def render_nd_e(self, token):     self.f.write(' ')
    def render_pbr(self, token):     self.f.write('\n')
    
    def render_nd_s(self, token):      self.inND = True
    def render_nd_e(self, token):      self.inND = False
    
    
    # Ignore...
    def render_x_s(self,token):       self.inX = True
    def render_x_e(self,token):       self.inX = False
    def render_f_s(self,token):       self.inFootnote = True
    def render_f_e(self,token):       self.inFootnote = False
    
    # Irrelevant
    def render_pb(self,token):       pass
    def render_wj_s(self,token):     pass
    def render_wj_e(self,token):     pass
           