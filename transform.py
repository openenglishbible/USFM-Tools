import sys
import os
import importlib
import subprocess
import getopt

# LOGGING
import logging
logger = logging.getLogger('USFM Tools')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)    

# Set Path for files in support/
rootdiroftools = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(rootdiroftools,'support'))

#IMPORT MODULES (TO BE DEPRECATED)
import readerise
import mediawikiPrinter
import loutRenderer
import htmlRenderer

def runscript(c, prefix='', repeatFilter = ''):
    logging.debug(prefix + ':: ' + c)
    pp = subprocess.Popen([c], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    (result, stderrdata) = pp.communicate()
    print result
    print stderrdata
    if not repeatFilter == '' and not stderrdata.find(repeatFilter) == -1:
        runscript(c, prefix, repeatFilter)

def buildLout(usfmDir, builtDir, buildName):
 
    print '#### Building Lout...'

    # Prepare
    print '     Clean working dir'
    runscript('rm "' + builtDir + '/working/lout/*"', '       ')

    # Convert to Lout
    print '     Converting to Lout'
    ensureOutputDir(builtDir + '/working/lout')
    c = loutRenderer.LoutRenderer(usfmDir, builtDir + '/working/lout/' + buildName + '.lout')
    c.render()
    
    # Run Lout
    print '     Copying support files'
    runscript('cp support/lout/oebbook working/lout', '       ')
    print '     Running Lout'
    runscript('cd "' + builtDir + '/working/lout"; lout "./' + buildName + '.lout" > "' + buildName + '.ps"', '       ', repeatFilter='unresolved cross reference')
    print '     Running ps2pdf'
    runscript('cd "' + builtDir + '/working/lout"; ps2pdf -dDEVICEWIDTHPOINTS=432 -dDEVICEHEIGHTPOINTS=648 "' + buildName + '.ps" "' + buildName + '.pdf" ', '       ')
    print '     Copying into builtDir'
    runscript('cp "' + builtDir + '/working/lout/' + buildName + '.pdf" "' + builtDir + '/' + buildName + '.pdf" ', '       ')

def buildReader(usfmDir, builtDir, buildName, order="normal"):
    # Convert to js for online reader
    print '#### Building for Reader...'
    ensureOutputDir(builtDir + 'en_oeb')
    c = readerise.ReaderRenderer(usfmDir, builtDir + '/' + buildName + '.js')
    c.render(order)

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
    # START
    saveCWD() 
    oebFlag = False  
    order="normal" 
    logger.info('Starting Build.')
    try:
        opts, args = getopt.getopt(argv, "ht:u:b:n:or:", ["help", "target=", "usfmDir=", "builtDir=", "name=","oeb","order="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            return usage()
        elif opt in ("-t", "--target"):
            targets =  arg
        elif opt in ("-u", "--usfmDir"):
            usfmDir = arg
        elif opt in ("-b", "--builtDir"):
            buildDir = arg
        elif opt in ("-n", "--name"):
            buildName = arg
        elif opt in ("-r", "--order"):
            order = arg
        elif opt in ("-o", "--oeb"):
            oebFlag = True
        else:
            usage()

    if targets == 'reader':
        buildReader(usfmDir, buildDir, buildName)
    elif targets == 'mediawiki':
        buildMediawiki(usfmDir, buildDir, buildName)
    elif targets == 'lout':
        buildLout(usfmDir, buildDir, buildName)
    else:
        try:
            m = importlib.import_module(targets + 'Renderer')
            ensureOutputDir(buildDir)
            logger.info("\n  Building: " + usfmDir + "\n  into: " + buildDir + "\n  as: " + buildName)
            c = m.Renderer(usfmDir, buildDir, buildName)
            if oebFlag is True: c.setOEBFlag()
            c.render()
        except Exception as e:
            logger.exception('ERROR IN BUILD')

    logger.info('Finished.')
    restoreCWD()

def usage():
    print """
        USFM-Tools
        ----------

        Build script.  See source for details.
        
        In essense:
        
        python transform.py
           --usfmDir=/dir/to/usfm
           --builtDir=/dir/to/build/in 
           --name=TranslationName
           --target=rendererName (eg docx or csv)
                
    """

if __name__ == "__main__":
    main(sys.argv[1:])