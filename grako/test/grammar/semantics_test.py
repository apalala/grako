# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from grako.tool import genmodel
from grako.semantics import ModelBuilderSemantics


class SemanticsTests(unittest.TestCase):

    def test_builder_semantics(self):
        grammar = '''
            start::sum = {number}+ $ ;
            number::int = /\d+/ ;
        '''
        text = '5 4 3 2 1'

        semantics = ModelBuilderSemantics()
        model = genmodel('test', grammar)
        ast = model.parse(text, semantics=semantics)
        self.assertEqual(15, ast)

        import functools
        dotted = functools.partial(type('').join, '.')
        dotted.__name__ = 'dotted'

        grammar = '''
            start::dotted = {number}+ $ ;
            number = /\d+/ ;
        '''

        semantics = ModelBuilderSemantics(types=[dotted])
        model = genmodel('test', grammar)
        ast = model.parse(text, semantics=semantics)
        self.assertEqual('5.4.3.2.1', ast)
