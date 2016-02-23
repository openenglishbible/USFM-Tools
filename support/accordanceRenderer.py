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
    
    def __init__(self, inputDir, outputDir, outputName, config):
        abstractRenderer.AbstractRenderer.__init__(self, inputDir, outputDir, outputName, config)
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
        self.inD = False
        
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
    def render_c(self, token):
        self.cc = token.value.zfill(3)
    def render_v(self, token):
        self.cv = token.value.zfill(3)
        if not self.verseHadContent: self.write(u' ~')
        self.verseHadContent = False
        if self.atStart:
            self.atStart = False
        else:
            self.f.write(u'\n')
        self.f.write(books.accordanceNameForBookKey(self.cb) + ' ' + str(int(self.cc)) + ':' + str(int(self.cv.split('-')[0]))   + ' ') # str(int(self.cb))
    def render_text(self, token):
        self.verseHadContent = True
        self.write(self.escape(token.value + ' '))
        if self.inD:
            self.inD = False
            self.write('</i>')
    def render_f_s(self, token):     self.write(u'<sup>[')
    def render_f_e(self, token):     self.write(u']</sup>')
    def render_p(self, token):       self.write(u' ¶ ')
    def render_pi(self, token):      self.write(u' ¶ ')
    def render_m(self, token):       self.write(u' ¶ ')
    def render_nb(self, token):      self.write(u' ¶ ')
    def render_nd_s(self,token):     self.ndStatus = IN; self.write(u'<c>')
    def render_nd_e(self,token):     self.ndStatus = JUSTOUT; self.write(u'</c>')
    def render_q1(self, token):      self.write(u'<br>\t')
    def render_q2(self, token):      self.write(u'<br>\t\t') 
    def render_q3(self, token):      self.write(u'<br>\t\t\t') 
    def render_b(self, token):       self.write(u'<br>') 
    def render_qs_s(self, token):    self.write(u'<i>') 
    def render_qs_e(self, token):    self.write(u'</i>') 
    def render_em_s(self, token):    self.write(u'<i>') 
    def render_em_e(self, token):    self.write(u'</i>') 
    
    def render_d(self, token):
        """ Accordance """
        self.inD = True
        # Accordance requries Psalms to have :0 verse
        if books.accordanceNameForBookKey(self.cb) == 'Psa':
            self.f.write(                         u'\n' +
                books.accordanceNameForBookKey(self.cb) + 
                                                    ' ' + 
                                      str(int(self.cc)) + 
                                            u':0 ¶ <i>' )
    
    # Ignored
    def render_h(self, token):      pass
    def render_mt(self, token):     pass
    def render_mt2(self, token):    pass
    def render_ms(self, token):     pass
    def render_ms2(self, token):    pass
    def render_s(self, token):      pass
    def render_wj_s(self, token):   pass
    def render_wj_e(self, token):   pass
