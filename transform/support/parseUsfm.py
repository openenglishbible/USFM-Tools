# -*- coding: utf-8 -*-
#

import sys

from pyparsing import *
import sharedLogger


#
# Setup
#
ParserElement.setDefaultWhitespaceChars('\n')

# 
# SUPPORT
#

def usfmTokenPart(key):                 return Suppress(backslash) + Literal(key) + Suppress(space)
def usfmParagraphTokenPart(key):        return Or([StringStart(), LineStart()]) + usfmTokenPart(key)

def usfmParagraphToken(key):            return Group(Suppress(backslash) + Literal(key)) #+ Suppress(Or([space, LineEnd()])))
def usfmParagraphTokenEmpty(key):       return Group(Suppress(backslash) + Literal(key)) #+ Suppress(LineEnd()))
def usfmParagraphTokenWord(key):        return Group(usfmParagraphTokenPart(key) + singleword + Or([Suppress(space), FollowedBy(LineEnd())]))
def usfmParagraphTokenLine(key):        return Group(usfmParagraphTokenPart(key) + line)

def usfmCharacterToken(key):            return Group(usfmTokenPart(key))
def usfmCharacterEndToken(key):         return Group(Suppress(backslash) + Combine(Literal(key) + Literal('*')))
def usfmCharacterTokenWord(key):        return Group(usfmTokenPart(key) + singleword)

#
# DEFINE GRAMMAR
#

space            = Literal(" ")
line             = CharsNotIn("\n\\")
singleword       = CharsNotIn(" \\\n")
backslash        = Literal("\\")
backslashEscaped = Literal("\\\\")

textBlock   = Group(Optional(NoMatch(), "text") + line )
unknown     = Group(Optional(NoMatch(), "unknown") + Suppress(backslash) + CharsNotIn(' \n\t\\') )
 
knownTokens  = []

# 
# BUILDERS
#
def buildTokenSimple(tokens, knownTokens):
    for t in tokens:
        knownTokens.append(usfmCharacterToken(t))
def buildTokenSimpleNumbered(tokens, knownTokens):
    for t in tokens:
        knownTokens.append(usfmCharacterToken(t))
        for n in range(0,9):
            knownTokens.append(usfmCharacterToken(t + str(n)))


def buildTokenEmpty(tokens, knownTokens):
    for t in tokens:
        knownTokens.append(usfmParagraphTokenEmpty(t))
def buildTokenLine(tokens, knownTokens):
    for t in tokens:
        knownTokens.append(usfmParagraphTokenLine(t))
def buildTokenLineNumbered(tokens, knownTokens):
    for t in tokens:
        knownTokens.append(usfmParagraphTokenLine(t))
        for n in range(0,9):
            knownTokens.append(usfmParagraphTokenLine(t + str(n)))

def buildTokenParagraph(tokens, knownTokens):
    for t in tokens:
        knownTokens.append(usfmParagraphToken(t))
def buildTokenParagraphNumbered(tokens, knownTokens):
    for t in tokens:
        knownTokens.append(usfmParagraphToken(t))
        for n in range(0,9):
            knownTokens.append(usfmParagraphToken(t + str(n)))

def buildTokenWord(tokens, knownTokens):
    for t in tokens:
        knownTokens.append(usfmParagraphTokenWord(t))

def buildPairTokens(pairTokens, knownTokens):
    for t in pairTokens:
        knownTokens.append(usfmCharacterToken(t))
        knownTokens.append(usfmCharacterEndToken(t))

def buildPairTokensPlus(pairTokens, knownTokens):
    for t in pairTokens:
        knownTokens.append(usfmCharacterTokenWord(t))
        knownTokens.append(usfmCharacterEndToken(t))

#
#   IDENTIFICATION
#
buildTokenLineNumbered(['h'], knownTokens)
buildTokenLine(['usfm', 'id', 'ide', 'sts', 'rem', 'toc1', 'toc2', 'toc3'], knownTokens)

#
#   TITLES, HEADINGS AND LABELS
#
buildTokenLineNumbered(['mt', 'mte', 'ms', 's'], knownTokens)
buildTokenLine(['sr', 'r', 'd', 'sp'], knownTokens)
buildPairTokens(['rq'], knownTokens)

