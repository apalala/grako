# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
from collections import namedtuple
from contextlib import contextmanager
from keyword import iskeyword

from grako.util import notnone, udecode
from grako.ast import AST
from grako import buffering
from grako.exceptions import (
    FailedCut,
    FailedLookahead,
    FailedParse,
    FailedPattern,
    FailedSemantics,
    FailedToken,
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
                 nameguard=None,
                 memoize_lookaheads=True,
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

        self._ast_stack = [AST()]
        self._concrete_stack = [None]
        self._rule_stack = []
        self._cut_stack = [False]
        self._memoization_cache = dict()
        self._last_node = None
        self._state = None
        self._lookahead = 0
        self._memoize_lookaheads = memoize_lookaheads

    def _clear_cache(self):
        self._memoization_cache = dict()

    def _reset(self,
               text=None,
               filename=None,
               semantics=None,
               trace=None,
               comments_re=None,
               whitespace=None,
               ignorecase=None,
               nameguard=None,
               memoize_lookaheads=None,
               **kwargs):
        if ignorecase is None:
            ignorecase = self.ignorecase
        if nameguard is None:
            nameguard = self.nameguard
        if memoize_lookaheads is not None:
            self._memoize_lookaheads = memoize_lookaheads
        if isinstance(text, buffering.Buffer):
            buffer = text
        else:
            buffer = buffering.Buffer(
                text,
                filename=filename,
                comments_re=comments_re or self.comments_re,
                whitespace=notnone(whitespace, default=self.whitespace),
                ignorecase=ignorecase,
                nameguard=nameguard,
                **kwargs)
        self._buffer = buffer
        if trace is not None:
            self.trace = trace
        if semantics is not None:
            self.semantics = semantics
        self._ast_stack = [AST()]
        self._concrete_stack = [None]
        self._rule_stack = []
        self._cut_stack = [False]
        self._memoization_cache = dict()
        if semantics is not None:
            self.semantics = semantics

    def parse(self,
              text,
              rule_name,
              filename=None,
              semantics=None,
              trace=False,
              whitespace=None,
              **kwargs):
        try:
            self.parseinfo = kwargs.pop('parseinfo', self.parseinfo)
            self._reset(
                text=text,
                filename=filename,
                semantics=semantics,
                trace=trace or self.trace,
                whitespace=whitespace if whitespace is not None else self.whitespace,
                **kwargs
            )
            rule = self._find_rule(rule_name)
            result = rule()
            self.ast[rule_name] = result
            return result
        except FailedCut as e:
            raise e.nested
        finally:
            self._clear_cache()

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
            self.ast._add(name, node, force_list)
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
        cutkeys = [(p, n, s) for p, n, s in cache if p < cutpos]
        for key in cutkeys:
            del cache[key]

    def _push_cut(self):
        self._cut_stack.append(False)

    def _pop_cut(self):
        return self._cut_stack.pop()

    def _enter_lookahead(self):
        self._lookahead += 1

    def _leave_lookahead(self):
        self._lookahead -= 1

    def _memoize_lookahead(self):
        return self._memoize_lookaheads or self._lookahead == 0

    def _rulestack(self):
        stack = '.'.join(self._rule_stack)
        if len(stack) > 60:
            stack = '...' + stack[-60:]
        return stack

    def _find_rule(self, name):
        return None

    def _find_semantic_rule(self, name):
        if self.semantics is None:
            return None, None

        postproc = getattr(self.semantics, '_postproc', None)
        if not callable(postproc):
            postproc = None

        rule = getattr(self.semantics, name, None)
        if callable(rule):
            return rule, postproc

        rule = getattr(self.semantics, '_default', None)
        if callable(rule):
            return rule, postproc

        return None, postproc

    def _trace(self, msg, *params):
        if self.trace:
            msg = msg % params
            print(udecode(msg), file=sys.stderr)

    def _trace_event(self, event):
        if self.trace:
            self._trace('%s \n%s   \n%s \n%s \n',
                        event,
                        self._rulestack(),
                        self._buffer.line_info().filename,
                        self._buffer.lookahead()
                        )

    def _trace_match(self, token, name=None):
        if self.trace:
            name = name if name else ''
            self._trace('MATCHED <%s> /%s/\n\t%s', token, name, self._buffer.lookahead())

    def _error(self, item, etype=FailedParse):
        raise etype(
            self._buffer,
            list(reversed(self._rule_stack[:])),
            item
        )

    def _fail(self):
        self._error('fail')

    def _call(self, rule, name, *params, **kwparams):
        self._rule_stack.append(name)
        pos = self._pos
        try:
            self._trace_event('ENTER ')
            self._last_node = None
            node, newpos, newstate = self._invoke_rule(rule, name, *params, **kwparams)
            self._goto(newpos)
            self._state = newstate
            self._trace_event('SUCCESS')
            self._add_cst_node(node)
            self._last_node = node
            return node
        except FailedParse:
            self._trace_event('FAILED')
            self._goto(pos)
            raise
        finally:
            self._rule_stack.pop()

    def _invoke_rule(self, rule, name, *params, **kwparams):
        pos = self._pos
        state = self._state
        key = (pos, rule, state)
        cache = self._memoization_cache

        if key in cache:
            result = cache[key]
            if isinstance(result, Exception):
                raise result
            return result

        self._push_ast()
        try:
            if name[0].islower():
                self._next_token()
            rule(self)
            node = self.ast
            if not node:
                node = self.cst
            elif '@' in node:
                node = node['@']  # override the AST
            elif self.parseinfo:
                node._add('_parseinfo', ParseInfo(self._buffer, name, pos, self._pos))
            semantic_rule, postproc = self._find_semantic_rule(name)
            try:
                if semantic_rule:
                    node = semantic_rule(node, *params, **kwparams)
                if postproc is not None:
                    postproc(self, node)
            except FailedSemantics as e:
                self._error(str(e), FailedParse)
            result = (node, self._pos, self._state)
            if self._memoize_lookahead():
                cache[key] = result
            return result
        except Exception as e:
            if self._memoize_lookahead():
                cache[key] = e
            raise
        finally:
            self._pop_ast()

    def _token(self, token):
        self._next_token()
        if self._buffer.match(token) is None:
            self._error(token, etype=FailedToken)
        self._trace_match(token)
        self._add_cst_node(token)
        self._last_node = token
        return token

    def _try_token(self, token):
        p = self._pos
        self._next_token()
        self._last_node = None
        if self._buffer.match(token) is None:
            self._goto(p)
            return None
        self._trace_match(token)
        self._add_cst_node(token)
        self._last_node = token
        return token

    def _pattern(self, pattern):
        token = self._buffer.matchre(pattern)
        if token is None:
            self._error(pattern, etype=FailedPattern)
        self._trace_match(token, pattern)
        self._add_cst_node(token)
        self._last_node = token
        return token

    def _try_pattern(self, pattern):
        p = self._pos
        token = self._buffer.matchre(pattern)
        self._last_node = None
        if token is None:
            self._goto(p)
            return None
        self._trace_match(token, pattern)
        self._add_cst_node(token)
        self._last_node = token
        return token

    @contextmanager
    def _try(self):
        p = self._pos
        s = self._state
        ast_copy = self.ast._copy()
        self._push_ast()
        self.last_node = None
        try:
            self.ast = ast_copy
            yield
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
                yield
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
        self.last_node = None
        with self._try():
            try:
                yield
            except OptionSucceeded:
                pass

    @contextmanager
    def _optional(self):
        self.last_node = None
        with self._choice():
            with self._option():
                yield

    @contextmanager
    def _group(self):
        self._push_cst()
        try:
            yield
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
        self._enter_lookahead()
        try:
            yield
        finally:
            self._leave_lookahead()
            self._goto(p)
            self._state = s
            self._pop_ast()  # simply discard
            self.last_node = None

    @contextmanager
    def _ifnot(self):
        try:
            with self._if():
                yield
        except FailedParse:
            pass
        else:
            self._error('', etype=FailedLookahead)

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
