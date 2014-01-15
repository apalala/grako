# -*- coding: utf-8 -*-
"""
Base definitions for models of programs.

** under construction **
"""
from __future__ import print_function, division, absolute_import, unicode_literals
from ..rendering import Renderer
from ..ast import AST

EOLCOL = 50


class Node(Renderer):
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
            parseinfo = ast.parseinfo if isinstance(ast, AST) else None
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

    def _adopt_children(self, ast):
        if isinstance(ast, Node):
            ast._parent = self
            self._children.append(ast)
        elif isinstance(ast, AST):
            self._adopt_children(ast.values())
        elif isinstance(ast, list):
            for c in ast:
                self._adopt_children(c)

    def __str__(self):
        return self.render()

    def __repr__(self):
        return str(self)
