# Setup list of patches and books to use
#

import os
import codecs

bookKeys = {
u'GEN': u'001',
u'EXO': u'002',
u'LEV': u'003',
u'NUM': u'004',
u'DEU': u'005',
u'JOS': u'006',
u'JDG': u'007',
u'RUT': u'008',
u'1SA': u'009',
u'2SA': u'010',
u'1KI': u'011',
u'2KI': u'012',
u'1CH': u'013',
u'2CH': u'014',
u'EZR': u'015',
u'NEH': u'016',
u'EST': u'017',
u'JOB': u'018',
u'PSA': u'019',
u'PRO': u'020',
u'ECC': u'021',
u'SNG': u'022',
u'ISA': u'023',
u'JER': u'024',
u'LAM': u'025',
u'EZK': u'026',
u'DAN': u'027',
u'HOS': u'028',
u'JOL': u'029',
u'AMO': u'030',
u'OBA': u'031',
u'JON': u'032',
u'MIC': u'033',
u'NAM': u'034',
u'HAB': u'035',
u'ZEP': u'036',
u'HAG': u'037',
u'ZEC': u'038',
u'MAL': u'039',
u'MAT': u'040',
u'MRK': u'041',
u'LUK': u'042',
u'JHN': u'043',
u'ACT': u'044',
u'ROM': u'045',
u'1CO': u'046',
u'2CO': u'047',
u'GAL': u'048',
u'EPH': u'049',
u'PHP': u'050',
u'COL': u'051',
u'1TH': u'052',
u'2TH': u'053',
u'1TI': u'054',
u'2TI': u'055',
u'TIT': u'056',
u'PHM': u'057',
u'HEB': u'058',
u'JAS': u'059',
u'1PE': u'060',
u'2PE': u'061',
u'1JN': u'062',
u'2JN': u'063',
u'3JN': u'064',
u'JUD': u'065',
u'REV': u'066'
}

silNames = [
u'GEN',
u'EXO',
u'LEV',
u'NUM',
u'DEU',
u'JOS',
u'JDG',
u'RUT',
u'1SA',
u'2SA',
u'1KI',
u'2KI',
u'1CH',
u'2CH',
u'EZR',
u'NEH',
u'EST',
u'JOB',
u'PSA',
u'PRO',
u'ECC',
u'SNG',
u'ISA',
u'JER',
u'LAM',
u'EZK',
u'DAN',
u'HOS',
u'JOL',
u'AMO',
u'OBA',
u'JON',
u'MIC',
u'NAM',
u'HAB',
u'ZEP',
u'HAG',
u'ZEC',
u'MAL',
u'MAT',
u'MRK',
u'LUK',
u'JHN',
u'ACT',
u'ROM',
u'1CO',
u'2CO',
u'GAL',
u'EPH',
u'PHP',
u'COL',
u'1TH',
u'2TH',
u'1TI',
u'2TI',
u'TIT',
u'PHM',
u'HEB',
u'JAS',
u'1PE',
u'2PE',
u'1JN',
u'2JN',
u'3JN',
u'JUD',
u'REV' ]

silNamesNTPsalms = [
u'MAT',
u'MRK',
u'LUK',
u'JHN',
u'ACT',
u'ROM',
u'1CO',
u'2CO',
u'GAL',
u'EPH',
u'PHP',
u'COL',
u'1TH',
u'2TH',
u'1TI',
u'2TI',
u'TIT',
u'PHM',
u'HEB',
u'JAS',
u'1PE',
u'2PE',
u'1JN',
u'2JN',
u'3JN',
u'JUD',
u'REV',
u'PSA' ]

readerNames = [
u'Gen',
u'Exod',
u'Lev',
u'Num',
u'Deut',
u'Josh',
u'Judg',
u'Ruth',
u'1Sam',
u'2Sam',
u'1Kgs',
u'2Kgs',
u'1Chr',
u'2Chr',
u'Ezra',
u'Nehm',
u'Esth',
u'Job',
u'Ps',
u'Prov',
u'Eccl',
u'Song',
u'Isa',
u'Jer',
u'Lam',
u'Ezek',
u'Dan',
u'Hos',
u'Joel',
u'Amos',
u'Obad',
u'Jonah',
u'Mic',
u'Nah',
u'Hab',
u'Zeph',
u'Hag',
u'Zech',
u'Mal',
u'Matt',
u'Mark',
u'Luke',
u'John',
u'Acts',
u'Rom',
u'1Cor',
u'2Cor',
u'Gal',
u'Eph',
u'Phil',
u'Col',
u'1Thess',
u'2Thess',
u'1Tim',
u'2Tim',
u'Titus',
u'Phlm',
u'Heb',
u'Jas',
u'1Pet',
u'2Pet',
u'1John',
u'2John',
u'3John',
u'Jude',
u'Rev' ]

