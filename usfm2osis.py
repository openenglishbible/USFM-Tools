#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

date = '$Date$'
rev = '$Rev$'
id = '$Id$'

usfmVersion = '2.35'  # http://ubs-icap.org/chm/usfm/2.35/index.html
osisVersion = '2.1.1' # http://www.bibletechnologies.net/osisCore.2.1.1.xsd
scriptVersion = '0.5'

# usfm2osis.py
# Copyright 2012 by the CrossWire Bible Society <http://www.crosswire.org/>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation version 2.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# The full text of the GNU General Public License is available at:
# <http://www.gnu.org/licenses/gpl-2.0.txt>.


### Guidelines & objectives:
# Target CPython 2.7+ (but support CPython 3 and other interpreters if possible)
# Require no non-default libraries
# Don't require SWORD bindings
# Handle all USFM characters from the USFM reference:
#      <http://paratext.ubs-translations.org/about/usfm>
# Employ best-practice conformant OSIS
# Employ modularity (functions rather than a big long script)
# Employ the same command-line syntax as usfm2osis.pl
# Use non-characters for milestoning

### Roadmap:
# 0.5 initial commit, including full coverage of core USFM tags
# 0.6 file sorting options (natural/alphabetic/canonical/none); expand sub-verses with ! in osisIDs; Python3 compatability; add optional schema validator (lxml probably); docstrings; unittest; make fully OO; PyDev project?
# 0.7 test suite incorporating all USFM examples from UBS ICAP and other complex cases
# 0.8 more clean-up & re-ordering to correctly encapsulate milestones within appropriate containers; clear remaining TODO items, to the extent possible
# 1.0 feature complete for release & production use
# 1.x xreffix.pl-functionality (osisParse(ref)), requiring SWORD bindings; use toc3 for localization
# 1.x SWORD-mode output?
# 1.x IMP output?
# 1.x SWORD module output?, requiring SWORD bindings

### TODO for 0.6:
# expand sub-verses with ! in osisIDs
# unittest
# make fully OO
# PyDev project?
# check Python2/3 compatibility

### Key to non-characters:
# Used   : \uFDD0\uFDD1\uFDD2\uFDD3\uFDD4\uFDD5\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA\uFDDB\uFDDC\uFDDD\uFDDE\uFDDF\uFDE0\uFDE1
# Unused : \uFDE7\uFDE8\uFDE9\uFDEA\uFDEB\uFDEC\uFDED\uFDEE\uFDEF
# \uFDD0 book
# \uFDD1 chapter
# \uFDD2 verse
# \uFDD3 paragraph
# \uFDD4 title
# \uFDD5 ms1
# \uFDD6 ms2
# \uFDD7 ms3
# \uFDD8 ms4
# \uFDD9 ms5
# \uFDDA s1
# \uFDDB s2
# \uFDDC s3
# \uFDDD s4
# \uFDDE s5
# \uFDDF notes
# \uFDE0 intro-list
# \uFDE1 intro-outline
# \uFDE2 is1
# \uFDE3 is2
# \uFDE4 is3
# \uFDE5 is4
# \uFDE6 is5

# \uFDD5\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA\uFDDB\uFDDC\uFDDD\uFDDE sections

import sys, codecs, re
from encodings.aliases import aliases
import multiprocessing
if sys.version_info[0] < 3:
    import Queue
else:
    import queue as Queue
import random

date = date.replace('$', '').strip()[6:16]
rev = rev.replace('$', '').strip()[5:]

bookDict = {
    ### Known USFM Book codes from Paratext
    ### Cf. http://ubs-icap.org/chm/usfm/2.35/index.html?book_codes.htm
    # OT
    'GEN':'Gen', 'EXO':'Exod', 'LEV':'Lev', 'NUM':'Num', 'DEU':'Deut', 'JOS':'Josh', 'JDG':'Judg', 'RUT':'Ruth',
    '1SA':'1Sam', '2SA':'2Sam', '1KI':'1Kgs', '2KI':'2Kgs', '1CH':'1Chr', '2CH':'2Chr', 'EZR':'Ezra', 'NEH':'Neh',
    'EST':'Esth', 'JOB':'Job', 'PSA':'Ps', 'PRO':'Prov', 'ECC':'Eccl', 'SNG':'Song', 'ISA':'Isa', 'JER':'Jer',
    'LAM':'Lam', 'EZK':'Ezek', 'DAN':'Dan', 'HOS':'Hos', 'JOL':'Joel', 'AMO':'Amos', 'OBA':'Obad', 'JON':'Jonah',
    'MIC':'Mic', 'NAM':'Nah', 'HAB':'Hab', 'ZEP':'Zeph', 'HAG':'Hag', 'ZEC':'Zech', 'MAL':'Mal',
    # NT
    'MAT':'Matt', 'MRK':'Mark', 'LUK':'Luke', 'JHN':'John', 'ACT':'Acts', 'ROM':'Rom', '1CO':'1Cor', '2CO':'2Cor',
    'GAL':'Gal', 'EPH':'Eph', 'PHP':'Phil', 'COL':'Col', '1TH':'1Thess', '2TH':'2Thess', '1TI':'1Tim', '2TI':'2Tim',
    'TIT':'Titus', 'PHM':'Phlm', 'HEB':'Heb', 'JAS':'Jas', '1PE':'1Pet', '2PE':'2Pet', '1JN':'1John', '2JN':'2John',
    '3JN':'3John', 'JUD':'Jude', 'REV':'Rev',
    # DC - Catholic
    'TOB':'Tob', 'JDT':'Jdt', 'ESG':'EsthGr', 'WIS':'Wis', 'SIR':'Sir', 'BAR':'Bar', 'LJE':'EpJer', 'S3Y':'PrAzar',
    'SUS':'Sus', 'BEL':'Bel', '1MA':'1Macc', '2MA':'2Macc',
    # DC - Eastern Orthodox
    '3MA':'3Macc', '4MA':'4Macc', '1ES':'1Esd', '2ES':'2Esd', 'MAN':'PrMan', 'PS2':'AddPs',
    # Rahlfs' LXX
    'ODA':'Odes', 'PSS':'PssSol',
    # Esdrae
    'EZA':'4Ezra', '5EZ':'5Ezra', '6EZ':'6Ezra',
    # Inconsistency with Esther
    'DAG':'DanGr',
    # Syriac
    'PS3':'5ApocSyrPss', '2BA':'2Bar', 'LBA':'EpBar',
    # Ethiopic
    'JUB':'Jub', 'ENO':'1En', '1MQ':'1Meq', '2MQ':'2Meq', '3MQ':'3Meq', 'REP':'Reproof', '4BA':'4Bar',
    # Vulgate
    'LAO':'EpLao',

    # Additional non-biblical books
    'XXA':'XXA', 'XXB':'XXB', 'XXC':'XXC', 'XXD':'XXD', 'XXE':'XXE', 'XXF':'XXF', 'XXG':'XXG',

    # Peripheral books
    'FRT':'FRONT', 'INT':'INTRODUCTION', 'BAK':'BACK', 'CNC':'CONCORDANCE', 'GLO':'GLOSSARY',
    'TDX':'INDEX', 'NDX':'GAZETTEER', 'OTH':'X-OTHER'
    }

addBookDict = {
    ### Deprecated
    # Rahlfs
    'JSA':'JoshA', 'JDB':'JudgB', 'TBS':'TobS', 'SST':'SusTh', 'DNT':'DanTh', 'BLT':'BelTh',
    # Esdrae
    '4ES':'4Ezra', '5ES':'5Ezra', '6ES':'6Ezra',


    ### Proposed Additions <http://lc.bfbs.org.uk/e107_files/downloads/canonicalissuesinparatext.pdf>
    # Alternate Psalms
    'PSB':'PsMet',
    # Vulgate
    'PSO':'PrSol', 'PJE':'PrJer',
    # Armenian
    'WSI':'WSir', 'COP':'EpCorPaul', '3CO':'3Cor', 'EUT':'PrEuth', 'DOJ':'DormJohn',
    # Apostolic Fathers
    '1CL':'1Clem', '2CL':'2Clem', 'SHE':'Herm', 'LBA':'Barn', 'DID':'Did',
    ###
    # Proposed replacements <http://lc.bfbs.org.uk/e107_files/downloads/canonicalissuesinparatext.pdf>
    'ODE':'Odes',

    # Additional biblical books
    'ADE':'AddEsth'
    }


canonicalOrder = [
    # General principles of ordering:
    # 1) Protocanonical books follow standard Protestant order within OT & NT
    # 2) Intertestamentals follow the OT
    # 3) NT-Apocrypha follow the NT
    # 4) Apostolic Fathers follow NT-deuterocanonicals
    # Specific principles:
    # 1) Book representing parts of protocanonical books follow the primary book
    # 2) Variants follow primary forms
    # 3) Books that appear in only one tradition or Bible appear following their traditional/attested antecedent

    # There's no fool-proof way to order books without knowing the tradition ahead of time,
    # but this ordering should get it right often for many common real Bibles.

    # Front Matter
    'FRONT', 'INTRODUCTION',

    # OT
    'Gen', 'Exod', 'Lev', 'Num', 'Deut', 'Josh', 'JoshA', 'Judg', 'JudgB', 'Ruth',
    '1Sam', '2Sam', '1Kgs', '2Kgs', '1Chr', '2Chr', 'PrMan', 'Jub', '1En',
    'Ezra', 'Neh', 'Tob', 'TobS', 'Jdt', 'Esth', 'EsthGr', 'AddEsth', '1Meq', '2Meq', '3Meq',
    'Job', 'Ps', 'AddPs', '5ApocSyrPss', 'PsMet', 'Odes', 'Prov', 'Reproof', 'Eccl', 'Song',
    'Wis', 'Sir', 'WSir', 'PrSol', 'PssSol',
    'Isa', 'Jer', 'Lam', 'PrJer', 'Bar', 'EpJer', '2Bar', 'EpBar', '4Bar',
    'Ezek', 'Dan', 'DanGr', 'DanTh', 'PrAzar', 'Sus', 'SusTh', 'Bel', 'BelTh',
    'Hos', 'Joel', 'Amos', 'Obad', 'Jonah', 'Mic', 'Nah', 'Hab', 'Zeph', 'Hag', 'Zech', 'Mal',

    # Intertestamentals
    '1Esd', '2Esd', '4Ezra', '5Ezra', '6Ezra',
    '1Macc', '2Macc', '3Macc', '4Macc',

    # NT
    'Matt', 'Mark', 'Luke', 'John', 'Acts', 'Rom', '1Cor', '2Cor',
    'Gal', 'Eph', 'Phil', 'Col', '1Thess', '2Thess', '1Tim', '2Tim',
    'Titus', 'Phlm', 'Heb', 'Jas', '1Pet', '2Pet', '1John', '2John',
    '3John', 'Jude', 'Rev',
    # NT-Apocrypha
    'EpLao', 'EpCorPaul', '3Cor', 'PrEuth', 'DormJohn',
    # AF
    '1Clem', '2Clem', 'Herm', 'Barn', 'Did',

    # Private-Use Extensions
    'XXA', 'XXB', 'XXC', 'XXD', 'XXE', 'XXF', 'XXG',

    # Back Matter
    'BACK', 'CONCORDANCE', 'GLOSSARY',
    'INDEX', 'GAZETTEER', 'X-OTHER'
    ]

usfmNumericOrder = [
    # Front Matter
    'FRONT', 'INTRODUCTION',

    # OT 01-39
    'Gen', 'Exod', 'Lev', 'Num', 'Deut', 'Josh', 'Judg', 'Ruth',
    '1Sam', '2Sam', '1Kgs', '2Kgs', '1Chr', '2Chr', 'Ezra', 'Neh',
    'Esth', 'Job', 'Ps', 'Prov', 'Eccl', 'Song', 'Isa', 'Jer',
    'Lam', 'Ezek', 'Dan', 'Hos', 'Joel', 'Amos', 'Obad', 'Jonah',
    'Mic', 'Nah', 'Hab', 'Zeph', 'Hag', 'Zech', 'Mal',

    # NT 41-67
    'Matt', 'Mark', 'Luke', 'John', 'Acts', 'Rom', '1Cor', '2Cor',
    'Gal', 'Eph', 'Phil', 'Col', '1Thess', '2Thess', '1Tim', '2Tim',
    'Titus', 'Phlm', 'Heb', 'Jas', '1Pet', '2Pet', '1John', '2John',
    '3John', 'Jude', 'Rev',

    # Apocrypha 68-87 (plus AddEsth, inserted after EsthGr)
    'Tob', 'Jdt', 'EsthGr', 'AddEsth', 'Wis', 'Sir', 'Bar', 'EpJer',
    'PrAzar', 'Sus', 'Bel', '1Macc', '2Macc', '3Macc', '4Macc',
    '1Esd', '2Esd', 'PrMan', 'AddPs', 'Odes', 'PssSol',

    # Esdrae A4-A6
    '4Ezra', '5Ezra', '6Ezra',

    # Gk. Daniel, Syriac additions, Ethiopic additions, Laodiceans B2-C2
    'DanGr', '5ApocSyrPss', '2Bar', 'EpBar', 'Jub', '1En',
    '1Meq', '2Meq', '3Meq', 'Reproof', '4Bar', 'EpLao',

    # Books not currently adopted into USFM, in order given by BFBS
    # Metrical Psalms
    'PsMet',
    # Vulgate
    'PrSol', 'PrJer',
    # Armenian
    'WSir', 'EpCorPaul', '3Cor', 'PrEuth', 'DormJohn',
    # NT Codices
    '1Clem', '2Clem', 'Herm', 'Barn', 'Did',

    # Books not currently adopted into USFM, recommended for removal by BFBS
    'JoshA', 'JudgB', 'TobS', 'DanTh', 'SusTh', 'BelTh',

    # Private-Use Extensions
    'XXA', 'XXB', 'XXC', 'XXD', 'XXE', 'XXF', 'XXG',

    # Back Matter
    'BACK', 'CONCORDANCE', 'GLOSSARY',
    'INDEX', 'GAZETTEER', 'X-OTHER'
    ]

specialBooks = ['FRONT', 'INTRODUCTION', 'BACK', 'CONCORDANCE', 'GLOSSARY', 'INDEX', 'GAZETTEER', 'X-OTHER']

peripherals = {
    'Title Page':'titlePage', 'Half Title Page':'x-halfTitlePage', 'Promotional Page':'x-promotionalPage',
    'Imprimatur':'imprimatur', 'Publication Data':'publicationData', 'Foreword':'x-foreword', 'Preface':'preface',
    'Table of Contents':'tableofContents', 'Alphabetical Contents':'x-alphabeticalContents',
    'Table of Abbreviations':'x-tableofAbbreviations', 'Chronology':'x-chronology',
    'Weights and Measures':'x-weightsAndMeasures', 'Map Index':'x-mapIndex',
    'NT Quotes from LXX':'x-ntQuotesFromLXX',
    'Cover':'coverPage',
    'Spine':'x-spine'
    }

introPeripherals = {
    'Bible Introduction':'bible', 'Old Testament Introduction':'oldTestament',
    'Pentateuch Introduction':'pentateuch', 'History Introduction':'history', 'Poetry Introduction':'poetry',
    'Prophecy Introduction':'prophecy', 'New Testament Introduction':'newTestament',
    'Gospels Introduction':'gospels', 'Acts Introduction':'acts', 'Epistles Introduction':'epistles',
    'Letters Introduction':'letters', 'Deuterocanon Introduction':'deuterocanon'
    }

osis2locBk = dict()
loc2osisBk = dict()
filename2osis = dict()
verbose = bool()
ucs4 = (sys.maxunicode > 0xFFFF)

# BEGIN PSF-licensed segment
# keynat from http://code.activestate.com/recipes/285264-natural-string-sorting/
def keynat(string):
    r'''A natural sort helper function for sort() and sorted()
    without using regular expressions or exceptions.

    >>> items = ('Z', 'a', '10th', '1st', '9')
    >>> sorted(items)
    ['10th', '1st', '9', 'Z', 'a']
    >>> sorted(items, key=keynat)
    ['1st', '9', '10th', 'a', 'Z']
    '''
    it = type(1)
    r = []
    for c in string:
        if c.isdigit():
            d = int(c)
            if r and type( r[-1] ) == it:
                r[-1] = r[-1] * 10 + d
            else:
                r.append(d)
        else:
            r.append(c.lower())
    return r
# END PSF-licened segment

def keycanon(filename):
    """Sort helper function that orders according to canon position (defined in canonicalOrder list), returning canonical position or infinity if not in the list."""
    if filename in filename2osis:
        return canonicalOrder.index(filename2osis[filename])
    return float('inf')

