# -*- coding: utf-8 -*-
#

import sys
import getopt
import os
import configparser
import itertools

#####################################################
#
# Logging
#
#####################################################

import logging

logLevel = logging.INFO
currentLogger = logging.getLogger('variants')
currentLogger.setLevel(logLevel)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logLevel)
ch.setFormatter(formatter)
currentLogger.addHandler(ch)


def log(level, message):
    global currentLogger

    if level == 'DEBUG':
        currentLogger.debug(message)
    elif level == 'INFO':
        currentLogger.info(message)
    elif level == 'WARNING':
        currentLogger.warning(message)
    elif level == 'ERROR':
        currentLogger.error(message)
    else:
        currentLogger.debug(message)


#####################################################
#
# Variants on individual files
#
#####################################################

from pyparsing import CharsNotIn, ZeroOrMore, Group, Suppress, OneOrMore, ParseResults, Optional, StringEnd

phrase = CharsNotIn("[|]")
tag = CharsNotIn("[|]:,")
tags = Group(Optional(tag, default="base") + ZeroOrMore(Suppress(',') + tag) + Suppress(":"))
option = Group(tags + Optional(phrase, default=''))
optionList = Group(Suppress("[") + option + ZeroOrMore(Suppress('|') + option) + Suppress("]"))
text = OneOrMore(phrase | optionList) + Suppress(StringEnd())


def clean(unicodeString):
    # We need to clean the input a bit. For a start, until
    # we work out what to do, non breaking spaces will be ignored
    # ie 0xa0
    return unicodeString.replace('\xa0', ' ')


def parseString(unicodeString):
    try:
        s = clean(unicodeString)
        tokens = text.parseString(s, parseAll=True)
    except Exception as e:
        log('ERROR', e)
        log('ERROR', repr(unicodeString[:50]))
        sys.exit()
    return tokens


def render(unicodeString, tags):
    s = parseString(unicodeString)
    r = ''
    for e in s:
        if type(e) == type('') or type(e) == type(''):
            r = r + e
        elif type(e) == ParseResults:
            for o in e:
                if len(set(tags).intersection(o[0])) > 0:
                    r = r + o[1]
        else:
            log('ERROR', type(e))
            log('ERROR', 'WTF?')
            sys.exit()
    return r


def listChanges(unicodeString, tags):
    chapter = '-'
    verse = '-'
    s = parseString(unicodeString)
    r = ''
    for e in s:
        if type(e) == type('') or type(e) == type(''):
            if r'\v ' in e:
                verse = e[e.rfind(r'\v ') + 3:e.rfind(r'\v ') + 10].split()[0]
            if r'\c ' in e:
                chapter = e[e.rfind(r'\c ') + 3:e.rfind(r'\c ') + 10].split()[0]
        elif type(e) == ParseResults:
            for o in e:
                if len(set(tags).intersection(o[0])) > 0:
                    r = r + '\n' + chapter + ':' + verse
                    for op in e:
                        r = r + '\n\t' + str(op[0]) + ' -> ' + str(op[1])
        else:
            log('ERROR', type(e))
            log('ERROR', 'WTF?')
            sys.exit()
    return r


def testHello():
    hello = "This is an option [test,t2:Hello, World!|oed:Goodbye]."
    assert (str(parseString(hello)) == str(
        ['This is an option ', [[['test', 't2'], 'Hello, World!'], [['oed'], 'Goodbye']], '.']))


def testHelloRender():
    hello = "This is an option [test,t2:Hello, World!|oed:Goodbye]."
    assert (str(render(hello, ['oed'])) == 'This is an option Goodbye.')
    assert (str(render(hello, ['test'])) == 'This is an option Hello, World!.')
    assert (str(render(hello, ['t2', 'oed'])) == 'This is an option Hello, World!Goodbye.')


def testEmptyRender():
    hello = "This is an option [test,t2:Hello, World!|oed:]."
    assert (str(render(hello, ['oed'])) == 'This is an option .')
    assert (str(render(hello, ['test'])) == 'This is an option Hello, World!.')
    assert (str(render(hello, ['t2', 'oed'])) == 'This is an option Hello, World!.')


