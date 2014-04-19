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
from __future__ import print_function, division, absolute_import, unicode_literals
import sys
import re
from collections import defaultdict
from copy import copy
import time
from .util import indent, trim
from .rendering import Renderer, render
from .model import Node
from .contexts import ParseContext, safe_name
from .exceptions import (FailedParse,
                         FailedToken,
                         FailedPattern,
                         FailedRef,
                         FailedCut,
                         FailedSemantics,
                         GrammarError)


def check(result):
    assert isinstance(result, _Model), str(result)


def dot(x, y, k):
    return set([(a + b)[:k] for a in x for b in y])


def urepr(obj):
    return repr(obj).lstrip('u')


def decode(s):
    return s.encode().decode('unicode-escape')


def udrepr(s):
    return urepr(decode(s))


class ModelContext(ParseContext):
    def __init__(self, rules, semantics=None, trace=False, **kwargs):
        super(ModelContext, self).__init__(trace=trace,
                                           **kwargs)
        self.rules = {rule.name: rule for rule in rules}

    @property
    def pos(self):
        return self._buffer.pos

    @property
    def buf(self):
        return self._buffer

    def _find_rule(self, name):
        return self.rules[name]


class _Model(Renderer, Node):
    def __init__(self):
        super(_Model, self).__init__()
        self._first_set = None

    def parse(self, ctx):
        return None

    @property
    def firstset(self, k=1):
        if self._first_set is None:
            self._first_set = self._first(k, {})
        return self._first_set

    def _validate(self, rules):
        return True

    def _first(self, k, F):
        return set()


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
            raise FailedParse(ctx.buf, 'Expecting end of text.')

    def __str__(self):
        return '$'

    template = 'self._check_eof()'


class _Decorator(_Model):
    def __init__(self, exp):
        assert isinstance(exp, _Model), str(exp)
        super(_Decorator, self).__init__()
        self.exp = exp

    def parse(self, ctx):
        return self.exp.parse(ctx)

    def _validate(self, rules):
        return self.exp._validate(rules)

    def _first(self, k, F):
        return self.exp._first(k, F)

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
        template = '(%s)'
        if isinstance(self.exp, Group):
            exp = str(exp.exp)
        if isinstance(exp, Choice):
            template = '\n' + trim(self.str_template)
        return template % exp

    template = '''\
                with self._group():
                {exp:1::}\
                '''

    str_template = '''
            (
            %s
            )
            '''


class Token(_Model):
    def __init__(self, token):
        super(Token, self).__init__()
        self.token = token
        if not self.token:
            raise GrammarError('invalid token %s' % self.token)

    def parse(self, ctx):
        ctx._next_token()
        token = ctx.buf.match(self.token)
        if token is None:
            raise FailedToken(ctx.buf, self.token)

        ctx._trace_match(self.token, None)
        ctx._add_cst_node(token)
        ctx.last_node = token
        return token

    def _first(self, k, F):
        return set([(self.token,)])

    def __str__(self):
        if "'" in self.token:
            if '"' in self.token:
                return "'%s'" % self.token.encode('string-escape')
            else:
                return '"%s"' % self.token
        return "'%s'" % self.token

    def render_fields(self, fields):
        #fields.update(token=urepr(self.token))
        fields.update(token=udrepr(self.token))

    template = "self._token({token})"


class Pattern(_Model):
    def __init__(self, pattern):
        super(Pattern, self).__init__()
        self.pattern = pattern
        self._re = re.compile(pattern)

    def parse(self, ctx):
        token = ctx.buf.matchre(self._re)
        if token is None:
            raise FailedPattern(ctx.buf, self.pattern)
        ctx._trace_match(token, self.pattern)
        ctx._add_cst_node(token)
        ctx.last_node = token
        return token

    def _first(self, k, F):
        return set([(self.pattern,)])

    def __str__(self):
        return '?/%s/?' % self.pattern

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
        for s in self.sequence:
            assert isinstance(s, _Model), str(s)

    def parse(self, ctx):
        result = []
        for s in self.sequence:
            tree = s.parse(ctx)
            if tree is not None:
                result.append(tree)
        ctx.last_node = result
        return result

    def _validate(self, rules):
        return all(s._validate(rules) for s in self.sequence)

    def _first(self, k, F):
        result = {()}
        for s in self.sequence:
            result = dot(result, s._first(k, F), k)
        return result

    def __str__(self):
        return ' '.join(str(s).strip() for s in self.sequence)

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
        for o in self.options:
            assert isinstance(o, _Model), str(o)

    def parse(self, ctx):
        with ctx._choice():
            for o in self.options:
                with ctx._option():
                    node = o.parse(ctx)
                    ctx.last_node = node
                    return node

            firstset = ' '.join(str(urepr(f[0])) for f in self.firstset if f)
            if firstset:
                raise FailedParse(ctx.buf, 'expecting one of {%s}' % firstset)
            raise FailedParse(ctx.buf, 'no available options')

    def _validate(self, rules):
        return all(o._validate(rules) for o in self.options)

    def _first(self, k, F):
        result = set()
        for o in self.options:
            result |= o._first(k, F)
        return result

    def __str__(self):
        return '  ' + '\n| '.join(str(o).strip() for o in self.options)

    def render_fields(self, fields):
        template = trim(self.option_template)
        options = [template.format(option=indent(render(o))) for o in self.options]
        options = '\n'.join(o for o in options)
        firstset = ' '.join(decode(f[0]) for f in self.firstset if f)
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
        exp = self.exp
        template = '{{{exp}}}'
        if isinstance(exp, Group):
            exp = exp.exp
        if isinstance(exp, Choice):
            template = trim(self.str_template)
        return template.format(exp=str(exp))

    def render_fields(self, fields):
        fields.update(n=self.counter())

    def render(self, **fields):
        if {()} in self.exp.firstset:
            raise GrammarError('may repeat empty sequence')
        return super(Closure, self).render(**fields)

    template = '''

                def block{n}():
                {exp:1::}
                self._closure(block{n})\
                '''

    str_template = '''
            {{
            {exp}
            }}
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
            {
            %s
            }
            '''