def keyusfm(filename):
    """Sort helper function that orders according to USFM book number (defined in usfmNumericOrder list), returning USFM book number or infinity if not in the list."""
    if filename in filename2osis:
        return usfmNumericOrder.index(filename2osis[filename])
    return float('inf')

def keysupplied(filename):
    """Sort helper function that keeps the items in the order in which they were supplied (i.e. it doesn't sort at all), returning the number of times the function has been called."""
    if not hasattr(keysupplied, "counter"):
       keysupplied.counter = 0
    keysupplied.counter += 1
    return keysupplied.counter

def convertToOsis(sFile):
    """Open a USFM file and return a string consisting of its OSIS equivalent.

    Keyword arguments:
    sFile -- Path to the USFM file to be converted

    """
    global encoding
    global relaxedConformance

    verbosePrint(('Processing: ' + sFile))

    def cvtPreprocess(osis, relaxedConformance):
        """Perform preprocessing on a USFM document, returning the processed text as a string.
        Removes excess spaces & CRs and escapes XML entities.

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # lines should never start with non-tags
        osis = re.sub('\n\s*([^\\\s])', r' \1', osis)  # TODO: test this
        # convert CR to LF
        osis = osis.replace('\r', '\n')
        # lines should never end with whitespace (other than \n)
        osis = re.sub('\s+\n', '\n', osis)
        # replace with XML entities, as necessary
        osis = osis.replace('&', '&amp;')
        osis = osis.replace('<', '&lt;')
        osis = osis.replace('>', '&gt;')

        #osis = re.sub('\n'+r'(\\[^\s]+\b\*)', r' \1', osis)

        return osis


    def cvtRelaxedConformanceRemaps(osis, relaxedConformance):
        """Perform preprocessing on a USFM document, returning the processed text as a string.
        Remaps certain deprecated USFM tags to recommended alternatives.

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        if not relaxedConformance:
            return osis

        # \tr#: DEP: map to \tr
        osis = re.sub(r'\\tr\d\b', r'\\tr', osis)

        # remapped 2.0 periphs
        # \pub
        osis = re.sub(r'\\pub\b\s', '\\periph Publication Data\n', osis)
        # \toc : \periph Table of Contents
        osis = re.sub(r'\\toc\b\s', '\\periph Table of Contents\n', osis)
        # \pref
        osis = re.sub(r'\\pref\b\s', '\\periph Preface\n', osis)
        # \maps
        osis = re.sub(r'\\maps\b\s', '\\periph Map Index\n', osis)
        # \cov
        osis = re.sub(r'\\cov\b\s', '\\periph Cover\n', osis)
        # \spine
        osis = re.sub(r'\\spine\b\s', '\\periph Spine\n', osis)
        # \pubinfo
        osis = re.sub(r'\\pubinfo\b\s', '\\periph Publication Information\n', osis)

        # \intro
        osis = re.sub(r'\\intro\b\s', '\\id INT\n', osis)
        # \conc
        osis = re.sub(r'\\conc\b\s', '\\id CNC\n', osis)
        # \glo
        osis = re.sub(r'\\glo\b\s', '\\id GLO\n', osis)
        # \idx
        osis = re.sub(r'\\idx\b\s', '\\id TDX\n', osis)

        return osis


    def cvtIdentification(osis, relaxedConformance):
        """Converts USFM **Identification** tags to OSIS, returning the processed text as a string.

        Supported tags: \id, \ide, \sts, \rem, \h, \toc1, \toc2, \toc3

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # \id_<CODE>_(Name of file, Book name, Language, Last edited, Date etc.)
        osis = re.sub(r'\\id\s+([A-Z0-9]{3})\b\s*([^\\'+'\n]*?)\n'+r'(.*)(?=\\id|$)', lambda m: '\uFDD0<div type="book" osisID="' + bookDict[m.group(1)] + '">\n' + (('<!-- id comment - ' + m.group(2) + ' -->\n') if m.group(2) else '') + m.group(3) + '</div type="book">\uFDD0\n' , osis, flags=re.DOTALL)

        # \ide_<ENCODING>
        osis = re.sub(r'\\ide\b.*'+'\n', '', osis) # delete, since this was handled above

        # \sts_<STATUS CODE>
        osis = re.sub(r'\\sts\b\s+(.+)\s*'+'\n', r'<milestone type="x-usfm-sts" n="\1"/>'+'\n', osis)

        # \rem_text...
        osis = re.sub(r'\\rem\b\s+(.+)', r'<!-- rem - \1 -->', osis)

        # \restore_text...
        if relaxedConformance:
            osis = re.sub(r'\\restore\b\s+(.+)', r'<!-- restore - \1 -->', osis)

        # \h#_text...
        osis = re.sub(r'\\h\b\s+(.+)\s*'+'\n', r'<title type="runningHead">\1</title>'+'\n', osis)
        osis = re.sub(r'\\h(\d)\b\s+(.+)\s*'+'\n', r'<title type="runningHead" n="\1">\2</title>'+'\n', osis)

        # \toc1_text...
        osis = re.sub(r'\\toc1\b\s+(.+)\s*'+'\n', r'<milestone type="x-usfm-toc1" n="\1"/>'+'\n', osis)

        # \toc2_text...
        osis = re.sub(r'\\toc2\b\s+(.+)\s*'+'\n', r'<milestone type="x-usfm-toc2" n="\1"/>'+'\n', osis)

        # \toc3_text...
        osis = re.sub(r'\\toc3\b\s+(.+)\s*'+'\n', lambda m: r'<milestone type="x-usfm-toc3" n="\1"/>'+'\n', osis)

        return osis


    def cvtIntroductions(osis, relaxedConformance):
        """Converts USFM **Introduction** tags to OSIS, returning the processed text as a string.

        Supported tags: \imt#, \is#, \ip, \ipi, \im, \imi, \ipq, \imq, \ipr, \iq#, \ib, \ili#, \iot, \io#, \ior...\ior*, \iex, \iqt...\iqt*, \imte, \ie

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # \imt#_text...
        osis = re.sub(r'\\imt(\d?)\s+(.+)', lambda m: '<title ' + ('level="'+m.group(1)+'" ' if m.group(1) else '') + 'type="main" subType="x-introduction">' + m.group(2) + '</title>', osis)

        # \imte#_text...
        osis = re.sub(r'\\imte(\d?)\b\s+(.+)', lambda m: '<title ' + ('level="'+m.group(1)+'" ' if m.group(1) else '') + 'type="main" subType="x-introduction-end">' + m.group(2) + '</title>', osis)

        # \is#_text...
        osis = re.sub(r'\\is1?\s+(.+)', lambda m: '\uFDDA<div type="section" subType="x-introduction"><title>' + m.group(1) + '</title>', osis)
        osis = re.sub('(\uFDDA[^\uFDD5\uFDD0\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA]+)', r'\1'+'</div>\uFDDA\n', osis, flags=re.DOTALL)
        osis = re.sub(r'\\is2\s+(.+)', lambda m: '\uFDDB<div type="subSection" subType="x-introduction"><title>' + m.group(1) + '</title>', osis)
        osis = re.sub('(\uFDDB[^\uFDD5\uFDD0\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA\uFDDB]+)', r'\1'+'</div>\uFDDB\n', osis, flags=re.DOTALL)
        osis = re.sub(r'\\is3\s+(.+)', lambda m: '\uFDDC<div type="x-subSubSection" subType="x-introduction"><title>' + m.group(1) + '</title>', osis)
        osis = re.sub('(\uFDDC[^\uFDD5\uFDD0\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA\uFDDB\uFDDC]+)', r'\1'+'</div>\uFDDC\n', osis, flags=re.DOTALL)
        osis = re.sub(r'\\is4\s+(.+)', lambda m: '\uFDDD<div type="x-subSubSubSection" subType="x-introduction"><title>' + m.group(1) + '</title>', osis)
        osis = re.sub('(\uFDDD[^\uFDD5\uFDD0\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA\uFDDB\uFDDC\uFDDD]+)', r'\1'+'</div>\uFDDD\n', osis, flags=re.DOTALL)
        osis = re.sub(r'\\is5\s+(.+)', lambda m: '\uFDDE<div type="x-subSubSubSubSection" subType="x-introduction"><title>' + m.group(1) + '</title>', osis)
        osis = re.sub('(\uFDDE[^\uFDD5\uFDD0\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA\uFDDB\uFDDC\uFDDD\uFDDE]+)', r'\1'+'</div>\uFDDE\n', osis, flags=re.DOTALL)

        # \ip_text...
        osis = re.sub(r'\\ip\s+(.*?)(?=(\\(i?m|i?p|nb|lit|cls|tr|io|iq|i?li|iex?|s)|<chapter eID|</?div\b|<(p|closer)\b))', lambda m: '\uFDD3<p subType="x-introduction">\n' + m.group(1) + '\uFDD3</p>\n', osis, flags=re.DOTALL)

        # \ipi_text...
        # \im_text...
        # \imi_text...
        # \ipq_text...
        # \imq_text...
        # \ipr_text...
        pType = {'ipi':'x-indented', 'im':'x-noindent', 'imi':'x-noindent-indented', 'ipq':'x-quote', 'imq':'x-noindent-quote', 'ipr':'x-right'}
        osis = re.sub(r'\\(ipi|im|ipq|imq|ipr)\s+(.*?)(?=(\\(i?m|i?p|nb|lit|cls|tr|io|iq|i?li|iex?|s)|<chapter eID|</?div\b|<(p|closer)\b))', lambda m: '\uFDD3<p type="' + pType[m.group(1)] + '" subType="x-introduction">\n' + m.group(2) + '\uFDD3</p>\n', osis, flags=re.DOTALL)

        # \iq#_text...
        osis = re.sub(r'\\iq\b\s*(.*?)(?=(['+'\uFDD0\uFDD1\uFDD3\uFDD4'+r']|\\i?q[\d\s]|\\fig|<l\b|<lb\b|<title\b))', r'<l level="1" subType="x-introduction">\1</l>', osis, flags=re.DOTALL)
        osis = re.sub(r'\\iq(\d)\b\s*(.*?)(?=(['+'\uFDD0\uFDD1\uFDD3\uFDD4'+r']|\\i?q[\d\s]|\\fig|<l\b|<lb\b|<title\b))', r'<l level="\1" subType="x-introduction">\2</l>', osis, flags=re.DOTALL)

        # \ib
        osis = re.sub(r'\\ib\b\s?', '<lb type="x-p"/>', osis)
        osis = osis.replace('\n</l>', '</l>\n')
        osis = re.sub('(<l [^\uFDD0\uFDD1\uFDD3\uFDD4]+</l>)', r'<lg>\1</lg>', osis, flags=re.DOTALL)
        osis = re.sub('(<lg>.+?</lg>)', lambda m: m.group(1).replace('<lb type="x-p"/>', '</lg><lg>'), osis, flags=re.DOTALL) # re-handle \b that occurs within <lg>

        # \ili#_text...
        osis = re.sub(r'\\ili\b\s*(.*?)(?=(['+'\uFDD0\uFDD1\uFDD3\uFDD4'+r']|\\ili[\d\s]|<lb\b|<title\b|<item\b))', '<item type="x-indent-1" subType="x-introduction">\uFDE0'+r'\1'+'\uFDE0</item>', osis, flags=re.DOTALL)
        osis = re.sub(r'\\ili(\d)\b\s*(.*?)(?=(['+'\uFDD0\uFDD1\uFDD3\uFDD4'+r']|\\ili[\d\s]|<lb\b|<title\b|<item\b))', '<item type="x-indent-\1" subType="x-introduction">\uFDE0'+r'\2'+'\uFDE0</item>', osis, flags=re.DOTALL)
        osis = osis.replace('\n</item>', '</item>\n')
        osis = re.sub('(<item [^\uFDD0\uFDD1\uFDD3\uFDD4]+</item>)', '\uFDD3<list>'+r'\1'+'</list>\uFDD3', osis, flags=re.DOTALL)

        # \iot_text...
        # \io#_text...(references range)
        osis = re.sub(r'\\io\b\s*(.*?)(?=(['+'\uFDD0\uFDD1\uFDD3\uFDD4'+r']|\\io[t\d\s]|\\iex?|<lb\b|<title\b|<item\b))', '<item type="x-indent-1" subType="x-introduction">\uFDE1'+r'\1'+'\uFDE1</item>', osis, flags=re.DOTALL)
        osis = re.sub(r'\\io(\d)\b\s*(.*?)(?=(['+'\uFDD0\uFDD1\uFDD3\uFDD4'+r']|\\io[t\d\s]|\\iex?|<lb\b|<title\b|<item\b))', '<item type="x-indent-\1" subType="x-introduction">\uFDE1'+r'\2'+'\uFDE1</item>', osis, flags=re.DOTALL)
        osis = re.sub(r'\\iot\b\s*(.*?)(?=(['+'\uFDD0\uFDD1\uFDD3\uFDD4'+r']|\\io[t\d\s]|\\iex?|<lb\b|<title\b|<item\b))', '<item type="head">\uFDE1'+r'\1'+'\uFDE1</item type="head">', osis, flags=re.DOTALL)
        osis = osis.replace('\n</item>', '</item>\n')
        osis = re.sub('(<item [^\uFDD0\uFDD1\uFDD3\uFDD4\uFDE0]+</item>)', '\uFDD3<div type="outline"><list>'+r'\1'+'</list></div>\uFDD3', osis, flags=re.DOTALL)
        osis = re.sub('item type="head"', 'head', osis)

        # \ior_text...\ior*
        osis = re.sub(r'\\ior\b\s+(.+?)\\ior\*', r'<reference>\1</reference>', osis, flags=re.DOTALL)

        # \iex  # TODO: look for example; I have no idea what this would look like in context
        osis = re.sub(r'\\iex\b\s*(.+?)'+'?=(\s*(\\c|</div type="book">\uFDD0))', r'<div type="bridge">\1</div>', osis, flags=re.DOTALL)

        # \iqt_text...\iqt*
        osis = re.sub(r'\\iqt\s+(.+?)\\iqt\*', r'<q subType="x-introduction">\1</q>', osis, flags=re.DOTALL)

        # \ie
        osis = re.sub(r'\\ie\b\s*', '<milestone type="x-usfm-ie"/>', osis)

        return osis


    def cvtTitles(osis, relaxedConformance):
        """Converts USFM **Title, Heading, and Label** tags to OSIS, returning the processed text as a string.

        Supported tags: \mt#, \mte#, \ms#, \mr, \s#, \sr, \r, \rq...\rq*, \d, \sp 

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # \ms#_text...
        osis = re.sub(r'\\ms1?\s+(.+)', lambda m: '\uFDD5<div type="majorSection"><title>' + m.group(1) + '</title>', osis)
        osis = re.sub('(\uFDD5[^\uFDD5\uFDD0]+)', r'\1'+'</div>\uFDD5\n', osis, flags=re.DOTALL)
        osis = re.sub(r'\\ms2\s+(.+)', lambda m: '\uFDD6<div type="majorSection" n="2"><title>' + m.group(1) + '</title>', osis)
        osis = re.sub('(\uFDD6[^\uFDD5\uFDD0\uFDD6]+)', r'\1'+'</div>\uFDD6\n', osis, flags=re.DOTALL)
        osis = re.sub(r'\\ms3\s+(.+)', lambda m: '\uFDD7<div type="majorSection" n="3"><title>' + m.group(1) + '</title>', osis)
        osis = re.sub('(\uFDD7[^\uFDD5\uFDD0\uFDD6\uFDD7]+)', r'\1'+'</div>\uFDD7\n', osis, flags=re.DOTALL)
        osis = re.sub(r'\\ms4\s+(.+)', lambda m: '\uFDD8<div type="majorSection" n="4"><title>' + m.group(1) + '</title>', osis)
        osis = re.sub('(\uFDD8[^\uFDD5\uFDD0\uFDD6\uFDD7\uFDD8]+)', r'\1'+'</div>\uFDD8\n', osis, flags=re.DOTALL)
        osis = re.sub(r'\\ms5\s+(.+)', lambda m: '\uFDD9<div type="majorSection" n="5"><title>' + m.group(1) + '</title>', osis)
        osis = re.sub('(\uFDD9[^\uFDD5\uFDD0\uFDD6\uFDD7\uFDD8\uFDD9]+)', r'\1'+'</div>\uFDD9\n', osis, flags=re.DOTALL)

        # \mr_text...
        osis = re.sub(r'\\mr\s+(.+)', '\uFDD4<title type="scope"><reference>'+r'\1</reference></title>', osis)

        # \s#_text...
        osis = re.sub(r'\\s1?\s+(.+)', lambda m: '\uFDDA<div type="section"><title>' + m.group(1) + '</title>', osis)
        osis = re.sub('(\uFDDA<div type="section">[^\uFDD5\uFDD0\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA]+)', r'\1'+'</div>\uFDDA\n', osis, flags=re.DOTALL)
        if relaxedConformance:
            osis = re.sub(r'\\ss\s+', r'\\s2 ', osis)
            osis = re.sub(r'\\sss\s+', r'\\s3 ', osis)
        osis = re.sub(r'\\s2\s+(.+)', lambda m: '\uFDDB<div type="subSection"><title>' + m.group(1) + '</title>', osis)
        osis = re.sub('(\uFDDB<div type="subSection">[^\uFDD5\uFDD0\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA\uFDDB]+)', r'\1'+'</div>\uFDDB\n', osis, flags=re.DOTALL)
        osis = re.sub(r'\\s3\s+(.+)', lambda m: '\uFDDC<div type="x-subSubSection"><title>' + m.group(1) + '</title>', osis)
        osis = re.sub('(\uFDDC<div type="x-subSubSection">[^\uFDD5\uFDD0\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA\uFDDB\uFDDC]+)', r'\1'+'</div>\uFDDC\n', osis, flags=re.DOTALL)
        osis = re.sub(r'\\s4\s+(.+)', lambda m: '\uFDDD<div type="x-subSubSubSection"><title>' + m.group(1) + '</title>', osis)
        osis = re.sub('(\uFDDD<div type="x-subSubSubSection">[^\uFDD5\uFDD0\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA\uFDDB\uFDDC\uFDDD]+)', r'\1'+'</div>\uFDDD\n', osis, flags=re.DOTALL)
        osis = re.sub(r'\\s5\s+(.+)', lambda m: '\uFDDE<div type="x-subSubSubSubSection"><title>' + m.group(1) + '</title>', osis)
        osis = re.sub('(\uFDDE<div type="x-subSubSubSubSection">[^\uFDD5\uFDD0\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA\uFDDB\uFDDC\uFDDD\uFDDE]+)', r'\1'+'</div>\uFDDE\n', osis, flags=re.DOTALL)

        # \sr_text...
        osis = re.sub(r'\\sr\s+(.+)', '\uFDD4<title type="scope"><reference>'+r'\1</reference></title>', osis)
        # \r_text...
        osis = re.sub(r'\\r\s+(.+)', '\uFDD4<title type="parallel"><reference type="parallel">'+r'\1</reference></title>', osis)
        # \rq_text...\rq*
        osis = re.sub(r'\\rq\s+(.+?)\\rq\*', r'<reference type="source">\1</reference>', osis, flags=re.DOTALL)

        # \d_text...
        osis = re.sub(r'\\d\s+(.+)', '\uFDD4<title canonical="true" type="psalm">'+r'\1</title>', osis)

        # \sp_text...
        osis = re.sub(r'\\sp\s+(.+)', r'<speaker>\1</speaker>', osis)

        # \mt#_text...
        osis = re.sub(r'\\mt(\d?)\s+(.+)', lambda m: '<title ' + ('level="'+m.group(1)+'" ' if m.group(1) else '') + 'type="main">' + m.group(2) + '</title>', osis)
        # \mte#_text...
        osis = re.sub(r'\\mte(\d?)\s+(.+)', lambda m: '<title ' + ('level="'+m.group(1)+'" ' if m.group(1) else '') + 'type="main" subType="x-end">' + m.group(2) + '</title>', osis)

        return osis


    def cvtChaptersAndVerses(osis, relaxedConformance):
        """Converts USFM **Chapter and Verse** tags to OSIS, returning the processed text as a string.

        Supported tags: \c, \ca...\ca*, \cl, \cp, \cd, \v, \va...\va*, \vp...\vp*

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # \c_#
        osis = re.sub(r'\\c\s+([^\s]+)\b(.+?)(?=(\\c\s+|</div type="book"))', lambda m: '\uFDD1<chapter osisID="$BOOK$.' + m.group(1) + r'" sID="$BOOK$.' + m.group(1) + '"/>' + m.group(2) + '<chapter eID="$BOOK$.' + m.group(1) + '"/>\uFDD3\n', osis, flags=re.DOTALL)

        # \cp_#
        # \ca_#\ca*
        def replaceChapterNumber(matchObject):
            """Regex helper function to replace chapter numbers from \c_# with values that appeared in \cp_# and \ca_#\ca*, returing the chapter text as a string.

            Keyword arguments:
            matchObject -- a regex match object in which the first element is the chapter text

            """
            ctext = matchObject.group(1)
            cp = re.search(r'\\cp\s+(.+?)(?=(\\|\s))', ctext)
            if cp:
                ctext = re.sub(r'\\cp\s+(.+?)\\cp*', '', ctext, flags=re.DOTALL)
                cp = cp.group(1)
                ctext = re.sub(r'"\$BOOK\$\.([^"\.]+)"', '"$BOOK$.'+ca+'"', ctext)
            ca = re.search(r'\\ca\s+(.+?)\\ca\*', ctext)
            if ca:
                ctext = re.sub(r'\\ca\s+(.+?)\\ca*', '', ctext, flags=re.DOTALL)
                ca = ca.group(1)
                ctext = re.sub(r'(osisID="\$BOOK\$\.[^"\.]+)"', r'\1 $BOOK$.'+ca+'"', ctext)
            return ctext
        osis = re.sub(r'(<chapter [^<]+sID[^<]+/>.+?<chapter eID[^>]+/>)', replaceChapterNumber, osis, flags=re.DOTALL)

        # \cl_
        osis = re.sub(r'\\cl\s+(.+)', '\uFDD4<title>'+r'\1</title>', osis)

        # \cd_#   <--This # seems to be an error
        osis = re.sub(r'\\cd\b\s+(.+)', '\uFDD4<title type="x-description">'+r'\1</title>', osis)

        # \v_#
        osis = re.sub(r'\\v\s+([^\s]+)\b\s*(.+?)(?=(\\v\s+|</div type="book"|<chapter eID))', lambda m: '\uFDD2<verse osisID="$BOOK$.$CHAP$.' + m.group(1) + '" sID="$BOOK$.$CHAP$.' + m.group(1) + '"/>' + m.group(2) + '<verse eID="$BOOK$.$CHAP$.' + m.group(1) + '"/>\uFDD2\n', osis, flags=re.DOTALL)

        # \vp_#\vp*
        # \va_#\va*
        def replaceVerseNumber(matchObject):
            """Regex helper function to replace verse numbers from \v_# with values that appeared in \vp_#\vp* and \va_#\va*, returing the verse text as a string.

            Keyword arguments:
            matchObject -- a regex match object in which the first element is the verse text

            """
            vtext = matchObject.group(1)
            vp = re.search(r'\\vp\s+(.+?)\\vp*', vtext)
            if vp:
                vtext = re.sub(r'\\vp\s+(.+?)\\vp*', '', vtext, flags=re.DOTALL)
                vp = vp.group(1)
                vtext = re.sub(r'"\$BOOK\$\.\$CHAP\$\.([^"\.]+)"', '"$BOOK$.$CHAP$.'+va+'"', vtext)
            va = re.search(r'\\va\s+(.+?)\\va\*', vtext)
            if va:
                vtext = re.sub(r'\\va\s+(.+?)\\va*', '', vtext, flags=re.DOTALL)
                va = va.group(1)
                vtext = re.sub(r'(osisID="\$BOOK\$\.\$CHAP\$\.[^"\.]+)"', r'\1 $BOOK$.$CHAP$.'+va+'"', vtext)
            return vtext
        osis = re.sub(r'(<verse [^<]+sID[^<]+/>.+?<verse eID[^>]+/>)', replaceVerseNumber, osis, flags=re.DOTALL)

        return osis


    def cvtParagraphs(osis, relaxedConformance):
        """Converts USFM **Paragraph** tags to OSIS, returning the processed text as a string.

        Supported tags: \p, \m, \pmo, \pm, \pmc, \pmr, \pi#, \mi, \nb, \cls, \li#, \pc, \pr, \ph#, \b

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # \p(_text...)
        osis = re.sub(r'\\p\s+(.*?)(?=(\\(i?m|i?p|nb|lit|cls|tr)|<chapter eID|</?div\b|<(p|closer)\b))', lambda m: '\uFDD3<p>\n' + m.group(1) + '\uFDD3</p>\n', osis, flags=re.DOTALL)

        # \pc(_text...)
        # \pr(_text...)
        # \m(_text...)
        # \pmo(_text...)
        # \pm(_text...)
        # \pmc(_text...)
        # \pmr_text...  # deprecated: map to same as \pr
        # \pi#(_Sample text...)
        # \mi(_text...)
        # \nb
        # \phi # deprecated
        # \ps # deprecated
        # \psi # deprecated
        # \p# # deprecated
        pType = {'pc':'x-center', 'pr':'x-right', 'm':'x-noindent', 'pmo':'x-embedded-opening', 'pm':'x-embedded', 'pmc':'x-embedded-closing', 'pmr':'x-right', 'pi':'x-indented-1', 'pi1':'x-indented-1', 'pi2':'x-indented-2', 'pi3':'x-indented-3', 'pi4':'x-indented-4', 'pi5':'x-indented-5', 'mi':'x-noindent-indented', 'nb':'x-nobreak', 'phi':'x-indented-hanging', 'ps':'x-nobreakNext', 'psi':'x-nobreakNext-indented', 'p1':'x-level-1', 'p2':'x-level-2', 'p3':'x-level-3', 'p4':'x-level-4', 'p5':'x-level-5'}
        paragraphregex = 'pc|pr|m|pmo|pm|pmc|pmr|pi|pi1|pi2|pi3|pi4|pi5|mi|nb'
        if relaxedConformance:
            paragraphregex += '|phi|ps|psi|p1|p2|p3|p4|p5'
        osis = re.sub(r'\\('+paragraphregex+r')\s+(.*?)(?=(\\(i?m|i?p|nb|lit|cls|tr)|<chapter eID|</?div\b|<(p|closer)\b))', lambda m: '\uFDD3<p type="' + pType[m.group(1)] + '">\n' + m.group(2) + '\uFDD3</p>\n', osis, flags=re.DOTALL)

        # \cls_text...
        osis = re.sub(r'\\m\s+(.+?)(?=(\\(i?m|i?p|nb|lit|cls|tr)|<chapter eID|</?div\b|<(p|closer)\b))', lambda m: '\uFDD3<closer>' + m.group(1) + '\uFDD3</closer>\n', osis, flags=re.DOTALL)

        # \ph#(_text...)
        # \li#(_text...)
        osis = re.sub(r'\\ph\b\s*', r'\\li ', osis)
        osis = re.sub(r'\\ph(\d)\b\s*', r'\\li\1 ', osis)
        osis = re.sub(r'\\li\b\s*(.*?)(?=(['+'\uFDD0\uFDD1\uFDD3\uFDD4'+r']|\\li[\d\s]|<lb\b|<title\b|<item\b))', r'<item type="x-indent-1">\1</item>', osis, flags=re.DOTALL)
        osis = re.sub(r'\\li(\d)\b\s*(.*?)(?=(['+'\uFDD0\uFDD1\uFDD3\uFDD4'+r']|\\li[\d\s]|<lb\b|<title\b|<item\b))', r'<item type="x-indent-\1">\2</item>', osis, flags=re.DOTALL)
        osis = osis.replace('\n</item>', '</item>\n')
        osis = re.sub('(<item [^\uFDD0\uFDD1\uFDD3\uFDD4\uFDE0\uFDE1]+</item>)', '\uFDD3<list>'+r'\1'+'</list>\uFDD3', osis, flags=re.DOTALL)

        # \b
        osis = re.sub(r'\\b\b\s?', '<lb type="x-p"/>', osis)

        return osis


    def cvtPoetry(osis, relaxedConformance):
        """Converts USFM **Poetry** tags to OSIS, returning the processed text as a string.

        Supported tags: \q#, \qr, \qc, \qs...\qs*, \qa, \qac...\qac*, \qm#, \b

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # \qs_(Selah)\qs*
        osis = re.sub(r'\\qs\b\s(.+?)\\qs\*', r'<l type="selah">\1</l>', osis, flags=re.DOTALL)

        # \q#(_text...)
        osis = re.sub(r'\\q\b\s*(.*?)(?=(['+'\uFDD0\uFDD1\uFDD3\uFDD4\uFDD5\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA\uFDDB\uFDDC\uFDDD\uFDDE'+r']|\\q[\d\s]|\\fig|<l\b|<lb\b|<title\b|<list\b|</?div\b))', r'<l level="1">\1</l>', osis, flags=re.DOTALL)
        osis = re.sub(r'\\q(\d)\b\s*(.*?)(?=(['+'\uFDD0\uFDD1\uFDD3\uFDD4\uFDD5\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA\uFDDB\uFDDC\uFDDD\uFDDE'+r']|\\q[\d\s]|\\fig|<l\b|<lb\b|<title\b|<list\b|</?div\b))', r'<l level="\1">\2</l>', osis, flags=re.DOTALL)

        # \qr_text...
        # \qc_text...
        # \qm#(_text...)
        qType = {'qr':'x-right', 'qc':'x-center', 'qm':'x-embedded" level="1', 'qm1':'x-embedded" level="1', 'qm2':'x-embedded" level="2', 'qm3':'x-embedded" level="3', 'qm4':'x-embedded" level="4', 'qm5':'x-embedded" level="5'}
        osis = re.sub(r'\\(qr|qc|qm\d)\b\s*(.*?)(?=(['+'\uFDD0\uFDD1\uFDD3\uFDD4\uFDD5\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA\uFDDB\uFDDC\uFDDD\uFDDE'+r']|\\q[\d\s]|\\fig|<l\b|<lb\b|<title\b|<list\b|</?div\b))', lambda m: '<l type="' + qType[m.group(1)] + '">' + m.group(2) + '</l>', osis, flags=re.DOTALL)

        osis = osis.replace('\n</l>', '</l>\n')
        osis = re.sub('(<l [^\uFDD0\uFDD1\uFDD3\uFDD4\uFDD5\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA\uFDDB\uFDDC\uFDDD\uFDDE]+</l>)', r'<lg>\1</lg>', osis, flags=re.DOTALL)

        # \b
        osis = re.sub('(<lg>.+?</lg>)', lambda m: m.group(1).replace('<lb type="x-p"/>', '</lg><lg>'), osis, flags=re.DOTALL) # re-handle \b that occurs within <lg>

        # \qa_text...
        osis = re.sub(r'\\qa\s+(.+)', '\uFDD4<title type="acrostic">'+r'\1</title>', osis)

        # \qac_text...\qac*
        osis = re.sub(r'\\qac\s+(.+?)\\qac\*', r'<hi type="acrostic">\1</hi>', osis, flags=re.DOTALL)

        return osis


    def cvtTables(osis, relaxedConformance):
        """Converts USFM **Table** tags to OSIS, returning the processed text as a string.

        Supported tags: \tr, \th#, \thr#, \tc#, \tcr#

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # \tr_
        osis = re.sub(r'\\tr\b\s*(.*?)(?=(['+'\uFDD0\uFDD1\uFDD3\uFDD4'+r']|\\tr\s|<lb\b|<title\b))', r'<row>\1</row>', osis, flags=re.DOTALL)

        # \th#_text...
        # \thr#_text...
        # \tc#_text...
        # \tcr#_text...
        tType = {'th':' role="label"', 'thr':' role="label" type="x-right"', 'tc':'', 'tcr':' type="x-right'}
        osis = re.sub(r'\\(thr?|tcr?)\d*\b\s*(.*?)(?=(\\t[hc]|</row))', lambda m: '<cell' + tType[m.group(1)] + '>' + m.group(2) + '</cell>', osis, flags=re.DOTALL)

        return osis


    def processNote(note):
        """Convert note-internal USFM tags to OSIS, returning the note as a string.

        Keyword arguments:
        note -- The note as a string.

        """

        note = note.replace('\n', ' ')

        # \fdc_refs...\fdc*
        note = re.sub(r'\\fdc\b\s(.+?)\\fdc\b\*', r'<seg editions="dc">\1</seg>', note)

        # \fq_
        note = re.sub(r'\\fq\b\s(.+?)(?=(\\f|'+'\uFDDF))', '\uFDDF'+r'<catchWord>\1</catchWord>', note)

        # \fqa_
        note = re.sub(r'\\fqa\b\s(.+?)(?=(\\f|'+'\uFDDF))', '\uFDDF'+r'<rdg type="alternate">\1</rdg>', note)

        # \ft_
        note = re.sub(r'\\ft\s', '', note)

        # \fr_##SEP##
        note = re.sub(r'\\fr\b\s(.+?)(?=(\\f|'+'\uFDDF))', '\uFDDF'+r'<reference type="annotateRef">\1</reference>', note)

        # \fk_
        note = re.sub(r'\\fk\b\s(.+?)(?=(\\f|'+'\uFDDF))', '\uFDDF'+r'<catchWord>\1</catchWord>', note)

        # \fl_
        note = re.sub(r'\\fl\b\s(.+?)(?=(\\f|'+'\uFDDF))', '\uFDDF'+r'<label>\1</label>', note)

        # \fp_
        note = re.sub(r'\\fp\b\s(.+?)(?=(\\fp|$))', r'<p>\1</p>', note)
        note = re.sub(r'(<note\b[^>]*?>)(.*?)<p>', r'\1<p>\2</p><p>', note)

        # \fv_
        note = re.sub(r'\\fv\b\s(.+?)(?=(\\f|'+'\uFDDF))', '\uFDDF'+r'<hi type="super">\1</hi>', note)

        # \fq*,\fqa*,\ft*,\fr*,\fk*,\fl*,\fp*,\fv*
        note = re.sub(r'\\f(q|qa|t|r|k|l|p|v)\*', '', note)

        note = note.replace('\uFDDF', '')
        return note


    def cvtFootnotes(osis, relaxedConformance):
        """Converts USFM **Footnote** tags to OSIS, returning the processed text as a string.

        Supported tags: \f...\f*, \fe...\fe*, \fr, \fk, \fq, \fqa, \fl, \fp, \fv, \ft, \fdc...\fdc*, \fm...\fm*

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # \f_+_...\f*
        osis = re.sub(r'\\f\s+([^\s\\]+)?\s*(.+?)\s*\\f\*', lambda m: '<note' + ((' n=""') if (m.group(1) == '-') else ('' if (m.group(1) == '+') else (' n="' + m.group(1) + '"'))) + ' placement="foot">' + m.group(2) + '\uFDDF</note>', osis, flags=re.DOTALL)

        # \fe_+_...\fe*
        osis = re.sub(r'\\fe\s+([^\s\\]+?)\s*(.+?)\s*\\fe\*', lambda m: '<note' + ((' n=""') if (m.group(1) == '-') else ('' if (m.group(1) == '+') else (' n="' + m.group(1) + '"'))) + ' placement="end">' + m.group(2) + '\uFDDF</note>', osis, flags=re.DOTALL)

        osis = re.sub(r'(<note\b[^>]*?>.*?</note>)', lambda m: processNote(m.group(1)), osis, flags=re.DOTALL)

        # \fm_...\fm*
        osis = re.sub(r'\\fm\b\s(.+?)\\fm\*', r'<hi type="super">\1</hi>', osis)

        return osis


    def processXref(note):
        """Convert cross-reference note-internal USFM tags to OSIS, returning the cross-reference note as a string.

        Keyword arguments:
        note -- The cross-reference note as a string.

        """

        note = note.replace('\n', ' ')

        # \xot_refs...\xot*
        note = re.sub(r'\\xot\b\s(.+?)\\xot\b\*', '\uFDDF'+r'<seg editions="ot">\1</seg>', note)

        # \xnt_refs...\xnt*
        note = re.sub(r'\\xnt\b\s(.+?)\\xnt\b\*', '\uFDDF'+r'<seg editions="nt">\1</seg>', note)

        # \xdc_refs...\xdc*
        note = re.sub(r'\\xdc\b\s(.+?)\\xdc\b\*', '\uFDDF'+r'<seg editions="dc">\1</seg>', note)

        # \xq_
        note = re.sub(r'\\xq\b\s(.+?)(?=(\\x|'+'\uFDDF))', '\uFDDF'+r'<catchWord>\1</catchWord>', note)

        # \xo_##SEP##
        note = re.sub(r'\\xo\b\s(.+?)(?=(\\x|'+'\uFDDF))', '\uFDDF'+r'<reference type="annotateRef">\1</reference>', note)

        # \xk_
        note = re.sub(r'\\xk\b\s(.+?)(?=(\\x|'+'\uFDDF))', '\uFDDF'+r'<catchWord>\1</catchWord>', note)

        # \xt_  # This isn't guaranteed to be *the* reference, but it's a good guess.
        note = re.sub(r'\\xt\b\s(.+?)(?=(\\x|'+'\uFDDF))', '\uFDDF'+r'<reference>\1</reference>', note)

        if relaxedConformance:
            # TODO: move this to a concorance/index-specific section?
            # \xtSee..\xtSee*: Concordance and Names Index markup for an alternate entry target reference.
            note = re.sub(r'\\xtSee\b\s(.+?)\\xtSee\b\*', '\uFDDF'+r'<reference osisRef="\1">See: \1</reference>', note)
            # \xtSeeAlso...\xtSeeAlso: Concordance and Names Index markup for an additional entry target reference.
            note = re.sub(r'\\xtSeeAlso\b\s(.+?)\\xtSeeAlso\b\*', '\uFDDF'+r'<reference osisRef="\1">See also: \1</reference>', note)

        # \xq*,\xt*,\xo*,\xk*
        note = re.sub(r'\\x(q|t|o|k)\*', '', note)

        note = note.replace('\uFDDF', '')
        return note


    def cvtCrossReferences(osis, relaxedConformance):
        """Converts USFM **Cross Reference** tags to OSIS, returning the processed text as a string.

        Supported tags: \\x...\\x*, \\xo, \\xk, \\xq, \\xt, \\xot...\\xot*, \\xnt...\\xnt*, \\xdc...\\xdc*

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # \x_+_...\x*
        osis = re.sub(r'\\x\s+([^\s]+?)\s+(.+?)\s*\\x\*', lambda m: '<note' + ((' n=""') if (m.group(1) == '-') else ('' if (m.group(1) == '+') else (' n="' + m.group(1) + '"'))) + ' type="crossReference">' + m.group(2) + '\uFDDF</note>', osis, flags=re.DOTALL)

        osis = re.sub(r'(<note [^>]*?type="crossReference"[^>]*>.*?</note>)', lambda m: processXref(m.group(1)), osis, flags=re.DOTALL)

        return osis


    ### Special Text and Character Styles
    def cvtSpecialText(osis, relaxedConformance):
        """Converts USFM **Special Text** tags to OSIS, returning the processed text as a string.

        Supported tags: \add...\add*, \bk...\bk*, \dc...\dc*, \k...\k*, \lit, \nd...\nd*, \ord...\ord*, \pn...\pn*, \qt...\qt*, \sig...\sig*, \sls...\sls*, \tl...\tl*, \wj...\wj*

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # \add_...\add*
        osis = re.sub(r'\\add\s+(.+?)\\add\*', r'<transChange type="added">\1</transChange>', osis, flags=re.DOTALL)

        # \wj_...\wj*
        osis = re.sub(r'\\wj\s+(.+?)\\wj\*', r'<q who="Jesus" marker="">\1</q>', osis, flags=re.DOTALL)

        # \nd_...\nd*
        osis = re.sub(r'\\nd\s+(.+?)\\nd\*', r'<divineName>\1</divineName>', osis, flags=re.DOTALL)

        # \pn_...\pn*
        osis = re.sub(r'\\pn\s+(.+?)\\pn\*', r'<name>\1</name>', osis, flags=re.DOTALL)

        # \qt_...\qt* # TODO:should this be <q>?
        osis = re.sub(r'\\qt\s+(.+?)\\qt\*', r'<seg type="otPassage">\1</seg>', osis, flags=re.DOTALL)

        # \sig_...\sig*
        osis = re.sub(r'\\sig\s+(.+?)\\sig\*', r'<signed>\1</signed>', osis, flags=re.DOTALL)

        # \ord_...\ord*
        osis = re.sub(r'\\ord\s+(.+?)\\ord\*', r'<hi type="super">\1</hi>', osis, flags=re.DOTALL) # semantic incongruity (ordinal -> superscript)

        # \tl_...\tl*
        osis = re.sub(r'\\tl\s+(.+?)\\tl\*', r'<foreign>\1</foreign>', osis, flags=re.DOTALL)

        # \bk_...\bk*
        osis = re.sub(r'\\bk\s+(.+?)\\bk\*', r'<name type="x-workTitle">\1</name>', osis, flags=re.DOTALL)

        # \k_...\k*
        osis = re.sub(r'\\k\s+(.+?)\\k\*', r'<seg type="keyword">\1</seg>', osis, flags=re.DOTALL)

        # \lit
        osis = re.sub(r'\\lit\s+(.*?)(?=(\\(i?m|i?p|nb|lit|cls|tr)|<chapter eID|</?div\b|<(p|closer)\b))', lambda m: '\uFDD3<p type="x-liturgical">\n' + m.group(1) + '\uFDD3</p>\n', osis, flags=re.DOTALL)

        # \dc_...\dc*  # TODO: Find an example---should this really be transChange?
        osis = re.sub(r'\\dc\b\s*(.+?)\\dc\*', r'<transChange type="added" editions="dc">\1</transChange>', osis, flags=re.DOTALL)

        # \sls_...\sls*
        osis = re.sub(r'\\sls\b\s*(.+?)\\sls\*', r'<foreign>/1</foreign>', osis, flags=re.DOTALL)  # TODO: find a better mapping than <foreign>?

        if relaxedConformance:
            # \addpn...\addpn*
            osis = re.sub(r'\\addpn\s+(.+?)\\addpn\*', r'<hi type="x-dotUnderline">\1</hi>', osis, flags=re.DOTALL)
            # \k# # TODO: unsure of this tag's purpose
            osis = re.sub(r'\\k1\s+(.+?)\\k1\*', r'<seg type="keyword" n="1">\1</seg>', osis, flags=re.DOTALL)
            osis = re.sub(r'\\k2\s+(.+?)\\k2\*', r'<seg type="keyword" n="2">\1</seg>', osis, flags=re.DOTALL)
            osis = re.sub(r'\\k3\s+(.+?)\\k3\*', r'<seg type="keyword" n="3">\1</seg>', osis, flags=re.DOTALL)
            osis = re.sub(r'\\k4\s+(.+?)\\k4\*', r'<seg type="keyword" n="4">\1</seg>', osis, flags=re.DOTALL)
            osis = re.sub(r'\\k5\s+(.+?)\\k5\*', r'<seg type="keyword" n="5">\1</seg>', osis, flags=re.DOTALL)

        return osis


    def cvtCharacterStyling(osis, relaxedConformance):
        """Converts USFM **Character Styling** tags to OSIS, returning the processed text as a string.

        Supported tags: \em...\em*, \bd...\bd*, \it...\it*, \bdit...\bdit*, \no...\no*, \sc...\sc*

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # \em_...\em*
        osis = re.sub(r'\\em\s+(.+?)\\em\*', r'<hi type="emphasis">\1</hi>', osis, flags=re.DOTALL)

        # \bd_...\bd*
        osis = re.sub(r'\\bd\s+(.+?)\\bd\*', r'<hi type="bold">\1</hi>', osis, flags=re.DOTALL)

        # \it_...\it*
        osis = re.sub(r'\\it\s+(.+?)\\it\*', r'<hi type="italic">\1</hi>', osis, flags=re.DOTALL)

        # \bdit_...\bdit*
        osis = re.sub(r'\\bdit\s+(.+?)\\bdit\*', r'<hi type="bold"><hi type="italic">\1</hi></hi>', osis, flags=re.DOTALL)

        # \no_...\no*
        osis = re.sub(r'\\no\s+(.+?)\\no\*', r'<hi type="normal">\1</hi>', osis, flags=re.DOTALL)

        # \sc_...\sc*
        osis = re.sub(r'\\sc\s+(.+?)\\sc\*', r'<hi type="small-caps">\1</hi>', osis, flags=re.DOTALL)

        return osis


    def cvtSpacingAndBreaks(osis, relaxedConformance):
        """Converts USFM **Spacing and Breaks** tags to OSIS, returning the processed text as a string.

        Supported tags: ~, //, \pb

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # ~
        osis = osis.replace('~', '\u00A0')

        # //
        osis = osis.replace('//', '<lb type="x-optional"/>')

        # \pb
        osis = re.sub(r'\\pb\s*', '<milestone type="pb"/>\n', osis, flags=re.DOTALL)

        return osis


    def cvtSpecialFeatures(osis, relaxedConformance):
        """Converts USFM **Special Feature** tags to OSIS, returning the processed text as a string.

        Supported tags: \fig...\fig*, \ndx...\ndx*, \pro...\pro*, \w...\w*, \wg...\wg*, \wh...\wh*

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # \fig DESC|FILE|SIZE|LOC|COPY|CAP|REF\fig*
        def makeFigure(matchObject):
            """Regex helper function to convert USFM \fig to OSIS <figure/>, returning the OSIS element as a string.

            Keyword arguments:
            matchObject -- a regex match object containing the elements of a USFM \fig tag

            """
            fig_desc,fig_file,fig_size,fig_loc,fig_copy,fig_cap,fig_ref = matchObject.groups()
            figure = '<figure'
            if fig_file:
                figure += ' src="' + fig_file + '"'
            if fig_size:
                figure += ' size="' + fig_size + '"'
            if fig_copy:
                figure += ' rights="' + fig_copy + '"'
            # TODO: implement parsing in osisParse(Bible reference string)
            # if fig_ref:
            #    figure += ' annotateRef="' + osisParse(fig_ref) + '"'
            figure += '>\n'
            if fig_cap:
                figure += '<caption>' + fig_cap + '</caption>\n'
            if fig_ref:
                figure += '<reference type="annotateRef">' + fig_ref + '</reference>\n'
            if fig_desc:
                figure += '<!-- fig DESC - ' + fig_desc + ' -->\n'
            if fig_loc:
                figure += '<!-- fig LOC - ' + fig_loc + ' -->\n'
            figure += '</figure>'
            return figure
        osis = re.sub(r'\\fig\b\s+([^\|]*)\s*\|([^\|]*)\s*\|([^\|]*)\s*\|([^\|]*)\s*\|([^\|]*)\s*\|([^\|]*)\s*\|([^\\]*)\s*\\fig\*', makeFigure, osis)

        # \ndx_...\ndx* # TODO tag with x-glossary instead of <index/>? Is <index/> containerable?
        osis = re.sub(r'\\ndx\s+(.+?)(\s*)\\ndx\*', r'\1<index index="Index" level1="\1"/>\2', osis, flags=re.DOTALL)

        # \pro_...\pro*
        osis = re.sub(r'([^\s]+)(\s*)\\pro\s+(.+?)(\s*)\\pro\*', r'<w xlit="\3">\1</w>\2\4', osis, flags=re.DOTALL)

        # \w_...\w*
        osis = re.sub(r'\\w\s+(.+?)(\s*)\\w\*', r'\1<index index="Glossary" level1="\1"/>\2', osis, flags=re.DOTALL)

        # \wg_...\wg*
        osis = re.sub(r'\\wg\s+(.+?)(\s*)\\wg\*', r'\1<index index="Greek" level1="\1"/>\2', osis, flags=re.DOTALL)

        # \wh_...\wh*
        osis = re.sub(r'\\wh\s+(.+?)(\s*)\\wh\*', r'\1<index index="Hebrew" level1="\1"/>\2', osis, flags=re.DOTALL)

        if relaxedConformance:
            # \wr...\wr*
            osis = re.sub(r'\\wr\s+(.+?)(\s*)\\wr\*', r'\1<index index="Reference" level1="\1"/>\2', osis, flags=re.DOTALL)

        return osis


    def cvtPeripherals(osis, relaxedConformance):
        """Converts USFM **Peripheral** tags to OSIS, returning the processed text as a string.

        Supported tag: \periph

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # \periph
        def tagPeriph(matchObject):
            """Regex helper function to tag peripherals, returning a <div>-encapsulated string.

            Keyword arguments:
            matchObject -- a regex match object containing the peripheral type and contents

            """
            periphType,contents = matchObject
            periph = '<div type="'
            if periphType in peripherals:
                periph += peripherals[periphType]
            elif periphType in introPeripherals:
                periph += 'introduction" subType="x-' + introPeripherals[periphType]
            else:
                periph += 'x-unknown'
            periph += '">\n' + contents + '</div>\n'
            return periph

        osis = re.sub(r'\\periph\s+([^'+'\n'+r']+)\s*'+'\n'+r'(.+?)(?=(</div type="book">|\\periph\s+))', tagPeriph, osis, flags=re.DOTALL)

        return osis


    def cvtStudyBibleContent(osis, relaxedConformance):
        """Converts USFM **Study Bible Content** tags to OSIS, returning the processed text as a string.

        Supported tags: \ef...\ef*, \ex...\ex*, \esb...\esbe, \cat

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # \ef...\ef*
        osis = re.sub(r'\\ef\s+([^\s\\]+?)\s*(.+?)\s*\\ef\*', lambda m: '<note' + ((' n=""') if (m.group(1) == '-') else ('' if (m.group(1) == '+') else (' n="' + m.group(1) + '"'))) + ' type="study">' + m.group(2) + '\uFDDF</note>', osis, flags=re.DOTALL)
        osis = re.sub(r'(<note\b[^>]*?>.*?</note>)', lambda m: processNote(m.group(1)), osis, flags=re.DOTALL)

        # \ex...\ex*
        osis = re.sub(r'\\ex\s+([^\s]+?)\s+(.+?)\s*\\ex\*', lambda m: '<note' + ((' n=""') if (m.group(1) == '-') else ('' if (m.group(1) == '+') else (' n="' + m.group(1) + '"'))) + ' type="crossReference" subType="x-study"><reference>' + m.group(2) + '</reference>\uFDDF</note>', osis, flags=re.DOTALL)
        osis = re.sub(r'(<note [^>]*?type="crossReference"[^>]*>.*?</note>)', lambda m: processXref(m.group(1)), osis, flags=re.DOTALL)

        # \esb...\esbex  # TODO: this likely needs to go much earlier in the process
        osis = re.sub(r'\\esb\b\s*(.+?)\\esbe\b\s*', '\uFDD5<div type="x-sidebar">'+r'\1'+'</div>\uFDD5\n', osis, flags=re.DOTALL)

        # \cat_<TAG>\cat*
        osis = re.sub(r'\\cat\b\s+(.+?)\\cat\*', r'<index index="category" level1="\1"/>', osis)

        return osis


    def cvtPrivateUseExtensions(osis, relaxedConformance):
        """Converts USFM **\z namespace** tags to OSIS, returning the processed text as a string.

        Supported tags: \z<Extension>

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        ### We can't really know what these mean, but will preserve them as <milestone/> elements.

        # publishing assistant markers
        # \zpa-xb...\zpa-xb* : \periph Book
        # \zpa-xc...\zpa-xc* : \periph Chapter
        # \zpa-xv...\zpa-xv* : \periph Verse
        # \zpa-xd...\zpa-xd* : \periph Description
        # TODO: Decide how these should actually be encoded. In lieu of that,
        # these can all be handled by the default \z Namespace handlers:

        # \z{X}...\z{X}*
        osis = re.sub(r'\z([^\s]+)\s(.+?)(\z\1\*)', r'<seg type="x-\1">\2</seg>', osis, flags=re.DOTALL)

        # \z{X}
        osis = re.sub(r'\\z([^\s]+)', r'<milestone type="x-usfm-z-\1"/>', osis)

        return osis


    def processOsisIDs(osis):
        """Perform postprocessing on an OSIS document, returning the processed text as a string.
        Recurses through chapter & verses, substituting acutal book IDs & chapter numbers for placeholders.

        Keyword arguments:
        osis -- The document as a string.

        """
        # TODO: add support for subverses, including in ranges/series, e.g. Matt.1.1!b-Matt.2.5,Matt.2.7!a
        # TODO: make sure that descending ranges generate invalid markup (osisID="")
        # expand verse ranges, series
        def expandRange(vRange):
            """Expands a verse range into its constituent verses as a string.

            Keyword arguments:
            vRange -- A string of the lower & upper bounds of the range, with a hypen in between.
            
            """
            vRange = re.findall(r'\d+', vRange)
            osisID = list()
            for n in range(int(vRange[0]), int(vRange[1])+1):
                osisID.append('$BOOK$.$CHAP$.'+str(n))
            return ' '.join(osisID)
        osis = re.sub(r'\$BOOK\$\.\$CHAP\$\.(\d+-\d+)"', lambda m: expandRange(m.group(1))+'"', osis)

        def expandSeries(vSeries):
            """Expands a verse series (list) into its constituent verses as a string.

            Keyword arguments:
            vSeries -- A comma-separated list of verses.
            
            """

            vSeries = re.findall(r'\d+', vSeries)
            osisID = list()
            for n in vSeries:
                osisID.append('$BOOK$.$CHAP$.'+str(n))
            return ' '.join(osisID)
        osis = re.sub(r'\$BOOK\$\.\$CHAP\$\.(\d+(,\d+)+)"', lambda m: expandSeries(m.group(1))+'"', osis)

        # fill in book & chapter values
        bookChunks = osis.split('\uFDD0')
        osis = ''
        for bc in bookChunks:
            bookValue = re.search(r'<div type="book" osisID="([^"]+?)"', bc)
            if bookValue:
                bookValue = bookValue.group(1)
                bc = bc.replace('$BOOK$', bookValue)
                chapChunks = bc.split('\uFDD1')
                newbc = ''
                for cc in chapChunks:
                    chapValue = re.search(r'<chapter osisID="[^\."]+\.([^"]+)', cc)
                    if chapValue:
                        chapValue = chapValue.group(1)
                        cc = cc.replace('$CHAP$', chapValue)
                    newbc += cc
                bc = newbc
            osis += bc
        return osis


    def osisReorderAndCleanup(osis):
        """Perform postprocessing on an OSIS document, returning the processed text as a string.
        Reorders elements, strips non-characters, and cleans up excess spaces & newlines

        Keyword arguments:
        osis -- The document as a string.
        relaxedConformance -- Boolean value indicating whether to process non-standard & deprecated USFM tags.

        """

        # assorted re-orderings
        osis = re.sub('(\uFDD3<chapter eID=.+?\n)(<verse eID=.+?>\uFDD2)\n?', r'\2'+'\n'+r'\1', osis)
        osis = re.sub('([\uFDD5\uFDD6\uFDD7\uFDD8\uFDD9]</div>)([^\uFDD5\uFDD6\uFDD7\uFDD8\uFDD9]*<chapter eID.+?>)', r'\2\1', osis)
        osis = re.sub('(\uFDD3</p>\n?\uFDD3<p>)\n?(<verse eID=.+?>\uFDD2)\n?', r'\2'+'\n'+r'\1'+'\n', osis)
        osis = re.sub('\n(<verse eID=.+?>\uFDD2)', r'\1'+'\n', osis)
        osis = re.sub('\n*(<l.+?>)(<verse eID=.+?>[\uFDD2\n]*<verse osisID=.+?>)', r'\2\1', osis)

        # delete attributes from end tags (since they are invalid)
        osis = re.sub(r'(</[^\s>]+) [^>]*>', r'\1>', osis)
        osis = osis.replace('<lb type="x-p"/>', '<lb/>')
        # delete Unicode non-characters
        for c in '\uFDD0\uFDD1\uFDD2\uFDD3\uFDD4\uFDD5\uFDD6\uFDD7\uFDD8\uFDD9\uFDDA\uFDDB\uFDDC\uFDDD\uFDDE\uFDDF\uFDE0\uFDE1\uFDE2\uFDE3\uFDE4\uFDE5\uFDE6\uFDE7\uFDE8\uFDE9\uFDEA\uFDEB\uFDEC\uFDED\uFDEE\uFDEF':
            osis = osis.replace(c, '')

        for endBlock in ['p', 'div', 'note', 'l', 'lg', 'chapter', 'verse', 'head', 'title', 'item', 'list']:
            osis = re.sub('\s+</'+endBlock+'>', '</'+endBlock+r'>\n', osis)
            osis = re.sub('\s+<'+endBlock+'( eID=[^/>]+/>)', '<'+endBlock+r'\1'+'\n', osis)
        osis = re.sub(' +((</[^>]+>)+) *', r'\1 ', osis)

        # strip extra spaces & newlines
        osis = re.sub('  +', ' ', osis)
        osis = re.sub(' ?\n\n+', '\n', osis)
        return osis

    ### Processing starts here
    if encoding:
        osis = codecs.open(sFile, 'r', encoding).read().strip() + '\n'
    else:
        encoding = 'utf-8'
        osis = codecs.open(sFile, 'r', encoding).read().strip() + '\n'
        # \ide_<ENCODING>
        encoding = re.search(r'\\ide\s+(.+)'+'\n', osis)
        if encoding:
            encoding = encoding.group(1).lower().strip()
            if encoding != 'utf-8':
                if encoding in aliases:
                    osis = codecs.open(sFile, 'r', encoding).read().strip() + '\n'
                else:
                    print(('WARNING: Encoding "' + encoding + '" unknown, processing ' + sFile + ' as UTF-8.'))
                    encoding = 'utf-8'

    # call individual conversion processors in series
    osis = cvtPreprocess(osis, relaxedConformance)
    osis = cvtRelaxedConformanceRemaps(osis, relaxedConformance)
    osis = cvtIdentification(osis, relaxedConformance)
    osis = cvtIntroductions(osis, relaxedConformance)
    osis = cvtTitles(osis, relaxedConformance)
    osis = cvtChaptersAndVerses(osis, relaxedConformance)
    osis = cvtParagraphs(osis, relaxedConformance)
    osis = cvtPoetry(osis, relaxedConformance)
    osis = cvtTables(osis, relaxedConformance)
    osis = cvtFootnotes(osis, relaxedConformance)
    osis = cvtCrossReferences(osis, relaxedConformance)
    osis = cvtSpecialText(osis, relaxedConformance)
    osis = cvtCharacterStyling(osis, relaxedConformance)
    osis = cvtSpacingAndBreaks(osis, relaxedConformance)
    osis = cvtSpecialFeatures(osis, relaxedConformance)
    osis = cvtPeripherals(osis, relaxedConformance)
    osis = cvtStudyBibleContent(osis, relaxedConformance)
    osis = cvtPrivateUseExtensions(osis, relaxedConformance)

    osis = processOsisIDs(osis)
    osis = osisReorderAndCleanup(osis)

    # change type on special books
    for sb in specialBooks:
        osis = osis.replace('<div type="book" osisID="' + sb + '">', '<div type="' + sb.lower() + '">')

    if DEBUG:
        localUnhandledTags = set(re.findall(r'(\\[^\s\*]+?\b\*?)', osis))
        if localUnhandledTags:
            print(('Unhandled USFM tags in ' + sFile + ': ' + ', '.join(localUnhandledTags) + ' (' + str(len(localUnhandledTags)) + ' total)'))

    return osis

