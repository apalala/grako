# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from grako.exceptions import FailedParse
from grako.tool import genmodel
from grako.codegen import codegen


class JoinTests(unittest.TestCase):

    def test_positive_join(self):
        grammar = '''
            start = ','.{'x' 'y'}+ ;
        '''

        grammar2 = '''
            start = (','.{'x'}+|{}) ;
        '''

        grammar3 = '''
            start = [','.{'x'}+] ;
        '''

        model = genmodel("test", grammar)
        codegen(model)
        ast = model.parse("x y, x y", nameguard=False)
        self.assertEqual([['x', 'y'], ['x', 'y']], ast)
        ast = model.parse("x y x y", nameguard=False)
        self.assertEqual([['x', 'y']], ast)
        try:
            ast = model.parse("y x", nameguard=False)
            self.Fail('closure not positive')
        except FailedParse:
            pass

        model = genmodel("test", grammar2)
        ast = model.parse("y x", nameguard=False)
        self.assertEqual([], ast)
        ast = model.parse("x", nameguard=False)
        self.assertEqual(['x'], ast)
        ast = model.parse("x,x", nameguard=False)
        self.assertEqual(['x', 'x'], ast)

        model = genmodel("test", grammar3)
        ast = model.parse("y x", nameguard=False)
        self.assertEqual(None, ast)

    def test_normal_join(self):
        grammar = '''
            start = ','.{'x' 'y'} 'z' ;
        '''

        model = genmodel("test", grammar)
        codegen(model)

        ast = model.parse("x y, x y z", nameguard=False)
        self.assertEqual([[['x', 'y'], ['x', 'y']], 'z'], ast)

        ast = model.parse("x y z", nameguard=False)
        self.assertEqual([[['x', 'y']], 'z'], ast)

        ast = model.parse("z", nameguard=False)
        self.assertEqual([[], 'z'], ast)

    def test_group_join(self):
        grammar = '''
            start = ('a' 'b').{'x'}+ ;
        '''
        model = genmodel("test", grammar)
        c = codegen(model)
        import parser
        parser.suite(c)

        ast = model.parse("x a b x", nameguard=False)
        self.assertEqual(['x', 'x'], ast)
