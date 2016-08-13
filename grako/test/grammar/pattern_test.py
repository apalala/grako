# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from grako.tool import genmodel
from grako.util import ustr


class PatternTests(unittest.TestCase):

    def test_patterns_with_newlines(self):
        grammar = '''
            start
                =
                blanklines $
                ;

            blanklines
                =
                blankline [blanklines]
                ;

            blankline
                =
                /^[^\n]*\n?$/
                ;

            blankline2 =
                ?/^[^\n]*\n?$/?
                ;
        '''

        model = genmodel("test", grammar)
        ast = model.parse('\n\n')
        self.assertEqual('', ustr(ast))

    def test_pattern_concatenation(self):
        grammar = '''
            start = {letters_digits}+ ;

            letters_digits
                =
                /[a-z]+/ + /[0-9]+/
                ;
        '''
        model = genmodel(grammar=grammar)
        ast = model.parse('abc123 def456')
        self.assertEqual(['abc123', 'def456'], ast)
