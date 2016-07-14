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

import os
import functools
from collections import defaultdict, Mapping
from copy import copy

from grako.util import indent, trim, ustr, urepr, strtype, compress_seq, chunks
from grako.util import re, RE_FLAGS
from grako.exceptions import FailedRef, GrammarError
from grako.ast import AST
from grako.buffering import Buffer
from grako.contexts import ParseContext
from grako.model import Node


PEP8_LLEN = 72


COMMENTS_RE = r'\(\*((?:.|\n)*?)\*\)'
EOL_COMMENTS_RE = r'#([^\n]*?)$'
PRAGMA_RE = r'^\s*#[a-z]+'


def dot(x, y, k):
    return set([(a + b)[:k] for a in x for b in y])


def pythonize_name(name):
    return ''.join('_' + c.lower() if c.isupper() else c for c in name)


class GrakoBuffer(Buffer):
    def __init__(
            self,
            text,
            filename=None,
            comments_re=None,
            eol_comments_re=None,
            **kwargs):
        super(GrakoBuffer, self).__init__(
            text,
            filename=filename,
            memoize_lookaheads=False,
            comment_recovery=True,
            comments_re=comments_re or COMMENTS_RE,
            eol_comments_re=eol_comments_re or EOL_COMMENTS_RE,
            **kwargs
        )

    def process_block(self, name, lines, index, **kwargs):
        i = 0
        while i < len(lines):
            line = lines[i]
            if re.match(PRAGMA_RE, line):
                directive, arg = line.split('#', 1)[1], ''
                if '::' in directive:
                    directive, arg = directive.split('::')
                directive, arg = directive.strip(), arg.strip()
                i = self.pragma(name, directive, arg, lines, index, i)
            else:
                i += 1
        return lines, index

    def pragma(self, source, name, arg, lines, index, i):
        # we only recognize the 'include' pragama
        if name == 'include':
            filename = arg.strip('\'"')
            return self.include_file(source, filename, lines, index, i, i)
        else:
            return i + 1  # will be treated as a directive by the parser


class GrakoContext(ParseContext):
    def parse(self, text, rule='start', filename=None, parseinfo=True, **kwargs):
        if not isinstance(text, Buffer):
            text = GrakoBuffer(
                text,
                filename=filename,
                **kwargs
            )
        return super(GrakoContext, self).parse(
            text,
            rule,
            filename=filename,
            parseinfo=parseinfo,
            **kwargs
        )


class ModelContext(GrakoContext):
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

    def _missing_rules(self, rules):
        return set()

    def _first(self, k, F):
        return set()

    def _follow(self, k, FL, A):
        return A

    def comments_str(self):
        comments, eol = self.comments
        if not comments:
            return ''

        return '\n'.join(
            '(* %s *)\n' % '\n'.join(c).replace('(*', '').replace('*)', '').strip()
            for c in comments
        )

    def nodecount(self):
        return 1


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


class EOLComment(Comment):
    def __str__(self):
        return '  # %s\n' % self.comment


class EOF(Model):
    def parse(self, ctx):
        ctx._next_token()
        if not ctx.buf.atend():
            ctx._error('Expecting end of text.')

    def __str__(self):
        return '$'


class _Decorator(Model):
    def __init__(self, ast=None, **kwargs):
        if not isinstance(ast, AST):
            ast = AST(exp=ast)
        super(_Decorator, self).__init__(ast)
        assert isinstance(self.exp, Model)

    def parse(self, ctx):
        return self.exp.parse(ctx)

    def defines(self):
        return self.exp.defines()

    def _missing_rules(self, rules):
        return self.exp._missing_rules(rules)

    def _first(self, k, F):
        return self.exp._first(k, F)

    def _follow(self, k, FL, A):
        return self.exp._follow(k, FL, A)

    def nodecount(self):
        return 1 + self.exp.nodecount()

    def __str__(self):
        return ustr(self.exp)


class Group(_Decorator):
    def parse(self, ctx):
        with ctx._group():
            self.exp.parse(ctx)
            return ctx.last_node

    def __str__(self):
        exp = ustr(self.exp)
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


class Constant(Model):
    def __postinit__(self, ast):
        super(Constant, self).__postinit__(ast)
        self.literal = ast

    def parse(self, ctx):
        return self.literal

    def __str__(self):
        return '`%s`' % urepr(self.literal)


class Pattern(Model):
    def __postinit__(self, ast):
        re.compile(ast, RE_FLAGS)
        super(Pattern, self).__postinit__(ast)
        self.pattern = ast

    def parse(self, ctx):
        return ctx._pattern(self.pattern)

    def _first(self, k, F):
        return set([(self.pattern,)])

    def __str__(self):
        pattern = ustr(self.pattern)
        if '/' not in pattern:
            template = '/%s/'
            return template % pattern
        else:
            template = '?/%s/?'
            result = template % pattern
            if result.count('?') % 2:
                result += '?'  # for the VIM syntax
            return result


