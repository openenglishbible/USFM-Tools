# -*- coding: utf-8 -*-
#

import sys

from pyparsing import Word, alphas, OneOrMore, nums, Literal, White, Group, Suppress, Empty, NoMatch, Optional, CharsNotIn, unicodeString

def usfmToken(key):
    return Group(Suppress(backslash) + Literal( key ) + Suppress(White()))
def usfmBackslashToken(key):
    return Group(Literal(key))
def usfmEndToken(key): 
    return Group(Suppress(backslash) + Literal( key +  u"*"))
def usfmTokenValue(key, value): 
    return Group(Suppress(backslash) + Literal( key ) + Suppress(White()) + Optional(value) )
def usfmTokenNumber(key): 
    return Group(Suppress(backslash) + Literal( key ) + Suppress(White()) + Word (nums + '-()') + Suppress(White()))


# define grammar
#phrase      = Word( alphas + u"-.,!? —–‘“”’;:()'\"[]/&%=*…{}" + nums )
phrase      = CharsNotIn( u"\n\\+"  )
backslash   = Literal(u"\\")
plus        = Literal(u"+")

textBlock   = Group(Optional(NoMatch(), u"text") + phrase )

id      = usfmTokenValue( u"id", phrase )
ide     = usfmTokenValue( u"ide", phrase )
h       = usfmTokenValue( u"h", phrase )
mt      = usfmTokenValue( u"mt", phrase )
mt1     = usfmTokenValue( u"mt1", phrase )
mt2     = usfmTokenValue( u"mt2", phrase )
mt3     = usfmTokenValue( u"mt3", phrase )
ms      = usfmTokenValue( u"ms", phrase )
ms1     = usfmTokenValue( u"ms1", phrase )
ms2     = usfmTokenValue( u"ms2", phrase )
mr      = usfmTokenValue( u"mr", phrase )
s       = usfmTokenValue( u"s", phrase )
s1      = usfmTokenValue( u"s1", phrase )
s2      = usfmTokenValue( u"s2", phrase )
s3      = usfmTokenValue( u"s3", phrase )
r       = usfmTokenValue( u"r", phrase )
p       = usfmToken(u"p")
pi      = usfmToken(u"pi")
b       = usfmToken(u"b")
c       = usfmTokenNumber(u"c")
v       = usfmTokenNumber(u"v")
wjs     = usfmToken(u"wj")
wje     = usfmEndToken(u"wj")
q       = usfmToken(u"q")
q1      = usfmToken(u"q1")
q2      = usfmToken(u"q2")
q3      = usfmToken(u"q3")
qts     = usfmToken(u"qt")
qte     = usfmEndToken(u"qt")
nb      = usfmToken(u"nb")
m       = usfmToken(u"m")

# Footnotes
fs      = usfmTokenValue(u"f", plus)
fr      = usfmTokenValue( u"fr", phrase )
fre     = usfmEndToken( u"fr" )
fk      = usfmTokenValue( u"fk", phrase )
ft      = usfmTokenValue( u"ft", phrase )
fq      = usfmTokenValue( u"fq", phrase )
fe      = usfmEndToken(u"f")

# Cross References
xs      = usfmTokenValue(u"x", plus)
xdcs    = usfmToken(u"xdc")
xdce    = usfmEndToken(u"xdc")
xo      = usfmTokenValue( u"xo", phrase )
xt      = usfmTokenValue( u"xt", phrase )
xe      = usfmEndToken(u"x")

# Transliterated
tls      = usfmToken(u"tl")
tle      = usfmEndToken(u"tl")

# Transliterated
scs      = usfmToken(u"sc")
sce      = usfmEndToken(u"sc")

# Italics
ist     = usfmToken(u"it")
ien     = usfmEndToken(u"it")

li      = usfmToken(u"li")
d       = usfmToken(u"d")
sp      = usfmToken(u"sp")
adds    = usfmToken(u"add")
adde    = usfmEndToken(u"add")
nds     = usfmToken(u"nd")
nde     = usfmEndToken(u"nd")
pbr     = usfmBackslashToken("\\\\")
mi      = usfmToken(u"mi")

# Comments
rem     = usfmTokenValue( u"rem", phrase )

# Table of Contents
toc1    =  usfmTokenValue( u"toc1", phrase )
toc2    =  usfmTokenValue( u"toc2", phrase )
toc3    =  usfmTokenValue( u"toc3", phrase )

