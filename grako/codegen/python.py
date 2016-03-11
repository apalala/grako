# -*- coding: utf-8 -*-
"""
Python code generation for models defined with grako.model
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from grako.util import (
    indent,
    safe_name,
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


class Constant(Base):
    def render_fields(self, fields):
        fields.update(literal=urepr(self.node.literal))

    template = "self._constant({literal})"


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
    template = '''
                def block{n}():
                {exp:1::}
                self._positive_closure(block{n})\
                '''


class Join(_Decorator):
    def render_fields(self, fields):
        fields.update(n=self.counter())

    def render(self, **fields):
        if {()} in self.node.exp.firstset:
            raise CodegenError('may repeat empty sequence')
        return '\n' + super(Join, self).render(**fields)

    template = '''\
                def sep{n}():
                {sep:1::}

                def block{n}():
                {exp:1::}
                self._positive_closure(block{n}, prefix=sep{n})\
                '''


class PositiveJoin(Join):
    template = '''\
                def sep{n}():
                {sep:1::}

                def block{n}():
                {exp:1::}
                self._positive_closure(block{n}, prefix=lambda: {sep})\
                '''


class EmptyClosure(Base):
    template = 'self._empty_closure()'


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
                self.name_last_node('{name}')\
                '''


class NamedList(Named):
    def defines(self):
        return [(self.name, True)] + super(Named, self).defines()

    template = '''
                {exp}
                self.add_last_node_to_name('{name}')\
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
        sdefs = [safe_name(d) for d, l in defines if not l]
        ldefs = [safe_name(d) for d, l in defines if l]
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
        fields.update(
            check_name='\n    self._check_name()' if self.is_name else '',
        )

    template = '''
                @graken({params})
                def _{name}_(self):
                {exp:1::}{check_name}{defines}
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

        if self.node.whitespace is not None:
            whitespace = urepr(self.node.whitespace)
        elif self.node.directives.get('whitespace') is not None:
            whitespace = 're.compile({0}, RE_FLAGS | re.DOTALL)'.format(urepr(self.node.directives.get('whitespace')))
        else:
            whitespace = 'None'

        if self.node.nameguard is not None:
            nameguard = urepr(self.node.nameguard)
        elif self.node.directives.get('nameguard') is not None:
            nameguard = self.node.directives.get('nameguard')
        else:
            nameguard = 'None'

        comments_re = urepr(self.node.directives.get('comments'))
        eol_comments_re = urepr(self.node.directives.get('eol_comments'))
        ignorecase = self.node.directives.get('ignorecase', 'None')
        left_recursion = self.node.directives.get('left_recursion', True)

        rules = '\n'.join([
            self.get_renderer(rule).render() for rule in self.node.rules
        ])

        version = str(tuple(int(n) for n in str(timestamp()).split('.')))

        keywords = '\n'.join("    %s," % urepr(k) for k in sorted(self.keywords))
        if keywords:
            keywords = '\n%s\n' % keywords

        fields.update(rules=indent(rules),
                      abstract_rules=abstract_rules,
                      version=version,
                      whitespace=whitespace,
                      nameguard=nameguard,
                      ignorecase=ignorecase,
                      comments_re=comments_re,
                      eol_comments_re=eol_comments_re,
                      left_recursion=left_recursion,
                      keywords=keywords,
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
                from grako.util import re, RE_FLAGS, generic_main  # noqa


                __version__ = {version}

                __all__ = [
                    '{name}Parser',
                    '{name}Semantics',
                    'main'
                ]

                KEYWORDS = set([{keywords}])


                class {name}Parser(Parser):
                    def __init__(self,
                                 whitespace={whitespace},
                                 nameguard={nameguard},
                                 comments_re={comments_re},
                                 eol_comments_re={eol_comments_re},
                                 ignorecase={ignorecase},
                                 left_recursion={left_recursion},
                                 keywords=KEYWORDS,
                                 **kwargs):
                        super({name}Parser, self).__init__(
                            whitespace=whitespace,
                            nameguard=nameguard,
                            comments_re=comments_re,
                            eol_comments_re=eol_comments_re,
                            ignorecase=ignorecase,
                            left_recursion=left_recursion,
                            **kwargs
                        )

                {rules}


                class {name}Semantics(object):
                {abstract_rules}


                def main(
                        filename,
                        startrule,
                        trace=False,
                        whitespace={whitespace},
                        nameguard={nameguard},
                        comments_re={comments_re},
                        eol_comments_re={eol_comments_re},
                        ignorecase={ignorecase},
                        left_recursion={left_recursion},
                        **kwargs):

                    with open(filename) as f:
                        text = f.read()
                    parser = {name}Parser(parseinfo=False)
                    ast = parser.parse(
                        text,
                        startrule,
                        filename=filename,
                        trace=trace,
                        whitespace=whitespace,
                        nameguard=nameguard,
                        ignorecase=ignorecase,
                        **kwargs)
                    return ast

                if __name__ == '__main__':
                    import json
                    ast = generic_main(main, {name}Parser, name='{name}')
                    print('AST:')
                    print(ast)
                    print()
                    print('JSON:')
                    print(json.dumps(ast, indent=2))
                    print()
                '''
