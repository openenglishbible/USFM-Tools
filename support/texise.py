import re
import os
import parseUsfm
import books
import datetime

class TexPrinter(object):
    def __init__(self):
        self.printerState = {u'li': False, u'd': False}
        self.smallCapSections = True  # Sometimes we don't want to do this, like for Psalms
        self.justDidLORD = False
        self.justDidNB = False
        self.doNB = False
        self.narrower = False
        self.doChapterOrVerse = u''
        self.smallcaps = False

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
                    
    def renderID(self, token):      return u''
    def renderIDE(self, token):     return u''
    def renderH(self, token):       return u'\n\n\RAHeader{' + token.value + u'}\n'
    def renderMT(self, token):      return self.stopLI() + self.stopNarrower() + u'\n\MT{' + token.value + u'}\n'
    def renderMT2(self, token):     return self.stopLI() + self.stopNarrower() + u'\n\MTT{' + token.value + u'}\n'
    def renderMS(self, token):      self.markForSmallCaps() ; r = self.stopNarrower() + u'\n\MS{' + token.value + u'}\n' ; self.doNB = True; return r
    def renderMS2(self, token):     self.doNB = True; self.markForSmallCaps() ; return self.stopNarrower() + u'\n\MSS{' + token.value + '}' + self.newLine()
    def renderP(self, token):       return self.stopD() + self.stopLI() + self.stopNarrower() + self.newLine() 
    def renderB(self, token):       return self.stopD() + self.stopLI() + self.stopNarrower() + u'\\blank \n'
    def renderS(self, token):       r = self.stopD() + self.stopLI() + self.stopNarrower() +  u'\n\\blank[big] ' + u'\n\MSS{' + token.getValue() + '}' + self.newLine() ; self.doNB = True; return r
    def renderS2(self, token):      self.doNB = True; return self.stopD() + self.stopLI() + self.stopNarrower() + u'\n\\blank[big] ' + u'\n\MSS{' + token.value + '}' + self.newLine() 
    def renderC(self, token):
        self.doChapterOrVerse = u'\C{' + token.value + u'}'
        return u' '
    def renderV(self, token):
        if not token.value == u'1':
            self.doChapterOrVerse =  u'\V{' + token.value + u'}'
        return ' '
    def renderWJS(self, token):     return u" "
    def renderWJE(self, token):     return u" "
    def renderTEXT(self, token):
        s = self.escapeText(token.value)
        if self.smallcaps and not self.doChapterOrVerse == u'':
            s = self.renderSmallCaps(s)
            #i = s.find(u'}')
            #s = s[:i+1] + self.doChapterOrVerse + s[i+1:]
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
        return s
    def renderQ(self, token):       return self.stopD() + self.stopLI() + self.startNarrower(1)
    def renderQ1(self, token):      return self.stopD() + self.stopLI() + self.startNarrower(1)
    def renderQ2(self, token):      return self.stopD() + self.stopLI() + self.startNarrower(2)
    def renderQ3(self, token):      return self.stopD() + self.stopLI() + self.startNarrower(3)
    def renderNB(self, token):      self.doNB = True ; return self.stopD() + self.stopLI() + self.stopNarrower() + u'\\blank[medium] ' + self.newLine() 
    def renderQTS(self, token):     return u''
    def renderQTE(self, token):     return u''
    def renderFS(self, token):      return u'\\footnote{'
    def renderFE(self, token):      return u'} '
    def renderIS(self, token):      return u'{\em '
    def renderIE(self, token):      return u'} '
    def renderADDS(self, token):    return u'{\em '
    def renderADDE(self, token):    return u'} '
    def renderNDS(self, token):     return u'{\sc '
    def renderNDE(self, token):     self.justDidLORD = True; return u'}'
    def renderLI(self, token):      return self.startLI()
    def renderD(self, token):       return self.startD()
    def renderSP(self, token):      return self.startD()
    def renderPBR(self, token):     return u' \\\\ '
    def renderTOC2(self, token):    return u''
    def renderR(self, token):       return u''
    def renderFR(self, token):      return u' ' + token.getValue() + u' '
    def renderFRE(self, token):     return u' '
    def renderFK(self, token):      return u' ' + token.getValue() + u' '
    def renderFT(self, token):      return u' ' + token.getValue() + u' '
    def renderXS(self, token):      return u'\\footnote{'
    def renderXE(self, token):      return u'} '
    def renderXO(self, token):      return u''
    def renderXT(self, token):      return u''
    def renderM(self, token):       return u''
    def renderMI(self, token):      return u''
    def renderPI(self, token):      return self.renderQ(token)
    def renderTLS(self, token):     return u''
    def renderTLE(self, token):     return u''
    def renderSCS(self, token):     return u''
    def renderSCE(self, token):     return u''
    def renderXDCS(self, token):    return u''
    def renderXDCE(self, token):    return u''
    def renderD(self, token):       return u'' # For now
    def renderREM(self, token):     return u'' # This is for comments in the USFM

class TransformToContext(object):
    
    texPrinter = None

    def translateBook(self, usfm, smallCap):
        
        tokens = parseUsfm.parseString(usfm)
        
        s = u''
        self.texPrinter.smallCapSections = smallCap
        for t in tokens: s = s + t.renderOn(self.texPrinter)
        s = s + self.texPrinter.stopNarrower()
        s = s + u"\marking[RAChapter]{ } \marking[RABook]{ } \marking[RASection]{ }"

        return s

        
    def stripUnicodeHeader(self, unicodeString):
        if unicodeString[0] == u'\ufeff':
            return unicodeString[1:]
        else:
            return unicodeString

    def saveAll(self, allBooks):

        s = unicode(r"""

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
        \define[1]\MSS{{\midaligned{\em #1}}}
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
        \page[right] % Cover page
        \page[left]
        Open English Bible. 
        \par Built """ + datetime.date.today().strftime("%A, %d %B %Y") + '. \par Version: ' + self.buildName + r"""     
        \page[right]
        \par ~
        {\midaligned {\tfc{\WORD{Table of Contents}}}}
        \par ~
        \placelist[chapter]
        """, 'ascii') + allBooks + ur"""

        \stoptext

        """

        f = open(self.outputDir + '/Bible.tex', 'w')
        f.write(s.encode('utf-8'))
        f.close()

    def loadBooks(self, path):
        books = {}
        dirList=os.listdir(path)
        for fname in dirList:
          if fname[-5:] == '.usfm':
              f = open(path + '/' + fname)
              usfm = f.read().decode('utf-8-sig')
              books[self.bookID(usfm)] = usfm
              f.close()
        return books

    def bookID(self, usfm):
        return books.bookID(usfm)

    def setupAndRun(self, patchedDir, outputDir, buildName, smallCap = True):
        self.outputDir = outputDir
        self.patchedDir = patchedDir
        self.buildName = buildName
        self.booksUsfm = self.loadBooks(patchedDir)
        self.texPrinter = TexPrinter()

        bookTex = u''

        for bookName in books.silNames:
            if self.booksUsfm.has_key(bookName):
                bookTex = bookTex + self.translateBook(self.booksUsfm[bookName], smallCap)
                print '      (' + bookName + ')'
        self.saveAll(bookTex)