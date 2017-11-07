# -*- coding: utf-8 -*-
#

import codecs

import abstractRenderer
import books


#
#   Simplest renderer. Ignores everything except ascii text.
#

class ReaderRenderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputFilename):
        # Unset
        self.f = None  # output file stream
        # IO
        self.outputFilename = outputFilename
        self.inputDir = inputDir
        # Position
        self.cb = ''    # Current Book
        self.cc = '001'    # Current Chapter
        self.cv = '001'    # Currrent Verse
        self.indentFlag = False
        self.bookName = ''
        self.preVFlag = False
        self.waitingForFirstVerse = False
        
    def render(self, order="normal"):
        self.f = open(self.outputFilename, 'w')
        self.f.write(('javascripture.data.oebusdev = {\n'))
        self.loadUSFM(self.inputDir)
        self.run(order)
        self.f.write("']]]]\n}")
        self.f.close()
        
    def escape(self, s):
        t = s.replace('~','&nbsp;').replace("'","\\'")
        t = "'], ['".join(t.split())
        return t

    def write(self, unicodeString):
        self.f.write(unicodeString.replace('~', ' '))
        
    def writeIndent(self, level):   pass

    def render_id(self, token): 
        i = int(books.bookKeyForIdValue(token.value)) - 1
        self.cb = books.bookNames[i]
        if self.cb == "Psalms":
            self.cb = "Psalm"
        if i > 0:
            self.write("']]]],\n\n")
        self.write("'" + self.cb + "' : [")
    def render_h(self, token):       pass 
    def render_mt(self, token):      pass
    def render_mt2(self, token):     pass
    def render_ms(self, token):      pass
    def renderMS2(self, token):     pass
    def render_p(self, token):       pass
    def render_s1(self, token):       pass
    def render_s2(self, token):      pass
    def render_c(self, token):
        if not token.value == '1':
            self.write("']]],")
        self.write("\n  [")
        self.preVFlag = True
        self.waitingForFirstVerse = True
    def render_v(self, token):
        self.preVFlag = False
        if not self.waitingForFirstVerse:
            self.write("']], ")
        self.waitingForFirstVerse = False
        self.write("\n    [['")
    def render_wj_s(self, token):     pass
    def render_wj_e(self, token):     pass
    def render_text(self, token):
        if not self.preVFlag and not self.waitingForFirstVerse:
            self.write(self.escape(token.value) + ' ')
    def render_q(self, token):       pass
    def render_q1(self, token):      pass
    def render_q2(self, token):      pass
    def render_q3(self, token):      pass
    def render_nb(self, token):      pass
    def render_b(self, token):       pass
    def render_i_s(self, token):      pass
    def render_i_e(self, token):      pass
    def render_nd_s(self, token):     pass
    def render_nd_e(self, token):     pass
    def render_pbr(self, token):     pass
    def render_sc_s(self, token):     pass
    def render_sc_e(self, token):     pass
    def render_f_s(self, token):      pass
    def render_f_e(self, token):      pass
