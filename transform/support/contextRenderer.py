# -*- coding: utf-8 -*-
#

import codecs
import os
import platform
import shutil
import subprocess
import sys
import tempfile

import abstractRenderer


#
#   Renders to ConTeXt so we can make PDF. Main renderer for PDF of OEB
#

class Renderer(abstractRenderer.AbstractRenderer):
    def runscript(self, c, prefix='', repeatFilter=''):
        pp = subprocess.Popen([c], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, executable="/bin/bash")
        (result, stderrdata) = pp.communicate()
        self.logger.debug(result)
        if not len(stderrdata) == 0:
            self.logger.warning(stderrdata)

    def __init__(self, inputDir, outputDir, outputName, config):
        self.identity = 'pdf renderer (via context)'
        self.outputDescription = os.path.join(outputDir, outputName + '.pdf')
        abstractRenderer.AbstractRenderer.__init__(self, inputDir, outputDir, outputName, config)
        # Unset
        self.f = None  # output file stream
        # IO
        self.outputDir = outputDir
        self.tempDir = tempfile.mkdtemp()
        self.texFileName = os.path.join(self.tempDir, 'bible.tex')
        self.outputFileName = os.path.join(self.outputDir, outputName + '.pdf')
        self.inputDir = inputDir
        # Flags
        self.printerState = {'li': False, 'd': False, 'm': False}
        self.smallCapSections = True  # Sometimes we don't want to do this, like for Psalms
        self.justDidLORD = False
        self.justDidNB = False
        self.doNB = False
        self.narrower = False
        self.doChapterOrVerse = ''
        self.smallcaps = False

    def introTeXt(self):
        tex = self.rawIntroTeXt
        # Layout
        if self.config.get('Context','layout') == 'singlesided':
             tex = tex.replace('{{{layout}}}', 'singlesided')
             tex = tex.replace('{{{position}}}', '\inleft')
             tex = tex.replace('{{{setuplayout}}}', '\setuplayout [leftedge=0.25in,leftmargin=0.75in,width=4in,rightmargin=0.5in,rightedge=0.5in]')
        else:
             tex = tex.replace('{{{layout}}}', 'doublesided')
             tex = tex.replace('{{{position}}}', '\inouter')
             tex = tex.replace('{{{setuplayout}}}', '\setuplayout [location=middle, rightmargin=1in, width=90mm, marking=on]')
        tex = tex.replace('{{{layout}}}', self.config.get('Context','layout'))
        # Font
        tex = tex.replace('{{{bodyFont}}}', self.config.get('Context','bodyFont'))
        tex = tex.replace('{{{bodyFontSize}}}', self.config.get('Context','bodyFontSize'))
        # Cover
        if self.config.get('Context','coverPage') == '/path/to/cover.pdf':
            tex = tex.replace('{{{coverPage}}}', '')
        else:
            tex = tex.replace('{{{coverPage}}}', '\externalfigure[' + self.config.get('Context','coverPage') + ']\page[right]')
        return tex

    def render(self, order='normal'):
        # RENDER
        self.f = open(self.texFileName, 'w')
        self.loadUSFM(self.inputDir)
        self.f.write(self.introTeXt())
        self.run(order)
        self.f.write(self.stopNarrower() + self.closeTeXt)
        self.f.close()
        # OPTIONALLY SAVE TEX FILE
        if self.config.get("Context",'saveTeX') == 'true':  shutil.copy(self.texFileName, self.outputFileName[:-4] + '.tex')

        c = '. ' + os.path.dirname(os.path.realpath(__file__)) + '/thirdparty/context/tex/setuptex && '
        if platform.system() == 'Darwin':
            c = c + 'export OSFONTDIR="/Library/Fonts//;/System/Library/Fonts;$HOME/Library/Fonts" && '
        elif platform.system() == 'Windows':
            print(" TODO: make this work on Windows ")
            sys.exit(1)
        elif platform.system() == 'Linux':
            c = c + 'export OSFONTDIR="/usr/share/fonts//;$HOME/.fonts" && '
        else:
            print(" No idea what platform I'm on...")
            sys.exit(1)
        c = c + 'mtxrun --script fonts --reload && '
        c = c + 'pushd "' + self.tempDir + '" && context bible.tex && cp bible.pdf "' + self.outputFileName + '" && popd'
        self.logger.debug(c)
        self.runscript(c, '    ')


    #
    #   Support
    #

    def startNarrower(self, n):
        s = '}' if self.narrower else '\n\\blank[medium] '
        self.narrower = True
        s = s + '\n\\noindentation \\Q{' + str(n) + '}{'
        self.doNB = True
        return s

    def stopNarrower(self):
        s = '}\n\\blank[medium] ' if self.narrower else ''
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
                 if s[i] == ',' or s[i] == ';' or s[i] == '(' or s[i:i+3] == 'and':
                     return '{\sc ' + s[:i+1] + '}' + s[i+1:]
             else: # look for space
                 if s[i] == ' ':
                     return '{\sc ' + s[:i] + '}' + s[i:]
             i = i + 1
         return '{\sc ' + s + '}'

    def startLI(self):
        if self.printerState['li'] == False:
            self.printerState['li'] = True
            #return u'\startitemize \item '
            return r'\startexdent '
        else:
            #return u'\item '
            return r'\par '

    def stopLI(self):
        if self.printerState['li'] == False:
            return ''
        else:
            self.printerState['li'] = False
            #return u'\stopitemize'
            return r'\stopexdent '

    def startD(self):
        if self.printerState['d'] == False:
            self.printerState['d'] = True
        return '\par {\startalignment[middle] \em '

    def stopD(self):
        if self.printerState['d'] == False:
            return ''
        else:
            self.printerState['d'] = False
            return '\stopalignment }'

    def startM(self):
        r = self.stopD() + self.stopLI() + self.stopNarrower()
        self.printerState['m'] = True
        return r + r'\par {\startalignment[flushleft] '

    def stopM(self):
        if self.printerState['m'] == False:
            return ''
        else:
            self.printerState['m'] = False
            return '\stopalignment }'

    def newLine(self):
        s = '\n\par \n'
        if self.doNB:
            self.doNB = False
            self.justDidNB = True
            s = s + r'\noindentation '
        elif self.justDidNB:
            self.justDidNB = False
            s = s + r'\indentation '
        return s


    #
    #   Tokens
    #

    def render_id(self, token):      self.f.write( self.stopNarrower() + '\n\n' + r"\marking[RAChapter]{ } \marking[RABook]{ } \marking[RASection]{ }" )
    def render_h(self, token):       self.f.write( '\n\n\RAHeader{' + token.value + '}\n')
    def render_mt1(self, token):     self.f.write( self.stopLI() + self.stopNarrower() + '\n\MT{' + token.value + '}\n')
    def render_mt2(self, token):     self.f.write( self.stopLI() + self.stopNarrower() + '\n\MTT{' + token.value + '}\n')
    def render_mt3(self, token):     self.f.write( self.stopLI() + self.stopNarrower() + '\n\MTTT{' + token.value + '}\n')
    def render_ms(self, token):      self.markForSmallCaps() ; self.f.write(self.stopNarrower() + '\n\MS{' + token.value + '}\n') ; self.doNB = True
    def render_ms2(self, token):     self.doNB = True; self.markForSmallCaps() ; self.f.write( self.stopNarrower() + '\n\MSS{' + token.value + '}' + self.newLine() )
    def render_p(self, token):       self.f.write( self.stopM() + self.stopD() + self.stopLI() + self.stopNarrower() + self.newLine() )
    def render_b(self, token):       self.f.write( self.stopM() + self.stopD() + self.stopLI() + self.stopNarrower() + '\\blank \n' )
    def render_s1(self, token):      self.f.write( self.stopM() + self.stopD() + self.stopLI() + self.stopNarrower() +  '\n\\blank[big] ' + '\n\MSS{' + token.getValue() + '}' + self.newLine() ) ; self.doNB = True
    def render_s2(self, token):      self.doNB = True; self.f.write( self.stopM() + self.stopD() + self.stopLI() + self.stopNarrower() + '\n\\blank[big] ' + '\n\MSS{' + token.value + '}' + self.newLine() )
    def render_c(self, token):
        self.doChapterOrVerse = '\C{' + token.value + '} '
        self.f.write( ' ' )
    def render_v(self, token):
        if not token.value == '1':
            self.doChapterOrVerse =  '\V{' + token.value + '} '
        self.f.write( ' ' )
    def render_wj_s(self, token):     self.f.write( " " )
    def render_wj_e(self, token):     self.f.write( " " )
    def render_text(self, token):
        s = self.escapeText(token.value)
        if self.smallcaps and not self.doChapterOrVerse == '':
            s = self.renderSmallCaps(s)
            s = self.doChapterOrVerse + s
            self.doChapterOrVerse = ''
        elif not self.doChapterOrVerse == '':
            i = s.find(' ')
            if i == -1:
                # No space found - try end
                i = len(s)
            s = s[:i] + self.doChapterOrVerse + s[i+1:]
            self.doChapterOrVerse = ''
        elif self.smallcaps:
            s = self.renderSmallCaps(s)
        if self.justDidLORD:
            if s[0].isalpha(): s = ' ' + s
            self.justDidLORD = False
        self.f.write( s )
    def render_q(self, token):       self.render_q1(token)
    def render_q1(self, token):      self.f.write( self.stopD() + self.stopLI() + self.startNarrower(1) )
    def render_q2(self, token):      self.f.write( self.stopD() + self.stopLI() + self.startNarrower(2) )
    def render_q3(self, token):      self.f.write( self.stopD() + self.stopLI() + self.startNarrower(3) )
    def render_nb(self, token):      self.doNB = True ; self.f.write( self.stopD() + self.stopLI() + self.stopNarrower() + '\\blank[medium] ' + self.newLine() )
    def render_f_s(self, token):     self.f.write( '\\footnote{' )
    def render_f_e(self, token):     self.f.write( '} ' )
    def render_em_s(self, token):    self.f.write( '{\em ' )
    def render_em_e(self, token):    self.f.write( '} ' )
    def render_add_s(self, token):   self.f.write( '{\em ' )
    def render_add_e(self, token):   self.f.write( '} ' )

    # Don't render in SC when in header
    def render_nd_s(self, token):
        if not self.printerState['d']:
            self.f.write( '{\sc ' )
    def render_nd_e(self, token):
        if not self.printerState['d']:
            self.justDidLORD = True; self.f.write( '}' )

    def render_li(self, token):      self.f.write( self.startLI() )
    def render_d(self, token):       self.f.write( self.startD() )
    def render_sp(self, token):      self.f.write( self.startD() )
    def render_pbr(self, token):     self.f.write( ' \\\\ ' )
    def render_fr(self, token):      self.f.write( ' ' + token.getValue() + ' ' )
    def render_fr_e(self, token):    self.f.write( ' ' )
    def render_fk(self, token):      self.f.write( ' ' + token.getValue() + ' ' )
    def render_ft(self, token):      self.f.write( ' ' + token.getValue() + ' ' )
    def render_pi(self, token):      self.render_q(token)

    def render_is1(self, token):    self.render_s1(token)
    def render_ip(self, token):     self.render_p(token)
    def render_iot(self, token):    self.render_q(token)
    def render_io1(self, token):    self.render_q2(token)

    def render_qs_s(self, token):   self.f.write( '{\em ' )
    def render_qs_e(self, token):   self.f.write( '} ' )


    def render_pb(self, token):     self.f.write('\page ')

    def render_m(self, token):      self.f.write( self.stopM() + self.startM() )

    def render_periph(self, token):
        if token.getValue() == 'Table of Contents':
            self.f.write("""
            \page[right]
            \par ~
            {\midaligned {\WORD{Table of Contents}}}
            \par ~
            \placelist[chapter][criterium=all]

            """)
    #
    #   Introductory codes
    #

    rawIntroTeXt = r"""
    \definemarking[RAChapter]
    \definemarking[RABook]
    \definemarking[RASection]

    \definepapersize [Trade][width=6in, height=9in]
    \setuppapersize [Trade][Trade]

    %\definepapersize [TwoTrade][width=12in, height=9in]
    %\setuppapersize [Trade][TwoTrade]
    %\setuparranging [2UP] % page numbering doesn't work this way
 
    \setuppagenumbering [alternative={{{layout}}}]
   
    {{{setuplayout}}}

    \definefontfamily [myfamily] [serif] [{{{bodyFont}}}]
    \definefontfeature
      [default]
      [default]
      [protrusion=quality,expansion=quality]
    \setupalign[hz,hanging]
    \setupbodyfont [myfamily, {{{bodyFontSize}}}]
    
    \setupbodyfontenvironment[default][em=italic]

    \setuppagenumbering[location=]
    \setupheadertexts[{\em \getmarking[RASection]}][{\getmarking[RABook] ~\getmarking[RAChapter]}]
    \setupfootertexts[pagenumber][]

    % Hide chapters but keep in TOC
    \setuphead[chapter][placehead=hidden,
                        incrementnumber=yes,  % keep track of the number
                        number=no]            % but don't show it
    \setuptexttexts[{\placerawheaddata[chapter]}]

    \setupspacing[packed]   % normal word space at the end of sentences
    \setupwhitespace[none]  % no space between paragraphs
    \setupindenting[small, yes]
    \setupinterlinespace[line=13pt] % Line spacing

    \setuphead[section][number=no, textstyle=em, before=\blank, after=\blank, align={middle, nothyphenated, verytolerant}]

    %\setuplist[chapter][alternative=c]

    \setupnote[footnote][way=bypage]

    \define[1]\V{\setupinmargin[style=small,stack=yes]{{{position}}}{#1}}
    \define[1]\C{\setupinmargin[style=bold,stack=yes]{{{position}}}{#1}\marking[RAChapter]{#1}}
    \define[1]\S{\par ~ \par \section{#1} \marking[RASection]{#1} \par }
    \define[1]\MS{\par ~ \par \section{#1} \marking[RASection]{#1} \par }
    \define[1]\MSS{\par ~ \par \section{#1} \marking[RASection]{#1} \par }
    \define[1]\SS{\blank{\midaligned{\em #1}}\blank}
    \define[1]\MT{  {\midaligned{\tfd{\WORD{#1}}}}\blank ~ } 
    \define[1]\MTT{ {\midaligned{\tfd{\WORD{#1}}}}\blank ~ }
    \define[1]\MTTT{ {\midaligned{\tfd{#1}}}\blank ~ }
    \define[1]\RAHeader{\page[right] \chapter{#1} \marking[RABook]{#1} }
    \define[2]\Q{\startnarrower[#1*left,1*right] #2\stopnarrower }
    
    \emergencystretch\maxdimen
    
    \definestartstop
      [exdent]
      [before={\startnarrower[left]\setupindenting[-\leftskip,yes]},
       after=\stopnarrower]

    % \showframe
    \starttext
    % \showlayout
    {{{coverPage}}}
    """

    closeTeXt = r"""
    \stoptext
    """
