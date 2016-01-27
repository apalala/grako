# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re

from grako.ast import AST
from grako import grammars as model


class ANTLRSemantics(object):
    def __init__(self, name):
        self.name = name
        self.tokens = {}

    def grammar(self, ast):
        return model.Grammar(self.name, ast.rules)

    def rule(self, ast):
        return model.Rule(ast, ast.name, ast.exp, ast.params, ast.kwparams)

    def alternatives(self, ast):
        options = [o for o in ast.options if o is not None]
        if len(options) == 1:
            return options[0]
        else:
            return model.Choice(options)

    def elements(self, ast):
        elements = [e for e in ast if e is not None]
        if not elements:
            return model.Void()
        elif len(elements) == 1:
            return elements[0]
        else:
            return model.Sequence(AST(sequence=elements))

    def predicate_or_action(self, ast):
        def flatten(s):
            if s is None:
                return ''
            elif isinstance(s, list):
                return ''.join(flatten(e) for e in s if e is not None)
            else:
                return s
        text = flatten(ast)
        return model.Comment(text)

    def named(self, ast):
        if ast.force_list:
            return model.NamedList(ast)
        else:
            return model.Named(ast)

    def syntactic_predicate(self, ast):
        return model.Lookahead(ast)

    def optional(self, ast):
        return model.Optional(ast)

    def closure(self, ast):
        return model.Closure(ast)

    def positive_closure(self, ast):
        return model.PositiveClosure(ast)

    def negative(self, ast):
        neg = model.NegativeLookahead(ast)
        any = model.Pattern('.')
        return model.Sequence(AST(sequence=[neg, any]))

    def subexp(self, ast):
        return model.Group(ast)

    def range(self, ast):
        return model.Pattern('[%s-%s]' % (ast.first, ast.last))

    def newrange(self, ast):
        return model.Pattern('[%s]' % re.escape(ast))

    def rule_ref(self, ast):
        return model.RuleRef(ast)

    def any(self, ast):
        return model.Pattern('\w+|\S+')

    def string(self, ast):
        text = ast
        if isinstance(text, list):
            text = ''.join(text)
        return model.Token(text)

    def eof(self, ast):
        return model.EOF()

    def token(self, ast):
        value = ast.value or ast.name
        self.tokens[ast.name] = value
        return value

    def token_ref(self, ast):
        value = self.tokens.get(ast)
        if not value:
            return model.RuleRef(ast)
        elif isinstance(value, model.Model):
            return value
        else:
            return model.Token(value)