def readIdentifiersFromOsis(filename):
    """Reads the USFM file and stores information about which Bible book it represents and localized abbrevations in global variables.

    Keyword arguments:
    filename -- a USFM filename

    """

    global encoding
    global loc2osisBk, osis2locBk, filename2osis

    ### Processing starts here
    if encoding:
        osis = codecs.open(filename, 'r', encoding).read().strip() + '\n'
    else:
        encoding = 'utf-8'
        osis = codecs.open(filename, 'r', encoding).read().strip() + '\n'
        # \ide_<ENCODING>
        encoding = re.search(r'\\ide\s+(.+)'+'\n', osis)
        if encoding:
            encoding = encoding.group(1).lower().strip()
            if encoding != 'utf-8':
                if encoding in aliases:
                    osis = codecs.open(filename, 'r', encoding).read().strip() + '\n'
                else:
                    #print(('WARNING: Encoding "' + encoding + '" unknown, processing ' + filename + ' as UTF-8.'))
                    encoding = 'utf-8'

    # keep a copy of the OSIS book abbreviation for below (\toc3 processing) to store for mapping localized book names to/from OSIS
    osisBook = re.search(r'\\id\s+([A-Z0-9]+)', osis)
    if osisBook:
        osisBook = bookDict[osisBook.group(1)]
        filename2osis[filename] = osisBook

    locBook = re.search(r'\\toc3\b\s+(.+)\s*'+'\n', osis)
    if locBook:
        locBook = locBook.group(1)
        if osisBook:
            osis2locBk[osisBook]=locBook
            loc2osisBk[locBook]=osisBook

