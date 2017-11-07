# -*- coding: utf-8 -*-
#

import sys

from pyparsing import Word, alphas, OneOrMore, nums, Literal, White, Group, Suppress, Empty, NoMatch, Optional, CharsNotIn, unicodeString, MatchFirst

# 
# SUPPORT
#

def usfmToken(key):
    return Group(Suppress(backslash) + Literal( key ) + Suppress(White()))
def usfmBackslashToken(key):
    return Group(Literal(key))
def usfmEndToken(key): 
    return Group(Suppress(backslash) + Literal( key +  "*"))
def usfmTokenValue(key, value): 
    return Group(Suppress(backslash) + Literal( key ) + Suppress(White()) + Optional(value) )
def usfmTokenNumber(key): 
    return Group(Suppress(backslash) + Literal( key ) + Suppress(White()) + CharsNotIn(' \n\t\\') + Suppress(White()))

#
# DEFINE GRAMMAR
#

#phrase      = Word( alphas + u"-.,!? —–‘“”’;:()'\"[]/&%=*…{}" + nums )
phrase      = CharsNotIn( "\n\\"  )
backslash   = Literal("\\")
plus        = Literal("+")

textBlock   = Group(Optional(NoMatch(), "text") + Optional(Suppress(newline)) + phrase )
unknown     = Group(Optional(NoMatch(), "unknown") + Suppress(backslash) + CharsNotIn(' \n\t\\') )
 
knownTokens  = []

simpleTokens = [
    'p', 'pi', 'b', 'q', 'q1', 'q2', 'q3', 'nb',
    'm', 'li', 'd', 'sp', 'mi', 'pb', 'ip', 'iot', 'io', 'io1', 'io2',
    'ip'
]
for st in simpleTokens: knownTokens.append(usfmToken(st))

numberTokens = [
    'c', 'v'
]
for nt in numberTokens: knownTokens.append(usfmTokenNumber(nt))

phraseTokens = [
    'id', 'ide', 'h', 'mt', 'mt1', 'mt2', 'mt3', 'ms', 'ms1', 'ms2',
    'mr', 's', 's2', 's2', 's3', 'r', 'periph', 'rem', 'toc1', 'toc2',
    'toc3', 'fk', 'ft', 'fq', 'xo', 'xt', 'is', 'is1', 'lit'
]
for pt in phraseTokens: knownTokens.append(usfmTokenValue(pt, phrase))

pairTokens = [
    # Special Text
    'add', 'bk', 'dc', 'k', 'nd', 'ord', 'pn', 'qt', 'sig', 'sis', 
    'sls', 'tl', 'wj', 
    # Character Styling
    'em', 'bd', 'it', 'bdit', 'no', 'sc',
    # Breaks
    'pb',
    # Special Features
    'fig', 'ndx', 'pro', 'w', 'wg', 'wh',
    # Cross Referencs
    'x', 'xot', 'xnt', 'xdc',
    # Footnotes
    'f', 'fe', 'fdc', 'fm',
    # Poetry
    'qs', 'qac',
    # Chapters and Verses
    'ca', 'va', 'vp',
    # Titles, Headings and Labels
    'rq', 
    # Introductions
    'ior', 'iqt'
]
for pt in pairTokens: 
    knownTokens.append(usfmToken(pt))
    knownTokens.append(usfmEndToken(pt))
    
plusPairTokens = [
    'f', 'x'
]
for pt in plusPairTokens:
    knownTokens.append(usfmTokenValue(pt, plus))
    knownTokens.append(usfmEndToken(pt))

phrasePairTokens = [
    'fr'
]
for pt in phrasePairTokens:
    knownTokens.append(usfmTokenValue(pt, phrase))
    knownTokens.append(usfmEndToken(pt))

knownTokens.append( usfmBackslashToken("\\\\") )
knownTokens.append( textBlock                  )
knownTokens.append( unknown                    )

usfm = OneOrMore( MatchFirst(knownTokens) )

#
# PARSING
#

def parseString( unicodeString ):
    try:
        s = clean(unicodeString)
        tokens = usfm.parseString(s, parseAll=True )
    except Exception as e:
        print(e)
        print(repr(unicodeString[:50]))
        sys.exit()
    return [createToken(t) for t in tokens]

def clean( unicodeString ):
    # We need to clean the input a bit. For a start, until
    # we work out what to do, non breaking spaces will be ignored
    # ie 0xa0
    return unicodeString.replace('\xa0', ' ')
    
def createToken(t):
    if len(t) == 1:
        return UsfmToken(t[0])
    else:
        return UsfmToken(t[0], t[1])

#
# TOKENS
#

class UsfmToken(object):
    def __init__(self, tokenType="", value=""):
        self.value = value
        self.tokenType = tokenType
    def getValue(self): return self.value
    def getType(self):  return self.tokenType
    
    # Handler for 'is' style calls
    def __getattr__(self, name):
        if name[:3] == 'is_':
            return name[3:] == self.getType().lower().replace('*', '_e')
        else:
            return super.__getattr__(name)
            
    def renderOn(self, printer):
        
        try:
            m = getattr(printer, 'render_' + self.getType().lower().replace('*', '_e'))
        except:
            m = getattr(printer, 'render_unhandled')
        return m(self)
        
