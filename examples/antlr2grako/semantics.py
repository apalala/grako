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
        self.token_rules = {}

    def grammar(self, ast):
        return model.Grammar(
            self.name,
            [r for r in ast.rules if r is not None]
        )

    def rule(self, ast):
        name = ast.name
        exp = ast.exp
        if isinstance(exp, model.Token) and name[0].isupper():
            if name in self.token_rules:
                self.token_rules[name].exp = exp  # it is a model._Decorator
            else:
                self.token_rules[name] = exp
            return None
        elif not ast.fragment and not isinstance(exp, model.Sequence):
            ref = model.RuleRef(name.lower())
            if name in self.token_rules:
                self.token_rules[name].exp = ref
            else:
                self.token_rules[name] = ref
            name = name.lower()

        return model.Rule(ast, name, exp, ast.params, ast.kwparams)

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
        return None

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

    def regexp(self, ast):
        return model.Pattern(''.join(ast))

    def charset_optional(self, ast):
        return '%s?' % ast

    def charset_closure(self, ast):
        return '%s*' % ast

    def charset_positive_closure(self, ast):
        return '%s+' % ast

    def charset_or(self, ast):
        return '[%s]' % ''.join(ast)

    @staticmethod
    def escape(s):
        return ''.join('\\' + c if c in '[]().*+{}^$' else c for c in s)

    def charset_atom(self, ast):
        return self.escape(ast)

    def charset_char(self, ast):
        return self.escape(ast)

    def charset_range(self, ast):
        return '%s-%s' % (ast.first, ast.last)

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
        name = ast

        value = self.tokens.get(name)
        if value:
            if isinstance(value, model.Model):
                return value
            else:
                return model.Token(value)

        if name in self.token_rules:
            exp = self.token_rules[name]
        else:
            exp = model._Decorator(model.RuleRef(name))
            self.token_rules[name] = exp
        return exp
