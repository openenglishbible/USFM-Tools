import sys
import os

# Set Path for files in support/
rootdiroftools = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(rootdiroftools,'support'))

#from subprocess import Popen, PIPE, call
import subprocess
import getopt

import readerise
import mediawikiPrinter

import asciiRenderer
import csvRenderer
import mdRenderer
import contextRenderer
import singlehtmlRenderer
import loutRenderer
import htmlRenderer

def runscriptold(c, prefix=''):
    print prefix + ':: ' + c
    pp = Popen(c, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    for ln in pp.stdout:
        print prefix + ln[:-1]

def runscript(c, prefix='', repeatFilter = ''):
    print prefix + ':: ' + c
    pp = subprocess.Popen([c], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    (result, stderrdata) = pp.communicate()
    print result
    print stderrdata
    if not repeatFilter == '' and not stderrdata.find(repeatFilter) == -1:
        runscript(c, prefix, repeatFilter)

def setup():
    c = """
    cd support/thirdparty
    rm -rf context
    mkdir context
    cd context
    curl -o first-setup.sh http://minimals.contextgarden.net/setup/first-setup.sh
    sh ./first-setup.sh
    . ./tex/setuptex
    cd ..
    curl -o usfm2osis.pl http://crosswire.org/ftpmirror/pub/sword/utils/perl/usfm2osis.pl
    """
    runscript(c)

def buildLout(usfmDir, builtDir, buildName):
 
    print '#### Building Lout...'

    # Prepare
    print '     Clean working dir'
    runscript('rm working/lout/*', '       ')

    # Convert to Lout
    print '     Converting to Lout'
    ensureOutputDir('working/lout')
    c = loutRenderer.LoutRenderer(usfmDir, 'working/lout/' + buildName + '.lout')
    c.render()
    
    # Run Lout
    print '     Copying support files'
    runscript('cp support/lout/oebbook working/lout', '       ')
    print '     Running Lout'
    runscript('cd working/lout; lout ./' + buildName + '.lout > ' + buildName + '.ps', '       ', repeatFilter='unresolved cross reference')
    print '     Running ps2pdf'
    runscript('cd working/lout; ps2pdf -dDEVICEWIDTHPOINTS=432 -dDEVICEHEIGHTPOINTS=648 ' + buildName + '.ps ' + buildName + '.pdf ', '       ')
    print '     Copying into builtDir'
    runscript('cp working/lout/' + buildName + '.pdf ' + builtDir + '/' + buildName + '.pdf ', '       ')

def buildConTeXt(usfmDir, builtDir, buildName):

    print '#### Building PDF via ConTeXt...'

    # Convert to ConTeXt
    print '     Converting to ConTeXt...'
    #c = texise.TransformToContext()
    #c.setupAndRun(usfmDir, 'working/tex', buildName)
    ensureOutputDir(builtDir)
    c = contextRenderer.ConTeXtRenderer(usfmDir, 'working/tex/bible.tex')
    c.render()

    # Build PDF
    print '     Building PDF..'
    c = """. ./support/thirdparty/context/tex/setuptex ; cd working/tex-working; rm * ; context ../tex/bible.tex; cp bible.pdf ../../""" + builtDir + '/' + buildName + '.pdf'
    runscript(c, '     ')

def buildWeb(usfmDir, builtDir, buildName):
    # Convert to HTML
    print '#### Building HTML...'
    ensureOutputDir(builtDir + '/' + buildName + '_html')
    c = htmlRenderer.HTMLRenderer(usfmDir, builtDir + '/' + buildName + '_html')
    c.render()

def buildSingleHtml(usfmDir, builtDir, buildName):
    # Convert to HTML
    print '#### Building HTML...'
    ensureOutputDir(builtDir)
    c = singlehtmlRenderer.SingleHTMLRenderer(usfmDir, builtDir + '/' + buildName + '.html')
    c.render()

def buildCSV(usfmDir, builtDir, buildName):
    # Convert to CSV
    print '#### Building CSV...'
    ensureOutputDir(builtDir)
    c = csvRenderer.CSVRenderer(usfmDir, builtDir + '/' + buildName + '.csv')
    c.render()

def buildReader(usfmDir, builtDir, buildName):
    # Convert to HTML for online reader
    print '#### Building for Reader...'
    ensureOutputDir(builtDir + 'en_oeb')
    c = readerise.TransformForReader()
    c.setupAndRun(usfmDir, builtDir + 'en_oeb')

def buildMarkdown(usfmDir, builtDir, buildName):
    # Convert to Markdown for Pandoc
    print '#### Building for Markdown...'
    ensureOutputDir(builtDir)
    c = mdRenderer.MarkdownRenderer(usfmDir, builtDir + '/' + buildName + '.md')
    c.render()

def buildASCII(usfmDir, builtDir, buildName):
    # Convert to ASCII
    print '#### Building for ASCII...'
    c = asciiRenderer.ASCIIRenderer(usfmDir, builtDir + '/' + buildName + '.txt')
    c.render()

def buildMediawiki(usfmDir, builtDir, buildName):
    # Convert to MediaWiki format for Door43
    print '#### Building for Mediawiki...'
    # Check output directory
    ensureOutputDir(builtDir + '/mediawiki')
    mediawikiPrinter.Transform().setupAndRun(usfmDir, builtDir + '/mediawiki')

def ensureOutputDir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

savedCWD = ''
def saveCWD():    global savedCWD ; savedCWD = os.getcwd() ; os.chdir(rootdiroftools)
def restoreCWD(): os.chdir(savedCWD)
    
def main(argv):
    saveCWD()    
    print '#### Starting Build.'
    try:
        opts, args = getopt.getopt(argv, "sht:u:b:n:", ["setup", "help", "target=", "usfmDir=", "builtDir=", "name="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            return usage()
        elif opt in ("-s", "--setup"):
            return setup()
        elif opt in ("-t", "--target"):
            targets =  arg
        elif opt in ("-u", "--usfmDir"):
            usfmDir = arg
        elif opt in ("-b", "--builtDir"):
            buildDir = arg
        elif opt in ("-n", "--name"):
            buildName = arg
        else:
            usage()

    if targets == 'context':
        buildConTeXt(usfmDir, buildDir, buildName)
    elif targets == 'html':
        buildWeb(usfmDir, buildDir, buildName)
    elif targets == 'singlehtml':
        buildSingleHtml(usfmDir, buildDir, buildName)
    elif targets == 'md':
        buildMarkdown(usfmDir, buildDir, buildName)
    elif targets == 'reader':
        buildReader(usfmDir, buildDir, buildName)
    elif targets == 'mediawiki':
        buildMediawiki(usfmDir, buildDir, buildName)
    elif targets == 'lout':
        buildLout(usfmDir, buildDir, buildName)
    elif targets == 'csv':
        buildCSV(usfmDir, buildDir, buildName)
    elif targets == 'ascii':
        buildASCII(usfmDir, buildDir, buildName)
    elif targets == 'csv':
        buildCSV(usfmDir, buildDir, buildName)
    else:
        usage()

    print '#### Finished.'
    restoreCWD()

def usage():
    print """
        USFM-Tools
        ----------

        Build script.  See source for details.
        
        Setup:
        transform.py --setup 
        
    """

if __name__ == "__main__":
    main(sys.argv[1:])