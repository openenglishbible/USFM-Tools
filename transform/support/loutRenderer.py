# -*- coding: utf-8 -*-
#

import codecs

import abstractRenderer
import books


#
#   Renders using Lout (TeX alternative)
#

class LoutRenderer(abstractRenderer.AbstractRenderer):
    
    def __init__(self, inputDir, outputFilename):
        # Unset
        self.f = None  # output file stream
        # IO
        self.outputFilename = outputFilename
        self.inputDir = inputDir
        # Position
        self.cb = ''    # Current Book
        self.cc = '001'    # Current Chapter
        self.cv = '001'    # Currrent Verse
        self.indentFlag = False
        self.bookName = ''
        self.inChapter = False
        self.inSections = False
        self.inSection = False
        self.startTextType = 'drop' # Or nomal or smallcaps
        self.inDropCap = False
        self.inPoetry = False
        self.registerForNextText = ''
        self.inD = False
        self.afterLord = False
        
    def render(self):
        self.f = open(self.outputFilename, 'w')
        self.f.write(r"""@Include { oebbook } 
@Book
    @Title {}
    @Author {}
    @Edition {}
    @Publisher {}
    @BeforeTitlePage {}
    @OnTitlePage {}
    @AfterTitlePage {}
    @AtEnd {}
    @InitialLanguage { English } 
    @PageOrientation { Portrait } 
    @PageHeaders { Titles } 
    @ColumnNumber { 1 } 
    @FirstPageNumber { 1 } 
    @IntroFirstPageNumber { 1 } 
    @OptimizePages { No } 
    @GlossaryText { @Null } 
    @IndexText { @Null }
    @IndexAText { @Null }
    @IndexBText { @Null } 
//

""".encode('utf-8'))
        self.loadUSFM(self.inputDir)
        self.run()
        self.f.close()
        
    def write(self, unicodeString):
        self.f.write(unicodeString + '\n')
                
    #   SUPPORT
    #
    #
    def escape(self, s, upper=False):
        if upper:
            t = s.upper()
        else:
            t = s
        t = t.replace('“', '{@Char quotedblleft}').replace('”', '{@Char quotedblright}').replace('—', '{@Char emdash}').replace('‘', '{@Char quoteleft}').replace('’', '{@Char quoteright}').replace('"', '{@Char quotedbl}')
        #t = t.replace(u'"', u'{@Char quotedbl}')
        #t = t.replace(u'’', u'{@Char quoteright}')
        return t
         
    def close(self):
        self.closeChapter()
    
    def closeChapter(self):
        self.closeSections()
        if self.inChapter:          # We need to close previous chapter (ie Book)
            self.inChapter = False
            self.write('\n@End @Chapter\n')   
            
    def closeSections(self):
        self.closeSection()
        if self.inSections:          # We need to close previous section 
            self.inSections = False
            self.write('\n@EndSections\n')   
            
    def closeSection(self):
        self.closeDropCap()
        self.closePoetry()
        if self.inSection:          # We need to close previous section 
            self.inSection = False
            self.write('\n@End @Section\n')  

    def closeDropCap(self):
        if self.inDropCap:          # We need to close previous section 
            self.inDropCap = False
            self.write('}')  
            
    def closeD(self):
        if self.inD:          # We need to close the D 
            self.inD = False
            self.write('}}')  
        
    def closePoetry(self):
        if self.inPoetry:
            self.inPoetry = False
 
    def writeIndent(self, level):
        self.closeD()
        self.closeDropCap()
        if not self.inPoetry:
            self.write('\n@DP ') 
            self.inPoetry = True
        else:
            self.write('\n@LLP ') 
        self.write('~ ~ ~ ~' * level)   
        
    def formatText(self, text):
        t = text
        if len(t) < 60: self.startTextType = 'normal'  # Don't do funky things with short first lines.

        # Handle poetry lines that want to wrap
        if self.inPoetry and len(t) > 60:
            n = t.find(' ', 50) # Give us buffer
            t = t[:n] + '\n@LLP ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ' + t[n:]

        if self.cb == '019': self.startTextType = 'normal'  # Don't do funky things with Psalms.
        if self.startTextType == 'drop':
            self.inDropCap = True
            self.write(t[0] + ' @DropCapTwo {')
            self.write(self.escape(self.smallCapText(t[1:])))
        elif self.startTextType == 'smallcaps':
            self.write(self.escape(self.smallCapText(t)))
        else:
            if self.afterLord and not (t[0] == "'" or t[0] == ',' or t[0] == '?'):
                self.afterLord = False
                t = ' ' + t
            self.write(self.escape(self.addNextText(t)))
        self.write(' ')
        self.startTextType = 'normal'
        
    def addNextText(self, text):
        t = text
        if not self.registerForNextText == '':
            try:
                i = t.index(' ')
                t = t[:i] + self.registerForNextText + ' ' + t[i+1:]
            except Exception:
                t = self.registerForNextText + t                
            self.registerForNextText = ''
        return t        

    def smallCapText(self, s):
         i = 0
         while i < len(s):
             if i < 60:  #we are early, look for comma
                 if s[i] == ',' or s[i] == ';' or s[i] == '.' or s[i] == '—':
                     return '{@S {' + self.addNextText(s[:i+1]) + '}} ' + s[i+1:]
                 i = i + 1
             else: # look for space
                 if s[i] == ' ':
                     return '{@S {' + self.addNextText(s[:i]) + '}}' + s[i:]
                 i = i + 1
         return self.addNextText(s)     
         
    def newPara(self, indent = True, outdent=False):
        # Don't indent at start of books
        if self.startTextType == 'drop': indent = False 
        if self.startTextType == 'smallcaps': indent = False 
        
        self.closeDropCap()
        if self.inPoetry:
            self.closePoetry()
            self.write('\n\n@DP ~\n')
        else:
            if outdent:
                self.write('\n\noutdent @Break { @PP }\n')
            elif indent:
                self.write('\n\n@PP\n')
            else:
                self.write('\n\n@LP\n')
            
    #   TOKENS
    #
    #
    def render_id(self, token): 
        self.cb = books.bookKeyForIdValue(token.value)
        self.indentFlag = False
        self.closeChapter()
    def render_id_e(self, token):
        pass
    def render_h(self, token):   
        self.close()    
        self.bookname = token.value
        self.write('\n@Chapter @Title { ' + self.escape(token.value) + ' } @RunningTitle { ' + self.bookname + ' } @Begin')
        self.inChapter = True
    def render_mt(self, token): 
        self.write('\n@Display  { 21p } @Font { ' + self.escape(token.value, upper=True) + '}')
        self.startTextType = 'drop'
    def render_mt2(self, token): 
        self.write('\n@Display  { 13p } @Font { ' + self.escape(token.value, upper=True) + '}')
    def render_mt3(self, token): 
        self.write('\n@Display  { 13p } @Font { ' + self.escape(token.value, upper=True) + '}')
    def render_ms(self, token):
        self.closeSection()
        if not self.inSections: self.write('@BeginSections '); self.inSections = True
        self.write('\n@Section @Title {' + self.escape(token.value) + '} @Begin @LP\n')
        self.inSection = True
        if self.startTextType == 'normal': self.startTextType = 'smallcaps'
    def renderMS2(self, token):
        self.write('\n@Display @Heading {' + self.escape(token.value) + '}\n')
    def render_p(self, token):
        self.newPara()
    def render_pi(self, token):
        self.newPara(outdent = True)
    def render_s1(self, token): 
        self.closePoetry();
        self.closeDropCap(); 
        self.write('\n@DP @CNP @Display @Heading {' + self.escape(token.value) + '}\n') 
    def render_s2(self, token):
        self.closeDropCap(); 
        self.write('\n\n@DP\n')
    def render_c(self, token):
        self.cc = token.value.zfill(3)
        self.registerForNextText = ' {@OuterNote { 10.5p @Font {@B ' + token.value + '}}}'
    def render_v(self, token):
        self.cv = token.value.zfill(3)
        if not self.cv == '001':   self.registerForNextText = ' {@OuterNote { 8p @Font {' + token.value + '}}}'
    def render_text(self, token):    self.formatText(token.value)
    def render_q(self, token):       self.writeIndent(1)
    def render_q1(self, token):      self.writeIndent(1)
    def render_q2(self, token):      self.writeIndent(2)
    def render_q3(self, token):      self.writeIndent(3)
    def render_nb(self, token):      self.newPara(indent = False)
    def render_b(self, token):       self.newPara(indent = False); self.inPoetry = True
    def render_f_s(self, token):      self.write('@FootNote { ')
    def render_f_e(self, token):      self.write(' }')
    def render_i_s(self, token):      self.write('{@I {')
    def render_i_e(self, token):      self.write('}}')
    def render_nd_s(self, token):     self.write('{@S {')
    def render_nd_e(self, token):     self.write('}}'); self.afterLord = True
    def render_pbr(self, token):     self.write('@LLP ')
    def render_sc_s(self, token):     self.write('{@B {')
    def render_sc_e(self, token):     self.write('}}')
    def render_d(self, token):       self.write('{@I {'); self.inD = True


   