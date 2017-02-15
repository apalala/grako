# -*- coding: utf-8 -*-
# Copyright (C) 2017      by Juancarlo Añez
# Copyright (C) 2012-2016 by Juancarlo Añez and Thomas Bragg
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from grako.exceptions import FailedParse
from grako.tool import genmodel


class LeftRecursionTests(unittest.TestCase):

    def test_direct_left_recursion(self, trace=False):
        grammar = '''
            @@left_recursion :: True
            start
                =
                expre $
                ;

            expre
                =
                expre '+' number
                |
                expre '*' number
                |
                number
                ;

            number
                =
                ?/[0-9]+/?
                ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("1*2+3*5", trace=trace, colorize=True)
        self.assertEqual(['1', '*', '2', '+', '3', '*', '5'], ast)

    def test_indirect_left_recursion(self, trace=False):
        grammar = '''
            @@left_recursion :: True
            start = x $ ;
            x = expr ;
            expr = x '-' num | num;
            num = ?/[0-9]+/? ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("5-87-32", trace=trace, colorize=True)
        self.assertEqual(['5', '-', '87', '-', '32'], ast)

    def test_indirect_left_recursion_with_cut(self, trace=False):
        grammar = '''
            @@left_recursion :: True
            start = x $ ;
            x = expr ;
            expr = x '-' ~ num | num;
            num = ?/[0-9]+/? ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("5-87-32", trace=trace, colorize=True)
        self.assertEqual(['5', '-', '87', '-', '32'], ast)

    def test_indirect_left_recursion_complex(self, trace=False):
        grammar = '''
            @@left_recursion :: True
            start = Primary $ ;
            Primary = PrimaryNoNewArray ;

            PrimaryNoNewArray =
              ClassInstanceCreationExpression
            | MethodInvocation
            | FieldAccess
            | ArrayAccess
            | 'this' ;

            ClassInstanceCreationExpression =
              'new' ClassOrInterfaceType '(' ')'
            | Primary '.new' Identifier '()' ;

            MethodInvocation =
              Primary '.' MethodName '()'
            | MethodName '()' ;

            FieldAccess =
              Primary '.' Identifier
            | 'super.' Identifier ;

            ArrayAccess =
              Primary '[' Expression ']'
            | ExpressionName '[' Expression ']' ;

            ClassOrInterfaceType =
              ClassName
            | InterfaceTypeName ;

            ClassName = 'C' | 'D' ;
            InterfaceTypeName = 'I' | 'J' ;
            Identifier = 'x' | 'y' | ClassOrInterfaceType ;
            MethodName = 'm' | 'n' ;
            ExpressionName = Identifier ;
            Expression = 'i' | 'j' ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("this", trace=trace, colorize=True)
        self.assertEqual('this', ast)
        ast = model.parse("this.x", trace=trace, colorize=True)
        self.assertEqual(['this', '.', 'x'], ast)
        ast = model.parse("this.x.y", trace=trace, colorize=True)
        self.assertEqual(['this', '.', 'x', '.', 'y'], ast)
        ast = model.parse("this.x.m()", trace=trace, colorize=True)
        self.assertEqual(['this', '.', 'x', '.', 'm', '()'], ast)
        ast = model.parse("x[i][j].y", trace=trace, colorize=True)
        self.assertEqual(['x', '[', 'i', ']', '[', 'j', ']', '.', 'y'], ast)

    def test_no_left_recursion(self, trace=False):
        grammar = '''
            @@left_recursion :: True
            start
                =
                expre $
                ;

            expre
                =
                expre '+' number
                |
                expre '*' number
                |
                number
                ;

            number
                =
                ?/[0-9]+/?
                ;
        '''
        model = genmodel("test", grammar)
        model.parse("1*2+3*5", trace=trace, colorize=True)
        try:
            model.parse("1*2+3*5", left_recursion=False, trace=trace, colorize=True)
            self.Fail('expected left recursion failure')
        except FailedParse:
            pass

    def test_nested_left_recursion(self, trace=False):
        grammar_a = '''
            @@left_recursion :: True
            s = e $ ;
            e = [e '+'] t ;
            t = [t '*'] a ;
            a = ?/[0-9]/? ;
        '''
        grammar_b = '''
            @@left_recursion :: True
            s = e $ ;
            e = [e '+'] a ;
            a = n | p ;
            n = ?/[0-9]/? ;
            p = '(' @:e ')' ;
        '''
        model_a = genmodel("test", grammar_a)
        model_b = genmodel("test", grammar_b)
        ast = model_a.parse("1*2+3*4", trace=trace, colorize=True)
        self.assertEqual(['1', '*', '2', '+', ['3', '*', '4']], ast)
        ast = model_b.parse("(1+2)+(3+4)", trace=trace, colorize=True)
        self.assertEqual(['1', '+', '2', '+', ['3', '+', '4']], ast)
        ast = model_a.parse("1*2*3", trace=trace, colorize=True)
        self.assertEqual(['1', '*', '2', '*', '3'], ast)
        ast = model_b.parse("(((1+2)))", trace=trace, colorize=True)
        self.assertEqual(['1', '+', '2'], ast)

    def notest_left_recursion_bug(self, trace=False):
        grammar = '''\
            @@grammar :: Minus
            @@left_recursion :: True

            start = expression $ ;

            expression =
                | paren_expression
                | minus_expression
                | value
                ;

            paren_expression
                =
                '(' expression ')'
                ;

            minus_expression
                =
                expression '-' value
                ;

            value = /[0-9]+/ ;
        '''
        model = genmodel(grammar=grammar)
        # model.parse('3', trace=trace, colorize=True)
        # model.parse('3 - 2', trace=trace, colorize=True)
        # model.parse('(3 - 2)', trace=trace, colorize=True)
        # model.parse('(3 - 2) - 1', trace=trace, colorize=True)
        # model.parse('3 - 2 - 1', trace=trace, colorize=True)
        model.parse('3 - (2 - 1)', trace=trace, colorize=True)


def main(trace=True):
    t = LeftRecursionTests('test_direct_left_recursion')
    # t.test_direct_left_recursion(trace=trace)
    # t.test_indirect_left_recursion(trace=trace)
    # t.test_indirect_left_recursion_with_cut(trace=trace)
    # t.test_indirect_left_recursion_complex(trace=trace)
    # t.test_no_left_recursion(trace=trace)
    # t.test_nested_left_recursion(trace=trace)
    t.no_test_left_recursion_bug(trace=trace)


if __name__ == '__main__':
    main()
