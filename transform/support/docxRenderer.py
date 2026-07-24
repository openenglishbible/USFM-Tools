# -*- coding: utf-8 -*-
#
#   Renders a real .docx (Office Open XML) document directly, using only
#   the standard library. Genuine Word footnotes, heading outline levels
#   for the navigation pane, small-caps runs for the divine name, poetry
#   indents and per-book page breaks. No external dependencies.
#

import os
import zipfile

import abstractRenderer
import books


def xmlEscape(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


class Renderer(abstractRenderer.AbstractRenderer):

    def __init__(self, inputDir, outputDir, outputName, config):
        self.identity = 'docx renderer'
        self.outputFilename = os.path.join(outputDir, outputName + '.docx')
        self.outputDescription = self.outputFilename
        abstractRenderer.AbstractRenderer.__init__(self, inputDir, outputDir, outputName, config)
        self.inputDir = inputDir
        # Document state
        self.body = []            # list of finished paragraph XML strings
        self.runs = None          # runs of the open body paragraph, or None
        self.paraStyle = 'Normal'
        self.footnotes = []       # finished <w:footnote> XML strings
        self.noteRuns = None      # runs of the open footnote, or None
        self.firstBook = True
        # Inline formatting depth
        self.smallCapsDepth = 0
        self.italicDepth = 0
        # Chapter/verse position
        self.cachedChapter = ''
        self.cc = '1'
        self.cv = '1'

    def render(self):
        self.loadUSFM(self.inputDir)
        self.run()
        self.closeParagraph()
        self.writeDocx()
        self.logger.info('Wrote ' + self.outputFilename)

    #
    #   Run and paragraph assembly
    #

    def currentRuns(self):
        return self.noteRuns if self.noteRuns is not None else self.runs

    def runProps(self, extra=''):
        p = extra
        if self.smallCapsDepth > 0:
            p = p + '<w:smallCaps/>'
        if self.italicDepth > 0:
            p = p + '<w:i/>'
        return '<w:rPr>' + p + '</w:rPr>' if p else ''

    def addRun(self, text, props='', literal=False):
        runs = self.currentRuns()
        if runs is None:
            self.openParagraph('Normal')
            runs = self.currentRuns()
        if not literal:
            # Insert the space lost at USFM line breaks, but never double
            # one up or push punctuation away from its word.
            tail = runs[-1][1] if runs else ''
            if (tail and not tail.endswith(' ') and text
                    and not text.startswith((' ', ',', '.', ';', ':', '!', '?',
                                             '’', '”', ')', '*'))):
                text = ' ' + text
        runs.append((props, text))

    def addMarkerRun(self, xml):
        runs = self.currentRuns()
        if runs is None:
            self.openParagraph('Normal')
            runs = self.currentRuns()
        runs.append((None, xml))

    def flushChapter(self):
        if self.cachedChapter:
            self.addMarkerRun('<w:r><w:rPr><w:b/><w:sz w:val="32"/></w:rPr><w:t xml:space="preserve">'
                              + self.cachedChapter + ' </w:t></w:r>')
            self.cachedChapter = ''

    def openParagraph(self, style):
        self.closeParagraph()
        self.runs = []
        self.paraStyle = style

    def closeParagraph(self):
        if self.runs is None:
            return
        xml = ['<w:p><w:pPr><w:pStyle w:val="' + self.paraStyle + '"/></w:pPr>']
        for props, text in self.runs:
            if props is None:
                xml.append(text)  # pre-built marker run
            else:
                xml.append('<w:r>' + props + '<w:t xml:space="preserve">'
                           + xmlEscape(text) + '</w:t></w:r>')
        xml.append('</w:p>')
        self.body.append(''.join(xml))
        self.runs = None

    def emptyParagraph(self, style='Normal'):
        self.closeParagraph()
        self.body.append('<w:p><w:pPr><w:pStyle w:val="' + style + '"/></w:pPr></w:p>')

    def styledLine(self, style, token):
        self.openParagraph(style)
        self.addRun(token.value)
        self.closeParagraph()

    #
    #   Token handlers
    #

    def render_id(self, token):
        self.closeParagraph()
        if not self.firstBook:
            self.body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        self.firstBook = False
        self.cachedChapter = ''
        self.cc = '1'
        self.cv = '1'

    def render_mt1(self, token):    self.styledLine('BookTitle', token)
    def render_mt2(self, token):    self.styledLine('BookSubtitle', token)
    def render_mt3(self, token):    self.styledLine('BookSubtitle', token)
    def render_ms1(self, token):    self.styledLine('Heading1', token)
    def render_ms2(self, token):    self.styledLine('Heading2', token)
    def render_s1(self, token):
        if token.value == '~':
            self.emptyParagraph()
        else:
            self.styledLine('Heading2', token)
    def render_s2(self, token):     self.styledLine('Heading3', token)

    def render_p(self, token):
        self.openParagraph('Normal')
        self.flushChapter()
    def render_m(self, token):      self.render_p(token)
    def render_pi(self, token):
        self.openParagraph('Indented')
        self.flushChapter()
    def render_d(self, token):
        self.openParagraph('PsalmTitle')
        self.flushChapter()
    def render_b(self, token):      self.emptyParagraph()
    def render_nb(self, token):     self.render_p(token)

    def render_q(self, token):      self.openParagraph('Poetry1'); self.flushChapter()
    def render_q1(self, token):     self.openParagraph('Poetry1'); self.flushChapter()
    def render_q2(self, token):     self.openParagraph('Poetry2'); self.flushChapter()
    def render_q3(self, token):     self.openParagraph('Poetry3'); self.flushChapter()

    def render_c(self, token):
        self.cc = token.value
        self.cachedChapter = token.value
    def render_v(self, token):
        self.cv = token.value
        if token.value == '1':
            self.flushChapter()
        else:
            self.addMarkerRun('<w:r><w:rPr><w:vertAlign w:val="superscript"/></w:rPr>'
                              '<w:t xml:space="preserve"> ' + xmlEscape(token.value) + ' </w:t></w:r>')

    def render_text(self, token):
        self.addRun(token.value, self.runProps())

    # Inline character styling
    def render_nd_s(self, token):   self.smallCapsDepth += 1
    def render_nd_e(self, token):   self.smallCapsDepth = max(0, self.smallCapsDepth - 1)
    def render_em_s(self, token):   self.italicDepth += 1
    def render_em_e(self, token):   self.italicDepth = max(0, self.italicDepth - 1)
    def render_qs_s(self, token):   self.italicDepth += 1
    def render_qs_e(self, token):   self.italicDepth = max(0, self.italicDepth - 1)
    # Words of Jesus: deliberately unstyled, matching the web edition.
    def render_wj_s(self, token):   pass
    def render_wj_e(self, token):   pass

    #
    #   Footnotes: real Word footnotes, auto-numbered.
    #

    def render_f_s(self, token):
        noteId = len(self.footnotes) + 1
        self.addMarkerRun('<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr>'
                          '<w:footnoteReference w:id="' + str(noteId) + '"/></w:r>')
        self.noteRuns = []

    def render_f_e(self, token):
        noteId = len(self.footnotes) + 1
        xml = ['<w:footnote w:id="' + str(noteId) + '"><w:p><w:pPr>'
               '<w:pStyle w:val="FootnoteText"/></w:pPr>'
               '<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr><w:footnoteRef/></w:r>'
               '<w:r><w:t xml:space="preserve"> </w:t></w:r>']
        for props, text in self.noteRuns:
            if props is None:
                xml.append(text)
            else:
                xml.append('<w:r>' + props + '<w:t xml:space="preserve">'
                           + xmlEscape(text) + '</w:t></w:r>')
        xml.append('</w:p></w:footnote>')
        self.footnotes.append(''.join(xml))
        self.noteRuns = None

    def render_fr(self, token):
        self.addMarkerRun('<w:r><w:rPr><w:i/></w:rPr><w:t xml:space="preserve">'
                          + xmlEscape(token.value) + ' </w:t></w:r>')
    def render_ft(self, token):     pass
    def render_ft_e(self, token):   pass

    # Structural metadata, not content.
    def render_periph(self, token): pass

    #
    #   Package assembly
    #

    def writeDocx(self):
        name = self.config.get('General', 'name')
        z = zipfile.ZipFile(self.outputFilename, 'w', zipfile.ZIP_DEFLATED)
        z.writestr('[Content_Types].xml', CONTENT_TYPES)
        z.writestr('_rels/.rels', ROOT_RELS)
        z.writestr('docProps/core.xml', CORE_PROPS.replace('{title}', xmlEscape(name)))
        z.writestr('word/_rels/document.xml.rels', DOCUMENT_RELS)
        z.writestr('word/styles.xml', STYLES)
        z.writestr('word/settings.xml', SETTINGS)
        z.writestr('word/footnotes.xml',
                   FOOTNOTES_SHELL.replace('{footnotes}', ''.join(self.footnotes)))
        z.writestr('word/document.xml',
                   DOCUMENT_SHELL.replace('{body}', ''.join(self.body)))
        z.close()


#
#   Static package parts
#

XMLDECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'

CONTENT_TYPES = XMLDECL + (
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
    '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
    '<Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>'
    '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
    '</Types>')

ROOT_RELS = XMLDECL + (
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
    '</Relationships>')

DOCUMENT_RELS = XMLDECL + (
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
    '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/>'
    '</Relationships>')

CORE_PROPS = XMLDECL + (
    '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
    'xmlns:dc="http://purl.org/dc/elements/1.1/">'
    '<dc:title>{title}</dc:title>'
    '<dc:creator>Open English Bible</dc:creator>'
    '</cp:coreProperties>')

SETTINGS = XMLDECL + (
    '<w:settings ' + W + '>'
    '<w:footnotePr><w:footnote w:id="-1"/><w:footnote w:id="0"/></w:footnotePr>'
    '</w:settings>')

FOOTNOTES_SHELL = XMLDECL + (
    '<w:footnotes ' + W + '>'
    '<w:footnote w:type="separator" w:id="-1"><w:p><w:r><w:separator/></w:r></w:p></w:footnote>'
    '<w:footnote w:type="continuationSeparator" w:id="0"><w:p><w:r><w:continuationSeparator/></w:r></w:p></w:footnote>'
    '{footnotes}'
    '</w:footnotes>')

DOCUMENT_SHELL = XMLDECL + (
    '<w:document ' + W + '><w:body>'
    '{body}'
    '<w:sectPr>'
    '<w:pgSz w:w="8640" w:h="12960"/>'
    '<w:pgMar w:top="1080" w:right="1080" w:bottom="1080" w:left="1080" w:header="720" w:footer="720"/>'
    '</w:sectPr>'
    '</w:body></w:document>')


def _style(styleId, name, paragraph=True, basedOn='Normal', pPr='', rPr='', outline=None):
    kind = 'paragraph' if paragraph else 'character'
    if outline is not None:
        pPr = pPr + '<w:outlineLvl w:val="' + str(outline) + '"/>'
    xml = '<w:style w:type="' + kind + '" w:styleId="' + styleId + '">'
    xml += '<w:name w:val="' + name + '"/>'
    if basedOn and styleId != 'Normal':
        xml += '<w:basedOn w:val="' + basedOn + '"/>'
    if paragraph and pPr:
        xml += '<w:pPr>' + pPr + '</w:pPr>'
    if rPr:
        xml += '<w:rPr>' + rPr + '</w:rPr>'
    return xml + '</w:style>'


CENTER = '<w:jc w:val="center"/>'
NOSPACE = '<w:spacing w:before="0" w:after="0"/>'

STYLES = XMLDECL + '<w:styles ' + W + '>' + (
    '<w:docDefaults><w:rPrDefault><w:rPr>'
    '<w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:sz w:val="22"/>'
    '</w:rPr></w:rPrDefault>'
    '<w:pPrDefault><w:pPr><w:spacing w:after="120"/></w:pPr></w:pPrDefault></w:docDefaults>'
    + _style('Normal', 'Normal', pPr='<w:jc w:val="both"/>')
    + _style('BookTitle', 'Book Title',
             pPr=CENTER + '<w:spacing w:before="480" w:after="240"/><w:keepNext/>',
             rPr='<w:b/><w:caps/><w:sz w:val="48"/>', outline=0)
    + _style('BookSubtitle', 'Book Subtitle', pPr=CENTER + '<w:keepNext/>',
             rPr='<w:caps/><w:sz w:val="30"/>')
    + _style('Heading1', 'Heading 1',
             pPr=CENTER + '<w:spacing w:before="360" w:after="180"/><w:keepNext/>',
             rPr='<w:b/><w:caps/><w:sz w:val="32"/>', outline=1)
    + _style('Heading2', 'Heading 2',
             pPr=CENTER + '<w:spacing w:before="300" w:after="150"/><w:keepNext/>',
             rPr='<w:b/><w:sz w:val="28"/>', outline=2)
    + _style('Heading3', 'Heading 3',
             pPr=CENTER + '<w:spacing w:before="240" w:after="120"/><w:keepNext/>',
             rPr='<w:b/><w:sz w:val="24"/>', outline=3)
    + _style('PsalmTitle', 'Descriptive Title', rPr='<w:i/>')
    + _style('Indented', 'Indented Paragraph', pPr='<w:ind w:left="360"/>')
    + _style('Poetry1', 'Poetry 1', pPr='<w:jc w:val="left"/><w:ind w:left="360"/>' + NOSPACE)
    + _style('Poetry2', 'Poetry 2', pPr='<w:jc w:val="left"/><w:ind w:left="720"/>' + NOSPACE)
    + _style('Poetry3', 'Poetry 3', pPr='<w:jc w:val="left"/><w:ind w:left="1080"/>' + NOSPACE)
    + _style('FootnoteText', 'Footnote Text', pPr='<w:jc w:val="left"/>' + NOSPACE,
             rPr='<w:sz w:val="18"/>')
    + _style('FootnoteReference', 'Footnote Reference', paragraph=False, basedOn='',
             rPr='<w:vertAlign w:val="superscript"/>')
    + '</w:styles>')
