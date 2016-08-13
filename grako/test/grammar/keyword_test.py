# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from grako.exceptions import FailedParse
from grako.tool import genmodel
from grako.codegen import codegen


class KeywordTests(unittest.TestCase):

    def test_keywords_in_rule_names(self):
        grammar = '''
            start
                =
                whitespace
                ;

            whitespace
                =
                    {'x'}+
                ;
        '''
        m = genmodel('Keywords', grammar)
        m.parse('x')

    def test_python_keywords_in_rule_names(self):
        # This is a regression test for
        # https://bitbucket.org/apalala/grako/issues/59
        # (semantic actions not called for rules with the same name as a python
        # keyword).
        grammar = '''
            not = 'x' ;
        '''
        m = genmodel('Keywords', grammar)

        class Semantics(object):
            def __init__(self):
                self.called = False

            def not_(self, ast):
                self.called = True

        semantics = Semantics()
        m.parse('x', semantics=semantics)
        assert semantics.called

    def test_define_keywords(self):
        import parser

        grammar = '''
            @@keyword :: B C
            @@keyword :: 'A'

            start = ('a' 'b').{'x'}+ ;
        '''
        model = genmodel("test", grammar)
        c = codegen(model)
        parser.suite(c)

        grammar2 = str(model)
        model2 = genmodel("test", grammar2)
        c2 = codegen(model2)
        parser.suite(c2)

        self.assertEqual(grammar2, str(model2))

    def test_check_keywords(self):
        import parser

        grammar = '''
            @@keyword :: A

            start = {id}+ $ ;

            @name
            id = /\w+/ ;
        '''
        model = genmodel('test', grammar)
        c = codegen(model)
        parser.suite(c)

        ast = model.parse('hello world')
        self.assertEqual(['hello', 'world'], ast)

        try:
            ast = model.parse("hello A world")
            self.assertEqual(['hello', 'A', 'world'], ast)
            self.fail('accepted keyword as name')
        except FailedParse as e:
            self.assertTrue('"A" is a reserved word' in str(e))
            pass
