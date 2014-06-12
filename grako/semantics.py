# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import OrderedDict

from grako.util import simplify_list
from grako import grammars
from grako.exceptions import FailedSemantics


class GrakoASTSemantics(object):

    def group(self, ast):
        return simplify_list(ast)

    def element(self, ast):
        return simplify_list(ast)

    def sequence(self, ast):
        return simplify_list(ast)

    def choice(self, ast):
        if len(ast) == 1:
            return simplify_list(ast[0])
        return ast


class GrakoSemantics(object):
    def __init__(self, grammar_name):
        super(GrakoSemantics, self).__init__()
        self.grammar_name = grammar_name
        self.rules = OrderedDict()

    def token(self, ast):
        return grammars.Token(ast)

    def call(self, ast):
        return grammars.RuleRef(ast)

    def pattern(self, ast):
        return grammars.Pattern(ast)

    def cut(self, ast):
        return grammars.Cut()

    def eof(self, ast):
        return grammars.EOF()

    def void(self, ast):
        return grammars.Void()

    def group(self, ast):
        return grammars.Group(ast)

    def optional(self, ast):
        return grammars.Optional(ast)

    def positive_closure(self, ast):
        return grammars.PositiveClosure(ast)

    def closure(self, ast):
        return grammars.Closure(ast)

    def special(self, ast):
        return grammars.Special(ast)

    def kif(self, ast):
        return grammars.Lookahead(ast)

    def knot(self, ast):
        return grammars.LookaheadNot(ast)

    def named_list(self, ast):
        return grammars.NamedList(ast.name, ast.value)

    def named_single(self, ast):
        return grammars.Named(ast.name, ast.value)

    def override_list(self, ast):
        return grammars.OverrideList(ast)

    def override_single(self, ast):
        return grammars.Override(ast)

    def sequence(self, ast):
        seq = ast
        assert isinstance(seq, list), str(seq)
        if len(seq) == 1:
            return seq[0]
        return grammars.Sequence(seq)

    def choice(self, ast):
        if len(ast) == 1:
            return ast[0]
        return grammars.Choice(ast)

    def new_name(self, ast):
        if ast in self.rules:
            raise FailedSemantics('rule "%s" already defined' % str(ast))
        return ast

    def known_name(self, ast):
        if ast not in self.rules:
            raise FailedSemantics('rule "%s" not yet defined' % str(ast))
        return ast

    def rule(self, ast):
        name = ast.name
        rhs = ast.rhs
        base = ast.base
        params = ast.params
        kwparams = ast.kwparams

        self.new_name(name)

        if not base:
            rule = grammars.Rule(name, rhs, params, kwparams)
        else:
            self.known_name(base)
            base_rule = self.rules[base]
            rule = grammars.BasedRule(name, rhs, base_rule, params, kwparams)

        self.rules[name] = rule
        return rule

    def rule_include(self, ast):
        name = str(ast)
        self.known_name(name)

        rule = self.rules[name]
        return grammars.RuleInclude(rule)

    def grammar(self, ast):
        return grammars.Grammar(self.grammar_name, list(self.rules.values()))
