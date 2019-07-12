# Setup list of patches and books to use
#

import os
import sys

# LOGGING
import sharedLogger

bookKeys = {
'FRT': '000',
'GEN': '001',
'EXO': '002',
'LEV': '003',
'NUM': '004',
'DEU': '005',
'JOS': '006',
'JDG': '007',
'RUT': '008',
'1SA': '009',
'2SA': '010',
'1KI': '011',
'2KI': '012',
'1CH': '013',
'2CH': '014',
'EZR': '015',
'NEH': '016',
'EST': '017',
'JOB': '018',
'PSA': '019',
'PRO': '020',
'ECC': '021',
'SNG': '022',
'ISA': '023',
'JER': '024',
'LAM': '025',
'EZK': '026',
'DAN': '027',
'HOS': '028',
'JOL': '029',
'AMO': '030',
'OBA': '031',
'JON': '032',
'MIC': '033',
'NAM': '034',
'HAB': '035',
'ZEP': '036',
'HAG': '037',
'ZEC': '038',
'MAL': '039',
'MAT': '040',
'MRK': '041',
'LUK': '042',
'JHN': '043',
'ACT': '044',
'ROM': '045',
'1CO': '046',
'2CO': '047',
'GAL': '048',
'EPH': '049',
'PHP': '050',
'COL': '051',
'1TH': '052',
'2TH': '053',
'1TI': '054',
'2TI': '055',
'TIT': '056',
'PHM': '057',
'HEB': '058',
'JAS': '059',
'1PE': '060',
'2PE': '061',
'1JN': '062',
'2JN': '063',
'3JN': '064',
'JUD': '065',
'REV': '066'
}

silNames = [
'FRT',
'GEN',
'EXO',
'LEV',
'NUM',
'DEU',
'JOS',
'JDG',
'RUT',
'1SA',
'2SA',
'1KI',
'2KI',
'1CH',
'2CH',
'EZR',
'NEH',
'EST',
'JOB',
'PSA',
'PRO',
'ECC',
'SNG',
'ISA',
'JER',
'LAM',
'EZK',
'DAN',
'HOS',
'JOL',
'AMO',
'OBA',
'JON',
'MIC',
'NAM',
'HAB',
'ZEP',
'HAG',
'ZEC',
'MAL',
'MAT',
'MRK',
'LUK',
'JHN',
'ACT',
'ROM',
'1CO',
'2CO',
'GAL',
'EPH',
'PHP',
'COL',
'1TH',
'2TH',
'1TI',
'2TI',
'TIT',
'PHM',
'HEB',
'JAS',
'1PE',
'2PE',
'1JN',
'2JN',
'3JN',
'JUD',
'REV' ]

silNamesNTPsalms = [
'MAT',
'MRK',
'LUK',
'JHN',
'ACT',
'ROM',
'1CO',
'2CO',
'GAL',
'EPH',
'PHP',
'COL',
'1TH',
'2TH',
'1TI',
'2TI',
'TIT',
'PHM',
'HEB',
'JAS',
'1PE',
'2PE',
'1JN',
'2JN',
'3JN',
'JUD',
'REV',
'PSA' ]

readerNames = [
'Gen',
'Exod',
'Lev',
'Num',
'Deut',
'Josh',
'Judg',
'Ruth',
'1Sam',
'2Sam',
'1Kgs',
'2Kgs',
'1Chr',
'2Chr',
'Ezra',
'Nehm',
'Esth',
'Job',
'Ps',
'Prov',
'Eccl',
'Song',
'Isa',
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
'1Thess',
'2Thess',
'1Tim',
'2Tim',
'Titus',
'Phlm',
'Heb',
'Jas',
'1Pet',
'2Pet',
'1John',
'2John',
'3John',
'Jude',
'Rev' ]

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
    s = usfm.find('\id ') + 4
    e = usfm.find(' ', s)
    e2 = usfm.find('\n', s)
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
    logger = sharedLogger.currentLogger
    books = {}
    dirList=os.listdir(path)
    logger.debug('Loading USFM files from ' + path)
    for fname in dirList:
      try:
          f = open(path + '/' + fname,'U') # U handles line endings
          usfm = f.read()
          if usfm[:4] == r'\id ' and usfm[4:7] in silNames:
              logger.debug('Loaded ' + fname + ' as ' + usfm[4:7])
              books[bookID(usfm)] = usfm
              f.close()
          else:
              logger.warning('Ignored ' + fname + ' - maybe ' + usfm[4:7] + ' ? ')
      except:
          logger.error('     Couldn\'t open ' + fname)
    logger.debug('Loaded USFM files from ' + path)
    return books

def orderFor(booksDict):
    order = silNames
    if "PSA" in booksDict and \
            "GEN" not in booksDict and "MAT" in booksDict:
        # This is a big hack. When doing Psalms + NT, put Psalms last
        order = silNamesNTPsalms       
    a = []
    for bookName in order:
        if bookName in booksDict:
            a.append(booksDict[bookName])
    return a
    
    
