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
        super(AST, self).__init__(*args, **kwargs)

    @property
    def parseinfo(self):
        """ Make the special attribute `_parseinfo` be available
            as a property without an underscore in the name.
            This patch helps with backwards compatibility.
        """
        return self._parseinfo

    def keys(self):
        return self._ordered_keys()

    def values(self):
        values = (self[k] for k in self)
        return values if PY3 else list(values)

    def items(self):
        items = ((k, self[k]) for k in self)
        return items if PY3 else list(items)

    def _ordered_keys(self):
        keys = iter(self)
        return keys if PY3 else list(keys)

    def __iter__(self):
        return (k for k in self._order if k in self)

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
        for key in list_keys or []:
            if key not in self:
                super(AST, self).__setitem__(key, [])
                self._order.append(key)
        for key in keys:
            if key not in self:
                super(AST, self).__setitem__(key, None)
                self._order.append(key)

    def _copy(self):
        haslists = any(isinstance(v, list) for v in self.values())
        if not haslists:
            return AST(self)
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
            for k in self._ordered_keys() if not k.startswith('_')
        }

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, super(AST, self).__repr__())
