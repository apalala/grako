# -*- coding: utf-8 -*-
"""
Elements for a model of a parsed Grako grammar.

A model constructed with these elements, and rooted in a Grammar instance is
able to parse the language defined by the grammar.

Models calculate the LL(k) FIRST function to aid in providing more significant
error messages when a choice fails to parse. FOLLOW(k) and LA(k) should be
computed, but they are not.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
import sys
import functools
from collections import defaultdict
from copy import copy

from grako.util import indent, trim, urepr, compress_seq
from grako.exceptions import FailedRef, GrammarError
from grako.ast import AST
from grako.model import Node
from grako.contexts import ParseContext


PEP8_LLEN = 72


def check(result):
    assert isinstance(result, Model), str(result)


def dot(x, y, k):
    return set([(a + b)[:k] for a in x for b in y])


class ModelContext(ParseContext):
    def __init__(self, rules, semantics=None, trace=False, **kwargs):
        super(ModelContext, self).__init__(
            semantics=semantics,
            trace=trace,
            **kwargs
        )
        self.rules = {rule.name: rule for rule in rules}

    @property
    def pos(self):
        return self._buffer.pos

    @property
    def buf(self):
        return self._buffer

    def _find_rule(self, name):
        return functools.partial(self.rules[name].parse, self)


class Model(Node):
    @staticmethod
    def classes():
        return [
            c for c in globals().values()
            if isinstance(c, type) and issubclass(c, Model)
        ]

    def __init__(self, ast=None, ctx=None):
        super(Model, self).__init__(ast=ast, ctx=ctx)
        self._lookahead = None
        self._first_set = None
        self._follow_set = set()

    def parse(self, ctx):
        return None

    def defines(self):
        return []

    @property
    def lookahead(self, k=1):
        if self._lookahead is None:
            self._lookahead = dot(self.firstset, self.followset, k)
        return self._lookahead

    @property
    def firstset(self, k=1):
        if self._first_set is None:
            self._first_set = self._first(k, {})
        return self._first_set

    @property
    def followset(self, k=1):
        return self._follow_set

    def _validate(self, rules):
        return True

    def _first(self, k, F):
        return set()

    def _follow(self, k, FL, A):
        return A


class Void(Model):
    def __str__(self):
        return '()'


class Fail(Model):
    def __str__(self):
        return '!()'


class Comment(Model):
    def __init__(self, ast=None, **kwargs):
        super(Comment, self).__init__(ast=AST(comment=ast))

    def __str__(self):
        return '(* %s *)' % self.comment


class EOF(Model):
    def parse(self, ctx):
        ctx._next_token()
        if not ctx.buf.atend():
            ctx._error('Expecting end of text.')

    def __str__(self):
        return '$'


class _Decorator(Model):
    def __init__(self, ast=None, **kwargs):
        super(_Decorator, self).__init__(ast=AST(exp=ast))
        assert isinstance(self.exp, Model)

    def parse(self, ctx):
        return self.exp.parse(ctx)

    def defines(self):
        return self.exp.defines()

    def _validate(self, rules):
        return self.exp._validate(rules)

    def _first(self, k, F):
        return self.exp._first(k, F)

    def _follow(self, k, FL, A):
        return self.exp._follow(k, FL, A)

    def __str__(self):
        return str(self.exp)


class Group(_Decorator):
    def parse(self, ctx):
        with ctx._group():
            self.exp.parse(ctx)
            return ctx.last_node

    def __str__(self):
        exp = str(self.exp)
        if len(exp.splitlines()) > 1:
            return '(\n%s\n)' % indent(exp)
        else:
            return '(%s)' % trim(exp)


class Token(Model):
    def __postinit__(self, ast):
        super(Token, self).__postinit__(ast)
        self.token = ast

    def parse(self, ctx):
        return ctx._token(self.token)

    def _first(self, k, F):
        return set([(self.token,)])

    def __str__(self):
        return urepr(self.token)


class Pattern(Model):
    def __postinit__(self, ast):
        re.compile(ast)
        super(Pattern, self).__postinit__(ast)
        self.pattern = ast

    def parse(self, ctx):
        return ctx._pattern(self.pattern)

    def _first(self, k, F):
        return set([(self.pattern,)])

    def __str__(self):
        pattern = str(self.pattern)
        template = '/%s/' if '/' not in pattern else '?/%s/?'
        result = template % pattern
        if pattern.count('?') % 2:
            return result + '?'
        else:
            return result


class Lookahead(_Decorator):
    def parse(self, ctx):
        with ctx._if():
            super(Lookahead, self).parse(ctx)

    def __str__(self):
        return '&' + str(self.exp)


class NegativeLookahead(_Decorator):
    def __str__(self):
        return '!' + str(self.exp)

    def parse(self, ctx):
        with ctx._ifnot():
            super(NegativeLookahead, self).parse(ctx)


class Sequence(Model):
    def __init__(self, ast=None, **kwargs):
        super(Sequence, self).__init__(ast=AST(sequence=ast))

    def parse(self, ctx):
        ctx.last_node = [s.parse(ctx) for s in self.sequence]
        return ctx.last_node

    def defines(self):
        return [d for s in self.sequence for d in s.defines()]

    def _validate(self, rules):
        return {True} == {s._validate(rules) for s in self.sequence}

    def _first(self, k, F):
        result = {()}
        for s in self.sequence:
            result = dot(result, s._first(k, F), k)
        return result

    def _follow(self, k, FL, A):
        fs = A
        for x in reversed(self.sequence):
            if isinstance(x, RuleRef):
                FL[x.name] |= fs
            x._follow(k, FL, fs)
            fs = dot(x.firstset, fs, k)
        return A

    def __str__(self):
        seq = [str(s) for s in self.sequence]
        single = ' '.join(seq)
        if len(single) <= PEP8_LLEN or len(single.splitlines()) <= 1:
            return single
        else:
            return '\n'.join(seq)


class Choice(Model):
    def __init__(self, ast=None, **kwargs):
        super(Choice, self).__init__(ast=AST(options=ast))
        assert isinstance(self.options, list), urepr(self.options)

    def parse(self, ctx):
        with ctx._choice():
            for o in self.options:
                with ctx._option():
                    ctx.last_node = o.parse(ctx)
                    return ctx.last_node

            lookahead = ' '.join(str(urepr(f[0])) for f in self.lookahead if f)
            if lookahead:
                ctx._error('expecting one of {%s}' % lookahead)
            ctx._error('no available options')

    def defines(self):
        return [d for o in self.options for d in o.defines()]

    def _validate(self, rules):
        return {True} == {o._validate(rules) for o in self.options}

    def _first(self, k, F):
        result = set()
        for o in self.options:
            result |= o._first(k, F)
        return result

    def _follow(self, k, FL, A):
        for o in self.options:
            o._follow(k, FL, A)
        return A

    def __str__(self):
        options = [str(o) for o in self.options]

        multi = any(len(o.splitlines()) > 1 for o in options)
        single = ' | '.join(o for o in options)

        if multi:
            return '\n|\n'.join(indent(o) for o in options)
        elif len(options) and len(single) > PEP8_LLEN:
            return '  ' + '\n| '.join(o for o in options)
        else:
            return single


class Closure(_Decorator):
    def parse(self, ctx):
        return ctx._closure(lambda: self.exp.parse(ctx))

    def _first(self, k, F):
        efirst = self.exp._first(k, F)
        result = {()}
        for _i in range(k):
            result = dot(result, efirst, k)
        return {()} | result

    def __str__(self):
        sexp = str(self.exp)
        if len(sexp.splitlines()) <= 1:
            return '{%s}' % sexp
        else:
            return '{\n%s\n}' % indent(sexp)


class PositiveClosure(Closure):
    def parse(self, ctx):
        return ctx._positive_closure(lambda: self.exp.parse(ctx))

    def _first(self, k, F):
        efirst = self.exp._first(k, F)
        result = {()}
        for _i in range(k):
            result = dot(result, efirst, k)
        return result

    def __str__(self):
        return super(PositiveClosure, self).__str__() + '+'


class Optional(_Decorator):
    def parse(self, ctx):
        ctx.last_node = None
        with ctx._optional():
            return self.exp.parse(ctx)

    def _first(self, k, F):
        return {()} | self.exp._first(k, F)

    def __str__(self):
        exp = str(self.exp)
        template = '[%s]'
        if isinstance(self.exp, Choice):
            template = trim(self.str_template)
        elif isinstance(self.exp, Group):
            exp = self.exp.exp
        return template % exp

    str_template = '''
            [
            %s
            ]
            '''


class Cut(Model):
    def parse(self, ctx):
        ctx._cut()
        return None

    def _first(self, k, F):
        return {('~',)}

    def __str__(self):
        return '~'


class Named(_Decorator):
    def __init__(self, ast=None, **kwargs):
        super(Named, self).__init__(ast.exp)
        self.name = ast.name

    def parse(self, ctx):
        value = self.exp.parse(ctx)
        ctx.ast[self.name] = value
        return value

    def defines(self):
        return [(self.name, False)] + super(Named, self).defines()

    def __str__(self):
        return '%s:%s' % (self.name, str(self.exp))


class NamedList(Named):
    def parse(self, ctx):
        value = self.exp.parse(ctx)
        ctx.ast.setlist(self.name, value)
        return value

    def defines(self):
        return [(self.name, True)] + super(Named, self).defines()

    def __str__(self):
        return '%s+:%s' % (self.name, str(self.exp))


class Override(Named):
    def __init__(self, ast=None, **kwargs):
        super(Override, self).__init__(ast=AST(name='@', exp=ast))

    def defines(self):
        return []


class OverrideList(NamedList):
    def __init__(self, ast=None, **kwargs):
        super(OverrideList, self).__init__(ast=AST(name='@', exp=ast))

    def defines(self):
        return []


class Special(Model):
    def _first(self, k, F):
        return set([(self.value,)])

    def __str__(self):
        return '?%s?' % self.value


class RuleRef(Model):
    def __postinit__(self, ast):
        super(RuleRef, self).__postinit__(ast)
        self.name = ast

    def parse(self, ctx):
        try:
            rule = ctx._find_rule(self.name)
            return rule()
        except KeyError:
            ctx.error(self.name, etype=FailedRef)

    def _validate(self, rules):
        if self.name not in rules:
            print("Reference to unknown rule '%s'." % self.name, file=sys.stderr)
            return False
        return True

    def _first(self, k, F):
        self._first_set = F.get(self.name, set())
        return self._first_set

    @property
    def firstset(self, k=1):
        if self._first_set is None:
            self._first_set = {('<%s>' % self.name,)}
        return self._first_set

    def __str__(self):
        return self.name


class RuleInclude(_Decorator):
    def __init__(self, rule):
        assert isinstance(rule, Rule), str(rule.name)
        super(RuleInclude, self).__init__(rule.exp)
        self.rule = rule

    def __str__(self):
        return '>%s' % (self.rule.name)


class Rule(_Decorator):
    def __init__(self, name, exp, params, kwparams):
        super(Rule, self).__init__(exp)
        self.name = name
        self.params = params
        self.kwparams = kwparams
        self._adopt_children([params, kwparams])

        self.base = None

    def parse(self, ctx):
        return self._parse_rhs(ctx, self.exp)

    def _parse_rhs(self, ctx, exp):
        result = ctx._call(exp.parse, self.name, self.params, self.kwparams)
        if isinstance(result, AST):
            defines = compress_seq(self.defines())
            result._define(
                [d for d, l in defines if not l],
                [d for d, l in defines if l]
            )
        return result

    def _first(self, k, F):
        if self._first_set:
            return self._first_set
        return self.exp._first(k, F)

    def _follow(self, k, FL, A):
        return self.exp._follow(k, FL, FL[self.name])

    def __str__(self):
        params = ', '.join(self.params) if self.params else ''
        kwparams = ','.join(self.kwparams) if self.kwparams else ''
        allparams = ''
        if kwparams:
            if params:
                allparams = '(%s, %s)' % (params, kwparams)
            else:
                allparams = '(%s, %s)' % (params, kwparams)
        elif params:
            allparams = '::%s' % params

        base = ' < %s' % self.base.name if self.base else ''

        return trim(self.str_template) % (
            self.name,
            base,
            allparams,
            indent(str(self.exp))
        )

    str_template = '''\
                %s%s%s
                    =
                %s
                    ;
                '''


class BasedRule(Rule):
    def __init__(self, name, exp, base, params, kwparams):
        super(BasedRule, self).__init__(
            name,
            exp,
            params or base.params,
            kwparams or base.kwparams
        )
        self.base = base
        self.rhs = Sequence([self.base.exp, self.exp])

    def parse(self, ctx):
        return self._parse_rhs(ctx, self.rhs)

    def defines(self):
        return self.rhs.defines()


class Grammar(Model):
    def __init__(self, name, rules, whitespace=None, nameguard=None):
        super(Grammar, self).__init__()
        assert isinstance(rules, list), str(rules)
        self.name = name
        self.whitespace = whitespace
        self.nameguard = nameguard
        self.rules = rules
        self._adopt_children(rules)
        if not self._validate({r.name for r in self.rules}):
            raise GrammarError('Unknown rules, no parser generated.')
        self._calc_lookahead_sets()

    def _validate(self, ruleset):
        return {True} == {rule._validate(ruleset) for rule in self.rules}

    @property
    def first_sets(self):
        return self._first_sets

    def _calc_lookahead_sets(self, k=1):
        self._calc_first_sets()
        self._calc_follow_sets()

    def _calc_first_sets(self, k=1):
        F = defaultdict(set)
        F1 = None
        while F1 != F:
            F1 = copy(F)
            for rule in self.rules:
                F[rule.name] |= rule._first(k, F)

        for rule in self.rules:
            rule._first_set = F[rule.name]

    def _calc_follow_sets(self, k=1):
        FL = defaultdict(set)
        FL1 = None
        while FL1 != FL:
            FL1 = copy(FL)
            for rule in self.rules:
                rule._follow(k, FL, set())

        for rule in self.rules:
            rule._follow_set = FL[rule.name]

    def parse(self,
              text,
              start=None,
              filename=None,
              semantics=None,
              trace=False,
              context=None,
              whitespace=None,
              **kwargs):
        ctx = context or ModelContext(self.rules, trace=trace, **kwargs)
        return ctx.parse(
            text,
            start or self.rules[0].name,
            filename=filename,
            semantics=semantics,
            trace=trace,
            whitespace=whitespace,
            **kwargs
        )

    def __str__(self):
        return (
            '\n\n'.join(str(rule)
                        for rule in self.rules)
        ).rstrip() + '\n'