class Lookahead(_Decorator):
    def parse(self, ctx):
        with ctx._if():
            super(Lookahead, self).parse(ctx)

    def __str__(self):
        return '&' + ustr(self.exp)


class NegativeLookahead(_Decorator):
    def __str__(self):
        return '!' + ustr(self.exp)

    def parse(self, ctx):
        with ctx._ifnot():
            super(NegativeLookahead, self).parse(ctx)


class Sequence(Model):
    def __init__(self, ast, **kwargs):
        assert ast.sequence
        super(Sequence, self).__init__(ast=ast)

    def parse(self, ctx):
        ctx.last_node = [s.parse(ctx) for s in self.sequence]
        return ctx.last_node

    def defines(self):
        return [d for s in self.sequence for d in s.defines()]

    def _missing_rules(self, ruleset):
        return set().union(*[s._missing_rules(ruleset) for s in self.sequence])

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

    def nodecount(self):
        return 1 + sum(s.nodecount() for s in self.sequence)

    def __str__(self):
        comments = self.comments_str()
        seq = [ustr(s) for s in self.sequence]
        single = ' '.join(seq)
        if len(single) <= PEP8_LLEN and len(single.splitlines()) <= 1:
            return comments + single
        else:
            return comments + '\n'.join(seq)


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

            lookahead = ' '.join(ustr(urepr(f[0])) for f in self.lookahead if f)
            if lookahead:
                ctx._error('expecting one of {%s}' % lookahead)
            ctx._error('no available options')

    def defines(self):
        return [d for o in self.options for d in o.defines()]

    def _missing_rules(self, rules):
        return set().union(*[o._missing_rules(rules) for o in self.options])

    def _first(self, k, F):
        result = set()
        for o in self.options:
            result |= o._first(k, F)
        return result

    def _follow(self, k, FL, A):
        for o in self.options:
            o._follow(k, FL, A)
        return A

    def nodecount(self):
        return 1 + sum(o.nodecount() for o in self.options)

    def __str__(self):
        options = [ustr(o) for o in self.options]

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
        sexp = ustr(self.exp)
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


class Join(_Decorator):
    def __init__(self, ast=None, **kwargs):
        super(Join, self).__init__(ast.exp)
        self.sep = ast.sep

    def parse(self, ctx):
        def sep():
            return self.sep.parse(ctx)

        def exp():
            return self.exp.parse(ctx)

        return ctx._positive_closure(exp, prefix=sep)

    def __str__(self):
        ssep = str(self.sep)
        sexp = ustr(self.exp)
        if len(sexp.splitlines()) <= 1:
            return '%s.{%s}' % (ssep, sexp)
        else:
            return '%s.{\n%s\n}' % (ssep, sexp)


class PositiveJoin(Join):
    def __str__(self):
        return super(PositiveJoin, self).__str__() + '+'


class EmptyClosure(Model):
    def parse(self, ctx):
        return ctx._empty_closure()

    def __str__(self):
        return '{}'


class Optional(_Decorator):
    def parse(self, ctx):
        ctx.last_node = None
        with ctx._optional():
            return self.exp.parse(ctx)

    def _first(self, k, F):
        return {()} | self.exp._first(k, F)

    def __str__(self):
        exp = ustr(self.exp)
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
        return '%s:%s' % (self.name, ustr(self.exp))


class NamedList(Named):
    def parse(self, ctx):
        value = self.exp.parse(ctx)
        ctx.ast.setlist(self.name, value)
        return value

    def defines(self):
        return [(self.name, True)] + super(Named, self).defines()

    def __str__(self):
        return '%s+:%s' % (self.name, ustr(self.exp))


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
            ctx._error(self.name, etype=FailedRef)

    def _missing_rules(self, ruleset):
        if self.name not in ruleset:
            return {self.name}
        return set()

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
        assert isinstance(rule, Rule), ustr(rule.name)
        super(RuleInclude, self).__init__(rule.exp)
        self.rule = rule

    def __str__(self):
        return '>%s' % (self.rule.name)


class Rule(_Decorator):
    def __init__(self, ast, name, exp, params, kwparams, decorators=None):
        assert kwparams is None or isinstance(kwparams, Mapping), kwparams
        super(Rule, self).__init__(ast)
        self.name = name
        self.params = params
        self.kwparams = kwparams
        self.decorators = decorators or []
        self._adopt_children([params, kwparams])

        self.is_name = 'name' in self.decorators
        self.base = None

    def parse(self, ctx):
        result = self._parse_rhs(ctx, self.exp)
        if self.is_name:
            ctx._check_name()
        return result

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

    @staticmethod
    def param_repr(p):
        if isinstance(p, (int, float)):
            return ustr(p)
        elif isinstance(p, strtype) and p.isalnum():
            return ustr(p)
        else:
            return urepr(p)

    def __str__(self):
        comments = self.comments_str()
        params = ', '.join(
            self.param_repr(p) for p in self.params
        ) if self.params else ''

        kwparams = ''
        if self.kwparams:
            kwparams = ', '.join(
                '%s=%s' % (k, self.param_repr(v)) for (k, v)
                in self.kwparams.items()
            )

        if params and kwparams:
            params = '(%s, %s)' % (params, kwparams)
        elif kwparams:
                params = '(%s)' % (kwparams)
        elif params:
            if len(self.params) == 1:
                params = '::%s' % params
            else:
                params = '(%s)' % params

        base = ' < %s' % ustr(self.base.name) if self.base else ''

        return trim(self.str_template).format(
            name=self.name,
            base=base,
            params=params,
            exp=indent(str(self.exp)),
            comments=comments,
            is_name='@name\n' if self.is_name else '',
        )

    str_template = '''\
                {is_name}{comments}{name}{base}{params}
                    =
                {exp}
                    ;
                '''


