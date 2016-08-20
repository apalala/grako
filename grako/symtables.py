# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from copy import copy
from collections import OrderedDict as odict

from .util import asjson
from .util import join_lists
from .exceptions import GrakoException
from .buffering import LineIndexEntry
from .collections import OrderedDefaultDict


DEFAULT_SEPARATOR = '.'


def join_symtables(tables):
    def join_namespaces(base, target):
        base = copy(base)
        for symbol in target.symbols:
            name = symbol.name
            if name not in base or base.duplicates:
                base.insert(symbol)
            else:
                join_namespaces(base[name], symbol)
        return base

    if not tables:
        return {}

    result = copy(tables[0])
    for table in tables[1:]:
        result = join_namespaces(table, result)
    return result


class SymbolTableError(GrakoException):
    pass


class EntryDict(OrderedDefaultDict):
    def __init__(self, *args, **kwargs):
        super(EntryDict, self).__init__(list, *args, **kwargs)


class Namespace(object):
    def __init__(self, duplicates=False, separator=DEFAULT_SEPARATOR):
        super(Namespace, self).__init__()
        self._duplicates = duplicates
        self.separator = separator
        self._entries = EntryDict()

    @property
    def duplicates(self):
        return self._duplicates

    @property
    def entries(self):
        return self._entries

    @property
    def symbols(self):
        return join_lists(self._entries.values())

    @property
    def names(self):
        return list(self._entries.keys())

    def all_names(self):
        result = []
        for name, symbols in self.entries.items():
            result.append(name)
            for symbol in symbols:
                result.extend(symbol.all_symbols())
        return result

    def __contains__(self, name):
        return name in self.entries

    def __getitem__(self, name):
        if self.duplicates:
            return self.entries[name]
        elif name in self.entries:
            return self.entries[name][0]
        else:
            raise KeyError(name)

    def insert(self, symbol):
        assert isinstance(symbol.name, str), '"%s" is not a valid symbol name' % str(symbol.name)
        if symbol.name in self._entries and not self.duplicates:
            raise SymbolTableError('Symbol "%s" already in namespace' % str(symbol.name))

        self._entries[symbol.name].append(symbol)

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
        return odict([(name, asjson(symbols)) for name, symbols in self.entries.items()])


class SymbolTable(Namespace):
    def add_reference(self, qualname, from_node):
        symbol = self.lookup(qualname)
        symbol.add_reference(qualname, from_node)




class Symbol(Namespace):
    def __init__(self, name, node, duplicates=False):
        super(Symbol, self).__init__(duplicates=duplicates)
        if not isinstance(name, str):
            raise ValueError('"%s" is not a valid symbol name' % name)
        self.name = name
        self._node = node
        self._parent = None
        self._references = []

    @property
    def node(self):
        return self._node

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
        return odict([
            ('node', type(self.node).__name__),
            ('entries', super(Symbol, self).__json__()),
            ('references', asjson(self._references)),
        ])


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

    def __json__(self):
        return odict([
            ('node', type(self.node).__name__),
            ('name', self.qualname),
            ('symbol', self.symbol.qualname()),
        ])
