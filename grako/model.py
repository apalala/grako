# -*- coding: utf-8 -*-
"""
Base definitions for models of programs.

** under construction **
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import collections

from grako.util import asjson, asjsons
from grako.exceptions import SemanticError
from grako.ast import AST

EOLCOL = 50


class Node(object):
    """ Base class for model nodes
    """

    inline = True

    def __init__(self, ctx=None, ast=None, parseinfo=None):
        super(Node, self).__init__()
        self._ctx = ctx
        self._parseinfo = parseinfo
        if isinstance(ast, AST):
            self._parseinfo = ast.parseinfo if not parseinfo else None

        self._parent = None
        self._adopt_children(ast)
        self.__postinit__(ast)

    def __postinit__(self, ast):
        if isinstance(ast, AST):
            for name, value in ast.items():
                if hasattr(self, name):
                    name = name + '_'
                setattr(self, name, value)

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

    @property
    def comments(self):
        if self.parseinfo:
            return self.parseinfo.buffer.comments(self.parseinfo.pos)
        return [], []

    def children(self):
        childl = []

        def cn(child):
            if isinstance(child, Node):
                childl.append(child)
            elif isinstance(child, dict):
                for c in child.values():
                    cn(c)
            elif isinstance(child, list):
                for c in child:
                    cn(c)

        for c in vars(self).values():
            cn(c)
        return childl

    def _adopt_children(self, ast, parent=None):
        if isinstance(ast, Node):
            if isinstance(parent, Node):
                ast._parent = parent
        elif isinstance(ast, dict):
            for c in ast.values():
                self._adopt_children(c, parent=ast)
        elif isinstance(ast, list):
            for c in ast:
                self._adopt_children(c, parent=ast)

    def _pubdict(self):
        return {
            k: v
            for k, v in vars(self).items()
            if not k.startswith('_')
        }

    def __json__(self):
        result = collections.OrderedDict(
            __class__=self.__class__.__name__,
        )
        result.update(self._pubdict())
        return asjson(result)

    def __str__(self):
        return asjsons(self)


class NodeWalker(object):
    def _find_walker(self, node, prefix='walk_'):
        classes = [node.__class__]
        while classes:
            cls = classes.pop()
            name = prefix + cls.__name__
            walker = getattr(self, name, None)
            if callable(walker):
                return walker
            for b in cls.__bases__:
                if b not in classes:
                    classes.append(b)

        return getattr(self, 'walk_default', None)

    def walk(self, node, *args, **kwargs):
        walker = self._find_walker(node)
        if callable(walker):
            return walker(node, *args, **kwargs)


class DepthFirstWalker(NodeWalker):
    def walk(self, node, *args, **kwargs):
        tv = super(DepthFirstWalker, self).walk
        if isinstance(node, Node):
            children = [self.walk(c, *args, **kwargs) for c in node.children()]
            return tv(node, children, *args, **kwargs)
        elif isinstance(node, collections.Iterable):
            return [tv(e, [], *args, **kwargs) for e in node]
        else:
            return tv(node, [], *args, **kwargs)


class ModelBuilderSemantics(object):
    """ Intended as a semantic action for parsing, a ModelBuilderSemantics creates
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
        typename = str(typename)
        if typename in self.nodetypes:
            return self.nodetypes[typename]

        # synthethize a new type
        nodetype = type(typename, (self.baseType,), {})
        self._register_nodetype(nodetype)
        return nodetype

    def _default(self, ast, *args, **kwargs):
        if not args:
            return ast
        name = args[0]
        nodetype = self._get_nodetype(name)
        try:
            return nodetype(ast=ast, ctx=self.ctx)
        except Exception as e:
            raise SemanticError(
                'Could not call constructor for %s: %s'
                % (
                    name,
                    str(e)
                )
            )
