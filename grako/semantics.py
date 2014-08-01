# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from collections import OrderedDict

from grako.util import simplify_list, eval_escapes, warning
from grako.util import re, RE_FLAGS
from grako import grammars
from grako.exceptions import FailedSemantics
from grako.model import ModelBuilderSemantics


class GrakoASTSemantics(object):

    def group(self, ast, *args):
        return simplify_list(ast)

    def element(self, ast, *args):
        return simplify_list(ast)

    def sequence(self, ast, *args):
        return simplify_list(ast)

    def choice(self, ast, *args):
        if len(ast) == 1:
            return simplify_list(ast[0])
        return ast


class GrakoSemantics(ModelBuilderSemantics):
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

    def pattern(self, ast, *args):
        pattern = ast
        try:
            re.compile(pattern, RE_FLAGS)
        except re.error as e:
            raise FailedSemantics('regexp error: ' + str(e))
        return grammars.Pattern(ast)

    def hext(self, ast):
        return int(ast, 16)

    def float(self, ast):
        return float(ast)

    def int(self, ast):
        return int(ast)

    def cut_deprecated(self, ast, *args):
        warning('The use of >> for cut is deprecated. Use the ~ symbol instead.')
        return grammars.Cut()

    def override_single_deprecated(self, ast, *args):
        warning('The use of @ for override is deprecated. Use @: instead')
        return grammars.Override(ast)

    def sequence(self, ast, *args):
        seq = ast.sequence
        assert isinstance(seq, list), str(seq)
        if len(seq) == 1:
            return seq[0]
        return grammars.Sequence(ast)

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
        exp = ast.exp
        base = ast.base
        params = ast.params
        kwparams = OrderedDict(ast.kwparams) if ast.kwparams else None

        self.new_name(name)

        if not base:
            rule = grammars.Rule(ast, name, exp, params, kwparams)
        else:
            self.known_name(base)
            base_rule = self.rules[base]
            rule = grammars.BasedRule(ast, name, exp, base_rule, params, kwparams)

        self.rules[name] = rule
        return rule

    def rule_include(self, ast, *args):
        name = str(ast)
        self.known_name(name)

        rule = self.rules[name]
        return grammars.RuleInclude(rule)

    def grammar(self, ast, *args):
        return grammars.Grammar(
            self.grammar_name,
            list(self.rules.values())
        )