def verbosePrint(text):
    """Wraper for print() that only prints if verbose is True."""
    if verbose:
        print(text)

def printUsage():
    """Prints usage statement."""
    print(('usfm2osis.py -- USFM ' + usfmVersion + ' to OSIS ' + osisVersion + ' converter version ' + scriptVersion))
    print(('                Revision: ' + rev + ' (' + date + ')'))
    print('')
    print('Usage: usfm2osis.py <osisWork> [OPTION] ...  <USFM filename|wildcard> ...')
    print('')
    print('  -d               debug mode (single-threaded, verbose output')
    print('  -e ENCODING      input encoding override (default is to read the USFM file\'s')
    print('                     \\ide value or assume UTF-8 encoding in its absence)')
    print('  -h, --help       print this usage information')
    print('  -o FILENAME      output filename (default is: <osisWork>.osis.xml)')
    print('  -r               enable relaxed markup processing (for non-standard USFM)')
    print('  -s mode          set book sorting mode: natural (default), alpha, canonical,')
    print('                     usfm, random, none')
    print('  -v               verbose feedback')
    print('  -x               disable XML validation')
    print('')
    print('As an example, if you want to generate the osisWork <Bible.KJV> and your USFM')
    print('  are located in the ./KJV folder, enter:')
    print('    python usfm2osis.py Bible.KJV ./KJV/*.usfm')
    verbosePrint('')
    verbosePrint('Supported encodings: ' + ', '.join(aliases))


