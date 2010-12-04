import sys
sys.path.append("support")

from subprocess import Popen, PIPE
import getopt

import patch
import texise
import htmlise
import readerise
import markdownise

def runscript(c, prefix=''):
    pp = Popen(c, shell=True, stdout=PIPE)
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
    """
    runscript(c)


def buildAll(usfmDir, buildDir):

    buildPDF(usfmDir, buildDir)
    buildWeb(usfmDir, buildDir)
    buildReader(usfmDir, buildDir)
    buildMarkdown(usfmDir, buildDir)

def buildPDF(usfmDir, builtDir):

    print '#### Building PDF...'

    # Convert to ConTeXt
    print '     Converting to TeX...'
    c = texise.TransformToContext()
    c.setupAndRun(usfmDir, 'preface', 'working/tex')

    # Build PDF
    print '     Building PDF..'
    c = """. ./support/thirdparty/context/tex/setuptex ; cd working/tex-working; rm * ; context ../tex/Bible.tex; cp *.pdf ../../""" + builtDir + '/'
    runscript(c, '     ')

def buildWeb(usfmDir, builtDir):
    # Convert to HTML
    print '#### Building HTML...'
    c = htmlise.TransformToHTML()
    c.setupAndRun(usfmDir, 'preface', builtDir)

def buildReader():
        # Convert to HTML
        print '#### Building for Reader...'
        c = readerise.TransformForReader()
        c.setupAndRun('usfmDir', 'preface', builtDir + '/reader')

def buildMarkdown():
        # Convert to HTML
        print '#### Building for Markdown...'
        c = markdownise.TransformToMarkdown()
        c.setupAndRun('usfmDir', 'preface', builtDir)

def main(argv):
    print '#### Starting Build.'
    try:
        opts, args = getopt.getopt(argv, "sht:u:b:", ["setup", "help", "target=", "usfmDir=", "builtDir="])
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
        else:
            usage()

    if targets == 'all':
        buildAll(usfmDir, buildDir)
    elif targets == 'pdf':
        buildPDF(usfmDir, buildDir)
    elif targets == 'html':
        buildWeb(usfmDir, buildDir)
    elif targets == 'txt':
        buildMarkdown(usfmDir, buildDir)
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