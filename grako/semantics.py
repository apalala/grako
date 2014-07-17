# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
from collections import OrderedDict

from grako.util import simplify_list, eval_escapes, warning
from grako import grammars
from grako.exceptions import FailedSemantics
from grako.model import ModelBuilder


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


class GrakoSemantics(ModelBuilder):
    def __init__(self, grammar_name):
        super(GrakoSemantics, self).__init__(
            baseType=grammars.Model,
            types=grammars.Model.classes()
        )
        self.grammar_name = grammar_name
        self.rules = OrderedDict()

    def token(self, ast, *args):
        token = eval_escapes(ast)
        return grammars.Token(token)

    def call(self, ast, *args):
        return grammars.RuleRef(ast)

    def pattern(self, ast, *args):
        pattern = ast
        try:
            re.compile(pattern)
        except re.error as e:
            raise FailedSemantics('regexp error: ' + str(e))
        return grammars.Pattern(ast)

    def cut(self, ast, *args):
        return grammars.Cut()

    def cut_deprecated(self, ast, *args):
        warning('The use of >> for cut is deprecated. Use the ~ symbol instead.')
        return grammars.Cut()

    def eof(self, ast, *args):
        return grammars.EOF()

    def void(self, ast, *args):
        return grammars.Void()

    def group(self, ast, *args):
        return grammars.Group(ast)

    def optional(self, ast, *args):
        # print('OPTIONAL', args)
        # raise Exception('How?', args)
        return grammars.Optional(ast)

    def positive_closure(self, ast, *args):
        return grammars.PositiveClosure(ast)

    def closure(self, ast, *args):
        return grammars.Closure(ast)

    def special(self, ast, *args):
        return grammars.Special(ast)

    def kif(self, ast, *args):
        return grammars.Lookahead(ast)

    def knot(self, ast, *args):
        return grammars.LookaheadNot(ast)

    def named_list(self, ast, *args):
        return grammars.NamedList(ast)

    def named_single(self, ast, *args):
        return grammars.Named(ast)

    def override_list(self, ast, *args):
        return grammars.OverrideList(ast)

    def override_single(self, ast, *args):
        return grammars.Override(ast)

    def override_single_deprecated(self, ast, *args):
        warning('The use of @ for override is deprecated. Use @: instead')
        return grammars.Override(ast)

    def sequence(self, ast, *args):
        seq = ast
        assert isinstance(seq, list), str(seq)
        if len(seq) == 1:
            return seq[0]
        return grammars.Sequence(seq)

    def choice(self, ast, *args):
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

    def rule(self, ast, *args):
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

    def rule_include(self, ast, *args):
        name = str(ast)
        self.known_name(name)

        rule = self.rules[name]
        return grammars.RuleInclude(rule)

    def grammar(self, ast, *args):
        return grammars.Grammar(self.grammar_name, list(self.rules.values()))