accordanceNames = [
    'Gen',
    'Ex',
    'Lev',
    'Num',
    'Deut',
    'Josh',
    'Judg',
    'Ruth',
    '1Sam',
    '2Sam',
    '1Kings',
    '2Kings',
    '1Chr',
    '2Chr',
    'Ezra',
    'Neh',
    'Esth',
    'Job',
    'Psa',
    'Prov',
    'Eccl',
    'Song',
    'Is',
    'Jer',
    'Lam',
    'Ezek',
    'Dan',
    'Hos',
    'Joel',
    'Amos',
    'Obad',
    'Jonah',
    'Mic',
    'Nah',
    'Hab',
    'Zeph',
    'Hag',
    'Zech',
    'Mal',
    'Matt',
    'Mark',
    'Luke',
    'John',
    'Acts',
    'Rom',
    '1Cor',
    '2Cor',
    'Gal',
    'Eph',
    'Phil',
    'Col',
    '1Th',
    '2Th',
    '1Tim',
    '2Tim',
    'Titus',
    'Philem',
    'Heb',
    'James',
    '1Pet',
    '2Pet',
    '1John',
    '2John',
    '3John',
    'Jude',
    'Rev'
]

def readerName(num):
    return readerNames[int(num)-1]

def fullName(num):
    return bookNames[int(num)-1]
    
def nextChapter(bookNumber, chapterNumber):
    return (1,1)
    
def previousChapter(bookNumber, chapterNumber):
    if chapterNumber > 1:
        return (bookNumber, chapterNumber - 1)
    else:
        if bookNumber > 1:
            return (bookNumber - 1, 50) #bookSize[bookNumber -1])
        else:
            return (1,1)

bookNames = ['Genesis',
            'Exodus',
            'Leviticus',
            'Numbers',
            'Deuteronomy',
            'Joshua',
            'Judges',
            'Ruth',
            '1 Samuel',
            '2 Samuel',
            '1 Kings',
            '2 Kings',
            '1 Chronicles',
            '2 Chronicles',
            'Ezra',
            'Nehemiah',
            'Esther',
            'Job',
            'Psalms',
            'Proverbs',
            'Ecclesiastes',
            'Song of Solomon',
            'Isaiah',
            'Jeremiah',
            'Lamentations',
            'Ezekiel',
            'Daniel',
            'Hosea',
            'Joel',
            'Amos',
            'Obadiah',
            'Jonah',
            'Micah',
            'Nahum',
            'Habakkuk',
            'Zephaniah',
            'Haggai',
            'Zechariah',
            'Malachi',
            'Matthew',
            'Mark',
            'Luke',
            'John',
            'Acts',
            'Romans',
            '1 Corinthians',
            '2 Corinthians',
            'Galatians',
            'Ephesians',
            'Philippians',
            'Colossians',
            '1 Thessalonians',
            '2 Thessalonians',
            '1 Timothy',
            '2 Timothy',
            'Titus',
            'Philemon',
            'Hebrews',
            'James',
            '1 Peter',
            '2 Peter',
            '1 John',
            '2 John',
            '3 John',
            'Jude',
            'Revelation']

books = bookNames 

def bookKeyForIdValue(id):
    e = id.find(' ')
    i = id if e == -1 else id[:e]
    return bookKeys[i] 

def bookID(usfm):
    s = usfm.find(u'\id ') + 4
    e = usfm.find(u' ', s)
    e2 = usfm.find(u'\n', s)
    e = e if e < e2 else e2
    return usfm[s:e].strip()
    
def bookName(usfm):
    id = bookID(usfm)
    index = silNames.index(id)
    return bookNames[index]

def silNameForBookKey(bk):
    return silNames[int(bk) - 1]

def accordanceNameForBookKey(bk):
    return accordanceNames[int(bk) - 1]
    
def loadBooks(path):
    books = {}
    dirList=os.listdir(path)
    print '\n     LOADING ALL USFM FILES FROM ' + path
    for fname in dirList:
      try:
          f = open(path + '/' + fname,'U') # U handles line endings
          usfm = f.read().decode('utf-8-sig')
          if usfm[:4] == ur'\id ' and usfm[4:7] in silNames:
              print '     Loaded ' + fname + ' as ' + usfm[4:7]
              books[bookID(usfm)] = usfm
              f.close()
          else:
              print '     Ignored ' + fname
      except:
          print '     Couldn\'t open ' + fname
    print '     FINISHED LOADING\n'
    return books

def orderFor(booksDict):
    order = silNames
    if booksDict.has_key("PSA") and not booksDict.has_key("GEN") and booksDict.has_key("MAT"):
        # This is a big hack. When doing Psalms + NT, put Psalms last
        order = silNamesNTPsalms       
    a = []
    for bookName in order:
        if booksDict.has_key(bookName):
            a.append(booksDict[bookName])
    return a