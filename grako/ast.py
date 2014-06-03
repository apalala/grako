# -*- coding: utf-8 -*-
"""
Define the AST class, a direct descendant of dict that's used during parsing
to store the values of named elements of grammar rules.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from .util import strtype, asjson, PY3


class AST(dict):
    def __init__(self, *args, **kwargs):
        super(AST, self).__setattr__('_order', [])
        super(AST, self).__init__()
        self.update(*args, **kwargs)

    @property
    def parseinfo(self):
        """ Make the special attribute `_parseinfo` be available
            as a property without an underscore in the name.
            This patch helps with backwards compatibility.
        """
        return self._parseinfo

    def keys(self):
        keys = self.__iter__()
        return keys if PY3 else list(keys)

    def values(self):
        values = (self[k] for k in self.keys())
        return values if PY3 else list(values)

    def items(self):
        items = ((k, self[k]) for k in self.keys())
        return items if PY3 else list(items)

    def update(self, *args, **kwargs):
        def upairs(d):
            for k, v in d:
                self[k] = v

        for d in args:
            if isinstance(d, dict):
                upairs(d.items())
            else:
                upairs(d)
        upairs(kwargs.items())

    def __iter__(self):
        assert set(self._order) == set(super(AST, self).__iter__())
        order = set(self._order)
        for k in self._order:
            if k in self:
                yield k
        for k in super(AST, self).__iter__():
            if not k in order:
                yield k

    def __setitem__(self, key, value):
        self._add(key, value)

    def __delitem__(self, key):
        super(AST, self).__delitem__(key)
        self._order.remove(key)

    def __setattr__(self, name, value):
        self.__setitem__(name, value)

    def __getattr_(self, key):
        if self.__hasattribute__(key):
            key += '_'
        return super.__getattr__(key)

    def __getattribute__(self, name):
        if isinstance(name, strtype):
            try:
                return super(AST, self).__getattribute__(name)
            except AttributeError:
                pass
        return self.get(name)

    def __hasattribute__(self, name):
        if not isinstance(name, strtype):
            return False
        try:
            super(AST, self).__getattribute__(name)
            return True
        except AttributeError:
            return False

    def _define(self, keys, list_keys=None):
        # WARNING: This is the *only* implementation that does what's intended
        for key in list_keys or []:
            if key not in self:
                self[key] = []

        for key in keys:
            if key not in self:
                super(AST, self).__setitem__(key, None)
                self._order.append(key)

    def _copy(self):
        return AST(
            (k, v[:] if isinstance(v, list) else v)
            for k, v in self.items()
        )


    def _add(self, key, value, force_list=False):
        if self.__hasattribute__(key):
            key += '_'

        previous = self.get(key, None)
        if previous is None:
            if force_list:
                super(AST, self).__setitem__(key, [value])
            else:
                super(AST, self).__setitem__(key, value)
            self._order.append(key)
        elif isinstance(previous, list):
            previous.append(value)
        else:
            super(AST, self).__setitem__(key, [previous, value])
        return self

    def _append(self, key, value):
        return self._add(key, value, force_list=True)

    def __json__(self):
        return {
            asjson(k): asjson(self[k])
            for k in self if not k.startswith('_')
        }

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, super(AST, self).__repr__())
