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

    def run(self, order='normal'):
        if order == 'normal':
            for bookName in books.silNames:
                self.renderBook(bookName)
        elif order == 'ntpsalms':
            for bookName in books.silNamesNTPsalms:
                self.renderBook(bookName)
            
    def renderBook(self, bookName):
        if self.booksUsfm.has_key(bookName):
            tokens = parseUsfm.parseString(self.booksUsfm[bookName])
            for t in tokens: t.renderOn(self)
            self.writeLog('     (' + bookName + ')')

    def render_periph(self, token): pass
        
    def renderID(self, token):      pass
    def renderIDE(self, token):     pass
    def renderH(self, token):       pass 

    def renderM(self, token):       pass
    def renderMT(self, token):      pass
    def renderMT1(self, token):     return self.renderMT(token)
    def renderMT2(self, token):     pass
    def renderMT3(self, token):     pass
    def renderMS(self, token):      pass
    def renderMS1(self, token):     return self.renderST(token)
    def renderMS2(self, token):     pass
    def renderMR(self, token):      pass
    def renderMI(self, token):      pass

    def renderP(self, token):       pass
    def renderSP(self, token):      pass

    def renderS(self, token):       pass
    def renderS1(self, token):      return self.renderS(token)
    def renderS2(self, token):      pass
    def renderS3(self, token):      pass

    def renderC(self, token):       pass
    def renderV(self, token):       pass

    def renderWJ(self, token):      return self.renderWJS(token)
    def renderWJS(self, token):     pass
    def renderWJE(self, token):     pass

    def renderTEXT(self, token):    pass

    def renderQ(self, token):       pass
    def renderQ1(self, token):      pass
    def renderQ2(self, token):      pass
    def renderQ3(self, token):      pass

    def renderNB(self, token):      pass
    def renderB(self, token):       pass

    def renderQT(self, token):      return self.renderQTS(token)
    def renderQTS(self, token):     pass
    def renderQTE(self, token):     pass

    def renderR(self, token):       pass

    def renderF(self, token):       return self.renderFS(token)
    def renderFS(self, token):      pass
    def renderFE(self, token):      pass
    def renderFR(self, token):      pass    
    def renderFRE(self, token):     pass    
    def renderFK(self, token):      pass    
    def renderFT(self, token):      pass    
    def renderFQ(self, token):      pass    

    # HACK!
    def renderIT(self, token):      return self.renderIS(token)
    def renderITE(self, token):     return self.renderIE(token)
    def renderIS(self, token):      pass
    def renderIE(self, token):      pass

    def renderND(self, token):      return self.renderNDS(token)
    def renderNDS(self, token):     pass
    def renderNDE(self, token):     pass

    def renderPBR(self, token):     pass
    def renderD(self, token):       pass 
    def renderREM(self, token):     pass 
    def renderPI(self, token):      pass
    def renderLI(self, token):      pass

    def renderX(self, token):       return self.renderXS(token)
    def renderXS(self, token):      pass
    def renderXE(self, token):      pass
    def renderXO(self, token):      pass
    def renderXT(self, token):      pass

    def renderXDC(self, token):     return self.renderXDCS(token)
    def renderXDCS(self, token):    pass
    def renderXDCE(self, token):    pass

    def renderTL(self, token):      return self.renderTLS(token)
    def renderTLS(self, token):     pass
    def renderTLE(self, token):     pass

    def renderADD(self, token):     return self.renderADDS(token)
    def renderADDS(self, token):    pass
    def renderADDE(self, token):    pass
    
    def render_toc1(self, token):   pass
    def render_toc2(self, token):   pass
    def render_toc3(self, token):   pass

    def render_is1(self, token):    pass
    def render_ip(self, token):     pass
    def render_iot(self, token):    pass
    def render_io1(self, token):    pass
    def render_io2(self, token):    pass

    def render_ior(self, token):    return self.render_ior_s(token)
    def render_ior_s(self, token):  pass
    def render_ior_e(self, token):  pass
    
    def render_bk(self, token):     return self.render_bk_s(token)
    def render_bk_s(self, token):   pass
    def render_bk_e(self, token):   pass

    def renderSC(self, token):      return self.renderSCS(token)
    def renderSCS(self, token):     pass
    def renderSCE(self, token):     pass

    def render_pb(self, token):     pass

    # This is unknown!
    def renderUnknown(self, token):  self.writeLog("WARNING: Unknown token '" + token.value + "'" )