# 
#   CHAPTERS AND VERSES
#
buildTokenLine(['c', 'cl', 'cp', 'cd'], knownTokens)
buildTokenWord(['v'], knownTokens)
buildPairTokens(['ca', 'va', 'vp'], knownTokens)

#
#   PARAGRAPHS
#
buildTokenParagraph(['p', 'm', 'pmo', 'pmc', 'pmr', 'mi', 'cls', 'pc', 'pr'], knownTokens)
buildTokenEmpty(['nb', 'b'], knownTokens)
buildTokenParagraphNumbered(['pi', 'li', 'ph'], knownTokens)

#
#   POETRY
#
buildTokenParagraphNumbered(['q', 'qm'], knownTokens)
buildTokenLine(['qr', 'qc', 'qa'], knownTokens)
buildPairTokens(['qs', 'qac'], knownTokens)
# Also \b - see paragraphs

#
#   TABLES
#
buildTokenParagraph(['tr'], knownTokens)
buildTokenSimpleNumbered(['th', 'thr', 'tc', 'trc'], knownTokens)

#
#   FOOTNOTES
#
# footnote
buildPairTokensPlus(['f', 'fe', 'fv', 'fdc'], knownTokens)
# inside
knownTokens.append(usfmCharacterTokenWord('fr'))
knownTokens.append(usfmCharacterToken('fr*'))
buildPairTokens(['fm', 'fk', 'fq', 'fqa', 'fl', 'fp', 'ft'], knownTokens)

#
#   CROSS REFERENCES
#
buildPairTokensPlus(['x', 'xot', 'xnt', 'xdc'], knownTokens)
knownTokens.append(usfmCharacterTokenWord('xo'))
buildTokenSimple(['xk', 'xq', 'xt'], knownTokens)
buildPairTokens(['rq'], knownTokens)

#
#   SPECIAL TEXT AND CHARACTER STYLES
#

# special text
buildPairTokens(['add', 'bk', 'dc', 'k', 'nd', 'ord', 'pn', 'qt', 'sig', 'sis', 'tl', 'wj'], knownTokens)
knownTokens.append(usfmParagraphTokenLine('lit'))

# character styling
buildPairTokens(['em', 'bd', 'it', 'bdit', 'no', 'sc'], knownTokens)

# spacing and breaks
buildTokenEmpty(['pb'], knownTokens)

# special features
buildPairTokens(['fig', 'ndx', 'pro', 'w', 'wg', 'wh'], knownTokens)

# nested text
buildPairTokens(['+nd'], knownTokens)


#
#   PERIPHERALS
#
buildTokenLine(['periph'], knownTokens)

#
#   STUDY BIBLE
#
#   NOT YET IMPLEMENTED

#
#   CLEANUP
#
    
knownTokens.append( backslashEscaped )
knownTokens.append( textBlock        )
#knownTokens.append( unknown          )

usfm = OneOrMore( MatchFirst(knownTokens) )

#
# PARSING
#

def parseString( unicodeString ):
    logger = sharedLogger.currentLogger
    try:
        s = clean(unicodeString)
        tokens = usfm.parseString(s, parseAll=True )
    except Exception as e:
        logger.error('\nParse error in book ' + unicodeString.split('\n')[0] +
                     '\n    in line reading <' + e.line + '>' +
                     '\n             at col ' + str(e.col) +
                     '\n              error ' + str(e))
        sys.exit()
    return [createToken(t) for t in tokens] # if isNotBlank(t)]

def clean( unicodeString ):
    # We need to clean the input a bit. For a start, until
    # we work out what to do, non breaking spaces will be ignored
    # ie 0xa0
    # multiple spaces = one space, easier than doing it in parser
    u = unicodeString.replace('\r\n', '\n')
    u = u.replace('\xa0', ' ')
    u = ' '.join(u.split(' '))
    return u
    
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
            return name[3:] == self.getType().lower().replace('*', '_e').replace('+', '_nested')
        else:
            return super.__getattr__(name)
            
    def renderOn(self, printer):
        
        try:
            m = getattr(printer, 'render_' + self.getType().lower().replace('*', '_e').replace('+', 'nested_'))
        except:
            m = getattr(printer, 'render_unhandled')
        return m(self)
        
