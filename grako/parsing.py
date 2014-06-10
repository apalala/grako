# -*- coding: utf-8 -*-
"""
Parser is the base class for generated parsers and for the bootstrap parser
(the parser that parses Grako grammars).

Parser does memoization at the rule invocation level, and provides the
decorators, context managers, and iterators needed to make generated parsers
simple.

Parser is also in charge of dealing with comments, with the help of
the .buffering module.

Parser.parse() will take the text to parse directly, or an instance of the
.buffeing.Buffer class.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import functools

from grako.exceptions import FailedRef
from grako.contexts import ParseContext


class Parser(ParseContext):

    @classmethod
    def rule_list(cls):
        import inspect
        methods = inspect.getmembers(cls, predicate=inspect.ismethod)
        result = []
        for m in methods:
            name = m[0]
            if name[0] != '_' or name[-1] != '_':
                continue
            if not name[1:-1].isalnum():
                continue
            result.append(name[1:-1])
        return result

    def result(self):
        return self.ast

    def _find_rule(self, name):
        rule = getattr(self, '_' + name + '_', None)
        if isinstance(rule, type(self._find_rule)):
            return rule
        rule = getattr(self, name, None)
        if isinstance(rule, type(self._find_rule)):
            return rule
        self._error(name, etype=FailedRef)

    def _eof(self):
        return self._buffer.atend()

    def _eol(self):
        return self._buffer.ateol()

    def _check_eof(self):
        self._next_token()
        if not self._buffer.atend():
            self._error('Expecting end of text.')


# decorator for rule implementation methods
def graken(*params, **kwparams):
    def decorator(rule):
        @functools.wraps(rule)
        def wrapper(self, *args, **kwargs):
            name = rule.__name__.strip('_')
            return self._call(rule, name, *params, **kwparams)
        return wrapper
    return decorator
