# -*- coding: utf-8 -*-
#

import books
import parseUsfm

class AbstractRenderer(object):

    booksUsfm = None
    
    def writeLog(self, s):
        pass
        
    def loadUSFM(self, usfmDir):
        self.booksUsfm = books.loadBooks(usfmDir)

    def run(self):
        for bookName in books.silNames:
            if self.booksUsfm.has_key(bookName):
                tokens = parseUsfm.parseString(self.booksUsfm[bookName])
                for t in tokens: t.renderOn(self)
                self.writeLog('     (' + bookName + ')')
        
    def renderID(self, token):      pass
    def renderIDE(self, token):     pass
    def renderH(self, token):       pass 

    def renderM(self, token):       pass
    def renderMT(self, token):      pass
    def renderMT2(self, token):     pass
    def renderMS(self, token):      pass
    def renderMS2(self, token):     pass
    def renderMR(self, token):      pass

    def renderP(self, token):       pass

    def renderS(self, token):       pass
    def renderS2(self, token):      pass
    def renderS3(self, token):      pass

    def renderC(self, token):       pass
    def renderV(self, token):       pass

    def renderWJS(self, token):     pass
    def renderWJE(self, token):     pass

    def renderTEXT(self, token):    pass

    def renderQ(self, token):       pass
    def renderQ1(self, token):      pass
    def renderQ2(self, token):      pass
    def renderQ3(self, token):      pass

    def renderNB(self, token):      pass
    def renderB(self, token):       pass
    def renderQTS(self, token):     pass
    def renderQTE(self, token):     pass
    def renderR(self, token):       pass

    def renderFS(self, token):      pass
    def renderFE(self, token):      pass
    def renderFR(self, token):      pass    
    def renderFT(self, token):      pass    
    def renderFQ(self, token):      pass    

    def renderIS(self, token):      pass
    def renderIE(self, token):      pass

    def renderNDS(self, token):     pass
    def renderNDE(self, token):     pass
    def renderPBR(self, token):     pass
    def renderD(self, token):       pass 
    def renderREM(self, token):     pass 
    def renderPI(self, token):      pass
    def renderLI(self, token):      pass

    def renderXS(self, token):      pass
    def renderXE(self, token):      pass
    def renderXO(self, token):      pass
    def renderXT(self, token):      pass

    def render_toc1(self, token):   pass
    def render_toc2(self, token):   pass
    def render_toc3(self, token):   pass

    def render_is1(self, token):    pass
    def render_ip(self, token):     pass
    def render_iot(self, token):    pass
    def render_io1(self, token):    pass
    def render_io2(self, token):    pass
    def render_ior_s(self, token):  pass
    def render_ior_e(self, token):  pass
    
    def render_bk_s(self, token):   pass
    def render_bk_e(self, token):   pass
