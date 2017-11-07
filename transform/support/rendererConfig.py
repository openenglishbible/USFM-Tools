# -*- coding: utf-8 -*-
#

import configparser
import sys

class RendererConfig(object):
    
    def __init__(self, fileName, default=None):
        self.config = configparser.ConfigParser()
        if not default == None: self.config.readfp(open(default))
        self.config.read(fileName)
        
    def get(self, section, option):
        try:
            return self.config.get(section, option)
        except:
            print("Bad option configuration.")
            sys.exit(1)
            