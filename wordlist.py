# -*- coding: utf-8 -*-
#

import re, getopt, sys

def bylength(word1, word2):
    """
    write your own compare function:
    returns value < 0 of word1 longer then word2
    returns value = 0 if the same length
    returns value > 0 of word2 longer than word1
    """
    return len(word2) - len(word1)
    
def main(argv):
    
    try:
        opts, args = getopt.getopt(argv, "b:", ["book="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-b", "--book"):
            bookname = arg
        else:
            usage()
    
    f = open(bookname)
    fc = unicode(f.read(), 'utf-8')
    f.close()
 
    # create a list of words separated at whitespaces
    wordList = re.split(r"\W", fc)

    #clean = []
    #for w in# wordList:
    #  #  nw = u''
    #    f#or c in w:
    #        if not c in u"""\n\t .,!? —‘“”’;:()'"[]\\01234567#89&*/=""":
    #            n#w = nw + c
    #    clean.#append(nw)
    #    #clean.append(n#w.lower())
    clean = wordList

    noDupes=[]
    [noDupes.append(i) for i in clean if not noDupes.count(i)]

    #filtered=[]
    #[filtered.append(i) for i in noDupes if i[-3:] == u'eth' or i[-3:] == u'est']
    filtered = noDupes

    filtered.sort(cmp=bylength)

    result = u''
    for n in filtered: result = result + u'\n' + n
    
    f = open('wordlist', 'w')
    f.write(result.encode('utf-8'))
    f.close()

def usage():
    print """
        USFM-Tools
        ----------

        Creates word list.  See source for details.
        
        python wordlist.py -b path/to/book.usfm
        
        writes to uft8 file 'wordlist'
        
    """

if __name__ == "__main__":
    main(sys.argv[1:])