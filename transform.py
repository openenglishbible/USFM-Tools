import sys
sys.path.append("support")

import os

from subprocess import Popen, PIPE
import getopt

import patch
import texise
import htmlise
import readerise
import markdownise
import mediawikiPrinter
import singlehtmlise

def runscript(c, prefix=''):
    pp = Popen(c, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    for ln in pp.stdout:
        print prefix + ln[:-1]

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

def buildAll(usfmDir, buildDir, buildName):

    buildPDF(usfmDir, buildDir, buildName)
    buildWeb(usfmDir, buildDir, buildName)
    buildReader(usfmDir, buildDir, buildName)
    buildMarkdown(usfmDir, buildDir, buildName)

def buildPDF(usfmDir, builtDir, buildName):

    print '#### Building PDF...'

    # Convert to ConTeXt
    print '     Converting to TeX...'
    c = texise.TransformToContext()
    c.setupAndRun(usfmDir, 'working/tex')

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

def buildReader(usfmDir, builtDir, buildName):
        # Convert to HTML for online reader
        print '#### Building for Reader...'
        ensureOutputDir(builtDir + '/assets/bib/en_oeb')
        c = readerise.TransformForReader()
        c.setupAndRun(usfmDir, 'preface', builtDir + '/assets/bib/en_oeb')

def buildMarkdown(usfmDir, builtDir, buildName):
        # Convert to Markdown
        print '#### Building for Markdown...'
        c = markdownise.TransformToMarkdown()
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

    if targets == 'all':
        buildAll(usfmDir, buildDir, buildName)
    elif targets == 'pdf':
        buildPDF(usfmDir, buildDir, buildName)
    elif targets == 'html':
        buildWeb(usfmDir, buildDir, buildName)
    elif targets == 'singlehtml':
        buildSingleHtml(usfmDir, buildDir, buildName)
    elif targets == 'text':
        buildMarkdown(usfmDir, buildDir, buildName)
    elif targets == 'reader':
        buildReader(usfmDir, buildDir, buildName)
    elif targets == 'mediawiki':
        buildMediawiki(usfmDir, buildDir, buildName)
    else:
        usage()

    print '#### Finished.'

def usage():
    print """
        USFM-Tools
        ----------

        Build script.

        -h or --help for options
        -s or --setup to setup up environment and load third party support
        
    """

if __name__ == "__main__":
    main(sys.argv[1:])