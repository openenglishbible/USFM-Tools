# -*- coding: utf-8 -*-
#

import abstractRenderer
import codecs
import datetime
import tempfile
import subprocess
import os

#
#   Renders to ConTeXt so we can make PDF. Main renderer for PDF of OEB
#

class Renderer(abstractRenderer.AbstractRenderer):
    
    def runscript(self, c, prefix='', repeatFilter = ''):
        print prefix + ':: ' + c
        pp = subprocess.Popen([c], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        (result, stderrdata) = pp.communicate()
        print result
        print stderrdata
        if not repeatFilter == '' and not stderrdata.find(repeatFilter) == -1:
            runscript(c, prefix, repeatFilter)

    def __init__(self, inputDir, outputDir, outputName):
        abstractRenderer.AbstractRenderer.__init__(self, inputDir, outputDir, outputName)
        # Unset
        self.f = None  # output file stream
        # IO
        self.texFile = tempfile.NamedTemporaryFile()
        self.texFileName = self.texFile.name
        self.outputFileName = os.path.join(outputDir, outputName + '.pdf')
        self.inputDir = inputDir
        # Flags
        self.printerState = {u'li': False, u'd': False, u'm': False}
        self.smallCapSections = True  # Sometimes we don't want to do this, like for Psalms
        self.justDidLORD = False
        self.justDidNB = False
        self.doNB = False
        self.narrower = False
        self.doChapterOrVerse = u''
        self.smallcaps = False

    def render(self, order='normal'):
        # RENDER
        self.f = codecs.open(self.texFileName, 'w', 'utf_8_sig')
        self.loadUSFM(self.inputDir)
        self.f.write(self.introTeXt)
        self.run(order)
        self.f.write(self.stopNarrower() + self.closeTeXt)
        self.f.close()    
        # GENERATE 
        t = tempfile.mkdtemp()
        c = '. ./support/thirdparty/context/tex/setuptex ; cd "' + t + '"; rm * ; context ' + self.texFileName + ' --result="' + self.outputFileName + '"'
        self.runscript(c, '     ')
        
    
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
        return u'\par {\startalignment[middle] \em '

    def stopD(self):
        if self.printerState[u'd'] == False:
            return u''
        else:
            self.printerState[u'd'] = False
            return u'\stopalignment }'
            
    def startM(self):
        r = self.stopD() + self.stopLI() + self.stopNarrower()
        self.printerState[u'm'] = True
        return r + ur'\par {\startalignment[flushleft] '

    def stopM(self):
        if self.printerState[u'm'] == False:
            return u''
        else:
            self.printerState[u'm'] = False
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

    def render_id(self, token):      self.f.write( self.stopNarrower() + ur"\marking[RAChapter]{ } \marking[RABook]{ } \marking[RASection]{ }" )
    def render_h(self, token):       self.f.write( u'\n\n\RAHeader{' + token.value + u'}\n')
    def render_mt(self, token):      self.f.write( self.stopLI() + self.stopNarrower() + u'\n\MT{' + token.value + u'}\n')
    def render_mt2(self, token):     self.f.write( self.stopLI() + self.stopNarrower() + u'\n\MTT{' + token.value + u'}\n')
    def render_ms(self, token):      self.markForSmallCaps() ; self.f.write(self.stopNarrower() + u'\n\MS{' + token.value + u'}\n') ; self.doNB = True
    def render_ms2(self, token):     self.doNB = True; self.markForSmallCaps() ; self.f.write( self.stopNarrower() + u'\n\MSS{' + token.value + '}' + self.newLine() )
    def render_p(self, token):       self.f.write( self.stopM() + self.stopD() + self.stopLI() + self.stopNarrower() + self.newLine() )
    def render_b(self, token):       self.f.write( self.stopM() + self.stopD() + self.stopLI() + self.stopNarrower() + u'\\blank \n' )
    def render_s1(self, token):      self.f.write( self.stopM() + self.stopD() + self.stopLI() + self.stopNarrower() +  u'\n\\blank[big] ' + u'\n\MSS{' + token.getValue() + '}' + self.newLine() ) ; self.doNB = True
    def render_s2(self, token):      self.doNB = True; self.f.write( self.stopM() + self.stopD() + self.stopLI() + self.stopNarrower() + u'\n\\blank[big] ' + u'\n\MSS{' + token.value + '}' + self.newLine() )
    def render_c(self, token):
        self.doChapterOrVerse = u'\C{' + token.value + u'}'
        self.f.write( u' ' )
    def render_v(self, token):
        if not token.value == u'1':
            self.doChapterOrVerse =  u'\V{' + token.value + u'}'
        self.f.write( ' ' )
    def render_wj_s(self, token):     self.f.write( u" " )
    def render_wj_e(self, token):     self.f.write( u" " )
    def render_text(self, token):
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
    def render_q(self, token):       self.render_q1(token)
    def render_q1(self, token):      self.f.write( self.stopD() + self.stopLI() + self.startNarrower(1) )
    def render_q2(self, token):      self.f.write( self.stopD() + self.stopLI() + self.startNarrower(2) )
    def render_q3(self, token):      self.f.write( self.stopD() + self.stopLI() + self.startNarrower(3) )
    def render_nb(self, token):      self.doNB = True ; self.f.write( self.stopD() + self.stopLI() + self.stopNarrower() + u'\\blank[medium] ' + self.newLine() )
    def render_f_s(self, token):     self.f.write( u'\\footnote{' )
    def render_f_e(self, token):     self.f.write( u'} ' )
    def render_em_s(self, token):    self.f.write( u'{\em ' )
    def render_em_e(self, token):    self.f.write( u'} ' )
    def render_add_s(self, token):   self.f.write( u'{\em ' )
    def render_add_e(self, token):   self.f.write( u'} ' )
    def render_nd_s(self, token):    self.f.write( u'{\sc ' )
    def render_nd_e(self, token):    self.justDidLORD = True; self.f.write( u'}' )
    def render_li(self, token):      self.f.write( self.startLI() )
    def render_d(self, token):       self.f.write( self.startD() )
    def render_sp(self, token):      self.f.write( self.startD() )
    def render_pbr(self, token):     self.f.write( u' \\\\ ' )
    def render_fr(self, token):      self.f.write( u' ' + token.getValue() + u' ' )
    def render_fr_e(self, token):    self.f.write( u' ' )
    def render_fk(self, token):      self.f.write( u' ' + token.getValue() + u' ' )
    def render_ft(self, token):      self.f.write( u' ' + token.getValue() + u' ' )
    def render_pi(self, token):      self.render_q(token)
    
    def render_is1(self, token):    self.render_s1(token)
    def render_ip(self, token):     self.render_p(token)
    def render_iot(self, token):    self.render_q(token)
    def render_io1(self, token):    self.render_q2(token)
    
    def render_qs_s(self, token):   self.f.write( u'{\em ' )
    def render_qs_e(self, token):   self.f.write( u'} ' )


    def render_pb(self, token):     self.f.write(u'\page ')
    
    def render_m(self, token):      self.f.write( self.stopM() + self.startM() )
    
    def render_periph(self, token):
        if token.getValue() == u'Table of Contents':
            self.f.write(u"""
            \page[right]
            \par ~
            {\midaligned {\tfd{\WORD{Table of Contents}}}}
            \par ~
            \placelist[chapter]    
            """)
    #
    #   Introductory codes
    #
    
    introTeXt = unicode(r"""
    \definemarking[RAChapter]
    \definemarking[RABook]
    \definemarking[RASection]

    \definepapersize [Trade][width=6in, height=9in]
    \setuppapersize [Trade][Trade]

    %\definepapersize [TwoTrade][width=12in, height=9in]
    %\setuppapersize [Trade][TwoTrade]
    %\setuparranging [2UP] % page numbering doesn't work this way
 
 
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
    \define[1]\S{\par ~ \par \section{#1} \marking[RASection]{#1} \par }
    \define[1]\MS{\par ~ \par \section{#1} \marking[RASection]{#1} \par }
    \define[1]\MSS{\par ~ \par \section{#1} \marking[RASection]{#1} \par }
    \define[1]\SS{\blank{\midaligned{\em #1}}\blank}
    \define[1]\MT{  {\midaligned{\tfd{\WORD{#1}}}}\blank ~ } 
    \define[1]\MTT{ {\midaligned{\tfd{\WORD{#1}}}}\blank ~ }
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
