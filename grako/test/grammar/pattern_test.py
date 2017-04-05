# -*- coding: utf-8 -*-
# Copyright (C) 2017      by Juancarlo Añez
# Copyright (C) 2012-2016 by Juancarlo Añez and Thomas Bragg
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from grako.util import trim
from grako.tool import compile


class PatternTests(unittest.TestCase):

    def test_patterns_with_newlines(self):
        grammar = '''
            @@whitespace :: /[ \t]/
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
                /^[^\\n]*\\n$/
                ;
        '''

        model = compile(grammar, "test")
        ast = model.parse('\n\n', trace=True)
        self.assertEqual(['\n', '\n'], ast)

    def test_pattern_concatenation(self):
        grammar = '''
            start
                =
                {letters_digits}+
                ;


            letters_digits
                =
                ?"[a-z]+"
                + ?'[0-9]+'
                ;
        '''
        pretty = '''
            start
                =
                {letters_digits}+
                ;


            letters_digits
                =
                /[a-z]+/
                + /[0-9]+/
                ;
        '''
        model = compile(grammar=grammar)
        ast = model.parse('abc123 def456')
        self.assertEqual(['abc123', 'def456'], ast)
        print(model.pretty())
        self.assertEqual(trim(pretty), model.pretty())
