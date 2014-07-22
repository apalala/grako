# -*- coding: utf-8 -*-
"""
Python code generation for models defined with grako.model
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import keyword

from grako.util import (
    indent,
    trim,
    timestamp,
    urepr,
    ustr,
    compress_seq
)
from grako.exceptions import CodegenError
from grako.model import Node
from grako.codegen.cgbase import ModelRenderer, CodeGenerator


class PythonCodeGenerator(CodeGenerator):
    def _find_renderer_class(self, item):
        if not isinstance(item, Node):
            return None

        name = item.__class__.__name__
        renderer = globals().get(name, None)
        if not renderer or not issubclass(renderer, Base):
            raise CodegenError('Renderer for %s not found' % name)
        return renderer


def safe_name(name):
    if keyword.iskeyword(name):
        return name + '_'
    return name


def codegen(model):
    return PythonCodeGenerator().render(model)


class Base(ModelRenderer):
    def defines(self):
        return []


class Void(Base):
    template = 'pass'


class Fail(Base):
    template = 'self._fail()'


class Comment(Base):
    def render_fields(self, fields):
        lines = '\n'.join(
            '# %s' % ustr(c) for c in self.node.comment.splitlines()
        )
        fields.update(lines=lines)

    template = '\n{lines}\n'


class EOLComment(Comment):
    pass


class EOF(Base):
    template = 'self._check_eof()'


class _Decorator(Base):
    def defines(self):
        return self.get_renderer(self.node.exp).defines()

    template = '{exp}'


class Group(_Decorator):
    template = '''\
                with self._group():
                {exp:1::}\
                '''


class Token(Base):
    def render_fields(self, fields):
        fields.update(token=urepr(self.node.token))

    template = "self._token({token})"


class Pattern(Base):
    def render_fields(self, fields):
        raw_repr = 'r' + urepr(self.node.pattern).replace("\\\\", '\\')
        fields.update(pattern=raw_repr)

    template = 'self._pattern({pattern})'


class Lookahead(_Decorator):
    template = '''\
                with self._if():
                {exp:1::}\
                '''


class NegativeLookahead(_Decorator):
    template = '''\
                with self._ifnot():
                {exp:1::}\
                '''


class Sequence(Base):
    def defines(self):
        return [d for s in self.node.sequence for d in s.defines()]

    def render_fields(self, fields):
        fields.update(seq='\n'.join(self.rend(s) for s in self.node.sequence))

    template = '''
                {seq}\
                '''


class Choice(Base):
    def defines(self):
        return [d for o in self.node.options for d in o.defines()]

    def render_fields(self, fields):
        template = trim(self.option_template)
        options = [
            template.format(
                option=indent(self.rend(o))) for o in self.node.options
        ]
        options = '\n'.join(o for o in options)
        firstset = ' '.join(f[0] for f in sorted(self.node.firstset) if f)
        if firstset:
            error = 'expecting one of: ' + firstset
        else:
            error = 'no available options'
        fields.update(n=self.counter(),
                      options=indent(options),
                      error=urepr(error)
                      )

    def render(self, **fields):
        if len(self.node.options) == 1:
            return self.rend(self.options[0], **fields)
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
    def render_fields(self, fields):
        fields.update(n=self.counter())

    def render(self, **fields):
        if {()} in self.node.exp.firstset:
            raise CodegenError('may repeat empty sequence')
        return '\n' + super(Closure, self).render(**fields)

    template = '''\
                def block{n}():
                {exp:1::}
                self._closure(block{n})\
                '''


class PositiveClosure(Closure):
    def render_fields(self, fields):
        fields.update(n=self.counter())

    template = '''
                def block{n}():
                {exp:1::}
                self._positive_closure(block{n})
                '''


class Optional(_Decorator):
    template = '''\
                with self._optional():
                {exp:1::}\
                '''


class Cut(Base):
    template = 'self._cut()'


class Named(_Decorator):
    def defines(self):
        return [(self.node.name, False)] + super(Named, self).defines()

    def __str__(self):
        return '%s:%s' % (self.name, self.rend(self.exp))

    def render_fields(self, fields):
        fields.update(n=self.counter(),
                      name=safe_name(self.node.name)
                      )

    template = '''
                {exp}
                self.ast['{name}'] = self.last_node\
                '''


class NamedList(Named):
    def defines(self):
        return [(self.name, True)] + super(Named, self).defines()

    template = '''
                {exp}
                self.ast.setlist('{name}', self.last_node)\
                '''


class Override(Named):
    def defines(self):
        return []


class OverrideList(NamedList):
    def defines(self):
        return []


class Special(Base):
    pass


class RuleRef(Base):
    template = "self._{name}_()"


class RuleInclude(_Decorator):
    def render_fields(self, fields):
        super(RuleInclude, self).render_fields(fields)
        fields.update(exp=self.rend(self.node.rule.exp))

    template = '''
                {exp}
                '''


class Rule(_Decorator):
    @staticmethod
    def param_repr(p):
        if isinstance(p, (int, float)):
            return ustr(p)
        else:
            return urepr(p)

    def render_fields(self, fields):
        self.reset_counter()

        params = kwparams = ''
        if self.node.params:
            params = ', '.join(
                self.param_repr(self.rend(p))
                for p in self.node.params
            )
        if self.node.kwparams:
            kwparams = ', '.join(
                '%s=%s'
                %
                (k, self.param_repr(self.rend(v)))
                for k, v in self.kwparams.items()
            )

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


class BasedRule(Rule):
    def defines(self):
        return self.rhs.defines()

    def render_fields(self, fields):
        super(BasedRule, self).render_fields(fields)
        fields.update(exp=self.rhs)


class Grammar(Base):
    def render_fields(self, fields):
        abstract_template = trim(self.abstract_rule_template)
        abstract_rules = [
            abstract_template.format(name=safe_name(rule.name))
            for rule in self.node.rules
        ]
        abstract_rules = indent('\n'.join(abstract_rules))

        if self.node.whitespace is None:
            whitespace = 'None'
        else:
            whitespace = urepr(self.node.whitespace)

        if self.node.nameguard is None:
            nameguard = 'None'
        else:
            nameguard = urepr(self.node.nameguard)

        rules = '\n'.join([
            self.get_renderer(rule).render() for rule in self.node.rules
        ])

        version = str(tuple(int(n) for n in str(timestamp()).split('.')))

        fields.update(rules=indent(rules),
                      abstract_rules=abstract_rules,
                      version=version,
                      whitespace=whitespace,
                      nameguard=nameguard
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


                __version__ = {version}

                __all__ = [
                    '{name}Parser',
                    '{name}Semantics',
                    'main'
                ]


                class {name}Parser(Parser):
                    def __init__(self, whitespace={whitespace}, nameguard={nameguard}, **kwargs):
                        super({name}Parser, self).__init__(
                            whitespace=whitespace,
                            nameguard=nameguard,
                            **kwargs
                        )

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

                    main(
                        args.file,
                        args.startrule,
                        trace=args.trace,
                        whitespace=args.whitespace
                    )
                    '''
