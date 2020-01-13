# -*- coding: utf-8 -*-
#

import codecs
import os

import abstractRenderer
import books

#
#   Renderer for Accordance - accordancebible.com
#

IN = 1
OUT = 2
JUSTOUT = 3

class Renderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputDir, outputName, config):
        self.identity = 'renderer for accordance bible software'
        self.outputDescription = os.path.join(outputDir, outputName + '.accordance.txt')
        abstractRenderer.AbstractRenderer.__init__(self, inputDir, outputDir, outputName, config)
        # Unset
        self.f = None  # output file stream
        # IO
        self.outputFilename = os.path.join(outputDir, outputName + '.accordance.txt')
        self.inputDir = inputDir
        # Flags
        self.cb = ''    # Current Book
        self.cc = '001'    # Current Chapter
        self.cv = '001'    # Currrent Verse  
        self.infootnote = False
        self.verseHadContent = True
        self.ndStatus = OUT
        self.beforeFirstVerse = True
        self.needsParagraph = True
        self.inEmphasis = False
        
    def render(self):
        self.f = open(self.outputFilename, 'w', encoding='macroman') # 'utf_8_sig macroman
        self.loadUSFM(self.inputDir)
        self.run()
        self.f.close()
        
    #   SUPPORT

    def escape(self, s):
        if self.ndStatus == IN: return s.strip()
        if self.ndStatus == JUSTOUT: self.ndStatus = OUT ; return ' ' + s if s[0].isalnum() else s
        return '' if self.infootnote else s
        
    def write(self, s):
        if not self.beforeFirstVerse:
            self.f.write(s)
            
    #   TOKENS

    def render_id(self, token): 
        self.cb = books.bookKeyForIdValue(token.value)
    def render_c(self, token):
        self.cc = token.value.zfill(3)
    def render_v(self, token):
        self.cv = token.value.zfill(3)
        if not self.verseHadContent: self.write(' ~')
        self.verseHadContent = False
        if self.cv.isdigit():
            if self.beforeFirstVerse:
                # No \n on first line
                self.beforeFirstVerse = False
            else:
                self.f.write('\n')
            self.f.write(books.accordanceNameForBookKey(self.cb) + ' ' + str(int(self.cc)) + ':' + str(int(self.cv.split('-')[0])) + ' ') # str(int(self.cb))
        else:
            # This shouldn't happen in release, but will happen in development
            # eg \v 23a
            self.logger.warning('Ignoring ' + books.accordanceNameForBookKey(self.cb) + ' ' + str(int(self.cc)) + ':' + self.cv)
        if self.needsParagraph:
            self.needsParagraph = False
            self.write(' ¶ ')
    def render_text(self, token):
        self.verseHadContent = True
        if self.inEmphasis:
            self.write('<i>')
        self.write(self.escape(token.value + ' '))
        if self.inEmphasis:
            self.write('</i>')
    def render_f_s(self, token):     self.write('<sup>[')
    def render_f_e(self, token):     self.write(']</sup>')
    def render_p(self, token):       self.needsParagraph = True
    def render_pi(self, token):      self.needsParagraph = True
    def render_m(self, token):       self.needsParagraph = True
    def render_nb(self, token):      self.needsParagraph = True
    def render_nd_s(self,token):     self.ndStatus = IN; self.write('<c>')
    def render_nd_e(self,token):     self.ndStatus = JUSTOUT; self.write('</c>')
    def render_q1(self, token):      self.write('<br>\t')
    def render_q2(self, token):      self.write('<br>\t\t') 
    def render_q3(self, token):      self.write('<br>\t\t\t') 
    def render_b(self, token):       self.write('<br>') 
    def render_qs_s(self, token):    self.inEmphasis = True
    def render_qs_e(self, token):    self.inEmphasis = False
    def render_em_s(self, token):    self.inEmphasis = True 
    def render_em_e(self, token):    self.inEmphasis = False
    
    def render_d(self, token):
        """ Accordance """
        # Accordance requries Psalms to have :0 verse
        if books.accordanceNameForBookKey(self.cb) == 'Psa':
            self.f.write(                         '\n' +
                                                  books.accordanceNameForBookKey(self.cb) +
                                                    ' ' +
                                                  str(int(self.cc)) +
                                            ':0 ¶ <i>' +
                                                  token.value +
                                                ' </i>')
    
    # Ignored
    def render_h(self, token):      pass
    def render_mt(self, token):     pass
    def render_mt2(self, token):    pass
    def render_ms(self, token):     pass
    def render_ms2(self, token):    pass
    def render_s(self, token):      pass
    def render_s2(self, token):     pass
    def render_wj_s(self, token):   pass
    def render_wj_e(self, token):   pass
