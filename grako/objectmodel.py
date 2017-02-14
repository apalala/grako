# -*- coding: utf-8 -*-
# Copyright (C) 2017      by Juancarlo Añez
# Copyright (C) 2012-2016 by Juancarlo Añez and Thomas Bragg
from __future__ import absolute_import, division, print_function, unicode_literals


import collections
import weakref

from grako.util import asjson, asjsons, Mapping
from grako.buffering import Comments
from grako.ast import AST


BASE_CLASS_TOKEN = '::'


class Node(object):
    """ Base class for model nodes
    """

    inline = True

    def __init__(self, ctx=None, ast=None, parseinfo=None, **kwargs):
        super(Node, self).__init__()
        self._ctx = ctx
        self._ast = ast

        if isinstance(ast, AST):
            parseinfo = ast.parseinfo if not parseinfo else None
        self._parseinfo = parseinfo

        attributes = ast or {}
        # asume that kwargs contains node attributes of interest
        if isinstance(attributes, Mapping):
            attributes.update({k: v for k, v in kwargs.items() if v is not None})

        self._parent = None  # will always be a weakref or None
        self._adopt_children(attributes)
        self.__postinit__(attributes)

    def __postinit__(self, ast):
        if isinstance(ast, Mapping):
            for name, value in ast.items():
                while hasattr(self, name):
                    name = name + '_'
                setattr(self, name, value)

    @property
    def ast(self):
        return self._ast

    @property
    def parent(self):
        if self._parent is not None:
            return self._parent()

    @property
    def line(self):
        pi = self._parseinfo
        if pi:
            return pi.line

    @property
    def endline(self):
        pi = self._parseinfo
        if pi:
            return pi.line

    def text_lines(self):
        pi = self._parseinfo
        if pi:
            return pi.buffer.get_lines(pi.line, pi.endline)

    def line_index(self):
        pi = self._parseinfo
        if pi:
            return pi.buffer.line_index(pi.line, pi.endline)

    @property
    def col(self):
        info = self.line_info
        if info:
            return info.col

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
        return Comments([], [])

    def __cn(self, add_child, child_collection, child, seen=None):
        if seen is None:
            seen = set()
        if isinstance(child, Node) and id(child) not in seen:
            add_child(child)
            seen.add(id(child))
        elif isinstance(child, Mapping):
            # ordering for the values in mapping
            for c in child.values():
                self.__cn(add_child, child_collection, c, seen=seen)
        elif isinstance(child, list):
            for c in child:
                self.__cn(add_child, child_collection, c, seen=seen)

    def children_set(self):
        childset = set()

        def cn(child):
            self.__cn(lambda x: childset.add(x), childset, child)

        for k, c in vars(self).items():
            if not k.startswith('_'):
                cn(c)
        return list(childset)

    def children_list(self, vars_sort_key=None):
        child_list = []

        def cn(child):
            self.__cn(lambda x: child_list.append(x), child_list, child)

        for k, c in sorted(vars(self).items(), key=vars_sort_key):
            if not k.startswith('_'):
                cn(c)
        return child_list

    children = children_list

    def asjson(self):
        return asjson(self)

    def _adopt_children(self, node, parent=None):
        if parent is None:
            parent = self
        if isinstance(node, Node):
            node._parent = weakref.ref(parent)
            for c in node.children():
                node._adopt_children(c, parent=node)
        elif isinstance(node, Mapping):
            for c in node.values():
                self._adopt_children(c, parent=parent)
        elif isinstance(node, list):
            for c in node:
                self._adopt_children(c, parent=parent)

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

    def __getstate__(self):
        state = self.__dict__.copy()
        state.update(_parent=self.parent)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if self._parent is not None:
            self._parent = weakref.ref(self._parent)


ParseModel = Node
