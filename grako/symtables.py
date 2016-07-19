# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from collections import OrderedDict as odict

from .util import asjson
from .exceptions import GrakoException


DEFAULT_SEPARATOR = '.'


class SymbolTableError(GrakoException):
    pass


class Namespace():
    def __init__(self, separator=DEFAULT_SEPARATOR):
        super(Namespace, self).__init__()
        self.separator = separator
        self._entries = odict()

    @property
    def entries(self):
        return self._entries

    @property
    def symbols(self):
        return self._entries.values()

    @property
    def names(self):
        return self._entries.keys()

    def all_symbols(self):
        result = []
        for entry in self.entries:
            result.append(entry.name)
            result.extend(entry.all_symbols())

    def __getitem__(self, name):
        return self.entries.get(name)

    def insert(self, symbol):
        assert isinstance(symbol.name, str), '"%s" is not a valid symbol name' % symbol.name
        if symbol.name in self._entries:
            raise SymbolTableError('Symbol "%s" already in namespace' % symbol.name)

        self._entries[symbol.name] = symbol

    def search(self, name):
        result = []
        for symbol in self.symbols:
            result.extend(symbol.search(name))
        return result

    def lookup(self, qualname):
        return self._lookup_drilldown(qualname.split(self.separator))

    def _lookup_drilldown(self, namelist):
        if not namelist:
            return None

        symbol = self.entries.get(namelist[0])
        if symbol:
            return symbol._lookup_drilldown(namelist[1:])

    def filter(self, condition):
        result = []
        for symbol in self.symbols:
            result.extend(symbol.filter(condition))
        return result

    def asjson(self):
        return asjson(self)

    def __json__(self):
        return odict([(entry.name, asjson(entry)) for entry in self.symbols])


class SymbolTable(Namespace):
    pass


class Symbol(Namespace):
    def __init__(self, name, node):
        super(Symbol, self).__init__()
        if not isinstance(name, str):
            raise ValueError('"%s" is not a valid symbol name' % name)
        self.name = name
        self.node = node
        self._parent = None

    @property
    def parent(self):
        return self._parent

    def insert(self, symbol):
        super(Symbol, self).insert(symbol)
        symbol._parent = self

    def qualpath(self):
        if self.parent:
            return self.parent.qualpath() + [self.name]
        return [self.name]

    def qualname(self, sep=DEFAULT_SEPARATOR):
        return sep.join(self.qualpath())

    def _lookup_drilldown(self, namelist):
        if not namelist:
            return self
        return super(Symbol, self)._lookup_drilldown(namelist)

    def filter(self, condition):
        result = super(Symbol, self).filter(condition)
        if condition(self):
            result.insert(0, self)
        return result

    def __json__(self):
        result = odict()

        result['level'] = self.level
        result['node'] = type(self.node).__name__
        result['entries'] = super(Symbol, self).__json__()

        return result