class Cut(_Model):
    def parse(self, ctx):
        ctx._cut()
        return None

    def _first(self, k, F):
        return {('>>',)}

    def __str__(self):
        return '>>'

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

    def __str__(self):
        return '%s+:%s' % (self.name, str(self.exp))

    template = '''
                {exp}
                self.ast.add_list('{name}', self.last_node)\
                '''


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
            return rule.parse(ctx)
        except KeyError:
            raise FailedRef(ctx.buf, self.name)

    def _validate(self, rules):
        if self.name not in rules:
            print("Reference to unknown rule '%s'." % self.name, file=sys.stderr)
            return False
        return True

    def _first(self, k, F):
        self._first_set = F.get(self.name, set())
        return self._first_set

    def __str__(self):
        return self.name

    template = "self._{name}_()"


class Rule(Named):
    def __init__(self, name, exp, ast_name=None):
        super(Rule, self).__init__(name, exp)
        self.ast_name = ast_name

    def parse(self, ctx):
        return ctx._call(self.exp.parse, self.name)

    def _call_semantics(self, ctx, name, node):
        semantic_rule = ctx._find_semantic_rule(name)
        if semantic_rule:
            try:
                node = semantic_rule(node)
            except FailedSemantics as e:
                ctx._error(str(e), FailedParse)
        return node

    def _first(self, k, F):
        if self._first_set:
            return self._first_set
        return self.exp._first(k, F)

    def __str__(self):
        return trim(self.str_template) % (self.name, indent(str(self.exp)))

    def render_fields(self, fields):
        self.reset_counter()
        if self.ast_name:
            ast_name_clause = '\nself.ast = AST(%s=self.ast)\n' % self.ast_name_
        else:
            ast_name_clause = ''
        fields.update(ast_name_clause=ast_name_clause)

    template = '''
                @rule_def
                def _{name}_(self):
                {exp:1::}{ast_name_clause}

                '''
    str_template = '''\
                %s
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
        self.nameguard = urepr(nameguard)
        self.rules = rules
        if not self._validate({r.name for r in self.rules}):
            raise GrammarError('Unknown rules, no parser generated.')
        self._first_sets = self._calc_first_sets()

    def _validate(self, ruleset):
        return all(rule._validate(ruleset) for rule in self.rules)

    @property
    def first_sets(self):
        return self._first_sets

    def _calc_first_sets(self, k=1):
        F = defaultdict(set)
        F1 = None
        while F1 != F:
            F1 = copy(F)
            for rule in self.rules:
                F[rule.name] |= rule._first(k, F)

        for rule in self.rules:
            rule._first_set = F[rule.name]
        return F

    def parse(self, text,
                    start=None,
                    filename=None,
                    semantics=None,
                    trace=False,
                    context=None,
                    **kwargs):
        ctx = context
        if ctx is None:
            ctx = ModelContext(self.rules, trace=trace, **kwargs)
        ctx._reset(text=text, semantics=semantics, **kwargs)
        start_rule = ctx._find_rule(start) if start else self.rules[0]
        try:
            with ctx._choice():
                return start_rule.parse(ctx)
        except FailedCut as e:
            raise e.nested
        finally:
            ctx._clear_cache()

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
                      version=time.strftime('%y.%j.%H.%M.%S', time.gmtime())
                      )

    abstract_rule_template = '''
            def {name}(self, ast):
                return ast
            '''

    template = '''\
                #!/usr/bin/env python
                # -*- coding: utf-8 -*-
                #
                # CAVEAT UTILITOR
                # This file was automatically generated by Grako.
                #    https://bitbucket.org/apalala/grako/
                # Any changes you make to it will be overwritten the
                # next time the file is generated.
                #

                from __future__ import print_function, division, absolute_import, unicode_literals
                from grako.parsing import * # noqa
                from grako.exceptions import * # noqa


                __version__ = '{version}'


                class {name}Parser(Parser):
                    def __init__(self, whitespace={whitespace}, **kwargs):
                        super({name}Parser, self).__init__(whitespace=whitespace, **kwargs)

                {rules}

                class {name}SemanticParser(CheckSemanticsMixin, {name}Parser):
                    pass


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

                    main(args.file, args.startrule, trace=args.trace, whitespace=args.whitespace) '''