# Introductory Materials
is1     =  usfmTokenValue( u"is1", phrase ) | usfmTokenValue( u"is", phrase )
ip      =  usfmTokenValue( u"ip", phrase )
iot     =  usfmTokenValue( u"iot", phrase )
io1     =  usfmTokenValue( u"io1", phrase ) | usfmTokenValue( u"io", phrase )
io2     =  usfmTokenValue( u"io2", phrase ) 
ior_s   =  usfmToken( u"ior")
ior_e   =  usfmEndToken( u"ior")

# Quoted book title
bk_s    =  usfmToken( u"bk")
bk_e    =  usfmEndToken( u"bk")

element =   ide  | id | h | mt | mt1 | mt2 | mt3 | ms | ms1 | ms2 | mr     \
          | s | s1 | s2 | s3 | r | p | pi | mi | b | c | v                 \
          | wjs | wje | nds | nde | q | q1 | q2 | q3 | qts | qte | nb | m  \
          | fs   | fr   | fre  | fk | ft | fq | fe \
          | xs   | xdcs | xdce | xo | xt | xe \
          | ist  | ien  | li | d | sp         \
          | adds | adde                       \
          | tls  | tle                        \
          | toc1 | toc2 | toc3                \
          | is1  | ip   | iot | io1 | io2 | ior_s | ior_e  \
          | bk_s | bk_e                       \
          | scs  | sce  | pbr | rem | textBlock
usfm    = OneOrMore( element )

# input string
def parseString( unicodeString ):
    try:
        s = clean(unicodeString)
        tokens = usfm.parseString(s, parseAll=True )
    except Exception as e:
        print e
        print repr(unicodeString[:50])
        sys.exit()
    return [createToken(t) for t in tokens]

def clean( unicodeString ):
    # We need to clean the input a bit. For a start, until
    # we work out what to do, non breaking spaces will be ignored
    # ie 0xa0
    return unicodeString.replace(u'\xa0', u' ')

def createToken(t):
    options = {
        u'id':   IDToken,
        u'ide':  IDEToken,
        u'h':    HToken,
        u'mt':   MTToken,
        u'mt1':  MTToken,
        u'mt2':  MT2Token,
        u'mt3':  MT3Token,
        u'ms':   MSToken,
        u'ms1':  MSToken,
        u'ms2':  MS2Token,
        u'mr':   MRToken,
        u'p':    PToken,
        u'pi':   PIToken,
        u'b':    BToken,
        u's':    SToken,
        u's1':   SToken,
        u's2':   S2Token,
        u's3':   S3Token,
        u'mi':   MIToken,
        u'r':    RToken,
        u'c':    CToken,
        u'v':    VToken,
        u'wj':   WJSToken,
        u'wj*':  WJEToken,
        u'q':    QToken,
        u'q1':   Q1Token,
        u'q2':   Q2Token,
        u'q3':   Q3Token,
        u'nb':   NBToken,
        u'qt':   QTSToken,
        u'qt*':  QTEToken,
        u'f':    FSToken,
        u'fr':   FRToken,
        u'fr*':  FREToken,
        u'fk':   FKToken,
        u'ft':   FTToken,
        u'fq':   FQToken,
        u'f*':   FEToken,
        u'x':    XSToken,
        u'xdc':  XDCSToken,
        u'xdc*': XDCEToken,
        u'xo':   XOToken,
        u'xt':   XTToken,
        u'x*':   XEToken,
        u'it':    ISToken,
        u'it*':   IEToken,
        u'li':   LIToken,
        u'd':    DToken,
        u'sp':   SPToken,
        u'i*':   IEToken,
        u'li':   LIToken,
        u'add':  ADDSToken,
        u'add*': ADDEToken,
        u'nd':   NDSToken,
        u'nd*':  NDEToken,
        u'sc':   SCSToken,
        u'sc*':  SCEToken,
        u'm':    MToken,
        u'tl':   TLSToken,
        u'tl*':  TLEToken,
        u'\\\\': PBRToken,
        u'rem':  REMToken,
        u'toc1': TOC1Token,
        u'toc2': TOC2Token,
        u'toc3': TOC3Token,
        u'is':   IS1_Token,
        u'is1':  IS1_Token,
        u'ip':   IP_Token,
        u'iot':  IOT_Token,
        u'io':   IO1_Token,
        u'io1':  IO1_Token,
        u'io2':  IO2_Token,
        u'ior':  IOR_S_Token,
        u'ior*': IOR_E_Token,
        u'bk':   BK_S_Token,
        u'bk*':  BK_E_Token,
        u'text': TEXTToken
    }
    for k, v in options.iteritems():
        if t[0] == k:
            if len(t) == 1:
                return v()
            else:
                return v(t[1])
    raise Exception(t[0])

