# -*- coding: utf-8 -*-
"""
Grako language parsing tests.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import unittest

from grako.util import trim, eval_escapes
from grako.grammars import GrakoBuffer


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

    def test_multiple_include(self):
        text = '''\
            first
                #include :: "something"
                #include :: "anotherthing"
            last\
        '''
        buf = MockIncludeBuffer(trim(text))
        self.assertEqual('first\n\nINCLUDED "something"\n\nINCLUDED "anotherthing"\nlast', buf.text)

    def test_escape_sequences(self):
        self.assertEqual(u'\n', eval_escapes(r'\n'))
        self.assertEqual(u'this \xeds a test', eval_escapes(r'this \xeds a test'))
        self.assertEqual(u'this ís a test', eval_escapes(r'this \xeds a test'))
        self.assertEqual(u'\nañez', eval_escapes(r'\na\xf1ez'))
        self.assertEqual(u'\nañez', eval_escapes(r'\nañez'))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ParsingTests)


def main():
    unittest.TextTestRunner(verbosity=2).run(suite())

if __name__ == '__main__':
    main()
