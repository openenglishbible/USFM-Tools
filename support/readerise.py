# -*- coding: utf-8 -*-
#

import abstractRenderer
import codecs
import datetime
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
        self.cb = u''    # Current Book
        self.cc = u'001'    # Current Chapter
        self.cv = u'001'    # Currrent Verse
        self.indentFlag = False
        self.bookName = u''
        self.preVFlag = False
        self.waitingForFirstVerse = False
        
    def render(self, order="normal"):
        self.f = codecs.open(self.outputFilename, 'w', 'utf_8_sig')
        self.f.write((u'javascripture.data.oebusdev = {\n').encode('utf-8'))
        self.loadUSFM(self.inputDir)
        self.run(order)
        self.f.write("']]]]\n}")
        self.f.close()
        
    def escape(self, s):
        t = s.replace(u'~',u'&nbsp;').replace(u"'",u"\\'")
        t = "'], ['".join(t.split())
        return t

    def write(self, unicodeString):
        self.f.write(unicodeString.replace(u'~', u' '))
        
    def writeIndent(self, level):   pass

    def render_id(self, token): 
        i = int(books.bookKeyForIdValue(token.value)) - 1
        self.cb = books.bookNames[i]
        if self.cb == "Psalms":
            self.cb = "Psalm"
        if i > 0:
            self.write(u"']]]],\n\n")
        self.write(u"'" + self.cb + u"' : [")
    def render_h(self, token):       pass 
    def render_mt(self, token):      pass
    def render_mt2(self, token):     pass
    def renderMS(self, token):      pass
    def renderMS2(self, token):     pass
    def render_p(self, token):       pass
    def render_s1(self, token):       pass
    def render_s2(self, token):      pass
    def renderC(self, token):
        if not token.value == '1':
            self.write(u"']]],")
        self.write("\n  [")
        self.preVFlag = True
        self.waitingForFirstVerse = True
    def renderV(self, token):
        self.preVFlag = False
        if not self.waitingForFirstVerse:
            self.write(u"']], ")
        self.waitingForFirstVerse = False
        self.write("\n    [['")
    def renderWJS(self, token):     pass
    def renderWJE(self, token):     pass
    def renderTEXT(self, token):
        if not self.preVFlag and not self.waitingForFirstVerse:
            self.write(self.escape(token.value) + ' ')
    def render_q(self, token):       pass
    def render_q1(self, token):      pass
    def render_q2(self, token):      pass
    def render_q3(self, token):      pass
    def renderNB(self, token):      pass
    def renderB(self, token):       pass
    def renderIS(self, token):      pass
    def renderIE(self, token):      pass
    def render_nd_s(self, token):     pass
    def render_nd_e(self, token):     pass
    def renderPBR(self, token):     pass
    def renderSCS(self, token):     pass
    def renderSCE(self, token):     pass
    def renderFS(self, token):      pass
    def renderFE(self, token):      pass
