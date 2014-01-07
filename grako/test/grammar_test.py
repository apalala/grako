# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
import unittest
from grako.tool import genmodel
from grako.grammars import ModelContext
from grako.exceptions import FailedSemantics


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
            item = @{ subitem } * "0" ;
            subitem = ?/1+/? ;
        '''
        m = genmodel('Update', grammar)
        ast = m.parse("1101110100", nameguard=False)
        self.assertEquals([['11'], ['111'], ['1'], []], ast.items)

    def test_stateful(self):
        # Parser for mediawiki-style unordered lists.
        grammar = r'''
        document = @ul [ nl ] $ ;
        ul = "*" ul_start el+:li { nl el:li } * ul_end ;
        li = ul | li_text ;
        (* Quirk: If a text line is followed by a sublist, the sublist does not get its own li.  *)
        li_text = text:text [ ul:li_followed_by_ul ] ;
        li_followed_by_ul = nl @ul ;
        text = ?/.*/? ;
        nl = ?/\n/? ul_marker ;
        (* The following rules are placeholders for state transitions.  *)
        ul_start = () ;
        ul_end = () ;
        (* The following rules are placeholders for state validations and grammar rules.  *)
        ul_marker = () ;
        '''

        class StatefulSemantics(object):
            def __init__(self, parser):
                self._context = parser

            def ul_start(self, ast):
                ctx = self._context
                ctx._state = 1 if ctx._state is None else ctx._state + 1
                return ast

            def ul_end(self, ast):
                ctx = self._context
                ctx._state = None if ctx._state is None or ctx._state <= 1 else ctx._state - 1
                return ast

            def ul_marker(self, ast):
                ctx = self._context
                if ctx._state is not None:
                    if not ctx.buf.match("*" * ctx._state):
                        raise FailedSemantics("not at correct level")
                return ast

            def ul(self, ast):
                return "<ul>" + "".join(ast.el) + "</ul>"

            def li(self, ast):
                return "<li>" + ast + "</li>"

            def li_text(self, ast):
                return ast.text if ast.ul is None else ast.text + ast.ul

        model = genmodel("test", grammar)
        context = ModelContext(model.rules, whitespace='', nameguard=False)
        ast = model.parse('*abc', "document", context=context, semantics=StatefulSemantics(context), whitespace='', nameguard=False)
        self.assertEqual(ast, "<ul><li>abc</li></ul>")
        ast = model.parse('*abc\n', "document", context=context, semantics=StatefulSemantics(context), whitespace='', nameguard=False)
        self.assertEqual(ast, "<ul><li>abc</li></ul>")
        ast = model.parse('*abc\n*def\n', "document", context=context, semantics=StatefulSemantics(context), whitespace='', nameguard=False)
        self.assertEqual(ast, "<ul><li>abc</li><li>def</li></ul>")
        ast = model.parse('**abc', "document", context=context, semantics=StatefulSemantics(context), whitespace='', nameguard=False)
        self.assertEqual(ast, "<ul><li><ul><li>abc</li></ul></li></ul>")
        ast = model.parse('*abc\n**def\n', "document", context=context, semantics=StatefulSemantics(context), whitespace='', nameguard=False)
        self.assertEqual(ast, "<ul><li>abc<ul><li>def</li></ul></li></ul>")

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
                @+:'a' {@'b'}
                $
                ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("a", nameguard=False)
        self.assertEquals(['a'], ast)

        grammar = '''
            start
                =
                @:'a' {@'b'}
                $
                ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("a", nameguard=False)
        self.assertEquals('a', ast)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(GrammarTests)


def main():
    unittest.TextTestRunner(verbosity=2).run(suite())

if __name__ == '__main__':
    main()
