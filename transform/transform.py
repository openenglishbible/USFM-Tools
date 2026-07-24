import getopt
import importlib
import logging
import os
import subprocess
import sys

# Set Path for files in support/
rootdiroftools = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(rootdiroftools,'support'))

# LOGGING
import sharedLogger

#IMPORT MODULES (TO BE DEPRECATED)
import readerise
import mediawikiPrinter
import loutRenderer
import rendererConfig

def runscript(c, prefix='', repeatFilter = ''):
    logging.debug(prefix + ':: ' + c)
    pp = subprocess.Popen([c], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
    (result, stderrdata) = pp.communicate()
    print(result)
    if not len(stderrdata) == 0:
        print(stderrdata)
    if not repeatFilter == '' and not stderrdata.find(repeatFilter) == -1:
        runscript(c, prefix, repeatFilter)
        return
    if pp.returncode != 0:
        raise RuntimeError('Command failed with status %d: %s' % (pp.returncode, c))

def buildLout(usfmDir, builtDir, buildName):
 
    print('#### Building Lout...')

    # Prepare
    print('     Clean working dir')
    runscript('rm "' + builtDir + '/working/lout/*"', '       ')

    # Convert to Lout
    print('     Converting to Lout')
    ensureOutputDir(builtDir + '/working/lout')
    c = loutRenderer.LoutRenderer(usfmDir, builtDir + '/working/lout/' + buildName + '.lout')
    c.render()
    
    # Run Lout
    print('     Copying support files')
    runscript('cp support/lout/oebbook working/lout', '       ')
    print('     Running Lout')
    runscript('cd "' + builtDir + '/working/lout"; lout "./' + buildName + '.lout" > "' + buildName + '.ps"', '       ', repeatFilter='unresolved cross reference')
    print('     Running ps2pdf')
    runscript('cd "' + builtDir + '/working/lout"; ps2pdf -dDEVICEWIDTHPOINTS=432 -dDEVICEHEIGHTPOINTS=648 "' + buildName + '.ps" "' + buildName + '.pdf" ', '       ')
    print('     Copying into builtDir')
    runscript('cp "' + builtDir + '/working/lout/' + buildName + '.pdf" "' + builtDir + '/' + buildName + '.pdf" ', '       ')

def buildReader(usfmDir, builtDir, buildName, order="normal"):
    # Convert to js for online reader
    print('#### Building for Reader...')
    ensureOutputDir(builtDir + 'en_oeb')
    c = readerise.ReaderRenderer(usfmDir, builtDir + '/' + buildName + '.js')
    c.render(order)

def buildMediawiki(usfmDir, builtDir, buildName):
    # Convert to MediaWiki format for Door43
    print('#### Building for Mediawiki...')
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
    if argv == []:
        usage()
        sys.exit(0)
 
    # START
    saveCWD()
    oebFlag = False
    strictFlag = False
    order="normal"
    targets = usfmDir = buildDir = buildName = None
    # Default config if not overriden later
    config = rendererConfig.RendererConfig(os.path.join(rootdiroftools, 'default.config'))
    try:
        opts, args = getopt.getopt(argv, "ht:u:b:n:or:c:s", ["help", "target=", "usfmDir=", "builtDir=", "name=","oeb","order=","config=","strict"])
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
        elif opt in ("-s", "--strict"):
            strictFlag = True
        elif opt in ("-c", "--config"):
            config = rendererConfig.RendererConfig(arg, os.path.join(rootdiroftools, 'default.config'))
        else:
            usage()

    if not (targets and usfmDir and buildDir and buildName):
        usage()
        sys.exit(2)

    logger = sharedLogger.initLogger(config.get("General", "logLevel"))

    ok = True
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
            c = m.Renderer(usfmDir, buildDir, buildName, config)
            if oebFlag is True: c.setOEBFlag()
            c.render()
            lost = getattr(c, 'unhandledLost', [])
            if lost and strictFlag:
                for tokenType, value in lost[:10]:
                    logger.error('--strict: content dropped by \\%s: %r' % (tokenType, value))
                logger.error('--strict: %d marker(s) with text content had no handler; failing build' % len(lost))
                ok = False
        except Exception as e:
            logger.exception('ERROR IN BUILD')
            ok = False

    logger.debug('Finished.')
    restoreCWD()
    if not ok:
        sys.exit(1)

def usage():
    print("""
        USFM-Tools
        ----------

        Build script.  See source for details.
        
        In essense:
        
        python transform.py
           --usfmDir=/dir/to/usfm
           --builtDir=/dir/to/build/in 
           --name=TranslationFileName (for determining output file names)
           --target=rendererName (eg rtf or csv)
           --config=myConfig.config (or default.config by default)
                
    """)

if __name__ == "__main__":
    main(sys.argv[1:])