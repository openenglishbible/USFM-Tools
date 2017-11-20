# -*- coding: utf-8 -*-
#

from configparser import ConfigParser, ExtendedInterpolation
import sys


class RendererConfig(object):
    def __init__(self, fileName, default=None):
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        if not default == None: self.config.read(default)
        self.config.read(fileName)

    def get(self, section, option):
        try:
            return self.config.get(section, option)
        except Exception as e:
            print("Bad option configuration: " + str(e))
            sys.exit(1)