class UsfmToken(object):
    def __init__(self, value=u""):
        self.value = value
    def getValue(self): return self.value
    def isID(self):     return False
    def isIDE(self):    return False
    def isH(self):      return False
    def isMT(self):     return False
    def isMT2(self):    return False
    def isMT3(self):    return False
    def isMS(self):     return False
    def isMS2(self):    return False
    def isMR(self):     return False
    def isR(self):      return False
    def isP(self):      return False
    def isP(self):      return False
    def isPI(self):     return False
    def isS(self):      return False
    def isS2(self):     return False
    def isS3(self):     return False
    def isMI(self):     return False
    def isC(self):      return False
    def isV(self):      return False
    def isWJS(self):    return False
    def isWJE(self):    return False
    def isTEXT(self):   return False
    def isQ(self):      return False
    def isQ1(self):     return False
    def isQ2(self):     return False
    def isQ3(self):     return False
    def isQTS(self):    return False
    def isQTE(self):    return False
    def isNB(self):     return False
    def isFS(self):     return False
    def isFR(self):     return False
    def isFRE(self):    return False
    def isFK(self):     return False
    def isFT(self):     return False
    def isFQ(self):     return False
    def isFE(self):     return False
    def isXS(self):     return False
    def isXDCS(self):   return False
    def isXDCE(self):   return False
    def isXO(self):     return False
    def isXT(self):     return False
    def isXE(self):     return False
    def isIS(self):     return False
    def isIE(self):     return False
    def isSCS(self):    return False
    def isSCE(self):    return False
    def isLI(self):     return False
    def isD(self):      return False
    def isSP(self):     return False
    def isADDS(self):   return False
    def isADDE(self):   return False
    def isNDS(self):    return False
    def isNDE(self):    return False
    def isTLS(self):    return False
    def isTLE(self):    return False
    def isPBR(self):    return False
    def isM(self):      return False
    def isREM(self):    return False
    def is_toc1(self):  return False
    def is_toc2(self):  return False
    def is_toc3(self):  return False
    def is_is1(self):   return False
    def is_ip(self):    return False
    def is_iot(self):   return False
    def is_io1(self):   return False
    def is_io2(self):   return False
    def is_ior_s(self): return False
    def is_ior_e(self): return False
    def is_bk_s(self):  return False
    def is_bk_e(self):  return False

class IDToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderID(self)
    def isID(self):     return True

class IDEToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderIDE(self)
    def isIDE(self):    return True

class TOC1Token(UsfmToken):
    def renderOn(self, printer):
        return printer.render_toc1(self)
    def is_toc1(self):    return True

class TOC2Token(UsfmToken):
    def renderOn(self, printer):
        return printer.render_toc2(self)
    def is_toc2(self):    return True

class TOC3Token(UsfmToken):
    def renderOn(self, printer):
        return printer.render_toc3(self)
    def is_toc3(self):    return True

class HToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderH(self)
    def isH(self):      return True

class MTToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderMT(self)
    def isMT(self):     return True

class MT2Token(UsfmToken):
    def renderOn(self, printer):
        return printer.renderMT2(self)
    def isMT2(self):     return True

class MT3Token(UsfmToken):
    def renderOn(self, printer):
        return printer.renderMT3(self)
    def isMT3(self):    return True

class MSToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderMS(self)
    def isMS(self):     return True

class MS2Token(UsfmToken):
    def renderOn(self, printer):
        return printer.renderMS2(self)
    def isMS2(self):    return True

class MRToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderMR(self)
    def isMR(self):    return True

class MIToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderMI(self)
    def isMI(self):     return True

class RToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderR(self)
    def isR(self):    return True

class PToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderP(self)
    def isP(self):      return True

class BToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderB(self)
    def isB(self):      return True

class CToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderC(self)
    def isC(self):      return True

class VToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderV(self)
    def isV(self):      return True

class TEXTToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderTEXT(self)
    def isTEXT(self):   return True

class WJSToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderWJS(self)
    def isWJS(self):    return True

class WJEToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderWJE(self)
    def isWJE(self):    return True

class SToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderS(self)
    def isS(self):      return True

