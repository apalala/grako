# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import OrderedDict

from . import grammars
from .util import simplify_list


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

    def named(self, ast):
        return grammars.Named(ast.name, ast.value)

    def override_list(self, ast):
        return grammars.OverrideList(ast)

    def override(self, ast):
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

    def rule(self, ast):
        name = ast.name
        rhs = ast.rhs
        if name not in self.rules:
            rule = grammars.Rule(name, rhs, ast.params, ast.kwparams)
            self.rules[name] = rule
        else:
            rule = self.rules[name]
            if isinstance(rule.exp, grammars.Choice):
                rule.exp.options.append(rhs)
            else:
                rule.exp = grammars.Choice([rule.exp, rhs])
        return rule

    def grammar(self, ast):
        return grammars.Grammar(self.grammar_name, list(self.rules.values()))
