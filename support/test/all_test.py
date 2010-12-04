import unittest

import sys
sys.path.append("..")

import patch
import texise
import htmlise
import readerise
import markdownise

class TestBooks(unittest.TestCase):

    def setUp(self):
        pass

    def test_isBook(self):
        self.assertTrue(3 == 4)


if __name__ == "__main__":
    unittest.main()