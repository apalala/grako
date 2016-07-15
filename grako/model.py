# -*- coding: utf-8 -*-
"""
Base definitions for models of programs.

** under construction **
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import collections

from grako.util import asjson, asjsons, Mapping, builtins
from grako.buffering import Comments
from grako.exceptions import SemanticError
from grako.ast import AST

EOLCOL = 50


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
        if isinstance(ast, Mapping):
            attributes.update({k: v for k, v in kwargs.items() if v is not None})

        self._parent = None
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
        return self._parent

    @property
    def line(self):
        info = self.line_info
        if info:
            return info.line

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

    def __cn(self, add_child, child_collection, child):
        if isinstance(child, Node):
            add_child(child)
        elif isinstance(child, Mapping):
            # ordering for the values in mapping
            for c in child.values():
                self.__cn(add_child, child_collection, c)
        elif isinstance(child, list):
            for c in child:
                self.__cn(add_child, child_collection, c)

    def children(self):
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

    def asjson(self):
        return asjson(self)

    def _adopt_children(self, node, parent=None):
        if parent is None:
            parent = self
        if isinstance(node, Node):
            node._parent = parent
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

        self.constructors = dict()

        for t in types or ():
            self._register_constructor(t)

    def _register_constructor(self, constructor):
        self.constructors[constructor.__name__] = constructor

    def _get_constructor(self, typename):
        typename = str(typename)
        if typename in self.constructors:
            return self.constructors[typename]

        constructor = builtins
        for name in typename.split('.'):
            try:
                context = vars(constructor)
            except Exception as e:
                raise SemanticError(
                    'Could not find constructor for %s (%s): %s'
                    % (typename, type(constructor).__name__, str(e))
                )
            if name in context:
                constructor = context[name]
            else:
                constructor = None
                break
        if constructor:
            return constructor

        # synthethize a new type
        constructor = type(typename, (self.baseType,), {})
        self._register_constructor(constructor)
        return constructor

    def _default(self, ast, *args, **kwargs):
        if not args:
            return ast
        name = args[0]
        constructor = self._get_constructor(name)
        try:
            if type(constructor) is type and issubclass(constructor, Node):
                return constructor(*args[1:], ast=ast, ctx=self.ctx, **kwargs)
            else:
                return constructor(ast, *args[1:], **kwargs)
        except Exception as e:
            raise SemanticError(
                'Could not call constructor for %s: %s'
                % (name, str(e))
            )
