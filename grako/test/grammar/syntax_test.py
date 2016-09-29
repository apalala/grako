# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import unittest

from grako.exceptions import FailedParse
from grako.tool import genmodel
from grako.util import trim, ustr
from grako.codegen import codegen
from grako.grammars import GrakoBuffer


class SyntaxTests(unittest.TestCase):
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
        self.assertEqual([['11'], ['111'], ['1'], []], ast.items_)

    def test_include_and_override(self):
        gr = 'included_grammar'
        included_grammar = "plu = 'aaaa';"

        overridden = "%s@override\nplu = 'plu';"
        inclusion = '#include :: %s.ebnf\n' % gr

        including_grammar = overridden % (inclusion)
        whole_grammar = overridden % (included_grammar)

        class FakeIncludesBuffer(GrakoBuffer):
            def get_include(self, source, filename):
                return included_grammar, source + '/' + filename

        genmodel("test", FakeIncludesBuffer(whole_grammar))
        genmodel("test", FakeIncludesBuffer(including_grammar))

    def test_ast_assignment(self):
        grammar = '''
            n  = @: {"a"}* $ ;
            f  = @+: {"a"}* $ ;
            nn = @: {"a"}*  @: {"b"}* $ ;
            nf = @: {"a"}*  @+: {"b"}* $ ;
            fn = @+: {"a"}* @: {"b"}* $ ;
            ff = @+: {"a"}* @+: {"b"}* $ ;
        '''

        model = genmodel("test", grammar)

        def p(input, rule):
            return model.parse(input, start=rule, whitespace='')

        e = self.assertEqual

        e([], p('', 'n'))
        e(['a'], p('a', 'n'))
        e(['a', 'a'], p('aa', 'n'))

        e([[]], p('', 'f'))
        e([['a']], p('a', 'f'))
        e([['a', 'a']], p('aa', 'f'))

        for r in ('nn', 'nf', 'fn', 'ff'):
            e([[], []], p('', r))
            e([['a'], []], p('a', r))
            e([[], ['b']], p('b', r))
            e([['a', 'a'], []], p('aa', r))
            e([[], ['b', 'b']], p('bb', r))
            e([['a', 'a'], ['b']], p('aab', r))

    def test_optional_closure(self):
        grammar = 'start = foo+:"x" foo:{"y"}* {foo:"z"}* ;'
        model = genmodel("test", grammar)
        ast = model.parse("xyyzz", nameguard=False)
        self.assertEqual(['x', ['y', 'y'], 'z', 'z'], ast.foo)

        grammar = 'start = foo+:"x" [foo+:{"y"}*] {foo:"z"}* ;'
        model = genmodel("test", grammar)
        ast = model.parse("xyyzz", nameguard=False)
        self.assertEqual(['x', ['y', 'y'], 'z', 'z'], ast.foo)

        grammar = 'start = foo+:"x" foo:[{"y"}*] {foo:"z"}* ;'
        model = genmodel("test", grammar)
        ast = model.parse("xyyzz", nameguard=False)
        self.assertEqual(['x', ['y', 'y'], 'z', 'z'], ast.foo)

        grammar = 'start = foo+:"x" [foo:{"y"}*] {foo:"z"}* ;'
        model = genmodel("test", grammar)
        ast = model.parse("xyyzz", nameguard=False)
        self.assertEqual(['x', ['y', 'y'], 'z', 'z'], ast.foo)

    def test_optional_sequence(self):
        grammar = '''
            start = '1' ['2' '3'] '4' $ ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("1234", nameguard=False)
        self.assertEqual(['1', '2', '3', '4'], ast)

        grammar = '''
            start = '1' foo:['2' '3'] '4' $ ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("1234", nameguard=False)
        self.assertEqual(['2', '3'], ast.foo)

    def test_group_ast(self):
        grammar = '''
            start = '1' ('2' '3') '4' $ ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("1234", nameguard=False)
        self.assertEqual(['1', '2', '3', '4'], ast)

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
        self.assertEqual(['A', 'B'], ast)

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
        self.assertEqual({'x': 'A', 'o': None}, ast)

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
        self.assertEqual(['a', 'b', 'b'], ast)

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
        self.assertEqual(['a'], ast)

        grammar = '''
            start
                =
                @:'a' {@:'b'}
                $
                ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("a", nameguard=False)
        self.assertEqual('a', ast)

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
        self.assertEqual(['a', 'b', 'b'], ast)
        self.assertEqual(trim(grammar), ustr(model))

    def test_rule_include(self):
        grammar = '''
            start = b $;

            a = @:'a' ;
            b = >a {@:'b'} ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("abb", nameguard=False)
        self.assertEqual(['a', 'b', 'b'], ast)

    def test_48_rule_override(self):
        grammar = '''
            start = ab $;

            ab = 'xyz' ;

            @override
            ab = @:'a' {@:'b'} ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("abb", nameguard=False)
        self.assertEqual(['a', 'b', 'b'], ast)

    def test_failed_ref(self):
        grammar = """
            final = object;
            type = /[^\s=()]+/;
            object = '('type')' '{' @:{pair} {',' @:{pair}}* [','] '}';
            pair = key '=' value;
            list = '('type')' '[' @:{object} {',' @:{object}}* [','] ']';
            key = /[^\s=]+/;
            value = @:(string|list|object|unset|boolean|number|null) [','];
            null = '('type')' @:{ 'null' };
            boolean = /(true|false)/;
            unset = '<unset>';
            string = '"' @:/[^"]*/ '"';
            number = /-?[0-9]+/;
        """

        model = genmodel("final", grammar)
        codegen(model)
        model.parse('(sometype){boolean = true}')

    def test_empty_match_token(self):
        grammar = """
            table = { row }+ ;
            row = (cell1:cell "|" cell2:cell) "\n";
            cell = /[a-z]+/ ;
        """
        try:
            genmodel("model", grammar)
            self.fail('allowed empty token')
        except FailedParse:
            pass

    def test_empty_closure(self):
        grammar = '''
            start = {'x'}+ {} 'y'$;
        '''
        model = genmodel("test", grammar)
        codegen(model)
        ast = model.parse("xxxy", nameguard=False)
        self.assertEqual([['x', 'x', 'x'], [], 'y'], ast)
