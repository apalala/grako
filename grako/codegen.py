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
    def render(self, item):
        result = self.delegate.render(item)
        if result is None:
            result = super(DelegatingRenderingFormatter).render(item)
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

        # FIXME: Could copy node fields to self right here
        # to allow simpler (copied) render_fields methods

    def render(self, template=None, **fields):
        fields.update({k: v for k, v in vars(self.node).items() if not k.startswith('_')})
        return super(ModelRenderer, self).render(template=template, **fields)


class CodeGenerator(object):
    def __init__(self):
        self.formatter = DelegatingRenderingFormatter(self)

    def _find_renderer(self, item):
        pass

    def render(self, item):
        rendererClass = self._find_renderer(item)
        if rendererClass is None:
            return render(item)
        assert issubclass(rendererClass, ModelRenderer)
        renderer = rendererClass(self, item)
        return renderer.render()
