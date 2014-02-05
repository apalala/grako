# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from grako.model import Node
from grako.rendering import render, Renderer, RenderingFormatter


class DelegatingRenderingFormatter(RenderingFormatter):
    def __init__(self, delegate):
        assert hasattr(delegate, 'render')
        super(DelegatingRenderingFormatter, self).__init__()
        self.delegate = delegate

    #override
    def render(self, item, join='', **fields):
        result = self.delegate.render(item, join=join, **fields)
        if result is None:
            result = super(DelegatingRenderingFormatter).render(item, join=join, **fields)
        return result

    def convert_field(self, value, conversion):
        if isinstance(value, Node):
            return self.render(value)
        else:
            return super(RenderingFormatter, self).convert_field(value, conversion)


class ModelRenderer(Renderer):
    def __init__(self, ctx, node, template=None):
        super(ModelRenderer, self).__init__(template=template)
        self.ctx = ctx
        self.node = node

        self.formatter = ctx.formatter

        for name, value in vars(node).items():
            setattr(self, name, value)

        self.__postinit__()

    def __postinit__(self):
        pass

    def get_renderer(self, item):
        return self.ctx.get_renderer(item)

    def render(self, template=None, **fields):
        fields.update({k: v for k, v in vars(self.node).items() if not k.startswith('_')})
        return super(ModelRenderer, self).render(template=template, **fields)


class CodeGenerator(object):
    def __init__(self):
        self.formatter = DelegatingRenderingFormatter(self)

    def _find_renderer(self, item):
        pass

    def get_renderer(self, item):
        rendererClass = self._find_renderer(item)
        if rendererClass is None:
            return None
        assert issubclass(rendererClass, ModelRenderer)
        try:
            return rendererClass(self, item)
        except Exception as e:
            raise type(e)(str(e), rendererClass.__name__)

    def render(self, item, join='', **fields):
        renderer = self.get_renderer(item)
        if renderer is None:
            return render(item, join=join, **fields)
        return renderer.render(**fields)
