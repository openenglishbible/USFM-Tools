#!/usr/bin/env python3
"""Smoke test for the generated HTML reading site.

Checks every page of a built site directory (the *_html output of
`usfm-tools transform --target=html`) for the failure classes that have
actually occurred:

  - books built but missing from the index (and index links to missing files)
  - internal hrefs or fragment anchors that do not resolve
  - references to css/js/image assets that were not shipped
  - pages without a closing </html>, empty titles, leftover {{{placeholders}}}
  - invalid markup: <h7>, </br>, raw ampersands, duplicate ids,
    unbalanced non-paragraph tags
  - missing viewport meta / theme toggle / book navigation

Exits 0 and prints a summary when clean; prints every finding and exits 1
otherwise. Stdlib only.
"""

import os
import re
import sys
from html.parser import HTMLParser

VOID_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
             'link', 'meta', 'param', 'source', 'track', 'wbr'}
BALANCED_TAGS = ['html', 'head', 'body', 'title', 'div', 'span', 'a', 'ul',
                 'li', 'label', 'form', 'small', 'button', 'em', 'i', 'b',
                 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
RAW_AMPERSAND = re.compile(r'&(?![a-zA-Z][a-zA-Z0-9]*;|#[0-9]+;|#x[0-9a-fA-F]+;)')
BOOK_PAGE = re.compile(r'^b\d{3}\.html$')


class PageScan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.hrefs = []
        self.srcs = []
        self.counts = {}
        self.title = ''
        self.has_viewport = False
        self.has_description = False
        self.imgs_missing_alt = []
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        self.counts[tag] = self.counts.get(tag, 0) + 1
        a = dict(attrs)
        if a.get('id'):
            self.ids.append(a['id'])
        if a.get('href') is not None and tag in ('a', 'link'):
            self.hrefs.append(a['href'])
        if a.get('src') is not None and tag in ('img', 'script'):
            self.srcs.append(a['src'])
        if tag == 'meta' and a.get('name') == 'viewport':
            self.has_viewport = True
        if tag == 'meta' and a.get('name') == 'description' and (a.get('content') or '').strip():
            self.has_description = True
        if tag == 'img' and not a.get('alt'):
            self.imgs_missing_alt.append(a.get('src', '?'))
        if tag == 'title':
            self._in_title = True

    def handle_endtag(self, tag):
        self.counts['/' + tag] = self.counts.get('/' + tag, 0) + 1
        if tag == 'title':
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def main():
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        print('usage: htmlsmoketest.py <built-site-directory>')
        return 2
    site = sys.argv[1]

    pages = sorted(f for f in os.listdir(site) if f.endswith('.html'))
    book_pages = [f for f in pages if BOOK_PAGE.match(f)]
    problems = []

    def problem(page, message):
        problems.append(page + ': ' + message)

    if 'index.html' not in pages:
        problems.append('index.html is missing')
    if not book_pages:
        problems.append('no bNNN.html book pages found')

    # Pass 1: parse every page.
    raw = {}
    scans = {}
    for page in pages:
        with open(os.path.join(site, page), encoding='utf-8') as f:
            raw[page] = f.read()
        scans[page] = PageScan()
        scans[page].feed(raw[page])

    # Per-page checks.
    checked_links = 0
    checked_anchors = 0
    for page in pages:
        text = raw[page]
        scan = scans[page]

        if not scan.title.strip():
            problem(page, 'empty or missing <title>')
        if not scan.has_viewport:
            problem(page, 'missing viewport meta')
        if not scan.has_description:
            problem(page, 'missing meta description')
        for src in scan.imgs_missing_alt:
            problem(page, 'img missing alt text (%s)' % src)
        if '</html>' not in text:
            problem(page, 'missing closing </html>')
        if '{{{' in text:
            problem(page, 'unreplaced {{{placeholder}}}')
        if '<h7' in text or '</br>' in text:
            problem(page, 'invalid markup (<h7> or </br>)')
        for m in RAW_AMPERSAND.finditer(text):
            problem(page, 'raw ampersand near "...%s..."'
                    % text[max(0, m.start() - 20):m.start() + 20].replace('\n', ' '))

        seen = set()
        for i in scan.ids:
            if i in seen:
                problem(page, 'duplicate id "%s"' % i)
            seen.add(i)

        for tag in BALANCED_TAGS:
            if tag in VOID_TAGS:
                continue
            opened = scan.counts.get(tag, 0)
            closed = scan.counts.get('/' + tag, 0)
            if opened != closed:
                problem(page, 'unbalanced <%s>: %d opened, %d closed'
                        % (tag, opened, closed))

        for href in scan.hrefs:
            if href.startswith(('http:', 'https:', 'mailto:')):
                continue
            checked_links += 1
            if href.startswith('#'):
                checked_anchors += 1
                if href[1:] not in scans[page].ids:
                    problem(page, 'broken fragment link "%s"' % href)
                continue
            target, _, frag = href.partition('#')
            if not os.path.exists(os.path.join(site, target)):
                problem(page, 'broken link "%s"' % href)
            elif frag and target in scans and frag not in scans[target].ids:
                problem(page, 'broken cross-page anchor "%s"' % href)
        for src in scan.srcs:
            checked_links += 1
            if not os.path.exists(os.path.join(site, src)):
                problem(page, 'missing asset "%s"' % src)

        if '<button id="themetoggle"' not in text:
            problem(page, 'missing theme toggle button')

    for page in book_pages:
        if 'id="nav-menu"' not in raw[page]:
            problem(page, 'missing nav menu')
        if 'class="booknav"' not in raw[page]:
            problem(page, 'missing book navigation footer')

    # Cross-page check: every built book must be linked from the index,
    # and every index book link must point at a built page.
    if 'index.html' in pages:
        index_books = set(h.partition('#')[0] for h in scans['index.html'].hrefs
                          if BOOK_PAGE.match(h.partition('#')[0]))
        built = set(book_pages)
        for missing in sorted(built - index_books):
            problems.append('index.html: built book %s is not linked' % missing)
        for gone in sorted(index_books - built):
            problems.append('index.html: links to %s which was not built' % gone)

    if problems:
        print('HTML smoke test FAILED (%d problems in %s):' % (len(problems), site))
        for p in problems:
            print('  ' + p)
        return 1
    print('HTML smoke test passed: %d pages, %d links/assets (%d anchors) checked in %s'
          % (len(pages), checked_links, checked_anchors, site))
    return 0


if __name__ == '__main__':
    sys.exit(main())