class Worker(multiprocessing.Process):
    """Worker object for multiprocessing."""
    def __init__(self, work_queue, result_queue):
        # base class initialization
        multiprocessing.Process.__init__(self)

        # job management stuff
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.kill_received = False

    def run(self):
        while not self.kill_received:
            # get a task
            try:
                job = self.work_queue.get_nowait()
            except Queue.Empty:
                break

            # the actual processing
            osis = convertToOsis(job)
            # TODO: move XML validation here?

            # store the result
            self.result_queue.put((job,osis))

osisSchema = r'<xs:schema targetNamespace="http://www.bibletechnologies.net/2003/OSIS/namespace" xmlns="http://www.bibletechnologies.net/2003/OSIS/namespace" xmlns:xs="http://www.w3.org/2001/XMLSchema" elementFormDefault="qualified" attributeFormDefault="unqualified" xml:lang="en"><xs:import namespace="http://www.w3.org/XML/1998/namespace" schemaLocation="http://www.w3.org/2001/xml.xsd"/><xs:element name="osis" type="osisCT"/><xs:complexType name="osisCT"><xs:choice><xs:element name="osisCorpus" type="osisCorpusCT" minOccurs="0"/><xs:element name="osisText" type="osisTextCT" minOccurs="0"/></xs:choice><xs:attribute name="TEIform" fixed="TEI.2"/></xs:complexType><xs:complexType name="osisCorpusCT"><xs:sequence><xs:element name="header" type="corpusHeaderCT" minOccurs="0"/><xs:element name="titlePage" type="titlePageCT" minOccurs="0" maxOccurs="1"/><xs:element name="osisText" type="osisTextCT" minOccurs="1" maxOccurs="unbounded"/></xs:sequence><xs:attribute name="TEIform" fixed="teiCorpus.2"/></xs:complexType><xs:complexType name="corpusHeaderCT"><xs:sequence><xs:element name="revisionDesc" type="revisionDescCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="work" type="workCT" maxOccurs="unbounded"/></xs:sequence><xs:attribute name="TEIform" fixed="teiHeader"/><xs:attribute name="canonical" type="xs:boolean" use="optional" default="false"/></xs:complexType><xs:complexType name="osisTextCT"><xs:sequence><xs:element name="header" type="headerCT"/><xs:element name="titlePage" type="titlePageCT" minOccurs="0" maxOccurs="1"/><xs:element name="div" type="divCT" minOccurs="0" maxOccurs="unbounded"/></xs:sequence><xs:attribute name="annotateRef" type="annotateRefType" use="optional"/><xs:attribute name="canonical" type="xs:boolean" use="optional" default="true"/><xs:attribute name="ID" type="xs:ID" use="optional"/><xs:attribute name="osisID" type="osisIDType" use="optional"/><xs:attribute name="osisIDWork" type="osisWorkType" use="required"/><xs:attribute name="osisRefWork" type="osisWorkType" use="optional" default="Bible"/><xs:attribute name="type" type="attributeExtension" use="optional"/><xs:attribute name="subType" type="attributeExtension" use="optional"/><xs:attribute ref="xml:lang" use="required"/><xs:attribute ref="xml:space" default="default"/><xs:attribute name="TEIform" fixed="text"/></xs:complexType><xs:complexType name="headerCT"><xs:sequence><xs:element name="revisionDesc" type="revisionDescCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="work" type="workCT" maxOccurs="unbounded"/><xs:element name="workPrefix" type="workPrefixCT" minOccurs="0" maxOccurs="unbounded"/></xs:sequence><xs:attribute name="TEIform" fixed="teiHeader"/><xs:attribute name="canonical" type="xs:boolean" use="optional" default="false"/></xs:complexType><xs:complexType name="actorCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="index" type="indexCT"/><xs:element name="note" type="noteCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="who" type="xs:string" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="actor"/></xs:complexType><xs:complexType name="castGroupCT"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="head" type="headCT"/><xs:element name="castItem" type="castItemCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="castGroup"/></xs:complexType><xs:complexType name="castItemCT"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="actor" type="actorCT"/><xs:element name="role" type="roleCT"/><xs:element name="roleDesc" type="roleDescCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="castItem"/></xs:complexType><xs:complexType name="castListCT"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="castGroup" type="castGroupCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="castList"/></xs:complexType><xs:complexType name="contributorCT"><xs:simpleContent><xs:extension base="xs:string"><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="file-as" type="xs:string" use="optional"/><xs:attribute name="role" type="roleType" use="optional"/><xs:attributeGroup ref="globalWithType"/></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="coverageCT"><xs:simpleContent><xs:extension base="xs:string"><xs:attributeGroup ref="globalWithType"/><xs:attribute name="canonical" type="xs:boolean" use="optional"/></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="creatorCT"><xs:simpleContent><xs:extension base="xs:string"><xs:attribute name="role" type="roleType" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="canonical" type="xs:boolean" use="optional"/></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="descriptionCT"><xs:simpleContent><xs:extension base="xs:string"><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="type" type="descriptionType" use="optional"/><xs:attribute name="canonical" type="xs:boolean" use="optional"/></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="formatCT"><xs:simpleContent><xs:extension base="xs:string"><xs:attributeGroup ref="globalWithType"/><xs:attribute name="canonical" type="xs:boolean" use="optional"/></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="identifierCT"><xs:simpleContent><xs:extension base="xs:string"><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="type" type="identifierType"/><xs:attribute name="canonical" type="xs:boolean" use="optional"/></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="languageCT"><xs:simpleContent><xs:extension base="xs:string"><xs:attribute name="type" type="languageType"/><xs:attribute name="use" type="languageUsage"/><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="canonical" type="xs:boolean" use="optional"/></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="publisherCT"><xs:simpleContent><xs:extension base="xs:string"><xs:attributeGroup ref="globalWithType"/><xs:attribute name="canonical" type="xs:boolean" use="optional"/></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="refSystemCT"><xs:simpleContent><xs:extension base="xs:string"><xs:attributeGroup ref="globalWithType"/><xs:attribute name="canonical" type="xs:boolean" use="optional"/></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="relationCT"><xs:simpleContent><xs:extension base="xs:string"><xs:attributeGroup ref="globalWithType"/><xs:attribute name="canonical" type="xs:boolean" use="optional"/></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="revisionDescCT"><xs:sequence><xs:element name="date" type="dateCT"/><xs:element name="p" type="pCT" maxOccurs="unbounded"/></xs:sequence><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="revisionDesc"/></xs:complexType><xs:complexType name="rightsCT"><xs:simpleContent><xs:extension base="xs:string"><xs:attributeGroup ref="globalWithType"/><xs:attribute name="canonical" type="xs:boolean" use="optional"/></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="roleCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="index" type="indexCT"/><xs:element name="note" type="noteCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="role"/></xs:complexType><xs:complexType name="roleDescCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="index" type="indexCT"/><xs:element name="note" type="noteCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="roleDesc"/></xs:complexType><xs:complexType name="subjectCT"><xs:simpleContent><xs:extension base="xs:string"><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="type" type="subjectType" use="optional"/><xs:attributeGroup ref="globalWithoutType"/></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="sourceCT"><xs:simpleContent><xs:extension base="xs:string"><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="scopeCT"><xs:simpleContent><xs:extension base="osisRefType"><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="teiHeaderCT" mixed="true"><xs:sequence><xs:any processContents="skip" maxOccurs="unbounded"/></xs:sequence><xs:attribute name="TEIform" fixed="teiHeader"/></xs:complexType><xs:complexType name="typeCT"><xs:simpleContent><xs:extension base="xs:string"><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="type" type="typeType" use="optional"/><xs:attributeGroup ref="globalWithoutType"/></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="workCT"><xs:sequence><xs:element name="title" type="titleCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="contributor" type="contributorCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="creator" type="creatorCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="subject" type="subjectCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="date" type="dateCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="description" type="descriptionCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="publisher" type="publisherCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="type" type="typeCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="format" type="formatCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="identifier" type="identifierCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="source" type="sourceCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="language" type="languageCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="relation" type="relationCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="coverage" type="coverageCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="rights" type="rightsCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="scope" type="scopeCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="castList" type="castListCT" minOccurs="0" maxOccurs="unbounded"/><xs:element name="teiHeader" type="teiHeaderCT" minOccurs="0"/><xs:element name="refSystem" type="refSystemCT" minOccurs="0" maxOccurs="unbounded"/></xs:sequence><xs:attribute name="osisWork" type="osisWorkType" use="required"/><xs:attributeGroup ref="globalWithType"/></xs:complexType><xs:complexType name="workPrefixCT"><xs:attribute name="path" type="osisWorkPrefix" use="required"/><xs:attribute name="osisWork" type="osisWorkType" use="required"/><xs:attributeGroup ref="globalWithoutType"/></xs:complexType><xs:complexType name="aCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="index" type="indexCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="href" type="xs:string" use="required"/><xs:attributeGroup ref="globalWithType"/></xs:complexType><xs:complexType name="abbrCT" mixed="true"><xs:complexContent mixed="true"><xs:extension base="milestoneable"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="index" type="indexCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="expansion" type="xs:string" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="abbr"/></xs:extension></xs:complexContent></xs:complexType><xs:complexType name="captionCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="lb" type="lbCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attributeGroup ref="globalWithType"/><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="TEIform" fixed="figDesc"/></xs:complexType><xs:complexType name="catchWordCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="inscription" type="inscriptionCT"/><xs:element name="lb" type="lbCT"/><xs:element name="list" type="listCT"/><xs:element name="mentioned" type="mentionedCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="speaker" type="speakerCT"/><xs:element name="title" type="titleCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="osisRef" type="osisRefType" use="optional"/><xs:attributeGroup ref="globalWithType"/></xs:complexType><xs:complexType name="cellCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="closer" type="closerCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="figure" type="figureCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="inscription" type="inscriptionCT"/><xs:element name="lb" type="lbCT"/><xs:element name="lg" type="lgCT"/><xs:element name="list" type="listCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="p" type="pCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="salute" type="saluteCT"/><xs:element name="seq" type="segCT"/><xs:element name="signed" type="signedCT"/><xs:element name="speaker" type="speakerCT"/><xs:element name="speech" type="speechCT"/><xs:element name="table" type="tableCT"/><xs:element name="title" type="titleCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="verse" type="verseCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="role" type="tableRole" use="optional" default="data"/><xs:attribute name="align" type="osisCellAlign" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="cell"/></xs:complexType><xs:complexType name="chapterCT" mixed="true"><xs:complexContent mixed="true"><xs:extension base="milestoneable"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="closer" type="closerCT"/><xs:element name="date" type="dateCT"/><xs:element name="div" type="divCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="figure" type="figureCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="inscription" type="inscriptionCT"/><xs:element name="lb" type="lbCT"/><xs:element name="lg" type="lgCT"/><xs:element name="list" type="listCT"/><xs:element name="mentioned" type="mentionedCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="p" type="pCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="salute" type="saluteCT"/><xs:element name="seg" type="segCT"/><xs:element name="signed" type="signedCT"/><xs:element name="speaker" type="speakerCT"/><xs:element name="speech" type="speechCT"/><xs:element name="table" type="tableCT"/><xs:element name="title" type="titleCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="verse" type="verseCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="chapterTitle" type="xs:string" use="optional"/><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="osisRef" type="osisRefType" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="div"/></xs:extension></xs:complexContent></xs:complexType><xs:complexType name="closerCT" mixed="true"><xs:complexContent mixed="true"><xs:extension base="milestoneable"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="lb" type="lbCT"/><xs:element name="lg" type="lgCT"/><xs:element name="list" type="listCT"/><xs:element name="mentioned" type="mentionedCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="p" type="pCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="signed" type="signedCT"/><xs:element name="speaker" type="speakerCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="verse" type="verseCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="closer"/></xs:extension></xs:complexContent></xs:complexType><xs:complexType name="dateCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="index" type="indexCT"/><xs:element name="note" type="noteCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="event" type="eventType" use="optional"/><xs:attribute name="type" type="calendar" use="optional" default="ISO"/><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="TEIform" fixed="date"/></xs:complexType><xs:complexType name="divCT" mixed="true"><xs:complexContent mixed="true"><xs:extension base="milestoneable"><xs:sequence><xs:element name="titlePage" type="titlePageCT" minOccurs="0" maxOccurs="1"/><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="chapter" type="chapterCT"/><xs:element name="closer" type="closerCT"/><xs:element name="date" type="dateCT"/><xs:element name="div" type="divCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="figure" type="figureCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="inscription" type="inscriptionCT"/><xs:element name="lb" type="lbCT"/><xs:element name="lg" type="lgCT"/><xs:element name="list" type="listCT"/><xs:element name="mentioned" type="mentionedCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="p" type="pCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="salute" type="saluteCT"/><xs:element name="seg" type="segCT"/><xs:element name="signed" type="signedCT"/><xs:element name="speaker" type="speakerCT"/><xs:element name="speech" type="speechCT"/><xs:element name="table" type="tableCT"/><xs:element name="title" type="titleCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="verse" type="verseCT"/><xs:element name="w" type="wCT"/></xs:choice></xs:sequence><xs:attribute name="canonical" type="xs:boolean" default="false" use="optional"/><xs:attribute name="osisRef" type="osisRefType" use="optional"/><xs:attribute name="scope" type="osisRefType" use="optional"/><xs:attribute name="type" type="divType" use="optional"/><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="TEIform" fixed="div"/></xs:extension></xs:complexContent></xs:complexType><xs:complexType name="divineNameCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="index" type="indexCT"/><xs:element name="note" type="noteCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/></xs:complexType><xs:complexType name="figureCT"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="caption" type="captionCT"/><xs:element name="index" type="indexCT"/><xs:element name="note" type="noteCT"/><xs:element name="reference" type="referenceCT"/></xs:choice><xs:attribute name="alt" type="xs:string" use="optional"/><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="catalog" type="xs:string" use="optional"/><xs:attribute name="location" type="xs:string" use="optional"/><xs:attribute name="osisRef" type="osisRefType" use="optional"/><xs:attribute name="rights" type="xs:string" use="optional"/><xs:attribute name="size" type="xs:string" use="optional"/><xs:attribute name="src" type="xs:string"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="figure"/></xs:complexType><xs:complexType name="foreignCT" mixed="true"><xs:complexContent mixed="true"><xs:extension base="milestoneable"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="lb" type="lbCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="title" type="titleCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="foreign"/></xs:extension></xs:complexContent></xs:complexType><xs:complexType name="headCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="head" type="headCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="lb" type="lbCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="head"/></xs:complexType><xs:complexType name="hiCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="lb" type="lbCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="type" type="hiType" use="optional"/><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="TEIform" fixed="hi"/></xs:complexType><xs:complexType name="indexCT"><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="index" type="xs:string" use="required"/><xs:attribute name="level1" type="xs:string" use="required"/><xs:attribute name="level2" type="xs:string" use="optional"/><xs:attribute name="level3" type="xs:string" use="optional"/><xs:attribute name="level4" type="xs:string" use="optional"/><xs:attribute name="see" type="xs:string" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="index"/></xs:complexType><xs:complexType name="inscriptionCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="lb" type="lbCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="speaker" type="speakerCT"/><xs:element name="speech" type="speechCT"/><xs:element name="title" type="titleCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/></xs:complexType><xs:complexType name="itemCT" mixed="true"><xs:sequence minOccurs="0" maxOccurs="unbounded"><xs:element name="label" type="labelCT" minOccurs="0"/><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="lg" type="lgCT"/><xs:element name="list" type="listCT"/><xs:element name="lb" type="lbCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="p" type="pCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="title" type="titleCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="verse" type="verseCT"/><xs:element name="w" type="wCT"/></xs:choice></xs:sequence><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="role" type="xs:string" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="item"/></xs:complexType><xs:complexType name="labelCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="lb" type="lbCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="role" type="xs:string" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="label"/></xs:complexType><xs:complexType name="lCT" mixed="true"><xs:complexContent mixed="true"><xs:extension base="milestoneable"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="chapter" type="chapterCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="lb" type="lbCT"/><xs:element name="mentioned" type="mentionedCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="speaker" type="speakerCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="verse" type="verseCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="level" type="xs:positiveInteger" use="optional"/><xs:attribute name="type" type="lineType" use="optional"/><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="TEIform" fixed="l"/></xs:extension></xs:complexContent></xs:complexType><xs:complexType name="lbCT"><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="milestone"/></xs:complexType><xs:complexType name="lgCT" mixed="false"><xs:complexContent><xs:extension base="milestoneable"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="chapter" type="chapterCT"/><xs:element name="index" type="indexCT"/><xs:element name="l" type="lCT"/><xs:element name="lb" type="lbCT"/><xs:element name="lg" type="lgCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="q" type="qCT"/><xs:element name="verse" type="verseCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="type" type="lineGroupType" use="optional"/><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="TEIform" fixed="lg"/></xs:extension></xs:complexContent></xs:complexType><xs:complexType name="listCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="chapter" type="chapterCT"/><xs:element name="head" type="headCT"/><xs:element name="index" type="indexCT"/><xs:element name="item" type="itemCT"/><xs:element name="lb" type="lbCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="q" type="qCT"/><xs:element name="verse" type="verseCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="list"/></xs:complexType><xs:complexType name="mentionedCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="lb" type="lbCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="mentioned"/></xs:complexType><xs:complexType name="milestoneCT"><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="type" type="milestonePt"/><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="marker" type="xs:string" default="DEFAULT" use="optional"/><xs:attribute name="TEIform" fixed="milestone"/></xs:complexType><xs:complexType name="milestoneEndCT"><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="type" type="milestoneSe"/><xs:attribute name="start" type="xs:string" use="required"/><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="TEIform" fixed="milestone"/></xs:complexType><xs:complexType name="milestoneStartCT"><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="end" type="xs:string" use="required"/><xs:attribute name="type" type="milestoneSe"/><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="TEIform" fixed="milestone"/></xs:complexType><xs:complexType name="nameCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="index" type="indexCT"/><xs:element name="note" type="noteCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="regular" type="xs:string" use="optional"/><xs:attribute name="type" type="nameType" use="optional"/><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="TEIform" fixed="name"/></xs:complexType><xs:complexType name="noteCT" mixed="true"><xs:sequence><xs:element name="note" type="noteCT" minOccurs="0" maxOccurs="unbounded"/><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="catchWord" type="catchWordCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="figure" type="figureCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="inscription" type="inscriptionCT"/><xs:element name="lb" type="lbCT"/><xs:element name="lg" type="lgCT"/><xs:element name="list" type="listCT"/><xs:element name="mentioned" type="mentionedCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="p" type="pCT"/><xs:element name="q" type="qCT"/><xs:element name="rdg" type="rdgCT"/><xs:element name="rdgGrp" type="rdgGrpCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="table" type="tableCT"/><xs:element name="title" type="titleCT"/><xs:element name="verse" type="verseCT"/><xs:element name="w" type="wCT"/></xs:choice></xs:sequence><xs:attribute name="canonical" type="xs:boolean" use="optional" default="false"/><xs:attribute name="osisRef" type="osisRefType" use="optional"/><xs:attribute name="placement" type="notePlacement" use="optional"/><xs:attribute name="type" type="noteType" use="optional"/><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="TEIform" fixed="note"/></xs:complexType><xs:complexType name="pCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="catchWord" type="catchWordCT"/><xs:element name="chapter" type="chapterCT"/><xs:element name="closer" type="closerCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="figure" type="figureCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="inscription" type="inscriptionCT"/><xs:element name="lb" type="lbCT"/><xs:element name="lg" type="lgCT"/><xs:element name="list" type="listCT"/><xs:element name="mentioned" type="mentionedCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="q" type="qCT"/><xs:element name="rdg" type="rdgCT"/><xs:element name="rdgGrp" type="rdgGrpCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="salute" type="saluteCT"/><xs:element name="seg" type="segCT"/><xs:element name="signed" type="signedCT"/><xs:element name="speaker" type="speakerCT"/><xs:element name="speech" type="speechCT"/><xs:element name="table" type="tableCT"/><xs:element name="title" type="titleCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="verse" type="verseCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="p"/></xs:complexType><xs:complexType name="qCT" mixed="true"><xs:complexContent mixed="true"><xs:extension base="milestoneable"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="closer" type="closerCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="inscription" type="inscriptionCT"/><xs:element name="lb" type="lbCT"/><xs:element name="lg" type="lgCT"/><xs:element name="list" type="listCT"/><xs:element name="mentioned" type="mentionedCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="p" type="pCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="salute" type="saluteCT"/><xs:element name="seg" type="segCT"/><xs:element name="signed" type="signedCT"/><xs:element name="speaker" type="speakerCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="verse" type="verseCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="level" type="xs:string" use="optional"/><xs:attribute name="marker" type="xs:string" default="DEFAULT" use="optional"/><xs:attribute name="osisRef" type="osisRefType" use="optional"/><xs:attribute name="type" type="quoteType" use="optional"/><xs:attribute name="who" type="xs:string" use="optional"/><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="TEIform" fixed="q"/></xs:extension></xs:complexContent></xs:complexType><xs:complexType name="rdgCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="lb" type="lbCT"/><xs:element name="lg" type="lgCT"/><xs:element name="list" type="listCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="p" type="pCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="witness" type="osisRefType" use="optional"/><xs:attribute name="type" type="rdgType" use="optional"/><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="TEIform" fixed="rdg"/></xs:complexType><xs:complexType name="rdgGrpCT" mixed="false"><xs:sequence><xs:element name="rdg" type="rdgCT" minOccurs="1" maxOccurs="unbounded"/></xs:sequence><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="rdgGrp"/></xs:complexType><xs:complexType name="referenceCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="lb" type="lbCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="seg" type="segCT"/><xs:element name="title" type="titleCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional" default="false"/><xs:attribute name="osisRef" type="osisRefType" use="optional"/><xs:attribute name="type" type="referenceType" use="optional"/><xs:attributeGroup ref="globalWithoutType"/></xs:complexType><xs:complexType name="rowCT"><xs:sequence><xs:element name="cell" type="cellCT" maxOccurs="unbounded"/></xs:sequence><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="role" type="tableRole" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="row"/></xs:complexType><xs:complexType name="saluteCT" mixed="true"><xs:complexContent mixed="true"><xs:extension base="milestoneable"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="lb" type="lbCT"/><xs:element name="lg" type="lgCT"/><xs:element name="list" type="listCT"/><xs:element name="mentioned" type="mentionedCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="p" type="pCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="speaker" type="speakerCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="verse" type="verseCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="salute"/></xs:extension></xs:complexContent></xs:complexType><xs:complexType name="segCT" mixed="true"><xs:complexContent mixed="true"><xs:extension base="milestoneable"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="lb" type="lbCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="type" type="segType" use="optional"/><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="TEIform" fixed="seg"/></xs:extension></xs:complexContent></xs:complexType><xs:complexType name="signedCT" mixed="true"><xs:complexContent mixed="true"><xs:extension base="milestoneable"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="lb" type="lbCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="signed"/></xs:extension></xs:complexContent></xs:complexType><xs:complexType name="speakerCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="index" type="indexCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="who" type="xs:string" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="sp"/></xs:complexType><xs:complexType name="speechCT" mixed="true"><xs:complexContent mixed="true"><xs:extension base="milestoneable"><xs:sequence><xs:element name="speech" type="speechCT" minOccurs="0" maxOccurs="unbounded"/><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="chapter" type="chapterCT"/><xs:element name="closer" type="closerCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="inscription" type="inscriptionCT"/><xs:element name="lb" type="lbCT"/><xs:element name="lg" type="lgCT"/><xs:element name="list" type="listCT"/><xs:element name="mentioned" type="mentionedCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="p" type="pCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="salute" type="saluteCT"/><xs:element name="seg" type="segCT"/><xs:element name="signed" type="signedCT"/><xs:element name="speaker" type="speakerCT"/><xs:element name="table" type="tableCT"/><xs:element name="title" type="titleCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="verse" type="verseCT"/><xs:element name="w" type="wCT"/></xs:choice></xs:sequence><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="marker" type="xs:string" default="DEFAULT" use="optional"/><xs:attribute name="TEIform" fixed="speech"/></xs:extension></xs:complexContent></xs:complexType><xs:complexType name="tableCT"><xs:sequence><xs:element name="head" type="headCT" minOccurs="0"/><xs:element name="row" type="rowCT" minOccurs="0" maxOccurs="unbounded"/></xs:sequence><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="cols" type="xs:positiveInteger" use="optional"/><xs:attribute name="rows" type="xs:positiveInteger" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="table"/></xs:complexType><xs:complexType name="titleCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="figure" type="figureCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="inscription" type="inscriptionCT"/><xs:element name="lb" type="lbCT"/><xs:element name="lg" type="lgCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="title" type="titleCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="verse" type="verseCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional" default="false"/><xs:attribute name="level" type="xs:integer" use="optional"/><xs:attribute name="placement" type="titlePlacement" use="optional"/><xs:attribute name="short" type="xs:string" use="optional"/><xs:attribute name="type" type="osisTitleType" use="optional"/><xs:attributeGroup ref="globalWithoutType"/><xs:attribute name="TEIform" fixed="title"/></xs:complexType><xs:complexType name="titlePageCT"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="title" type="titleCT"/><xs:element name="contributor" type="contributorCT"/><xs:element name="creator" type="creatorCT"/><xs:element name="subject" type="subjectCT"/><xs:element name="date" type="dateCT"/><xs:element name="description" type="descriptionCT"/><xs:element name="publisher" type="publisherCT"/><xs:element name="type" type="typeCT"/><xs:element name="format" type="formatCT"/><xs:element name="identifier" type="identifierCT"/><xs:element name="source" type="sourceCT"/><xs:element name="language" type="languageCT"/><xs:element name="relation" type="relationCT"/><xs:element name="coverage" type="coverageCT"/><xs:element name="p" type="pCT"/><xs:element name="figure" type="figureCT"/><xs:element name="milestone" type="milestoneCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional" default="false"/><xs:attributeGroup ref="globalWithType"/></xs:complexType><xs:complexType name="transChangeCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="lb" type="lbCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="type" type="changeType" use="optional"/><xs:attributeGroup ref="globalWithoutType"/></xs:complexType><xs:complexType name="verseCT" mixed="true"><xs:complexContent mixed="true"><xs:extension base="milestoneable"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="abbr" type="abbrCT"/><xs:element name="date" type="dateCT"/><xs:element name="divineName" type="divineNameCT"/><xs:element name="foreign" type="foreignCT"/><xs:element name="hi" type="hiCT"/><xs:element name="index" type="indexCT"/><xs:element name="inscription" type="inscriptionCT"/><xs:element name="lb" type="lbCT"/><xs:element name="list" type="listCT"/><xs:element name="mentioned" type="mentionedCT"/><xs:element name="milestone" type="milestoneCT"/><xs:element name="milestoneEnd" type="milestoneEndCT"/><xs:element name="milestoneStart" type="milestoneStartCT"/><xs:element name="name" type="nameCT"/><xs:element name="note" type="noteCT"/><xs:element name="q" type="qCT"/><xs:element name="reference" type="referenceCT"/><xs:element name="seg" type="segCT"/><xs:element name="speaker" type="speakerCT"/><xs:element name="title" type="titleCT"/><xs:element name="transChange" type="transChangeCT"/><xs:element name="w" type="wCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional" default="true"/><xs:attributeGroup ref="globalWithType"/></xs:extension></xs:complexContent></xs:complexType><xs:complexType name="wCT" mixed="true"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="a" type="aCT"/><xs:element name="index" type="indexCT"/><xs:element name="note" type="noteCT"/><xs:element name="seg" type="segCT"/></xs:choice><xs:attribute name="canonical" type="xs:boolean" use="optional"/><xs:attribute name="gloss" type="xs:string" use="optional"/><xs:attribute name="lemma" type="osisGenType" use="optional"/><xs:attribute name="morph" type="osisGenType" use="optional"/><xs:attribute name="POS" type="osisGenType" use="optional"/><xs:attribute name="src" type="xs:string" use="optional"/><xs:attribute name="xlit" type="xs:string" use="optional"/><xs:attributeGroup ref="globalWithType"/><xs:attribute name="TEIform" fixed="w"/></xs:complexType><xs:attributeGroup name="globalWithType"><xs:attribute name="annotateRef" type="annotateRefType" use="optional"/><xs:attribute name="annotateWork" type="xs:string" use="optional"/><xs:attribute name="annotateType" type="annotationType" use="optional"/><xs:attribute name="editions" type="xs:NMTOKENS" use="optional"/><xs:attribute name="ID" type="xs:ID" use="optional"/><xs:attribute name="osisID" type="osisIDType" use="optional"/><xs:attribute name="resp" type="xs:string" use="optional"/><xs:attribute name="type" type="attributeExtension" use="optional"/><xs:attribute name="subType" type="attributeExtension" use="optional"/><xs:attribute name="n" type="xs:string" use="optional"/><xs:attribute ref="xml:lang" use="optional"/><xs:attribute ref="xml:space" use="optional"/><xs:attribute name="script" type="osisScripts" use="optional"/></xs:attributeGroup><xs:attributeGroup name="globalWithoutType"><xs:attribute name="annotateRef" type="annotateRefType" use="optional"/><xs:attribute name="annotateWork" type="xs:string" use="optional"/><xs:attribute name="annotateType" type="annotationType" use="optional"/><xs:attribute name="editions" type="xs:NMTOKENS" use="optional"/><xs:attribute name="ID" type="xs:ID" use="optional"/><xs:attribute name="osisID" type="osisIDType" use="optional"/><xs:attribute name="resp" type="xs:string" use="optional"/><xs:attribute name="subType" type="attributeExtension" use="optional"/><xs:attribute name="n" type="xs:string" use="optional"/><xs:attribute ref="xml:lang" use="optional"/><xs:attribute ref="xml:space" use="optional"/><xs:attribute name="script" type="osisScripts" use="optional"/></xs:attributeGroup><xs:complexType name="milestoneable"><xs:attribute name="sID" type="xs:string" use="optional"/><xs:attribute name="eID" type="xs:string" use="optional"/></xs:complexType><xs:simpleType name="osisGenRegex"><xs:restriction base="xs:string"><xs:pattern value="((((\p{L}|\p{N}|_)+)(\.(\p{L}|\p{N}|_))*:)?([^:\s])+)"/></xs:restriction></xs:simpleType><xs:simpleType name="osisIDRegex"><xs:restriction base="xs:string"><xs:pattern value="(((\p{L}|\p{N}|_)+)((\.(\p{L}|\p{N}|_)+)*)?:)?((\p{L}|\p{N}|_|(\\[^\s]))+)((\.(\p{L}|\p{N}|_|(\\[^\s]))+)*)?(!((\p{L}|\p{N}|_|(\\[^\s]))+)((\.(\p{L}|\p{N}|_|(\\[^\s]))+)*)?)?"/></xs:restriction></xs:simpleType><xs:simpleType name="osisRefRegex"><xs:restriction base="xs:string"><xs:pattern value="(((\p{L}|\p{N}|_)+)((\.(\p{L}|\p{N}|_)+)*)?:)?((\p{L}|\p{N}|_|(\\[^\s]))+)(\.(\p{L}|\p{N}|_|(\\[^\s]))*)*(!((\p{L}|\p{N}|_|(\\[^\s]))+)((\.(\p{L}|\p{N}|_|(\\[^\s]))+)*)?)?(@(cp\[(\p{Nd})*\]|s\[(\p{L}|\p{N})+\](\[(\p{N})+\])?))?(\-((((\p{L}|\p{N}|_|(\\[^\s]))+)(\.(\p{L}|\p{N}|_|(\\[^\s]))*)*)+)(!((\p{L}|\p{N}|_|(\\[^\s]))+)((\.(\p{L}|\p{N}|_|(\\[^\s]))+)*)?)?(@(cp\[(\p{Nd})*\]|s\[(\p{L}|\p{N})+\](\[(\p{N})+\])?))?)?"/></xs:restriction></xs:simpleType><xs:simpleType name="osisScripts"><xs:restriction base="xs:string"><xs:pattern value="([A-Z][a-z]{3}|x-[A-Za-z0-9]+)"/></xs:restriction></xs:simpleType><xs:simpleType name="osisWorkPrefix"><xs:restriction base="xs:string"><xs:pattern value="((//((\p{L}|\p{N}|_|-|\.|:)+))(/(\p{L}|\p{N}|_|-|\.|:)+)?(/@(\p{L}|\p{N}|_|-|\.|:)+))"/></xs:restriction></xs:simpleType><xs:simpleType name="osisWorkType"><xs:restriction base="xs:string"><xs:pattern value="((\p{L}|\p{N}|_)+)((\.(\p{L}|\p{N}|_)+)*)?"/></xs:restriction></xs:simpleType><xs:simpleType name="annotateRefType"><xs:list itemType="osisAnnotateRefType"/></xs:simpleType><xs:simpleType name="annotationType"><xs:union memberTypes="osisAnnotation attributeExtension"/></xs:simpleType><xs:simpleType name="attributeExtension"><xs:restriction base="xs:string"><xs:pattern value="x-([^\s])+"/></xs:restriction></xs:simpleType><xs:simpleType name="calendar"><xs:restriction base="xs:string"><xs:enumeration value="Chinese"/><xs:enumeration value="Gregorian"/><xs:enumeration value="Islamic"/><xs:enumeration value="ISO"/><xs:enumeration value="Jewish"/><xs:enumeration value="Julian"/></xs:restriction></xs:simpleType><xs:simpleType name="changeType"><xs:union memberTypes="osisChanges attributeExtension"/></xs:simpleType><xs:simpleType name="descriptionType"><xs:union memberTypes="osisDescription attributeExtension"/></xs:simpleType><xs:simpleType name="divType"><xs:union memberTypes="osisDivs attributeExtension"/></xs:simpleType><xs:simpleType name="eventType"><xs:union memberTypes="osisEvents attributeExtension"/></xs:simpleType><xs:simpleType name="hiType"><xs:union memberTypes="osisHi attributeExtension"/></xs:simpleType><xs:simpleType name="identifierType"><xs:union memberTypes="osisIdentifier attributeExtension"/></xs:simpleType><xs:simpleType name="languageType"><xs:union memberTypes="osisLanguage attributeExtension"/></xs:simpleType><xs:simpleType name="languageUsage"><xs:union memberTypes="osisLanguageUsage attributeExtension"/></xs:simpleType><xs:simpleType name="lineType"><xs:union memberTypes="osisLine attributeExtension xs:string"/></xs:simpleType><xs:simpleType name="lineGroupType"><xs:union memberTypes="osisLineGroup attributeExtension xs:string"/></xs:simpleType><xs:simpleType name="milestonePt"><xs:union memberTypes="osisMilestonePt attributeExtension"/></xs:simpleType><xs:simpleType name="milestoneSe"><xs:restriction base="xs:string"><xs:enumeration value="abbr"/><xs:enumeration value="chapter"/><xs:enumeration value="closer"/><xs:enumeration value="div"/><xs:enumeration value="foreign"/><xs:enumeration value="l"/><xs:enumeration value="lg"/><xs:enumeration value="q"/><xs:enumeration value="salute"/><xs:enumeration value="seg"/><xs:enumeration value="signed"/><xs:enumeration value="speech"/><xs:enumeration value="verse"/></xs:restriction></xs:simpleType><xs:simpleType name="nameType"><xs:union memberTypes="osisNames attributeExtension"/></xs:simpleType><xs:simpleType name="notePlacement"><xs:union memberTypes="osisPlacementNote attributeExtension"/></xs:simpleType><xs:simpleType name="noteType"><xs:union memberTypes="osisNotes attributeExtension"/></xs:simpleType><xs:simpleType name="quoteType"><xs:union memberTypes="osisQuotes attributeExtension"/></xs:simpleType><xs:simpleType name="referenceType"><xs:union memberTypes="osisReferences attributeExtension"/></xs:simpleType><xs:simpleType name="rdgType"><xs:union memberTypes="osisRdg attributeExtension xs:string"/></xs:simpleType><xs:simpleType name="segType"><xs:union memberTypes="osisSegs attributeExtension"/></xs:simpleType><xs:simpleType name="subjectType"><xs:union memberTypes="osisSubjects attributeExtension"/></xs:simpleType><xs:simpleType name="titlePlacement"><xs:union memberTypes="osisPlacementTitle attributeExtension"/></xs:simpleType><xs:simpleType name="typeType"><xs:union memberTypes="osisType attributeExtension"/></xs:simpleType><xs:simpleType name="osisAnnotateRefType"><xs:union memberTypes="osisRefRegex osisGenRegex"/></xs:simpleType><xs:simpleType name="osisAnnotation"><xs:restriction base="xs:string"><xs:enumeration value="commentary"/><xs:enumeration value="exposition"/><xs:enumeration value="meditation"/><xs:enumeration value="outline"/><xs:enumeration value="rebuttal"/><xs:enumeration value="sermon"/><xs:enumeration value="studyGuide"/><xs:enumeration value="translation"/></xs:restriction></xs:simpleType><xs:simpleType name="osisCellAlign"><xs:restriction base="xs:string"><xs:enumeration value="left"/><xs:enumeration value="right"/><xs:enumeration value="center"/><xs:enumeration value="justify"/><xs:enumeration value="start"/><xs:enumeration value="end"/></xs:restriction></xs:simpleType><xs:simpleType name="osisChanges"><xs:restriction base="xs:string"><xs:enumeration value="added"/><xs:enumeration value="amplified"/><xs:enumeration value="changed"/><xs:enumeration value="deleted"/><xs:enumeration value="implied"/><xs:enumeration value="moved"/><xs:enumeration value="tenseChange"/></xs:restriction></xs:simpleType><xs:simpleType name="osisDescription"><xs:restriction base="xs:string"><xs:enumeration value="usfm"/></xs:restriction></xs:simpleType><xs:simpleType name="osisDivs"><xs:restriction base="xs:string"><xs:enumeration value="acknowledgement"/><xs:enumeration value="afterword"/><xs:enumeration value="annotant"/><xs:enumeration value="appendix"/><xs:enumeration value="article"/><xs:enumeration value="back"/><xs:enumeration value="bibliography"/><xs:enumeration value="body"/><xs:enumeration value="book"/><xs:enumeration value="bookGroup"/><xs:enumeration value="bridge"/><xs:enumeration value="chapter"/><xs:enumeration value="colophon"/><xs:enumeration value="commentary"/><xs:enumeration value="concordance"/><xs:enumeration value="coverPage"/><xs:enumeration value="dedication"/><xs:enumeration value="devotional"/><xs:enumeration value="entry"/><xs:enumeration value="front"/><xs:enumeration value="gazetteer"/><xs:enumeration value="glossary"/><xs:enumeration value="imprimatur"/><xs:enumeration value="index"/><xs:enumeration value="introduction"/><xs:enumeration value="majorSection"/><xs:enumeration value="map"/><xs:enumeration value="outline"/><xs:enumeration value="paragraph"/><xs:enumeration value="part"/><xs:enumeration value="preface"/><xs:enumeration value="publicationData"/><xs:enumeration value="section"/><xs:enumeration value="subSection"/><xs:enumeration value="summary"/><xs:enumeration value="tableofContents"/><xs:enumeration value="titlePage"/></xs:restriction></xs:simpleType><xs:simpleType name="osisEvents"><xs:restriction base="xs:string"><xs:enumeration value="edition"/><xs:enumeration value="eversion"/><xs:enumeration value="imprint"/><xs:enumeration value="original"/></xs:restriction></xs:simpleType><xs:simpleType name="osisGenType"><xs:list itemType="osisGenRegex"/></xs:simpleType><xs:simpleType name="osisHi"><xs:restriction base="xs:string"><xs:enumeration value="acrostic"/><xs:enumeration value="bold"/><xs:enumeration value="emphasis"/><xs:enumeration value="illuminated"/><xs:enumeration value="italic"/><xs:enumeration value="line-through"/><xs:enumeration value="normal"/><xs:enumeration value="small-caps"/><xs:enumeration value="sub"/><xs:enumeration value="super"/><xs:enumeration value="underline"/></xs:restriction></xs:simpleType><xs:simpleType name="osisIdentifier"><xs:restriction base="xs:string"><xs:enumeration value="Dewey"/><xs:enumeration value="DOI"/><xs:enumeration value="ISBN"/><xs:enumeration value="ISSN"/><xs:enumeration value="LCCN"/><xs:enumeration value="OSIS"/><xs:enumeration value="SICI"/><xs:enumeration value="URI"/><xs:enumeration value="URL"/><xs:enumeration value="URN"/></xs:restriction></xs:simpleType><xs:simpleType name="osisIDType"><xs:list itemType="osisIDRegex"/></xs:simpleType><xs:simpleType name="osisLanguage"><xs:restriction base="xs:string"><xs:enumeration value="IANA"/><xs:enumeration value="IETF"/><xs:enumeration value="ISO-639-1"/><xs:enumeration value="ISO-639-2"/><xs:enumeration value="ISO-639-2-B"/><xs:enumeration value="ISO-639-2-T"/><xs:enumeration value="LINGUIST"/><xs:enumeration value="other"/><xs:enumeration value="SIL"/></xs:restriction></xs:simpleType><xs:simpleType name="osisLanguageUsage"><xs:restriction base="xs:string"><xs:enumeration value="base"/><xs:enumeration value="didactic"/><xs:enumeration value="interlinear"/><xs:enumeration value="original"/><xs:enumeration value="quotation"/><xs:enumeration value="source"/><xs:enumeration value="target"/><xs:enumeration value="translation"/></xs:restriction></xs:simpleType><xs:simpleType name="osisLine"><xs:restriction base="xs:string"><xs:enumeration value="refrain"/><xs:enumeration value="doxology"/><xs:enumeration value="selah"/><xs:enumeration value="attribution"/></xs:restriction></xs:simpleType><xs:simpleType name="osisLineGroup"><xs:restriction base="xs:string"></xs:restriction></xs:simpleType><xs:simpleType name="osisMilestonePt"><xs:restriction base="xs:string"><xs:enumeration value="column"/><xs:enumeration value="cQuote"/><xs:enumeration value="footer"/><xs:enumeration value="halfLine"/><xs:enumeration value="header"/><xs:enumeration value="line"/><xs:enumeration value="pb"/><xs:enumeration value="screen"/></xs:restriction></xs:simpleType><xs:simpleType name="osisNames"><xs:restriction base="xs:string"><xs:enumeration value="geographic"/><xs:enumeration value="holiday"/><xs:enumeration value="nonhuman"/><xs:enumeration value="person"/><xs:enumeration value="ritual"/></xs:restriction></xs:simpleType><xs:simpleType name="osisNotes"><xs:restriction base="xs:string"><xs:enumeration value="allusion"/><xs:enumeration value="alternative"/><xs:enumeration value="background"/><xs:enumeration value="citation"/><xs:enumeration value="crossReference"/><xs:enumeration value="devotional"/><xs:enumeration value="encoder"/><xs:enumeration value="exegesis"/><xs:enumeration value="explanation"/><xs:enumeration value="liturgical"/><xs:enumeration value="speaker"/><xs:enumeration value="study"/><xs:enumeration value="translation"/><xs:enumeration value="variant"/></xs:restriction></xs:simpleType><xs:simpleType name="osisPlacementNote"><xs:restriction base="xs:string"><xs:enumeration value="foot"/><xs:enumeration value="end"/><xs:enumeration value="inline"/><xs:enumeration value="left"/><xs:enumeration value="right"/><xs:enumeration value="interlinear"/><xs:enumeration value="apparatus"/></xs:restriction></xs:simpleType><xs:simpleType name="osisPlacementTitle"><xs:restriction base="xs:string"><xs:enumeration value="leftHead"/><xs:enumeration value="centerHead"/><xs:enumeration value="rightHead"/><xs:enumeration value="insideHead"/><xs:enumeration value="outsideHead"/><xs:enumeration value="leftFoot"/><xs:enumeration value="centerFoot"/><xs:enumeration value="rightFoot"/><xs:enumeration value="insideFoot"/><xs:enumeration value="outsideFoot"/></xs:restriction></xs:simpleType><xs:simpleType name="osisQuotes"><xs:restriction base="xs:string"><xs:enumeration value="block"/><xs:enumeration value="citation"/><xs:enumeration value="embedded"/></xs:restriction></xs:simpleType><xs:simpleType name="osisReferences"><xs:restriction base="xs:string"><xs:enumeration value="annotateRef"/><xs:enumeration value="parallel"/><xs:enumeration value="source"/></xs:restriction></xs:simpleType><xs:simpleType name="osisRdg"><xs:restriction base="xs:string"><xs:enumeration value="alternate"/><xs:enumeration value="variant"/></xs:restriction></xs:simpleType><xs:simpleType name="osisRefType"><xs:list itemType="osisRefRegex"/></xs:simpleType><xs:simpleType name="osisRoles"><xs:restriction base="xs:string"><xs:enumeration value="adp"/><xs:enumeration value="ann"/><xs:enumeration value="art"/><xs:enumeration value="aut"/><xs:enumeration value="aqt"/><xs:enumeration value="aft"/><xs:enumeration value="aui"/><xs:enumeration value="bnd"/><xs:enumeration value="bdd"/><xs:enumeration value="bkd"/><xs:enumeration value="bkp"/><xs:enumeration value="bjd"/><xs:enumeration value="bpd"/><xs:enumeration value="ctg"/><xs:enumeration value="clb"/><xs:enumeration value="cmm"/><xs:enumeration value="cwt"/><xs:enumeration value="com"/><xs:enumeration value="ctb"/><xs:enumeration value="cre"/><xs:enumeration value="edt"/><xs:enumeration value="encoder"/><xs:enumeration value="ilu"/><xs:enumeration value="ill"/><xs:enumeration value="pbl"/><xs:enumeration value="trl"/></xs:restriction></xs:simpleType><xs:simpleType name="osisSegs"><xs:restriction base="xs:string"><xs:enumeration value="alluded"/><xs:enumeration value="keyword"/><xs:enumeration value="otPassage"/><xs:enumeration value="verseNumber"/></xs:restriction></xs:simpleType><xs:simpleType name="osisSubjects"><xs:restriction base="xs:string"><xs:enumeration value="ATLA"/><xs:enumeration value="BILDI"/><xs:enumeration value="DBC"/><xs:enumeration value="DDC"/><xs:enumeration value="EUT"/><xs:enumeration value="FGT"/><xs:enumeration value="LCC"/><xs:enumeration value="LCSH"/><xs:enumeration value="MeSH"/><xs:enumeration value="NLSH"/><xs:enumeration value="RSWK"/><xs:enumeration value="SEARS"/><xs:enumeration value="SOG"/><xs:enumeration value="SWD_RSWK"/><xs:enumeration value="UDC"/><xs:enumeration value="VAT"/></xs:restriction></xs:simpleType><xs:simpleType name="roleType"><xs:union memberTypes="osisRoles attributeExtension"/></xs:simpleType><xs:simpleType name="osisTitles"><xs:restriction base="xs:string"><xs:enumeration value="acrostic"/><xs:enumeration value="chapter"/><xs:enumeration value="continued"/><xs:enumeration value="main"/><xs:enumeration value="parallel"/><xs:enumeration value="psalm"/><xs:enumeration value="runningHead"/><xs:enumeration value="scope"/><xs:enumeration value="sub"/></xs:restriction></xs:simpleType><xs:simpleType name="osisTitleType"><xs:union memberTypes="osisTitles attributeExtension"/></xs:simpleType><xs:simpleType name="osisType"><xs:restriction base="xs:string"><xs:enumeration value="OSIS"/></xs:restriction></xs:simpleType><xs:simpleType name="tableRole"><xs:restriction base="xs:string"><xs:enumeration value="label"/><xs:enumeration value="data"/></xs:restriction></xs:simpleType></xs:schema>'

