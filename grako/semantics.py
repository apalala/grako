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

    def word(self, ast):
        return ast

    def qualified(self, ast):
        return ast.qualified

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

    def plus(self, ast):
        return ast

    def closure(self, ast):
        if ast.plus:
            return grammars.PositiveClosure(ast.exp)
        return grammars.Closure(ast.exp)

    def special(self, ast):
        return grammars.Special(ast.special)

    def kif(self, ast):
        return grammars.Lookahead(ast)

    def knot(self, ast):
        return grammars.LookaheadNot(ast)

    def atom(self, ast):
        return ast

    def term(self, ast):
        return ast

    def named(self, ast):
        if ast.name != '@':
            if not ast.force_list:
                return grammars.Named(ast.name, ast.value)
            else:
                return grammars.NamedList(ast.name, ast.value)
        else:
            if not ast.force_list:
                return grammars.Override(ast.value)
            else:
                return grammars.OverrideList(ast.value)

    def override(self, ast):
        return grammars.Override(ast)

    def element(self, ast):
        return ast

    def sequence(self, ast):
        seq = ast
        assert isinstance(seq, list), str(seq)
        if len(seq) == 1:
            return simplify_list(seq)
        return grammars.Sequence(seq)

    def choice(self, ast):
        if len(ast) == 1:
            return ast[0]
        return grammars.Choice(ast)

    def expre(self, ast):
        return ast

    def rule(self, ast):
        ast_name = ast.ast_name
        name = ast.name
        rhs = ast.rhs
        if not name in self.rules:
            rule = grammars.Rule(name,
                                 rhs,
                                 ast.params,
                                 ast.kwparams,
                                 ast_name=ast_name)
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
