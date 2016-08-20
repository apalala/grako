# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import copy
from collections import OrderedDict, Callable


# Source: http://stackoverflow.com/a/6190500/562769
class OrderedDefaultDict(OrderedDict):
    def __init__(self, default_factory=None, *args, **kwargs):
        if not isinstance(default_factory, (Callable, type(None))):
            raise TypeError('first argument must be callable or None')

        super(OrderedDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return super(OrderedDict, self).__getitem__(key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        return type(self)(self.default_factory, copy.deepcopy(self.items()))

    def __repr__(self):
        return 'OrderedDefaultDict(%s, %s)' % (
            self.default_factory,
            OrderedDict.__repr__(self)
        )