if __name__ == "__main__":
    global encoding
    global relaxedConformance

    num_processes = multiprocessing.cpu_count()
    num_jobs = num_processes

    encoding = ''
    relaxedConformance = False
    inputFilesIdx = 2 # This marks the point in the sys.argv array, after which all values represent USFM files to be converted.
    usfmDocList = list()

    if '-v' in sys.argv:
        verbose = True
        inputFilesIdx += 1
    else:
        verbose = False

    if '-x' in sys.argv:
        validatexml = False
        inputFilesIdx += 1
    else:
        validatexml = True

    if '-d' in sys.argv:
        DEBUG = True
        inputFilesIdx += 1
        num_processes = 1
        num_jobs = 1
        verbose = True
    else:
        DEBUG = False

    if '-h' in sys.argv or '--help' in sys.argv or len(sys.argv) < 3:
        printUsage()
    else:
        osisWork = sys.argv[1]

        if '-o' in sys.argv:
            i = sys.argv.index('-o')+1
            if len(sys.argv) < i+1:
                printUsage()
            osisFileName = sys.argv[i]
            inputFilesIdx += 2 # increment 2, reflecting 2 args for -o
        else:
            osisFileName = osisWork + '.osis.xml'

        if '-e' in sys.argv:
            i = sys.argv.index('-e')+1
            if len(sys.argv) < i+1:
                printUsage()
            encoding = sys.argv[i]
            inputFilesIdx += 2 # increment 2, reflecting 2 args for -e

        if '-r' in sys.argv:
            relaxedConformance = True
            bookDict = dict(list(bookDict.items()) + list(addBookDict.items()))
            inputFilesIdx += 1

        if '-s' in sys.argv:
            i = sys.argv.index('-s')+1
            if len(sys.argv) < i+1:
                printUsage()
            if sys.argv[i].startswith('a'):
                sortKey = None
                print('Sorting book files alphanumerically.')
            elif sys.argv[i].startswith('na'):
                sortKey = keynat
                print('Sorting book files naturally.')
            elif sys.argv[i].startswith('c'):
                sortKey = keycanon
                print('Sorting book files canonically.')
            elif sys.argv[i].startswith('u'):
                sortKey = keyusfm
                print('Sorting book files by USFM book number.')
            elif sys.argv[i].startswith('random'): # for testing only
                sortKey = lambda filename: int(random.random()*256)
                print('Sorting book files randomly.')
            else:
                sortKey = keysupplied
                print('Leaving book files unsorted, in the order in which they were supplied.')
            inputFilesIdx += 2 # increment 2, reflecting 2 args for -s
        else:
            sortKey = keynat
            print('Sorting book files naturally.')

        usfmDocList = sys.argv[inputFilesIdx:]

        for filename in usfmDocList:
            readIdentifiersFromOsis(filename)
        usfmDocList = sorted(usfmDocList, key=sortKey)

        # run
        # load up work queue
        work_queue = multiprocessing.Queue()
        for job in usfmDocList:
            work_queue.put(job)

        # create a queue to pass to workers to store the results
        result_queue = multiprocessing.Queue()

        # spawn workers
        for i in range(num_processes):
            worker = Worker(work_queue, result_queue)
            worker.start()

        # collect the results off the queue
        osisSegment = dict()
        for i in usfmDocList:
            k,v=result_queue.get()
            osisSegment[k]=v

        verbosePrint('Assembling OSIS document...')
        osisDoc = '<osis xmlns="http://www.bibletechnologies.net/2003/OSIS/namespace" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.bibletechnologies.net/2003/OSIS/namespace http://www.bibletechnologies.net/osisCore.'+osisVersion+'.xsd">\n<osisText osisRefWork="Bible" xml:lang="und" osisIDWork="' + osisWork + '">\n<header>\n<work osisWork="' + osisWork + '"/>\n</header>\n'

        unhandledTags = set()
        for doc in usfmDocList:
            unhandledTags |= set(re.findall(r'(\\[^\s\*]+?\b\*?)', osisSegment[doc]))
            osisDoc += osisSegment[doc]

        osisDoc += '</osisText>\n</osis>\n'

        if validatexml:
            try:
                #import urllib
                from lxml import etree
                verbosePrint('Validating XML...')
                osisParser = etree.XMLParser(schema = etree.XMLSchema(etree.XML(osisSchema)))
                #osisParser = etree.XMLParser(schema = etree.XMLSchema(etree.XML(urllib.urlopen('http://www.bibletechnologies.net/osisCore.' + osisVersion + '.xsd').read())))
                etree.fromstring(osisDoc, osisParser)
                verbosePrint('XML Valid')
            except ImportError:
                verbosePrint('For schema validation, install lxml')
            except etree.XMLSyntaxError as eVal:
                print('XML Validation error: ' + str(eVal))

        osisFile = codecs.open(osisFileName, 'w', 'utf-8')
        osisFile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        osisFile.write(osisDoc)

        if unhandledTags:
            if verbose:
                print('')
            print(('Unhandled USFM tags: ' + ', '.join(sorted(unhandledTags)) + ' (' + str(len(unhandledTags)) + ' total)'))
            if not relaxedConformance:
                print('Consider using the -r option for relaxed markup processing.')
