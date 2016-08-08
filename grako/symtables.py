# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from collections import OrderedDict as odict

from .util import asjson
from .exceptions import GrakoException
from .buffering import LineIndexEntry


DEFAULT_SEPARATOR = '.'


class SymbolTableError(GrakoException):
    pass


class Namespace(object):
    def __init__(self, separator=DEFAULT_SEPARATOR):
        super(Namespace, self).__init__()
        self.separator = separator
        self._entries = odict()

    @property
    def entries(self):
        return self._entries

    @property
    def symbols(self):
        return list(self._entries.values())

    @property
    def names(self):
        return list(self._entries.keys())

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

        for symbol in self.symbols:
            result = symbol._lookup_drilldown(namelist)
            if result:
                return result

    def filter(self, condition):
        return sum((symbol.filter(condition) for symbol in self.symbols), [])

    def filter_first(self, condition):
        for symbol in self.symbols:
            result = symbol.filter_first(condition)
            if result:
                return result

    def all(self):
        return self.filter(lambda: True)

    def asjson(self):
        return asjson(self)

    def __json__(self):
        return odict([(entry.name, asjson(entry)) for entry in self.symbols])


class SymbolTable(Namespace):
    def add_reference(self, qualname, from_node):
        symbol = self.lookup(qualname)
        symbol.add_reference(qualname, from_node)


class Symbol(Namespace):
    def __init__(self, name, node):
        super(Symbol, self).__init__()
        if not isinstance(name, str):
            raise ValueError('"%s" is not a valid symbol name' % name)
        self.name = name
        self.node = node
        self._parent = None
        self._references = []

    @property
    def line(self):
        return self.node.line

    @property
    def endline(self):
        return self.node.endline

    @property
    def parent(self):
        return self._parent

    @property
    def references(self):
        return self._references

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
        if [self.name] == namelist:
            return self
        elif self.name == namelist[0]:
            return super(Symbol, self)._lookup_drilldown(namelist[1:])
        return super(Symbol, self)._lookup_drilldown(namelist)

    def filter(self, condition):
        this_case = [self] if condition(self) else []
        return this_case + super(Symbol, self).filter(condition)

    def filter_first(self, condition):
        if condition(self):
            return self
        return super(Symbol, self).filter(condition)

    def add_reference(self, qualname, node):
        reference = SymbolReference(self, qualname, node)
        if reference not in self.references:
            self._references.append(reference)

    def line_index(self, include_entries=False, include_references=False):
        result = set(self.node.line_index())

        if include_references:
            result.update(self.reference_line_index())

        if include_entries:
            for s in self.symbols:
                index = s.line_index(
                    include_entries=include_entries,
                    include_references=include_references,
                )
                result.update(index)
        assert isinstance(result, set)
        assert all(isinstance(i, LineIndexEntry) for i in result)
        return list(sorted(result))

    def reference_line_index(self):
        result = set()
        for r in self.references:
            result.update(r.line_index())
        assert isinstance(result, set)
        assert all(isinstance(i, LineIndexEntry) for i in result)
        return result

    def __json__(self):
        result = odict()

        result['level'] = self.level
        result['node'] = type(self.node).__name__
        result['entries'] = super(Symbol, self).__json__()

        return result


class SymbolReference():
    def __init__(self, symbol, qualname, node):
        super(SymbolReference, self).__init__()
        self.symbol = symbol
        self.qualname = qualname
        self.node = node

    def line_index(self):
        result = set(self.node.line_index())
        assert isinstance(result, set)
        assert all(isinstance(i, LineIndexEntry) for i in result)
        return result

    def __hash__(self):
        return hash(self.symbol) ^ hash(self.node)

    def __eq__(self, other):
        return self.symbol == other.symbol and self.node == other.node