def testEmptyTags():
    hello = "This is an option [:Hello, World!|oed:something]."
    assert (str(render(hello, ['oed'])) == 'This is an option something.')
    assert (str(render(hello, ['base'])) == 'This is an option Hello, World!.')


def tests():
    testHello()
    testHelloRender()
    testEmptyRender()
    testEmptyTags()
    log('INFO', "Tests OK")


#####################################################
#
# Variants on whole project
#
#####################################################

def tagCombinations(dir):
    config = configparser.RawConfigParser()
    tags = []
    try:
        config.read(dir + '/tags.db')
    except:
        log('ERROR', 'Could not read tags file')
        sys.exit(0)
    for s in config.sections():
        tags.append(config.options(s))
    return list(itertools.product(*tags))


def swapPunctuation(s):
    s = s.replace('“', '@leftdoublequote@')
    s = s.replace('”', '@rightdoublequote@')
    s = s.replace('‘', '@leftsinglequote@')
    s = s.replace('’', '@rightsinglequote@')
    s = s.replace('@leftdoublequote@', '‘')
    s = s.replace('@rightdoublequote@', '’')
    s = s.replace('@leftsinglequote@', '“')
    s = s.replace('@rightsinglequote@', '”')
    return s


def stage(src, to, tags, booklist, swap):
    log('DEBUG', 'Tags: ' + str(tags))
    log('DEBUG', 'Booklist: ' + str(booklist))
    for fn in sorted(os.listdir(src)):
        if fn[-8:] == '.usfm.db' and (booklist == [] or fn[:-3] in booklist):

            log('DEBUG', 'Beginning: ' + fn)
            f = open(os.path.join(src, fn))
            b = f.read()
            f.close()

            s = render(b, tags)

            # To get quotes right to Cth versions, swap “”‘’ to get US and Cth OK
            if swap:
                s = swapPunctuation(s)

            # Now deal with contractions and possessives
            s = s.replace('\'', '’')

            f = open(os.path.join(to, fn), 'w')
            f.write(s)
            f.close()
            log('DEBUG', 'Wrote ' + fn)


#####################################################
#
# Script
#
#####################################################

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "has:d:b:t:up",
                                   ["help", "all", "source=", "destination=", "booklist=", "tags=", "unittests",
                                    "punctuation"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    source = build = tags = ''
    doAll = swap = False
    booklist = []
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-u", "--unittests"):
            tests()
            sys.exit(1)
        elif opt in ("-s", "--source"):
            source = arg
        elif opt in ("-d", "--destination"):
            build = arg
        elif opt in ("-t", "--tags"):
            tags = arg.split('-')
        elif opt in ("-a", "--all"):
            doAll = True
        elif opt in ("-p", "--punctuation"):
            swap = True
        elif opt in ("-b", "--booklist"):
            if not arg == 'all':
                with open(arg, 'r') as fin:
                    booklist = fin.read().split('\n')

    if doAll == True:
        for tc in tagCombinations(source):
            d = build + '-'.join(tc)
            if not os.path.exists(d):
                os.makedirs(d)
            stage(source, d, tc, booklist, swap)
    else:
        log('INFO', "\n  Rendering: " + source +
            "\n  as: " + build +
            "\n  using: " + str(tags) +
            "\n  swap: " + str(swap))

        stage(source, build, tags, booklist, swap)


def usage():
    print("""
        USFM-Tools Variant
        ------------------

        USFM Variant Tool

        -h or --help for these options
        -s or --source for directory of source .usfm.db files
        -d or --destination for directory of built .usfm files
        -t or --tags for hyphen separated list of tags
        -a or --all to build all tag combinations
        -b or --booklist to limit books built to list in file, or 'all'
        -u or --unittests to to a self check
        -p or --punctuation to swap punctuation
    """)


if __name__ == "__main__":
    main(sys.argv[1:])
