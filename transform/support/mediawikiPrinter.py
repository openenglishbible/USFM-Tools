# -*- coding: utf-8 -*-
#

import books
import parseUsfm


class DummyFile(object):
    def close(self):
        pass
    def write(self, str):
        pass

class MediaWikiPrinter(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        self.f = DummyFile()
        self.cb = ''       # Current Book
        self.cc = '001'    # Current Chapter
        self.ccUnfil = '1' # same, not padded.
        self.cv = '001'    # Currrent Verse
        self.indentFlag   = False
        self.footnoteFlag = False

    def write(self, unicodeString):
        self.f.write(unicodeString)

    def render_id(self, token):
        self.write('</p>')
        self.f.close()
        self.cb = books.bookKeyForIdValue(token.value)
        self.f = open(self.outputDir + '/c' + self.cb + '001.html', 'w')
        self.write('\n<!-- \\id ' + self.cb + ' -->')
        self.indentFlag = False
    def render_id_e(self, token):     pass
    def renderTOC2(self, token):    self.write(' Bible:' + token.value + '_# ')
    def render_h(self, token):       self.write('\n<!-- \\h ' + token.value + ' -->')
    def render_mt(self, token):      self.write('\n<!-- \\mt1 ' + token.value + ' -->')
    def render_ms(self, token):      pass
    def renderMS2(self, token):     pass
    def render_p(self, token):
        self.indentFlag = False
        self.write('\n\n')
    def render_s1(self, token):
        self.indentFlag = False
        self.write('\n=== ' + token.value + ' === ')
    def render_s2(self, token):
        self.indentFlag = False
        pass
    def render_r(self, token):       self.write('\n<span class="srefs">' + token.value + '</span>')
    def render_c(self, token):
        self.cc = token.value.zfill(3)
        self.ccUnfil = token.getValue()
        if self.cc == '001':
            self.write('Bible:' + self.cb + '_' + token.value + ' ')
        else:
            self.write('\n\n')
            self.f.close()
            self.f = open(self.outputDir + '/c' + self.cb + self.cc + '.html', 'w')
            self.write('Bible:' + self.cb + '_' + token.value + ' ')
    def render_v(self, token):
        self.cv = token.value.zfill(3)
        if not self.cv == '001': self.write('<\span>\n')
        self.write('<span id="' + self.ccUnfil + '_' + token.getValue() + '"><sup>' + token.getValue() + '</sup>')

    def render_wj_s(self, token):     pass
    def render_wj_e(self, token):     pass
    def render_text(self, token):
        if self.footnoteFlag:       self.footnoteFlag = False; self.write(' -->')
        self.write(token.getValue())
    def render_q(self, token):       self.write('\n:')
    def render_q1(self, token):      self.write('\n::')
    def render_q2(self, token):      pass
    def render_q3(self, token):      pass
    def render_nb(self, token):      pass
    def render_qt_s(self, token):     pass
    def render_qt_e(self, token):     pass
    def render_f_s(self, token):      self.write('<ref><!-- '); self.footnoteFlag = True
    def render_ft(self, token):      self.write('\\ft ' + token.getValue())
    def render_fk(self, token):      self.write('\\fk ' + token.getValue())
    def render_f_e(self, token):
        if self.footnoteFlag:       self.footnoteFlag = False; self.write(' -->')
        self.write('</ref>')
    def render_i_s(self, token):      pass
    def render_i_e(self, token):      pass
    def render_b(self, token):       pass
    def render_d(self, token):       pass
    def render_add_s(self, token):    pass
    def render_add_e(self, token):    pass
    def render_li(self, token):      self.write('\n:<!-- \li -->')
    def render_sp(self, token):      pass
    def render_nd_s(self, token):     pass
    def render_nd_e(self, token):     pass
    def render_pbr(self, token):     pass
    def render_fr(self, token):      pass
    def render_fr_e(self, token):     pass
    def render_x_s(self, token):      pass
    def render_x_e(self, token):      pass
    def render_xdc_s(self, token):    pass
    def render_xdc_e(self, token):    pass
    def render_xo(self, token):      pass
    def render_xt(self, token):      pass
    def render_m(self, token):      pass
    def render_mi(self, token):      pass
    def render_tl_s(self, token):     pass
    def render_tl_e(self, token):     pass
    def render_pi(self, token):      pass
    def render_sc_s(self, token):     pass
    def render_sc_e(self, token):     pass
    def render_d(self, token):       pass # For now    
    def render_rem(self, token):     pass # This is for comments in the USFM

class Transform(object):

    def stripUnicodeHeader(self, unicodeString):
        if unicodeString[0] == '\ufeff':
            return unicodeString[1:]
        else:
            return unicodeString

    def translateBook(self, usfm):
         tokens = parseUsfm.parseString(usfm)
         tp = MediaWikiPrinter(self.outputDir)
         for t in tokens: t.renderOn(tp)

    def setupAndRun(self, patchedDir, outputDir):
        self.outputDir = outputDir
        self.booksUsfm = books.loadBooks(patchedDir)

        for bookName in books.silNames:
            if bookName in self.booksUsfm:
                print('     ' + bookName)
                self.translateBook(self.booksUsfm[bookName])
