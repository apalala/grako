# -*- coding: utf-8 -*-
"""
Base definitions for models of programs.

** under construction **
"""
from __future__ import print_function, division, absolute_import, unicode_literals

EOLCOL = 50


class Node(object):
    """ Base class for model nodes, in charge of the rendering infrastructure.

        Rendering consists of providing arguments through object attributes
        and the :meth:render_fields method for them to be applied to a
        :class:`string.Template` instance created from the *template* class
        variable.
    """

    inline = True
    template = '{clasname}'

    def __init__(self, ctx, ast=None, parseinfo=None):
        super(Node, self).__init__()
        self._ctx = ctx
        if not parseinfo:
            parseinfo = ast.parseinfo if hasattr(ast, 'parseinfo') else None
        self._parseinfo = parseinfo

        self.clasname = self.__class__.__name__
        self._parent = None
        self._children = []

        self._adopt_children(ast)
        self.__postinit__(ast)

    def __postinit__(self, ast):
        pass

    @property
    def context(self):
        return self.ctx

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return self._children

    @property
    def line(self):
        info = self.line_info
        if info:
            return info.line

    @property
    def ctx(self):
        return self._ctx

    @property
    def parseinfo(self):
        return self._parseinfo

    @property
    def line_info(self):
        if self.parseinfo:
            return self.parseinfo.buffer.line_info(self.parseinfo.pos)

    @property
    def text(self):
        if self.parseinfo:
            text = self.parseinfo.buffer.text
            return text[self.parseinfo.pos:self.parseinfo.endpos]

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit(self, *args, **kwargs)

    def _adopt_children(self, ast):
        if isinstance(ast, Node):
            ast._parent = self
            self._children.append(ast)
        elif isinstance(ast, dict):
            self._adopt_children(list(ast.values()))
        elif isinstance(ast, list):
            for c in ast:
                self._adopt_children(c)


class NodeVisitor(object):
    def _find_visitor(self, obj):
        name = 'visit_' + obj.__class__.__name__
        return getattr(self, name, None)

    def visit(self, obj, *args, **kwargs):
        visitor = self._find_visitor(obj)
        if callable(visitor):
            return visitor(obj, *args, **kwargs)


class DdepthFirstVisitor(object):
    def visit(self, obj, *args, **kwargs):
        # assume obj is a Node
        children = [self.visit(c, *args, **kwargs) for c in obj.children]
        return super(DdepthFirstVisitor, self).visit(obj, children, *args, **kwargs)


class DelegatingVisitor(object):
    def __init__(self, delegate):
        self.delegate = delegate

    def _find_visitor(self, obj):
        name = obj.__class__.__name__
        return getattr(self.delegate, name, None)
