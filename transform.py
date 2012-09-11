import sys
sys.path.append("support")

import os

#from subprocess import Popen, PIPE, call
import subprocess
import getopt

import texise
import htmlise
import readerise
import markdownise
import mediawikiPrinter
import singlehtmlise
import loutise
import csvise
import asciiPrinter

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
    c = loutise.TransformToLout()
    c.setupAndRun(usfmDir, 'working/lout/', buildName + '.lout')
    
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

    print '#### Building PDF...'

    # Convert to ConTeXt
    print '     Converting to ConTeXt...'
    c = texise.TransformToContext()
    c.setupAndRun(usfmDir, 'working/tex', buildName)

    # Build PDF
    print '     Building PDF..'
    c = """. ./support/thirdparty/context/tex/setuptex ; cd working/tex-working; rm * ; context ../tex/Bible.tex; cp Bible.pdf ../../""" + builtDir + '/' + buildName + '.pdf'
    runscript(c, '     ')

def buildWeb(usfmDir, builtDir, buildName):
    # Convert to HTML
    print '#### Building HTML...'
    c = htmlise.TransformToHTML()
    ensureOutputDir(builtDir + '/simple')
    c.setupAndRun(usfmDir, 'preface', builtDir + '/simple')

def buildSingleHtml(usfmDir, builtDir, buildName):
    # Convert to HTML
    print '#### Building HTML...'
    c = singlehtmlise.TransformToHTML()
    ensureOutputDir(builtDir)
    c.setupAndRun(usfmDir, 'preface', builtDir, buildName + '.html')

def buildCSV(usfmDir, builtDir, buildName):
    # Convert to CSV
    print '#### Building CSV...'
    c = csvise.TransformToCSV()
    ensureOutputDir(builtDir)
    c.setupAndRun(usfmDir, builtDir, buildName + '.csv')

def buildReader(usfmDir, builtDir, buildName):
    # Convert to HTML for online reader
    print '#### Building for Reader...'
    ensureOutputDir(builtDir + 'en_oeb')
    c = readerise.TransformForReader()
    c.setupAndRun(usfmDir, builtDir + 'en_oeb')

def buildMarkdown(usfmDir, builtDir, buildName):
        # Convert to Markdown
        print '#### Building for Markdown...'
        c = markdownise.TransformToMarkdown()
        c.setupAndRun(usfmDir, builtDir, buildName + '.md')

def buildASCII(usfmDir, builtDir, buildName):
        # Convert to ASCII
        print '#### Building for ASCII...'
        c = asciiPrinter.TransformToASCII()
        c.setupAndRun(usfmDir, builtDir, buildName + '.txt')

def buildMediawiki(usfmDir, builtDir, buildName):
        # Convert to MediaWiki format for Door43
        print '#### Building for Mediawiki...'
        # Check output directory
        ensureOutputDir(builtDir + '/mediawiki')
        mediawikiPrinter.Transform().setupAndRun(usfmDir, builtDir + '/mediawiki')

def ensureOutputDir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def main(argv):
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
    else:
        usage()

    print '#### Finished.'

def usage():
    print """
        USFM-Tools
        ----------

        Build script.  See source for details.
        
        Requires lout and Context
        
    """

if __name__ == "__main__":
    main(sys.argv[1:])