# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
import sys
from contextlib import contextmanager
from collections import namedtuple
from keyword import iskeyword
from .ast import AST
from . import buffering
from .exceptions import (FailedParse,
                         FailedCut,
                         FailedLookahead,
                         OptionSucceeded
                         )


__all__ = ['ParseInfo', 'ParseContext']


ParseInfo = namedtuple('ParseInfo', ['buffer', 'rule', 'pos', 'endpos'])


def safe_name(s):
    if iskeyword(s):
        return s + '_'
    return s


def is_list(o):
    return type(o) == list


class Closure(list):
    pass


class ParseContext(object):
    def __init__(self,
                 semantics=None,
                 parseinfo=False,
                 trace=False,
                 encoding='utf-8',
                 comments_re=None,
                 whitespace=None,
                 ignorecase=False,
                 nameguard=True,
                 **kwargs):
        super(ParseContext, self).__init__()

        self._buffer = None
        self.semantics = semantics
        self.encoding = encoding
        self.parseinfo = parseinfo
        self.trace = trace

        self.comments_re = comments_re
        self.whitespace = whitespace
        self.ignorecase = ignorecase
        self.nameguard = nameguard

        self._ast_stack = []
        self._concrete_stack = [None]
        self._rule_stack = []
        self._cut_stack = [False]
        self._memoization_cache = dict()
        self._last_node = None
        self._state = None

    def _reset(self, text=None,
              filename=None,
              semantics=None,
              trace=None,
              comments_re=None,
              whitespace=None,
              ignorecase=None,
              nameguard=None,
              **kwargs):
        if ignorecase is None:
            ignorecase = self.ignorecase
        if nameguard is None:
            nameguard = self.nameguard
        if isinstance(text, buffering.Buffer):
            buffer = text
        else:

            buffer = buffering.Buffer(text,
                                      filename=filename,
                                      comments_re=comments_re or self.comments_re,
                                      whitespace=whitespace or self.whitespace,
                                      ignorecase=ignorecase,
                                      nameguard=nameguard,
                                      **kwargs)
        self._buffer = buffer
        if trace is not None:
            self.trace = trace
        if semantics is not None:
            self.semantics = semantics
        self._ast_stack = []
        self._concrete_stack = [None]
        self._rule_stack = []
        self._cut_stack = [False]
        self._memoization_cache = dict()
        if semantics is not None:
            self.semantics = semantics

    def goto(self, pos):
        self._buffer.goto(pos)

    @property
    def last_node(self):
        return self._last_node

    @last_node.setter
    def last_node(self, value):
        self._last_node = value

    @property
    def _pos(self):
        return self._buffer.pos

    def _goto(self, pos):
        self._buffer.goto(pos)

    def _next_token(self):
        self._buffer.next_token()

    @property
    def ast(self):
        return self._ast_stack[-1]

    @ast.setter
    def ast(self, value):
        self._ast_stack[-1] = value

    def _push_ast(self):
        self._push_cst()
        self._ast_stack.append(AST())

    def _pop_ast(self):
        self._pop_cst()
        return self._ast_stack.pop()

    def _add_ast_node(self, name, node, force_list=False):
        if name is not None:  # and node:
            self.ast.add(name, node, force_list)
        return node

    @property
    def cst(self):
        return self._concrete_stack[-1]

    @cst.setter
    def cst(self, value):
        self._concrete_stack[-1] = value

    def _push_cst(self):
        self._concrete_stack.append(None)

    def _pop_cst(self):
        return self._concrete_stack.pop()

    def _add_cst_node(self, node):
        if node is None:
            return
        previous = self.cst
        if previous is None:
            if is_list(node):
                node = node[:]  # copy it
            self.cst = node
        elif is_list(previous):
            previous.append(node)
        else:
            self.cst = [previous, node]

    def _extend_cst(self, node):
        if node is None:
            return
        previous = self.cst
        if previous is None:
            if isinstance(node, list):
                node = node[:]  # copy it
            self.cst = node
        elif is_list(node):
            if is_list(previous):
                previous.extend(node)
            else:
                self.cst = [previous] + node
        elif is_list(previous):
            previous.append(node)
        else:
            self.cst = [previous, node]

    def _copy_cst(self):
        cst = self.cst
        if cst is None:
            return None
        elif isinstance(cst, list):
            return cst[:]
        else:
            return cst

    def _is_cut_set(self):
        return self._cut_stack[-1]

    def _cut(self):
        self._cut_stack[-1] = True

        # Kota Mizushima et al say that we can throw away
        # memos for previous positions in the buffer under
        # certain circumstances, without affecting the linearity
        # of PEG parsing.
        #   http://goo.gl/VaGpj
        #
        # We adopt the heuristic of always dropping the cache for
        # positions less than the current cut position. It remains to
        # be proven if doing it this way affects linearity. Empirically,
        # it hasn't.
        cutpos = self._pos
        cache = self._memoization_cache
        cutkeys = [(p, n, s) for p, n, s in cache.keys() if p < cutpos]
        for key in cutkeys:
            del cache[key]

    def _push_cut(self):
        self._cut_stack.append(False)

    def _pop_cut(self):
        return self._cut_stack.pop()

    def _rulestack(self):
        stack = '.'.join(self._rule_stack)
        if len(stack) > 60:
            stack = '...' + stack[-60:]
        return stack

    def _find_rule(self, name):
        return None

    def _find_semantic_rule(self, name):
        if self.semantics is None:
            return None
        result = getattr(self.semantics, name, None)
        if result is None or not callable(result):
            return None
        return result

    def _trace(self, msg, *params):
        if self.trace:
            print(unicode(msg % params).encode(self.encoding), file=sys.stderr)

    def _trace_event(self, event):
        if self.trace:
            self._trace('%s \n%s   \n%s \n\t%s \n',
                        event,
                        self._buffer.line_info().filename,
                        self._rulestack(),
                        self._buffer.lookahead()
                        )

    def _trace_match(self, token, name=None):
        if self.trace:
            name = name if name else ''
            self._trace('MATCHED <%s> /%s/\n\t%s', token, name, self._buffer.lookahead())

    def _error(self, item, etype=FailedParse):
        raise etype(self._buffer, item)

    def _fail(self):
        self._error('fail')

    @contextmanager
    def _try(self):
        p = self._pos
        s = self._state
        ast_copy = self.ast.copy()
        self._push_ast()
        self.last_node = None
        try:
            self.ast = ast_copy
            yield None
            ast = self.ast
            cst = self.cst
        except:
            self._goto(p)
            self._state = s
            raise
        finally:
            self._pop_ast()
        self.ast = ast
        self._extend_cst(cst)
        self.last_node = cst

    @contextmanager
    def _option(self):
        self.last_node = None
        self._push_cut()
        try:
            with self._try():
                yield None
            raise OptionSucceeded()
        except FailedCut:
            raise
        except FailedParse as e:
            if self._is_cut_set():
                raise FailedCut(e)
        finally:
            self._pop_cut()

    @contextmanager
    def _choice(self):
        try:
            yield None
        except OptionSucceeded:
            pass
        except FailedCut as e:
            raise e.nested

    @contextmanager
    def _optional(self):
        self.last_node = None
        with self._choice():
            with self._option():
                yield None

    @contextmanager
    def _group(self):
        self._push_cst()
        try:
            yield None
            cst = self.cst
        finally:
            self._pop_cst()
        self._extend_cst(cst)
        self.last_node = cst

    @contextmanager
    def _if(self):
        p = self._pos
        s = self._state
        self._push_ast()
        try:
            yield None
        finally:
            self._goto(p)
            self._state = s
            self._pop_ast()  # simply discard
            self.last_node = None

    @contextmanager
    def _ifnot(self):
        p = self._pos
        s = self._state
        self._push_ast()
        self.last_node = None
        try:
            yield None
        except FailedParse:
            pass
        else:
            self._error('', etype=FailedLookahead)
        finally:
            self._goto(p)
            self._state = s
            self._pop_ast()  # simply discard
            self.last_node = None

    def _repeater(self, f):
        while True:
            self._push_cut()
            try:
                p = self._pos
                with self._try():
                    f()
                if self._pos == p:
                    self._error('empty closure')
            except FailedCut:
                raise
            except FailedParse as e:
                if self._is_cut_set():
                    raise FailedCut(e)
                break
            finally:
                self._pop_cut()

    def _closure(self, block):
        self._push_cst()
        try:
            self.cst = []
            self._repeater(block)
            cst = Closure(self.cst)
        finally:
            self._pop_cst()
        self._add_cst_node(cst)
        self.last_node = cst
        return cst

    def _positive_closure(self, block):
        self._push_cst()
        try:
            self.cst = []
            with self._try():
                block()
            self._repeater(block)
            cst = Closure(self.cst)
        finally:
            self._pop_cst()
        self._add_cst_node(cst)
        self.last_node = cst
        return cst
