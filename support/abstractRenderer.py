# -*- coding: utf-8 -*-
#

import books
import parseUsfm
import logging

class AbstractRenderer(object):
    
    def __init__(self, inputDir, outputDir, outputName):
        
        # LOGGING
        self.logger = logging.getLogger('Renderer')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)    

        self.oebFlag = False
        
    def setOEBFlag(self):
        self.oebFlag = True
        
    booksUsfm = None
    
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
            self.logger.info('Rendered ' + bookName)

    def render_periph(self, token): return self.render_unhandled(token)
        
    def render_id(self, token):     pass
    def render_ide(self, token):    pass
    def render_h(self, token):      return self.render_unhandled(token) 

    def render_mt(self, token):     return self.render_mt1(token)
    def render_mt1(self, token):    return self.render_unhandled(token)
    def render_mt2(self, token):    return self.render_unhandled(token)
    def render_mt3(self, token):    return self.render_unhandled(token)

    def render_ms(self, token):      return self.render_ms1(token)
    def render_ms1(self, token):     return self.render_unhandled(token)
    def render_ms2(self, token):     return self.render_unhandled(token)
    def render_mr(self, token):      return self.render_unhandled(token)
    def render_mi(self, token):      return self.render_unhandled(token)

    def render_p(self, token):      return self.render_unhandled(token)
    def render_sp(self, token):     return self.render_unhandled(token)
    def render_m(self, token):      return self.render_unhandled(token)

    def render_s(self, token):      return self.render_s1(token)
    def render_s1(self, token):     return self.render_unhandled(token)
    def render_s2(self, token):     return self.render_unhandled(token)
    def render_s3(self, token):     return self.render_unhandled(token)

    def render_c(self, token):       return self.render_unhandled(token)
    def render_v(self, token):       return self.render_unhandled(token)

    def render_wj(self, token):      return self.render_wj_s(token)
    def render_wj_s(self, token):     return self.render_unhandled(token)
    def render_wj_e(self, token):     return self.render_unhandled(token)

    def render_text(self, token):    return self.render_unhandled(token)

    def render_q(self, token):      return self.render_q1(token)
    def render_q1(self, token):     return self.render_unhandled(token)
    def render_q2(self, token):     return self.render_unhandled(token)
    def render_q3(self, token):     return self.render_unhandled(token)

    def render_nb(self, token):      return self.render_unhandled(token)
    def render_b(self, token):       return self.render_unhandled(token)

    def render_qt(self, token):      return self.render_qt_s(token)
    def render_qt_s(self, token):     return self.render_unhandled(token)
    def render_qt_e(self, token):     return self.render_unhandled(token)

    def render_r(self, token):       return self.render_unhandled(token)

    def render_f(self, token):       return self.render_f_s(token)
    def render_f_s(self, token):      return self.render_unhandled(token)
    def render_f_e(self, token):      return self.render_unhandled(token)
    def render_fr(self, token):      return self.render_unhandled(token)    
    def render_fr_e(self, token):     return self.render_unhandled(token)    
    def render_fk(self, token):      return self.render_unhandled(token)    
    def render_ft(self, token):      return self.render_unhandled(token)    
    def render_fq(self, token):      return self.render_unhandled(token)    

    def render_it(self, token):      return self.render_it_s(token)
    def render_it_s(self, token):      return self.render_unhandled(token)
    def render_it_e(self, token):      return self.render_unhandled(token)
    def render_em(self, token):      return self.render_em_s(token)
    def render_em_s(self, token):      return self.render_unhandled(token)
    def render_em_e(self, token):      return self.render_unhandled(token)

    def render_qs(self, token):      return self.render_qs_s(token)
    def render_qs_s(self, token):      return self.render_unhandled(token)
    def render_qs_e(self, token):      return self.render_unhandled(token)

    def render_nd(self, token):       return self.render_nd_s(token)
    def render_nd_s(self, token):     return self.render_unhandled(token)
    def render_nd_e(self, token):     return self.render_unhandled(token)

    def render_pbr(self, token):     return self.render_unhandled(token)
    def render_d(self, token):       return self.render_unhandled(token) 
    def render_rem(self, token):     pass
    def render_pi(self, token):      return self.render_unhandled(token)
    def render_li(self, token):      return self.render_unhandled(token)

    def render_x(self, token):       return self.render_x_s(token)
    def render_x_s(self, token):      return self.render_unhandled(token)
    def render_x_e(self, token):      return self.render_unhandled(token)
    def render_xo(self, token):      return self.render_unhandled(token)
    def render_xt(self, token):      return self.render_unhandled(token)

    def render_xdc(self, token):     return self.render_xdc_s(token)
    def render_xdc_s(self, token):    return self.render_unhandled(token)
    def render_xdc_e(self, token):    return self.render_unhandled(token)

    def render_tl(self, token):      return self.render_tl_s(token)
    def render_tl_s(self, token):     return self.render_unhandled(token)
    def render_tl_e(self, token):     return self.render_unhandled(token)

    def render_add(self, token):     return self.render_add_s(token)
    def render_add_s(self, token):    return self.render_unhandled(token)
    def render_add_e(self, token):    return self.render_unhandled(token)
    
    def render_toc1(self, token):   return self.render_unhandled(token)
    def render_toc2(self, token):   return self.render_unhandled(token)
    def render_toc3(self, token):   return self.render_unhandled(token)

    def render_is1(self, token):    return self.render_unhandled(token)
    def render_ip(self, token):     return self.render_unhandled(token)
    def render_iot(self, token):    return self.render_unhandled(token)
    def render_io1(self, token):    return self.render_unhandled(token)
    def render_io2(self, token):    return self.render_unhandled(token)

    def render_ior(self, token):    return self.render_ior_s(token)
    def render_ior_s(self, token):  return self.render_unhandled(token)
    def render_ior_e(self, token):  return self.render_unhandled(token)
    
    def render_bk(self, token):     return self.render_bk_s(token)
    def render_bk_s(self, token):   return self.render_unhandled(token)
    def render_bk_e(self, token):   return self.render_unhandled(token)

    def render_sc(self, token):      return self.render_sc_s(token)
    def render_sc_s(self, token):     return self.render_unhandled(token)
    def render_sc_e(self, token):     return self.render_unhandled(token)

    def render_q_s(self, token):    return self.render_qs_s(token)
    def render_qs_s(self, token):  return self.render_unhandled(token)
    def render_qs_e(self, token):  return self.render_unhandled(token)

    def render_pb(self, token):     return self.render_unhandled(token)

    # This is unknown!
    def render_unknown(self, token):  self.logger.warning("Unknown token ignored: " + token.getType() + " of value '" + token.getValue() + "'" )

    # We do not handle this!
    def render_unhandled(self, token):  self.logger.warning("Unhandled token ignored: " + token.getType() + " of value '" + token.getValue() + "'" )
