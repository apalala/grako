# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime
from collections import OrderedDict as odict

from grako.util import (
    compress_seq,
    indent,
    re,
    safe_name,
)
from grako.model import Node
from grako.exceptions import CodegenError
from grako.codegen.cgbase import ModelRenderer, CodeGenerator


def codegen(model):
    return ObjectModelCodeGenerator().render(model)


class ObjectModelCodeGenerator(CodeGenerator):
    def _find_renderer_class(self, item):
        if not isinstance(item, Node):
            return None

        name = item.__class__.__name__
        renderer = globals().get(name, None)
        if not renderer or not issubclass(renderer, ModelRenderer):
            raise CodegenError('Renderer for %s not found' % name)
        return renderer


class Rule(ModelRenderer):
    def render_fields(self, fields):
        defs = [safe_name(d) for d, l in compress_seq(self.defines())]
        defs = list(sorted(set(defs)))

        kwargs = '\n'.join('%s=None, ' % d for d in defs)
        params = '\n'.join('%s=%s,' % (d, d) for d in defs)
        if params:
            params = '\n*_args_,\n' + params + '\n**_kwargs_\n'
            params = indent(params, 3)
            params = params + '\n' + indent(')', 2)

            kwargs = '\n' + indent(kwargs + '\n**_kwargs_', indent=17, multiplier=1)
        else:
            kwargs = ' **_kwargs_'
            params = '*_args_, **_kwargs_)'

        fields.update(
            class_name=safe_name(self.params[0]),
            _kwargs_=kwargs,
            params=params,
        )

    template = '''
            class {class_name}(ModelBase):
                def __init__(self, *_args_,{_kwargs_}):
                    super({class_name}, self).__init__({params}\
            '''


class Grammar(ModelRenderer):
    @staticmethod
    def object_model_typename(rule):
        if not rule.params:
            return
        if not re.match('(?!\d)\w+', rule.params[0]):
            return
        if not rule.params[0][0].isupper():
            return
        return rule.params[0]

    def render_fields(self, fields):
        model_rules = odict([
            (self.object_model_typename(rule), rule)
            for rule in self.node.rules
        ])
        del model_rules[None]
        model_rules = list(model_rules.values())

        model_class_declarations = [
            self.get_renderer(rule).render() for rule in model_rules
        ]
        model_class_declarations = '\n\n\n'.join(model_class_declarations)

        version = datetime.now().strftime('%Y.%m.%d.%H')

        fields.update(
            model_class_declarations=model_class_declarations,
            version=version,
        )

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

                from grako.model import Node
                from grako.semantics import ModelBuilderSemantics


                __version__ = '{version}'


                class {name}ModelBuilderSemantics(ModelBuilderSemantics):
                    def __init__(self):
                        types = [
                            t for t in globals().values()
                            if type(t) is type and issubclass(t, ModelBase)
                        ]
                        super({name}ModelBuilderSemantics, self).__init__(types=types)


                class ModelBase(Node):
                    pass


                {model_class_declarations}
                '''
