# -*- coding: utf-8 -*-
#

import epubRenderer

#
#   Requires Calibre ebook tools installed.
#

class Renderer(epubRenderer.Renderer):

    suffix = '.mobi'
    identity = 'renderer for kindle (.mobi)'