class S2Token(UsfmToken):
    def renderOn(self, printer):
        return printer.renderS2(self)
    def isS2(self):      return True

class S3Token(UsfmToken):
    def renderOn(self, printer):
        return printer.renderS3(self)
    def isS3(self):      return True

class QToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderQ(self)
    def isQ(self):      return True

class Q1Token(UsfmToken):
    def renderOn(self, printer):
        return printer.renderQ1(self)
    def isQ1(self):      return True

class Q2Token(UsfmToken):
    def renderOn(self, printer):
        return printer.renderQ2(self)
    def isQ2(self):      return True

class Q3Token(UsfmToken):
    def renderOn(self, printer):
        return printer.renderQ3(self)
    def isQ3(self):      return True

class NBToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderNB(self)
    def isNB(self):      return True

class QTSToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderQTS(self)
    def isQTS(self):      return True

class QTEToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderQTE(self)
    def isQTE(self):      return True

class FSToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderFS(self)
    def isFS(self):      return True

class FRToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderFR(self)
    def isFR(self):      return True

class FREToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderFRE(self)
    def isFRE(self):      return True

class FKToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderFK(self)
    def isFK(self):      return True

class FTToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderFT(self)
    def isFT(self):      return True

class FQToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderFQ(self)
    def isFQ(self):      return True

class FEToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderFE(self)
    def isFE(self):      return True

class ISToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderIS(self)
    def isIS(self):      return True

class IEToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderIE(self)
    def isIE(self):      return True

class LIToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderLI(self)
    def isLI(self):      return True

class DToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderD(self)
    def isD(self):      return True
    
class SPToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderSP(self)
    def isSP(self):      return True
    
class ADDSToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderADDS(self)
    def isADDS(self):    return True

class ADDEToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderADDE(self)
    def isADDE(self):    return True

class NDSToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderNDS(self)
    def isNDS(self):    return True

class NDEToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderNDE(self)
    def isNDE(self):    return True

class PBRToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderPBR(self)
    def isPBR(self):    return True


# Cross References
class XSToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderXS(self)
    def isXS(self):      return True

class XDCSToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderXDCS(self)
    def isXDCS(self):      return True

class XDCEToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderXDCE(self)
    def isXDCE(self):      return True

class XOToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderXO(self)
    def isXO(self):      return True

class XTToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderXT(self)
    def isXT(self):      return True

class XEToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderXE(self)
    def isXE(self):      return True

class MToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderM(self)
    def isM(self):      return True

# Transliterated Words
class TLSToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderTLS(self)
    def isTLS(self):      return True

class TLEToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderTLE(self)
    def isTLE(self):      return True

# Indenting paragraphs
class PIToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderPI(self)
    def isPI(self):      return True

# Small caps
class SCSToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderSCS(self)
    def isSCS(self):      return True

class SCEToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderSCE(self)
    def isSCE(self):      return True
    
# REMarks
class REMToken(UsfmToken):
    def renderOn(self, printer):
        return printer.renderREM(self)
    def isREM(self):      return True
    
# Introductions
class IS1_Token(UsfmToken):
    def renderOn(self, printer):
        return printer.render_is1(self)
    def is_is1(self):     return True

class IP_Token(UsfmToken):
    def renderOn(self, printer):  return printer.render_ip(self)
    def is_ip(self):              return True
    
class IOT_Token(UsfmToken):
    def renderOn(self, printer):  return printer.render_iot(self)
    def is_iot(self):             return True
    
class IO1_Token(UsfmToken):
    def renderOn(self, printer):  return printer.render_io1(self)
    def is_io1(self):             return True
    
class IO2_Token(UsfmToken):
    def renderOn(self, printer):  return printer.render_io2(self)
    def is_io2(self):             return True
    
class IOR_S_Token(UsfmToken):
    def renderOn(self, printer):  return printer.render_ior_s(self)
    def is_ior_s(self):           return True

class IOR_E_Token(UsfmToken):
    def renderOn(self, printer):  return printer.render_ior_e(self)
    def is_ior_e(self):           return True

# Quoted book title
class BK_S_Token(UsfmToken):
    def renderOn(self, printer):  return printer.render_bk_s(self)
    def is_bk_s(self):            return True

class BK_E_Token(UsfmToken):
    def renderOn(self, printer):  return printer.render_bk_e(self)
    def is_bk_e(self):            return True


