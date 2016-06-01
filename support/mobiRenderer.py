# -*- coding: utf-8 -*-
#

import epubRenderer

#
#   Requires Calibre ebook tools installed.
#

class Renderer(epubRenderer.Renderer):
    def suffix(self):
        return '.mobi'