# -*- coding: utf-8 -*-
"""
Grako language parsing tests.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import unittest

from grako.util import trim
from grako.parser import GrakoBuffer


class MockIncludeBuffer(GrakoBuffer):
    def get_include(self, source, name):
        return '\nINCLUDED "%s"\n' % name, name


class ParsingTests(unittest.TestCase):
    def test_include(self):
        text = '''\
            first
                #include :: "something"
            last\
        '''
        buf = MockIncludeBuffer(trim(text))
        self.assertEqual('first\n\nINCLUDED "something"\nlast', buf.text)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ParsingTests)


def main():
    unittest.TextTestRunner(verbosity=2).run(suite())

if __name__ == '__main__':
    main()
