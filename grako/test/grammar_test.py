# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import unittest

from grako.tool import genmodel
from grako.util import trim


class GrammarTests(unittest.TestCase):
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

    def test_update_ast(self):
        grammar = '''
            foo = name:"1" [ name: bar ] ;
            bar = { "2" } * ;
        '''
        m = genmodel('Keywords', grammar)
        ast = m.parse('1 2')
        self.assertEqual(['1', ['2']], ast.name)

        grammar = '''
            start = items: { item } * $ ;
            item = @:{ subitem } * "0" ;
            subitem = ?/1+/? ;
        '''
        m = genmodel('Update', grammar)
        ast = m.parse("1101110100", nameguard=False)
        self.assertEquals([['11'], ['111'], ['1'], []], ast.items)

    def test_optional_closure(self):
        grammar = 'start = foo+:"x" foo:{"y"}* {foo:"z"}* ;'
        model = genmodel("test", grammar)
        ast = model.parse("xyyzz", nameguard=False)
        self.assertEquals(['x', ['y', 'y'], 'z', 'z'], ast.foo)

        grammar = 'start = foo+:"x" [foo+:{"y"}*] {foo:"z"}* ;'
        model = genmodel("test", grammar)
        ast = model.parse("xyyzz", nameguard=False)
        self.assertEquals(['x', ['y', 'y'], 'z', 'z'], ast.foo)

        grammar = 'start = foo+:"x" foo:[{"y"}*] {foo:"z"}* ;'
        model = genmodel("test", grammar)
        ast = model.parse("xyyzz", nameguard=False)
        self.assertEquals(['x', ['y', 'y'], 'z', 'z'], ast.foo)

        grammar = 'start = foo+:"x" [foo:{"y"}*] {foo:"z"}* ;'
        model = genmodel("test", grammar)
        ast = model.parse("xyyzz", nameguard=False)
        self.assertEquals(['x', ['y', 'y'], 'z', 'z'], ast.foo)

    def test_optional_sequence(self):
        grammar = '''
            start = '1' ['2' '3'] '4' $ ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("1234", nameguard=False)
        self.assertEquals(['1', '2', '3', '4'], ast)

        grammar = '''
            start = '1' foo:['2' '3'] '4' $ ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("1234", nameguard=False)
        self.assertEquals(['2', '3'], ast.foo)

    def test_group_ast(self):
        grammar = '''
            start = '1' ('2' '3') '4' $ ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("1234", nameguard=False)
        self.assertEquals(['1', '2', '3', '4'], ast)

    def test_partial_options(self):
        grammar = '''
            start
                =
                [a]
                [
                    'A' 'A'
                |
                    'A' 'B'
                ]
                $
                ;
            a
                =
                'A' !('A'|'B')
                ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("AB", nameguard=False)
        self.assertEquals(['A', 'B'], ast)

    def test_partial_choice(self):
        grammar = '''
            start
                =
                o:[o]
                x:'A'
                $
                ;
            o
                =
                'A' a:'A'
                |
                'A' b:'B'
                ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("A", nameguard=False)
        self.assertEquals({'x': 'A', 'o': None}, ast)

    def test_new_override(self):
        grammar = '''
            start
                =
                @:'a' {@:'b'}
                $
                ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("abb", nameguard=False)
        self.assertEquals(['a', 'b', 'b'], ast)

    def test_list_override(self):
        grammar = '''
            start
                =
                @+:'a' {@:'b'}
                $
                ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("a", nameguard=False)
        self.assertEquals(['a'], ast)

        grammar = '''
            start
                =
                @:'a' {@:'b'}
                $
                ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("a", nameguard=False)
        self.assertEquals('a', ast)

    def test_based_rule(self):
        grammar = '''\
            start
                =
                b $
                ;


            a
                =
                @:'a'
                ;


            b < a
                =
                {@:'b'}
                ;

            '''
        model = genmodel("test", grammar)
        ast = model.parse("abb", nameguard=False)
        self.assertEquals(['a', 'b', 'b'], ast)
        self.assertEqual(trim(grammar), str(model))

    def test_rule_include(self):
        grammar = '''
            start = b $;

            a = @:'a' ;
            b = >a {@:'b'} ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("abb", nameguard=False)
        self.assertEquals(['a', 'b', 'b'], ast)

    def test_direct_left_recursion(self):
        grammar = '''
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
        ast = model.parse("1*2+3*5")
        self.assertEquals(['1', '*', '2', '+', '3', '*', '5'], ast)

    def test_indirect_left_recursion(self):
        grammar = '''
        start = x $ ;
        x = expr ;
        expr = x '-' num | num;
        num = ?/[0-9]+/? ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("5-87-32")
        self.assertEquals(['5', '-', '87', '-', '32'], ast)

    def test_indirect_left_recursion_with_cut(self):
        grammar = '''
        start = x $ ;
        x = expr ;
        expr = x '-' ~ num | num;
        num = ?/[0-9]+/? ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("5-87-32")
        self.assertEquals(['5', '-', '87', '-', '32'], ast)

    def test_indirect_left_recursion_complex(self):
        grammar = '''
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
        ast = model.parse("this")
        self.assertEquals('this', ast)
        ast = model.parse("this.x")
        self.assertEquals(['this', '.', 'x'], ast)
        ast = model.parse("this.x.y")
        self.assertEquals(['this', '.', 'x', '.', 'y'], ast)
        ast = model.parse("this.x.m()")
        self.assertEquals(['this', '.', 'x', '.', 'm', '()'], ast)
        ast = model.parse("x[i][j].y")
        self.assertEquals(['x', '[', 'i', ']', '[', 'j', ']', '.', 'y'], ast)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(GrammarTests)


def main():
    unittest.TextTestRunner(verbosity=2).run(suite())

if __name__ == '__main__':
    main()
