# -*- coding: utf-8 -*-
#

import abstractRenderer
import codecs
import datetime

#
#   Renders to ConTeXt so we can make PDF. Main renderer for PDF of OEB
#

class ConTeXtRenderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputFilename):
        # Unset
        self.f = None  # output file stream
        # IO
        self.outputFilename = outputFilename
        self.inputDir = inputDir
        # Flags
        self.printerState = {u'li': False, u'd': False}
        self.smallCapSections = True  # Sometimes we don't want to do this, like for Psalms
        self.justDidLORD = False
        self.justDidNB = False
        self.doNB = False
        self.narrower = False
        self.doChapterOrVerse = u''
        self.smallcaps = False

    def render(self):
        self.f = codecs.open(self.outputFilename, 'w', 'utf_8_sig')
        self.loadUSFM(self.inputDir)
        self.f.write(self.introTeXt)
        self.f.write(u"""
            \page[right] % Cover page
            \page[left]
            \par 
            \par Built by github.com/openenglishbible/USFM-Tools
            \par on """ + datetime.date.today().strftime("%A, %d %B %Y") + r"""
            \par     
            \page[right]
            \par ~
            {\midaligned {\tfc{\WORD{Table of Contents}}}}
            \par ~
            \placelist[chapter]
        """)
        self.run()
        self.f.write(self.closeTeXt)
        self.f.close()
        
    def writeLog(self, s):
        print s
        
    
    #
    #   Support
    #

    def startNarrower(self, n):
        s = u'}' if self.narrower else u'\n\\blank[medium] '
        self.narrower = True
        s = s + u'\n\\noindentation \\Q{' + str(n) + u'}{'
        self.doNB = True
        return s

    def stopNarrower(self):
        s = u'}\n\\blank[medium] ' if self.narrower else u''
        self.narrower = False
        return s

    def escapeText(self, s):
        return s.replace('&', '\\&').replace('%', '\\%')
 
    def markForSmallCaps(self):
        if self.smallCapSections: 
             self.smallcaps = True

    def renderSmallCaps(self, s):
        if self.smallcaps == True:
            self.smallcaps = False
            return self.smallCapText(s)
        return s

    def smallCapText(self, s):
         i = 0
         while i < len(s):
             if i < 50:  #we are early, look for comma
                 if s[i] == u',' or s[i] == u';' or s[i] == u'(' or s[i:i+3] == u'and':
                     return u'{\sc ' + s[:i+1] + u'}' + s[i+1:]
             else: # look for space
                 if s[i] == ' ':
                     return u'{\sc ' + s[:i] + u'}' + s[i:]
             i = i + 1
         return u'{\sc ' + s + u'}'
         
    def startLI(self):
        if self.printerState[u'li'] == False:
            self.printerState[u'li'] = True
            #return u'\startitemize \item '
            return ur'\startexdent '
        else:
            #return u'\item '
            return ur'\par '
        
    def stopLI(self):
        if self.printerState[u'li'] == False:
            return u''
        else:
            self.printerState[u'li'] = False
            #return u'\stopitemize'
            return ur'\stopexdent '

    def startD(self):
        if self.printerState[u'd'] == False:
            self.printerState[u'd'] = True
        return u'\par {\startalignment[center] \em '

    def stopD(self):
        if self.printerState[u'd'] == False:
            return u''
        else:
            self.printerState[u'd'] = False
            return u'\stopalignment }'
            
    def newLine(self):
        s = u'\n\par \n'
        if self.doNB:
            self.doNB = False
            self.justDidNB = True
            s = s + ur'\noindentation '
        elif self.justDidNB:
            self.justDidNB = False
            s = s + ur'\indentation '
        return s
                    

    #
    #   Tokens
    #

    def renderID(self, token):      self.f.write( self.stopNarrower() + ur"\marking[RAChapter]{ } \marking[RABook]{ } \marking[RASection]{ }" )
    def renderH(self, token):       self.f.write( u'\n\n\RAHeader{' + token.value + u'}\n')
    def renderMT(self, token):      self.f.write( self.stopLI() + self.stopNarrower() + u'\n\MT{' + token.value + u'}\n')
    def renderMT2(self, token):     self.f.write( self.stopLI() + self.stopNarrower() + u'\n\MTT{' + token.value + u'}\n')
    def renderMS(self, token):      self.markForSmallCaps() ; self.f.write(self.stopNarrower() + u'\n\MS{' + token.value + u'}\n') ; self.doNB = True
    def renderMS2(self, token):     self.doNB = True; self.markForSmallCaps() ; self.f.write( self.stopNarrower() + u'\n\MSS{' + token.value + '}' + self.newLine() )
    def renderP(self, token):       self.f.write( self.stopD() + self.stopLI() + self.stopNarrower() + self.newLine() )
    def renderB(self, token):       self.f.write( self.stopD() + self.stopLI() + self.stopNarrower() + u'\\blank \n' )
    def renderS(self, token):       self.f.write( self.stopD() + self.stopLI() + self.stopNarrower() +  u'\n\\blank[big] ' + u'\n\MSS{' + token.getValue() + '}' + self.newLine() ) ; self.doNB = True
    def renderS2(self, token):      self.doNB = True; self.f.write( self.stopD() + self.stopLI() + self.stopNarrower() + u'\n\\blank[big] ' + u'\n\MSS{' + token.value + '}' + self.newLine() )
    def renderC(self, token):
        self.doChapterOrVerse = u'\C{' + token.value + u'}'
        self.f.write( u' ' )
    def renderV(self, token):
        if not token.value == u'1':
            self.doChapterOrVerse =  u'\V{' + token.value + u'}'
        self.f.write( ' ' )
    def renderWJS(self, token):     self.f.write( u" " )
    def renderWJE(self, token):     self.f.write( u" " )
    def renderTEXT(self, token):
        s = self.escapeText(token.value)
        if self.smallcaps and not self.doChapterOrVerse == u'':
            s = self.renderSmallCaps(s)
            s = self.doChapterOrVerse + s
            self.doChapterOrVerse = u''
        elif not self.doChapterOrVerse == u'':
            i = s.find(u' ')   
            if i == -1: 
                # No space found - try end
                i = len(s)       
            s = s[:i] + self.doChapterOrVerse + s[i+1:]
            self.doChapterOrVerse = u''
        elif self.smallcaps:
            s = self.renderSmallCaps(s)
        if self.justDidLORD:
            if s[0].isalpha():
                s = u' ' + s
            self.justDidLORD = False    
        self.f.write( s )
    def renderQ(self, token):       self.f.write( self.stopD() + self.stopLI() + self.startNarrower(1) )
    def renderQ1(self, token):      self.f.write( self.stopD() + self.stopLI() + self.startNarrower(1) )
    def renderQ2(self, token):      self.f.write( self.stopD() + self.stopLI() + self.startNarrower(2) )
    def renderQ3(self, token):      self.f.write( self.stopD() + self.stopLI() + self.startNarrower(3) )
    def renderNB(self, token):      self.doNB = True ; self.f.write( self.stopD() + self.stopLI() + self.stopNarrower() + u'\\blank[medium] ' + self.newLine() )
    def renderFS(self, token):      self.f.write( u'\\footnote{' )
    def renderFE(self, token):      self.f.write( u'} ' )
    def renderIS(self, token):      self.f.write( u'{\em ' )
    def renderIE(self, token):      self.f.write( u'} ' )
    def renderADDS(self, token):    self.f.write( u'{\em ' )
    def renderADDE(self, token):    self.f.write( u'} ' )
    def renderNDS(self, token):     self.f.write( u'{\sc ' )
    def renderNDE(self, token):     self.justDidLORD = True; self.f.write( u'}' )
    def renderLI(self, token):      self.f.write( self.startLI() )
    def renderD(self, token):       self.f.write( self.startD() )
    def renderSP(self, token):      self.f.write( self.startD() )
    def renderPBR(self, token):     self.f.write( u' \\\\ ' )
    def renderFR(self, token):      self.f.write( u' ' + token.getValue() + u' ' )
    def renderFRE(self, token):     self.f.write( u' ' )
    def renderFK(self, token):      self.f.write( u' ' + token.getValue() + u' ' )
    def renderFT(self, token):      self.f.write( u' ' + token.getValue() + u' ' )
    def renderPI(self, token):      self.f.write( self.renderQ(token) )
    
    #
    #   Introductory codes
    #
    
    introTeXt = unicode(r"""
    \definemarking[RAChapter]
    \definemarking[RABook]
    \definemarking[RASection]

    \definepapersize [Trade][width=6in, height=9in]
    \setuppapersize [Trade][Trade]
    %\setuparranging [2UP, rotated, doublesided]
    \setuppagenumbering [alternative=doublesided]
    \setuplayout [location=middle, 
        rightmargin=20mm,
        width=90mm,
        marking=on]

    \usetypescript[pagella]
    \setupbodyfont [pagella, 9pt]

    %\setupalign[normal,hanging,hz,tolerant,hyphenated]
    \setupalign[hanging]

    \setupbodyfontenvironment[default][em=italic]

    \setuppagenumbering[location=]
    \setupheadertexts[{\em \getmarking[RASection]}][{\getmarking[RABook] ~\getmarking[RAChapter]}]
    \setupfootertexts[pagenumber][]

    % Hide chapters but keep in TOC
    \setuphead[chapter][placehead=hidden]
    \setuptexttexts[{\placerawheaddata[chapter]}]

    \setupspacing[packed]   % normal word space at the end of sentences
    \setupwhitespace[none]  % no space between paragraphs
    \setupindenting[small, yes]
    \setupinterlinespace[line=11.5pt] % Line spacing

    \setuphead[section][number=no, textstyle=em, before=\blank, after=\blank, align={middle, nothyphenated, verytolerant}]

    \setuplist[chapter][alternative=c]

    \setupnote[footnote][way=bypage]

    \define[1]\V{\setupinmargin[style=small,stack=yes] \inouter{#1} }
    \define[1]\C{\setupinmargin[style=bold,stack=yes] \inouter{#1} \marking[RAChapter]{#1} }
    \define[1]\MS{\par ~ \par \section{#1} \marking[RASection]{#1} \par }
    \define[1]\MSS{\blank{\midaligned{\em #1}}\blank}
    \define[1]\MT{  {\midaligned{\tfd{\WORD{#1}}}}\blank ~ } 
    \define[1]\MTT{ {\midaligned{\tfc{\WORD{#1}}}}\blank ~ }
    \define[1]\RAHeader{\page[right] \chapter{#1} \marking[RABook]{#1} }
    \define[2]\Q{\startnarrower[#1*left,1*right] #2\stopnarrower }
    
    \emergencystretch\maxdimen
    
    \definestartstop
      [exdent]
      [before={\startnarrower[left]\setupindenting[-\leftskip,yes]},
       after=\stopnarrower]

    \starttext
    """)
    
    closeTeXt = ur"""
    \stoptext
    """
