# -*- coding: utf-8 -*-
"""
Base definitions for models of programs.

** under construction **
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import collections
from .ast import AST

EOLCOL = 50


class Node(object):
    """ Base class for model nodes
    """

    inline = True

    def __init__(self, ctx, ast=None, parseinfo=None):
        super(Node, self).__init__()
        self._ctx = ctx
        self._ast = ast
        if parseinfo is None and isinstance(ast, AST):
            parseinfo = ast._parseinfo
        self._parseinfo = parseinfo

        self._parent = None
        self._children = []
        self._adopt_children(ast)
        self.__postinit__(ast)

    def __postinit__(self, ast):
        if not isinstance(ast, AST):
            self.value = ast
        else:
            for name, value in ast.items():
                if hasattr(self, name):
                    name = '_' + name
                setattr(self, name, value)

    @property
    def ast(self):
        return self._ast

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
    def context(self):
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
        elif isinstance(ast, dict):
            self._adopt_children(list(ast.values()))
        elif isinstance(ast, list):
            for c in ast:
                self._adopt_children(c)

    def __str__(self):
        return str({k: str(v) for k, v in vars(self).items()
                        if not k.startswith('_')
                    }
                   )


class NodeTraverser(object):
    def _find_traverser(self, node):
        classes = [node.__class__]
        while classes:
            cls = classes.pop()
            name = '_traverse_' + cls.__name__
            traverser = getattr(self, name, None)
            if callable(traverser):
                return traverser
            for b in cls.__bases__:
                if not b in classes:
                    classes.append(b)

        return getattr(self, '_traverse_default', None)

    def traverse(self, node, *args, **kwargs):
        traverser = self._find_traverser(node)
        if callable(traverser):
            return traverser(node, *args, **kwargs)


class DepthFirstTraverser(NodeTraverser):
    def traverse(self, node, *args, **kwargs):
        strv = super(DepthFirstTraverser, self).traverse
        if isinstance(node, Node):
            children = [self.traverse(c, *args, **kwargs) for c in node.children]
            return strv(node, children, *args, **kwargs)
        elif isinstance(node, collections.Iterable):
            return [strv(e) for e in node]
        else:
            return strv(node)


class ModelBuilder(object):
    """ Intended as a semantic action for parsing, a ModelBuilder creates
        nodes using the class name given as first parameter to a grammar
        rule, and synthesizes the class/type if it's not known.
    """
    def __init__(self, context=None, baseType=Node, types=None):
        self.ctx = context
        self.baseType = baseType

        self.nodetypes = dict()

        for t in types or ():
            self._register_nodetype(t)

    def _register_nodetype(self, nodetype):
        self.nodetypes[nodetype.__name__] = nodetype

    def _get_nodetype(self, typename):
        if typename in self.nodetypes:
            return self.nodetypes[typename]
        # create a new type
        nodetype = type(typename, (self.baseType,), {})
        self._register_nodetype(nodetype)
        return nodetype

    def _default(self, ast, *args, **kwargs):
        if not args:
            return ast
        nodetype = self._get_nodetype(args[0])
        node = nodetype(self.ctx, ast=ast)
        return node
