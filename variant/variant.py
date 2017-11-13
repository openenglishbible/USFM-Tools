# -*- coding: utf-8 -*-
#

import sys, getopt

from pyparsing import CharsNotIn, ZeroOrMore, Group, Suppress, OneOrMore, ParseResults, Optional, StringEnd

phrase = CharsNotIn( "[|]"  )
tag = CharsNotIn( "[|]:,"  )
tags = Group( Optional(tag, default="base") + ZeroOrMore( Suppress(',') + tag ) + Suppress(":") )
option = Group( tags + Optional(phrase, default='') )
optionList = Group( Suppress("[") + option + ZeroOrMore( Suppress('|') + option )  + Suppress("]") ) 
text = OneOrMore( phrase | optionList ) + Suppress( StringEnd() )

# input string
def clean( unicodeString ):
    # We need to clean the input a bit. For a start, until
    # we work out what to do, non breaking spaces will be ignored
    # ie 0xa0
    return unicodeString.replace('\xa0', ' ')

def parseString( unicodeString ):
    try:
        s = clean(unicodeString)
        tokens = text.parseString(s, parseAll=True )
    except Exception as e:
        print(e)
        print(repr(unicodeString[:50]))
        sys.exit()
    return tokens
    
def render( unicodeString, tags):
    s = parseString( unicodeString )
    r = ''
    for e in s:
        if type(e) == type('') or type(e) == type(''):
            r = r + e
        elif type(e) == ParseResults:
            for o in e:
                 if len(set(tags).intersection(o[0])) > 0:
                    r = r + o[1]
        else:
            print(type(e))
            print('WTF?')
            sys.exit()
    return r
    
def listChanges( unicodeString, tags):
    chapter = '-'
    verse = '-'
    s = parseString( unicodeString )
    r = ''
    for e in s:
        if type(e) == type('') or type(e) == type(''):
            if r'\v ' in e:
                verse = e[e.rfind(r'\v ') +3:e.rfind(r'\v ') + 10].split()[0]
            if r'\c ' in e:
                chapter = e[e.rfind(r'\c ') +3:e.rfind(r'\c ') + 10].split()[0]
        elif type(e) == ParseResults:
            for o in e:
                 if len(set(tags).intersection(o[0])) > 0:
                    r = r + '\n' + chapter + ':' + verse
                    for op in e:
                         r = r + '\n\t' + str(op[0]) + ' -> ' + str(op[1])
        else:
            print(type(e))
            print('WTF?')
            sys.exit()
    return r    
                        
def testHello():
    hello = "This is an option [test,t2:Hello, World!|oed:Goodbye]."
    assert( str(parseString( hello )) == str(['This is an option ', [[['test', 't2'], 'Hello, World!'], [['oed'], 'Goodbye']], '.']) )
 
def testHelloRender():
    hello = "This is an option [test,t2:Hello, World!|oed:Goodbye]."
    assert( str(render( hello, ['oed'] )) == 'This is an option Goodbye.') 
    assert( str(render( hello, ['test'] )) == 'This is an option Hello, World!.') 
    assert( str(render( hello, ['t2','oed'] )) == 'This is an option Hello, World!Goodbye.') 

def testEmptyRender():
    hello = "This is an option [test,t2:Hello, World!|oed:]."
    assert( str(render( hello, ['oed'] )) == 'This is an option .') 
    assert( str(render( hello, ['test'] )) == 'This is an option Hello, World!.') 
    assert( str(render( hello, ['t2','oed'] )) == 'This is an option Hello, World!.') 
   
def testEmptyTags():
    hello = "This is an option [:Hello, World!|oed:something]."
    assert( str(render( hello, ['oed'] )) == 'This is an option something.') 
    assert( str(render( hello, ['base'] )) == 'This is an option Hello, World!.') 
   
def tests():
    testHello()
    testHelloRender()
    testEmptyRender()
    testEmptyTags()
    print("Tests OK")
    
def usage():
    print("""
        OEB-Tools - Variant
        -------------------

        Variant handler. See source for details.
        
        python3 variant.py -i infile -o outfile -t tag+anothertag
        
    """)

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "ui:o:t:c", ["unittest","in=", "out=", "tags=",'changes'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
        
    action = 'b'
    inF = ''
    outF = ''
    tags = ''
    for opt, arg in opts:
        if opt in ("-i", "--in"):
            inF =  arg
        elif opt in ("-o", "--out"):
            outF = arg
        elif opt in ("-t", "--tags"):
            tags = arg.split('+')
        elif opt in ("-u", "--unittest"):
            tests()
            sys.exit(0)
        elif opt in ("-c", "--changes"):
            action = 'c'

    if inF == '' or outF == '' or tags == '':
        usage()
        sys.exit(1)
            
    if action == 'c':
        f = open(inF)
        s = f.read()
        f.close()
        print(listChanges(s,tags))
    else:
        f = open(inF)
        s = f.read()
        f.close()
        s = render(s,tags)
        f = open(outF,'w')
        f.write(s)
        f.close()

if __name__ == "__main__":
    main(sys.argv[1:])
