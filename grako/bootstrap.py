# -*- coding: utf-8 -*-
"""
Implements parsing of Grako's EBNF idiom for grammars, and grammar model
creation using the .grammars module.

GrakoParserRoot is the bootstrap parser. It uses the facilities of parsing.Parser
as generated parsers do, but it does not conform to the patterns in the generated
code. Why? Because having Grako bootstrap itself from its grammar would be cool,
but very bad engineering. GrakoParserRoot is hand-crafted.

The GrakoGrammarGenerator class, a descendant of GrakoParserRoot constructs
a model of the grammar using semantic actions the model elements defined
in the .grammars module.
"""
from __future__ import print_function, division, absolute_import, unicode_literals
from .buffering import Buffer
from .parsing import Parser, rule_def
from .semantics import GrakoASTSemantics, GrakoSemantics

__all__ = ['GrakoParser', 'GrakoGrammarGenerator']

COMMENTS_RE = r'\(\*(?:.|\n)*?\*\)'


class GrakoParserBase(Parser):

    def parse(self, text, rule='grammar', filename=None, **kwargs):
        if not isinstance(text, Buffer):
            text = Buffer(text, comments_re=COMMENTS_RE, **kwargs)
        return super(GrakoParserBase, self).parse(text,
                                                  rule,
                                                  filename=filename,
                                                  **kwargs)

    @rule_def
    def _grammar_(self):
        def block0():
            self._rule_()
        self._positive_closure(block0)

        self.ast['@'] = self.last_node
        self._check_eof()

    @rule_def
    def _rule_(self):
        self._word_()
        self.ast['name'] = self.last_node
        self._token('=')
        self._cut()
        self._expre_()
        self.ast['rhs'] = self.last_node
        with self._group():
            with self._choice():
                with self._option():
                    self._token('.')
                with self._option():
                    self._token(';')
                self._error('expecting one of: ; .')
        self._cut()

    @rule_def
    def _expre_(self):
        with self._choice():
            with self._option():
                self._choice_()
            with self._option():
                self._sequence_()
            self._error('no available options')

    @rule_def
    def _choice_(self):
        self._sequence_()
        self.ast.add_list('options', self.last_node)

        def block1():
            self._token('|')
            self._cut()
            self._sequence_()
            self.ast['options'] = self.last_node
        self._positive_closure(block1)

    @rule_def
    def _sequence_(self):
        def block1():
            self._element_()
        self._positive_closure(block1)

        self.ast['sequence'] = self.last_node

    @rule_def
    def _element_(self):
        with self._choice():
            with self._option():
                self._named_()
            with self._option():
                self._override_()
            with self._option():
                self._term_()
            self._error('no available options')

    @rule_def
    def _named_(self):
        self._name_()
        self.ast['name'] = self.last_node
        with self._group():
            with self._choice():
                with self._option():
                    self._token('+:')
                    self.ast['force_list'] = self.last_node
                with self._option():
                    self._token(':')
                self._error('expecting one of: : +:')
        self._element_()
        self.ast['value'] = self.last_node

    @rule_def
    def _name_(self):
        with self._choice():
            with self._option():
                self._word_()
            with self._option():
                self._token('@')
            self._error('expecting one of: @')

    @rule_def
    def _override_(self):
        self._token('@')
        self._cut()
        self._element_()
        self.ast['@'] = self.last_node

    @rule_def
    def _term_(self):
        with self._choice():
            with self._option():
                self._void_()
            with self._option():
                self._group_()
            with self._option():
                self._closure_()
            with self._option():
                self._optional_()
            with self._option():
                self._special_()
            with self._option():
                self._kif_()
            with self._option():
                self._knot_()
            with self._option():
                self._atom_()
            self._error('no available options')

    @rule_def
    def _group_(self):
        self._token('(')
        self._cut()
        self._expre_()
        self.ast['@'] = self.last_node
        self._token(')')
        self._cut()

    @rule_def
    def _closure_(self):
        self._token('{')
        self._cut()
        self._expre_()
        self.ast['exp'] = self.last_node
        self._token('}')
        self._cut()
        with self._group():
            with self._choice():
                with self._option():
                    with self._group():
                        with self._choice():
                            with self._option():
                                self._token('-')
                            with self._option():
                                self._token('+')
                            self._error('expecting one of: - +')
                    self.ast['plus'] = self.last_node
                with self._option():
                    with self._optional():
                        self._token('*')
                self._error('expecting one of: - * +')
        self._cut()

    @rule_def
    def _optional_(self):
        self._token('[')
        self._cut()
        self._expre_()
        self.ast['@'] = self.last_node
        self._token(']')
        self._cut()

    @rule_def
    def _special_(self):
        self._token('?(')
        self._cut()
        self._pattern(r'(.*)')
        self.ast['@'] = self.last_node
        self._token(')?')
        self._cut()

    @rule_def
    def _kif_(self):
        self._token('&')
        self._cut()
        self._term_()
        self.ast['@'] = self.last_node

    @rule_def
    def _knot_(self):
        self._token('!')
        self._cut()
        self._term_()
        self.ast['@'] = self.last_node

    @rule_def
    def _atom_(self):
        with self._choice():
            with self._option():
                self._cut_()
            with self._option():
                self._token_()
            with self._option():
                self._call_()
            with self._option():
                self._pattern_()
            with self._option():
                self._eof_()
            self._error('no available options')

    @rule_def
    def _call_(self):
        self._word_()

    @rule_def
    def _void_(self):
        self._token('()')

    @rule_def
    def _cut_(self):
        self._token('>>')

    @rule_def
    def _token_(self):
        with self._choice():
            with self._option():
                self._token('"')
                self._cut()
                self._pattern(r'([^"\n]|\\"|\\\\)*')
                self.ast['@'] = self.last_node
                self._token('"')
            with self._option():
                self._token("'")
                self._cut()
                self._pattern(r"([^'\n]|\\'|\\\\)*")
                self.ast['@'] = self.last_node
                self._token("'")
            self._error('expecting one of: \' "')

    @rule_def
    def _word_(self):
        self._pattern(r'[-_A-Za-z0-9]+')

    @rule_def
    def _pattern_(self):
        self._token('?/')
        self._cut()
        self._pattern(r'(.*?)(?=/\?)')
        self.ast['@'] = self.last_node
        self._token('/?')
        self._cut()

    @rule_def
    def _eof_(self):
        self._token('$')
        self._cut()


class GrakoParser(GrakoParserBase):
    def __init__(self, grammar_name, semantics=None, **kwargs):
        if semantics is None:
            semantics = GrakoASTSemantics()
        super(GrakoParser, self).__init__(semantics=semantics, **kwargs)


class GrakoGrammarGenerator(GrakoParserBase):
    def __init__(self, grammar_name, semantics=None, **kwargs):
        if semantics is None:
            semantics = GrakoSemantics(grammar_name)
        super(GrakoGrammarGenerator, self).__init__(semantics=semantics, **kwargs)