#
#   NEW SYSTEM
#
class Book(object):
  def __init__(self, number, sil, full, chapters):
    self.number = number
    self.sil = sil
    self.full = full
    self.chapters = chapters
    
  def fileName(self):
    return self.number + '-' + self.full + '.usfm'
    
class Books(object):
  def __init__(self):
    self.books = [
        Book('00', 'FRT', 'Front Material', 0   ),
        Book('01', 'GEN', 'Genesis', 50         ),
        Book('02', 'EXO', 'Exodus', 40          ),
        Book('03', 'LEV', 'Leviticus', 27       ),
        Book('04', 'NUM', 'Numbers', 36         ),
        Book('05', 'DEU', 'Deuteronomy', 34     ),

        Book('06', 'JOS', 'Joshua', 24          ),
        Book('07', 'JUD', 'Judges', 21          ),
        Book('08', 'RUT', 'Ruth', 4             ),
        Book('09', '1SA', '1 Samuel', 31        ),
        Book('10', '2SA', '2 Samuel', 24        ),
        Book('11', '1KI', '1 Kings', 22         ),
        Book('12', '2KI', '2 Kings', 25         ),
        Book('13', '1CH', '1 Chronicles', 29    ),
        Book('14', '2CH', '2 Chronicles', 36    ),
        Book('15', 'EZR', 'Ezra', 10            ),
        Book('16', 'NEH', 'Nehemiah', 13        ),
        Book('17', 'EST', 'Esther', 10          ),

        Book('18', 'JOB', 'Job', 42             ),
        Book('19', 'PSA', 'Psalms', 150         ),
        Book('20', 'PRO', 'Proverbs', 31        ),
        Book('21', 'ECC', 'Ecclesiastes', 12    ),
        Book('22', 'SNG', 'Song of Solomon', 8  ),

        Book('23', 'ISA', 'Isaiah', 66          ),
        Book('24', 'JER', 'Jeremiah', 52        ),
        Book('25', 'LAM', 'Lamentations', 5     ),
        Book('26', 'EZK', 'Ezekiel', 48         ),
        Book('27', 'DAN', 'Daniel', 12          ),

        Book('28', 'HOS', 'Hosea', 14           ),
        Book('29', 'JOL', 'Joel', 3             ),
        Book('30', 'AMO', 'Amos', 9             ),
        Book('31', 'OBA', 'Obadiah', 1          ),
        Book('32', 'JON', 'Jonah', 4            ),
        Book('33', 'MIC', 'Micah', 7            ),
        Book('34', 'NAM', 'Nahum', 3            ),
        Book('35', 'HAB', 'Habakkuk', 3         ),
        Book('36', 'ZEP', 'Zephaniah', 3        ),
        Book('37', 'HAG', 'Haggai', 2           ),
        Book('38', 'ZEC', 'Zechariah', 14       ),
        Book('39', 'MAL', 'Malachi', 4          ),

        Book('40', 'MAT', 'Matthew', 28         ),
        Book('41', 'MRK', 'Mark', 16            ),
        Book('42', 'LUK', 'Luke', 24            ),
        Book('43', 'JON', 'John', 21            ),
        Book('44', 'ACT', 'Acts', 28            ),

        Book('45', 'ROM', 'Romans', 16          ),
        Book('46', '1CO', '1 Corinthians', 16   ),
        Book('47', '2CO', '2 Corinthians', 13   ),
        Book('48', 'GAL', 'Galatians', 6        ),
        Book('49', 'EPH', 'Ephesians', 6        ),
        Book('50', 'PHP', 'Philippians', 4      ),
        Book('51', 'COL', 'Colossians', 4       ),
        Book('52', '1TH', '1 Thessalonians', 5  ),
        Book('53', '2TH', '2 Thessalonians', 3  ),
        Book('54', '1TI', '1 Timothy', 6        ),
        Book('55', '2TI', '2 Timothy', 4        ),
        Book('56', 'TIT', 'Titus', 3            ),
        Book('57', 'PHL', 'Philemon', 1         ),
    
        Book('58', 'HEB', 'Hebrews', 13         ),
        Book('59', 'JAS', 'James', 5            ),
        Book('60', '1PE', '1 Peter', 5          ),
        Book('61', '2PE', '2 Peter', 3          ),
        Book('62', '1JN', '1 John', 5           ),
        Book('63', '2JN', '2 John', 1           ),
        Book('64', '3JN', '3 John', 1           ),
        Book('65', 'JUD', 'Jude', 1             ),

        Book('66', 'REV', 'Revelation', 22      )
    ]
    
  def bookForNumber(self, number):
    logger = sharedLogger.currentLogger
    for b in self.books:
      if b.number == str(int(number)).zfill(2):
        return b
    logger.error("Cant find book: " + str(int(number)).zfill(2)) 
    sys.exit(1)

