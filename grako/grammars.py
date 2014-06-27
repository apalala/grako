# -*- coding: utf-8 -*-
"""
Elements for a model of a parsed Grako grammar.

A model constructed with these elements, and rooted in a Grammar instance is
able to parse the language defined by the grammar, but the main purpose of
the model is the generation of independent, top-down, verbose, and debugable
parsers through the inline templates from the .rendering module.

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

from grako.util import indent, trim, timestamp, unescape
from grako.exceptions import FailedRef, GrammarError
from grako.ast import AST
from grako.model import Node
from grako.rendering import render, Renderer
from grako.contexts import ParseContext, safe_name


PEP8_LLEN = 72


def check(result):
    assert isinstance(result, _Model), str(result)


def dot(x, y, k):
    return set([(a + b)[:k] for a in x for b in y])


def urepr(obj):
    return repr(obj).lstrip('u')


def compress_seq(seq):
    seen = set()
    result = []
    for x in seq:
        if x not in seen:
            result.append(x)
            seen.add(x)
    return result


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


class _Model(Node, Renderer):
    def __init__(self):
        super(_Model, self).__init__()
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


class Void(_Model):
    def __str__(self):
        return '()'

    template = 'pass'


class Fail(_Model):
    def __str__(self):
        return '!()'

    template = 'self._fail()'


class Comment(_Model):
    def __init__(self, comment):
        super(Comment, self).__init__()
        self.comment = comment.strip()

    def __str__(self):
        return self.render()

    template = '''
        (* {comment} *)

        '''


class EOF(_Model):
    def parse(self, ctx):
        ctx._next_token()
        if not ctx.buf.atend():
            ctx._error('Expecting end of text.')

    def __str__(self):
        return '$'

    template = 'self._check_eof()'


class _Decorator(_Model):
    def __init__(self, exp):
        assert isinstance(exp, _Model), str(exp)
        super(_Decorator, self).__init__()
        self.exp = exp
        self._adopt_children(exp)

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

    template = '{exp}'


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

    template = '''\
                with self._group():
                {exp:1::}\
                '''


class Token(_Model):
    def __init__(self, token):
        super(Token, self).__init__()
        self.token = unescape(token)
        if not self.token:
            raise GrammarError('invalid token %s' % self.token)

    def parse(self, ctx):
        return ctx._token(self.token)

    def _first(self, k, F):
        return set([(self.token,)])

    def __str__(self):
        return urepr(self.token)

    def render_fields(self, fields):
        fields.update(token=urepr(self.token))

    template = "self._token({token})"


class Pattern(_Model):
    def __init__(self, pattern):
        super(Pattern, self).__init__()
        self.pattern = pattern  # don't encode. asume as raw
        re.compile(pattern)

    def parse(self, ctx):
        return ctx._pattern(self.pattern)

    def _first(self, k, F):
        return set([(self.pattern,)])

    def __str__(self):
        pattern = str(self.pattern)
        result = '?/%s/?' % pattern
        if pattern.count('?') % 2:
            return result + '?'
        else:
            return result

    def render_fields(self, fields):
        raw_repr = 'r' + urepr(self.pattern).replace("\\\\", '\\')
        fields.update(pattern=raw_repr)

    template = 'self._pattern({pattern})'


class Lookahead(_Decorator):
    def __str__(self):
        return '&' + str(self.exp)

    def parse(self, ctx):
        with ctx._if():
            super(Lookahead, self).parse(ctx)

    template = '''\
                with self._if():
                {exp:1::}\
                '''


class LookaheadNot(_Decorator):
    def __str__(self):
        return '!' + str(self.exp)

    def parse(self, ctx):
        with ctx._ifnot():
            super(LookaheadNot, self).parse(ctx)

    template = '''\
                with self._ifnot():
                {exp:1::}\
                '''


class Sequence(_Model):
    def __init__(self, sequence):
        super(Sequence, self).__init__()
        assert isinstance(sequence, list), str(sequence)
        self.sequence = sequence
        self._adopt_children(sequence)
        for s in self.sequence:
            assert isinstance(s, _Model), str(s)

    def parse(self, ctx):
        ctx.last_node = [s.parse(ctx) for s in self.sequence]
        return ctx.last_node

    def defines(self):
        return [d for s in self.sequence for d in s.defines()]

    def _validate(self, rules):
        return all(s._validate(rules) for s in self.sequence)

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

    def render_fields(self, fields):
        fields.update(seq='\n'.join(render(s) for s in self.sequence))

    template = '''
                {seq}\
                '''


class Choice(_Model):
    def __init__(self, options):
        super(Choice, self).__init__()
        assert isinstance(options, list), urepr(options)
        self.options = options
        self._adopt_children(options)
        for o in self.options:
            assert isinstance(o, _Model), str(o)

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
        return all(o._validate(rules) for o in self.options)

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

    def render_fields(self, fields):
        template = trim(self.option_template)
        options = [template.format(option=indent(render(o))) for o in self.options]
        options = '\n'.join(o for o in options)
        firstset = ' '.join(f[0] for f in sorted(self.firstset) if f)
        if firstset:
            error = 'expecting one of: ' + firstset
        else:
            error = 'no available options'
        fields.update(n=self.counter(),
                      options=indent(options),
                      error=urepr(error)
                      )

    def render(self, **fields):
        if len(self.options) == 1:
            return render(self.options[0], **fields)
        else:
            return super(Choice, self).render(**fields)

    option_template = '''\
                    with self._option():
                    {option}\
                    '''

    template = '''\
                with self._choice():
                {options}
                    self._error({error})\
                '''


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

    def render_fields(self, fields):
        fields.update(n=self.counter())

    def render(self, **fields):
        if {()} in self.exp.firstset:
            raise GrammarError('may repeat empty sequence')
        return '\n' + super(Closure, self).render(**fields)

    template = '''\
                def block{n}():
                {exp:1::}
                self._closure(block{n})\
                '''


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

    def render_fields(self, fields):
        fields.update(n=self.counter())

    template = '''
                def block{n}():
                {exp:1::}
                self._positive_closure(block{n})
                '''


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

    template = '''\
                with self._optional():
                {exp:1::}\
                '''

    str_template = '''
            [
            %s
            ]
            '''


class Cut(_Model):
    def parse(self, ctx):
        ctx._cut()
        return None

    def _first(self, k, F):
        return {('~',)}

    def __str__(self):
        return '~'

    template = 'self._cut()'


class Named(_Decorator):
    def __init__(self, name, exp):
        super(Named, self).__init__(exp)
        assert isinstance(exp, _Model), str(exp)
        self.name = name

    def parse(self, ctx):
        value = self.exp.parse(ctx)
        ctx._add_ast_node(self.name, value)
        return value

    def defines(self):
        return [(self.name, False)] + super(Named, self).defines()

    def __str__(self):
        return '%s:%s' % (self.name, str(self.exp))

    def render_fields(self, fields):
        fields.update(n=self.counter(),
                      name=safe_name(self.name)
                      )

    template = '''
                {exp}
                self.ast['{name}'] = self.last_node\
                '''


class NamedList(Named):
    def parse(self, ctx):
        value = self.exp.parse(ctx)
        ctx._add_ast_node(self.name, value, True)
        return value

    def defines(self):
        return [(self.name, True)] + super(Named, self).defines()

    def __str__(self):
        return '%s+:%s' % (self.name, str(self.exp))

    template = '''
                {exp}
                self.ast._append('{name}', self.last_node)\
                '''


class Override(Named):
    def __init__(self, exp):
        super(Override, self).__init__('@', exp)

    def defines(self):
        return []


class OverrideList(NamedList):
    def __init__(self, exp):
        super(OverrideList, self).__init__('@', exp)

    def defines(self):
        return []


class Special(_Model):
    def __init__(self, special):
        super(Special, self).__init__()
        self.special = special

    def _first(self, k, F):
        return set([(self.special,)])

    def __str__(self):
        return '?%s?' % self.special


class RuleRef(_Model):
    def __init__(self, name):
        super(RuleRef, self).__init__()
        self.name = name

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

    template = "self._{name}_()"


class RuleInclude(_Decorator):
    def __init__(self, rule):
        assert isinstance(rule, Rule), str(rule.name)
        super(RuleInclude, self).__init__(rule.exp)
        self.rule = rule

    def __str__(self):
        return '>%s' % (self.rule.name)

    def render_fields(self, fields):
        super(RuleInclude, self).render_fields(fields)
        fields.update(exp=self.rule.exp)

    template = '''
                {exp}
                '''


class Rule(_Decorator):
    def __init__(self, name, exp, params, kwparams):
        super(Rule, self).__init__(exp)
        self.name = name
        self.params = params
        self.kwparams = kwparams

    def parse(self, ctx):
        return self._parse_rhs(ctx, self.exp)

    def _parse_rhs(self, ctx, exp):
        result = ctx._call(exp.parse, self.name)
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
        return trim(self.str_template) % (self.name, indent(str(self.exp)))

    def render_fields(self, fields):
        self.reset_counter()

        params = kwparams = ''
        if self.params:
            params = ', '.join(repr(str(p)) for p in self.params)
        if self.kwparams:
            kwparams = ', '.join('%s=%s' % (k, repr(str(v))) for k, v in self.kwparams.items())

        if params and kwparams:
            params = params + ', ' + kwparams
        elif kwparams:
            params = kwparams

        fields.update(params=params)

        defines = compress_seq(self.defines())
        sdefs = [d for d, l in defines if not l]
        ldefs = [d for d, l in defines if l]
        if not (sdefs or ldefs):
            sdefines = ''
        else:
            sdefs = '[%s]' % ', '.join(urepr(d) for d in sdefs)
            ldefs = '[%s]' % ', '.join(urepr(d) for d in ldefs)
            if not ldefs:
                sdefines = '\n\n    self.ast._define(%s, %s)' % (sdefs, ldefs)
            else:
                sdefines = indent('\n\n' + trim('''\
                                                self.ast._define(
                                                    %s,
                                                    %s
                                                )''' % (sdefs, ldefs)
                                                )
                                  )

        fields.update(defines=sdefines)

    template = '''
                @graken({params})
                def _{name}_(self):
                {exp:1::}{defines}

                '''

    str_template = '''\
                %s
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

    def render_fields(self, fields):
        super(BasedRule, self).render_fields(fields)
        fields.update(exp=self.rhs)

    def __str__(self):
        return trim(self.str_template) % (
            self.name,
            self.base.name,
            indent(str(self.exp))
        )

    str_template = '''\
                %s < %s
                    =
                %s
                    ;
                '''


class Grammar(_Model):
    def __init__(self, name, rules, whitespace=None, nameguard=None):
        super(Grammar, self).__init__()
        assert isinstance(rules, list), str(rules)
        self.name = name
        self.whitespace = urepr(whitespace)
        self.nameguard = nameguard
        self.rules = rules
        self._adopt_children(rules)
        if not self._validate({r.name for r in self.rules}):
            raise GrammarError('Unknown rules, no parser generated.')
        self._calc_lookahead_sets()

    def _validate(self, ruleset):
        return all(rule._validate(ruleset) for rule in self.rules)

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

    def codegen(self):
        return self.render()

    def __str__(self):
        return '\n\n'.join(str(rule) for rule in self.rules) + '\n'

    def render_fields(self, fields):
        abstract_template = trim(self.abstract_rule_template)
        abstract_rules = [abstract_template.format(name=safe_name(rule.name)) for rule in self.rules]
        abstract_rules = indent('\n'.join(abstract_rules))
        fields.update(rules=indent(render(self.rules)),
                      abstract_rules=abstract_rules,
                      version=timestamp()
                      )

    abstract_rule_template = '''
            def {name}(self, ast):
                return ast
            '''

    template = '''\
                #!/usr/bin/env python
                # -*- coding: utf-8 -*-

                # CAVEAT UTILITOR
                #
                # This file was automatically generated by Grako.
                #
                #    https://pypi.python.org/pypi/grako/
                #
                # Any changes you make to it will be overwritten the next time
                # the file is generated.


                from __future__ import print_function, division, absolute_import, unicode_literals
                from grako.parsing import graken, Parser
                from grako.exceptions import *  # noqa


                __version__ = '{version}'

                __all__ = [
                    '{name}Parser',
                    '{name}SemanticParser',
                    '{name}Semantics',
                    'main'
                ]


                class {name}Parser(Parser):
                    def __init__(self, whitespace={whitespace}, **kwargs):
                        super({name}Parser, self).__init__(whitespace=whitespace, **kwargs)

                {rules}

                class {name}Semantics(object):
                {abstract_rules}


                def main(filename, startrule, trace=False, whitespace=None):
                    import json
                    with open(filename) as f:
                        text = f.read()
                    parser = {name}Parser(parseinfo=False)
                    ast = parser.parse(
                        text,
                        startrule,
                        filename=filename,
                        trace=trace,
                        whitespace=whitespace)
                    print('AST:')
                    print(ast)
                    print()
                    print('JSON:')
                    print(json.dumps(ast, indent=2))
                    print()

                if __name__ == '__main__':
                    import argparse
                    import string
                    import sys

                    class ListRules(argparse.Action):
                        def __call__(self, parser, namespace, values, option_string):
                            print('Rules:')
                            for r in {name}Parser.rule_list():
                                print(r)
                            print()
                            sys.exit(0)

                    parser = argparse.ArgumentParser(description="Simple parser for {name}.")
                    parser.add_argument('-l', '--list', action=ListRules, nargs=0,
                                        help="list all rules and exit")
                    parser.add_argument('-t', '--trace', action='store_true',
                                        help="output trace information")
                    parser.add_argument('-w', '--whitespace', type=str, default=string.whitespace,
                                        help="whitespace specification")
                    parser.add_argument('file', metavar="FILE", help="the input file to parse")
                    parser.add_argument('startrule', metavar="STARTRULE",
                                        help="the start rule for parsing")
                    args = parser.parse_args()

                    main(args.file, args.startrule, trace=args.trace, whitespace=args.whitespace)
                    '''
