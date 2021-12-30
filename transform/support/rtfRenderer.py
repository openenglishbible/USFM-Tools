# -*- coding: utf-8 -*-
#

import codecs
import os
import string

import abstractRenderer

#
#   Simplest renderer. Ignores everything except ascii text.
#
STANDARD_SUFFIX = '.rtf'

class Renderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputDir, outputName, config):
        self.identity = 'rtf renderer'
        self.outputDescription = os.path.join(outputDir, outputName + '.rtf')
        abstractRenderer.AbstractRenderer.__init__(self, inputDir, outputDir, outputName, config)
        # Unset
        self.f = None  # output file stream
        # IO
        self.outputFilename = os.path.join(outputDir, outputName + STANDARD_SUFFIX)
        self.inputDir = inputDir
        # Position
        self.in_p = False
        self.needsEnd = False
        self.h = ''
        self.cv = ''
        self.cc =  ''
        
    def render(self, order="normal"):
        self.f = open(self.outputFilename, 'w', encoding='cp1252') # ie ansi
        self.f.write(r"""{\rtf1\ansi\ansicpg1252\deff0 
{\fonttbl{
\f0\froman Georgia;
\f1\fswiss Verdana;
}}\fs24 
{\colortbl
;
\red255\green0\blue0;
\red0\green0\blue255;
\red255\green255\blue255;
\red0\green0\blue0;
}
\hyphauto\ftnbj
""")
        self.loadUSFM(self.inputDir)
        self.run(order)
        self.end_par()
        self.f.write('\n}')
        self.f.close()
        
    def clean(self, unicodeString):
        u = unicodeString.replace('~', r' ')
        n = []
        for c in u:
            if ord(c) > 127:
                n.append('\\uc1\\u' + str(ord(c)) + '*')
            else:
                n.append(c)
        u = ''.join(n)
        u = u.replace('\n', "\r\n")
        return u
        
    def write(self, unicodeString):
        self.f.write(self.clean(unicodeString))
        
    #
    #   END PAR
    #
    def end_par(self):
        if self.needsEnd:
            self.write('\n\\par}\n')
        self.needsEnd = True
                    
    def set_header(self):
        self.write('\sectd\sect{\\header \\pard\\qr\\plain\\f0\\fs16 ' + self.h + ' (Page \\chpgn) \\par}')
        

    #
    #   CORE
    #
    
    # Book makes new page
    def render_h(self, token):
        self.h = token.getValue()
        self.end_par()
        self.set_header()
        self.write('{\\pard \\pagebb')
    
    def render_heading_template(self, token, size, italic=False):
        self.end_par()
        self.write('\n{\\pard\\sb360\\sa360\\fs' + str(size) + ' ')
        self.write('{\\i ' + token.getValue() + '}') if italic else self.write(token.getValue())
        self.write('\n')
        self.in_p = False
    def render_mt1(self, token):   self.render_heading_template(token, 72)
    def render_mt2(self, token):   self.render_heading_template(token, 56)
    def render_ms1(self, token):   self.render_heading_template(token, 44)
    def render_ms2(self, token):   self.render_heading_template(token, 36)
    def render_s1(self, token):    self.render_heading_template(token, 32)
    def render_s2(self, token):    self.render_heading_template(token, 24, italic=True)
        

    # Chapter and verse markers are a little different. We don't want them where they
    # are marked but at the start of the relevant text.
    # However, they act as whitespace so we need to allow for that.
    # (removed self.write(' '); )
    def render_c(self, token):  self.cc = token.getValue()
    def render_v(self, token):  self.cv = token.getValue()
        
    def render_p(self, token):
        self.end_par()
        if not self.in_p:
            self.write('\n{\\pard\n\\par}')
        self.write('\n{\\pard\sl280\slmult1\\fs24')  
        if self.in_p:
            self.write('\\fi360')
        self.write(' \n')
        self.in_p = True      
    def render_pi(self, token):
        self.end_par()
        if not self.in_p:
            self.write('\n{\\pard\n\\par}\n')
        self.write('\n{\\pard\sl280\slmult1\\fs24\\fi0\\li360') 
        if self.in_p:
            self.write('\\fi360')
        self.in_p = True       
    def render_m(self, token):
        self.end_par()
        if not self.in_p:
            self.write('\n{\\pard\n\\par}')
        self.write('\n{\\pard\sl280\slmult1\\fs24\\fi0 \n') 
        self.in_p = True       
    
    def render_q_template(self, level, token):
        self.end_par()
        if self.in_p:
            self.write('\n{\\pard\n\\par}\n')
        self.write('\n{\\pard\sl280\slmult1\\fs24\\fi' + str((360 * level) - 2800) + '\\li2800\n')
        self.in_p = False
    def render_q1(self, token):      self.render_q_template(1, token)
    def render_q2(self, token):      self.render_q_template(2, token)
    def render_q3(self, token):      self.render_q_template(3, token)
        
    def render_f_s(self, token):     self.write(r'{\super\chftn}{\footnote\pard\plain\chftn ')
    def render_f_e(self, token):     self.write(r' }')
    def render_x_s(self, token):     self.write(r'{\super\chftn}{\footnote\pard\plain\chftn ')
    def render_x_e(self, token):     self.write(r' }')
    
    def render_nd_s(self, token):     self.write(r'{\scaps ')
    def render_nd_e(self, token):     self.write(r'}')
    
    def render_b(self, token):        self.end_par() ; self.write('\n{\\pard \n')
    
    def render_em_s(self, token):     self.write('{\i ')
    def render_em_e(self, token):     self.write('}')
        
    def render_d(self, token):        self.render_m(token) ; self.write('{\i ' + token.getValue() + '}')

    # Que selah selah
    def render_qs_s(self, token):     self.write('{\i ')
    def render_qs_e(self, token):     self.write('}')

    # Words of Jesus - ignore or mark
    def render_wj_s(self, token):     pass
    def render_wj_e(self, token):     pass

    def render_text(self, token):
        if not self.cc == '':
            self.write(r'{\cf1\f1\fs22 ' + self.cc + r'}')
            self.cc = ''
        elif not self.cv == '' and not self.cv == '1':
            # elif because when we have a chapter number to write we don't need a verse number
            self.write(r'{\super\f1\cf2\fs24 ' + self.cv + r'}')
            self.cv = ''
        self.write(token.getValue())