class BasedRule(Rule):
    def __init__(self, ast, name, exp, base, params, kwparams, decorators=None):
        super(BasedRule, self).__init__(
            ast,
            name,
            exp,
            params or base.params,
            kwparams or base.kwparams,
            decorators=decorators
        )
        self.base = base
        ast = AST(sequence=[self.base.exp, self.exp])
        ast._parseinfo = self.base.parseinfo
        self.rhs = Sequence(ast)

    def parse(self, ctx):
        return self._parse_rhs(ctx, self.rhs)

    def defines(self):
        return self.rhs.defines()


class Grammar(Model):
    def __init__(self,
                 name,
                 rules,
                 filename='Unknown',
                 whitespace=None,
                 nameguard=None,
                 left_recursion=None,
                 comments_re=None,
                 eol_comments_re=None,
                 directives=None,
                 keywords=None):
        super(Grammar, self).__init__()
        assert isinstance(rules, list), str(rules)

        self.rules = rules

        directives = directives or {}
        self.directives = directives

        if name is None:
            name = self.directives.get('grammar')
        if name is None:
            name = os.path.splitext(os.path.basename(filename))[0]
        self.name = name

        if whitespace is None:
            whitespace = directives.get('whitespace')
        self.whitespace = whitespace

        if nameguard is None:
            nameguard = directives.get('nameguard')
        self.nameguard = nameguard

        if left_recursion is None:
            left_recursion = directives.get('left_recursion')
        self.left_recursion = left_recursion

        if comments_re is None:
            comments_re = directives.get('comments')
        self.comments_re = comments_re

        if eol_comments_re is None:
            eol_comments_re = directives.get('eol_comments')
        self.eol_comments_re = eol_comments_re

        self.keywords = keywords or set()

        self._adopt_children(rules)
        missing = self._missing_rules({r.name for r in self.rules})
        if missing:
            print('\nunknown rule: '.join([''] + list(sorted(missing))))
            raise GrammarError('Unknown rules, no parser generated.')
        self._calc_lookahead_sets()

    def _missing_rules(self, ruleset):
        return set().union(*[rule._missing_rules(ruleset) for rule in self.rules])

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
              left_recursion=None,
              comments_re=None,
              eol_comments_re=None,
              **kwargs):
        ctx = context or ModelContext(
            self.rules,
            trace=trace,
            keywords=self.keywords,
            **kwargs)

        if whitespace is None:
            whitespace = self.whitespace
        if whitespace:
            whitespace = re.compile(whitespace)

        if left_recursion is None:
            left_recursion = self.left_recursion

        if comments_re is None:
            comments_re = self.comments_re

        if eol_comments_re is None:
            eol_comments_re = self.eol_comments_re

        return ctx.parse(
            text,
            start or self.rules[0].name,
            filename=filename,
            semantics=semantics,
            trace=trace,
            whitespace=whitespace,
            comments_re=comments_re,
            eol_comments_re=eol_comments_re,
            left_recursion=left_recursion,
            **kwargs
        )

    def nodecount(self):
        return 1 + sum(r.nodecount() for r in self.rules)

    def __str__(self):
        regex_directives = {'comments', 'eol_comments', 'whitespace'}
        ustr_directives = {'comments', 'grammar'}
        string_directives = {'namechars'}

        directives = ''
        for directive, value in self.directives.items():
            fmt = dict(
                name=directive,
                frame='/' if directive in regex_directives else '',
                value=(
                    urepr(value) if directive in string_directives
                    else ustr(value) if directive in ustr_directives
                    else value
                ),
            )
            directives += '@@{name} :: {frame}{value}{frame}\n'.format(**fmt)
        if directives:
            directives += '\n'

        keywords = '\n'.join(
            '@@keyword :: ' + ' '.join(urepr(k) for k in c if k is not None)
            for c in chunks(sorted(self.keywords), 8)
        ).strip()
        keywords = '\n\n' + keywords + '\n' if keywords else ''

        rules = (
            '\n\n'.join(ustr(rule)
                        for rule in self.rules)
        ).rstrip() + '\n'
        return directives + keywords + rules
