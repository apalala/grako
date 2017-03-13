# -*- coding: utf-8 -*-
# Copyright (C) 2017      by Juancarlo Añez
# Copyright (C) 2012-2016 by Juancarlo Añez and Thomas Bragg
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import functools
from collections import namedtuple
from contextlib import contextmanager

from ._unicode_characters import (
    C_DERIVE,
    C_ENTRY,
    C_SUCCESS,
    C_FAILURE,
    C_RECURSION,
)

from grako.util import notnone, ustr, prune_dict, is_list, info, safe_name
from grako.ast import AST
from grako import buffering
from grako import color
from grako.exceptions import (
    FailedCut,
    FailedLeftRecursion,
    FailedLookahead,
    FailedParse,
    FailedPattern,
    FailedRef,
    FailedSemantics,
    FailedKeywordSemantics,
    FailedToken,
    OptionSucceeded
)

__all__ = ['ParseInfo', 'ParseContext']


ParseInfo = namedtuple(
    'ParseInfo',
    [
        'buffer',
        'rule',
        'pos',
        'endpos',
        'line',
        'endline',
    ]
)


# decorator for rule implementation methods
def graken(*params, **kwparams):
    def decorator(rule):
        @functools.wraps(rule)
        def wrapper(self):
            name = rule.__name__
            # remove the single leading and trailing underscore
            # that the parser generator added
            name = name[1:-1]
            return self._call(rule, name, params, kwparams)
        return wrapper
    return decorator


class Closure(list):
    pass


class ParseContext(object):
    def __init__(self,
                 buffer_class=buffering.Buffer,
                 semantics=None,
                 parseinfo=False,
                 trace=False,
                 encoding='utf-8',
                 comments_re=None,
                 eol_comments_re=None,
                 whitespace=None,
                 ignorecase=False,
                 nameguard=None,
                 memoize_lookaheads=True,
                 left_recursion=False,
                 trace_length=72,
                 trace_separator=C_DERIVE,
                 trace_filename=False,
                 colorize=None,
                 keywords=None,
                 namechars='',
                 **kwargs):
        super(ParseContext, self).__init__()

        self._buffer = None
        self.buffer_class = buffer_class
        self.semantics = semantics
        self.encoding = encoding
        self.parseinfo = parseinfo
        self.trace = trace
        self.trace_length = trace_length
        self.trace_separator = trace_separator
        self.trace_filename = trace_filename

        self.comments_re = comments_re
        self.eol_comments_re = eol_comments_re
        self.whitespace = whitespace
        self.ignorecase = ignorecase
        self.nameguard = nameguard
        self.memoize_lookaheads = memoize_lookaheads
        self.left_recursion = left_recursion
        self.colorize = colorize
        self.keywords = set(keywords or [])
        self.namechars = namechars

        self._initialize_caches()

    def _initialize_caches(self):
        self._ast_stack = [AST()]
        self._concrete_stack = [None]
        self._rule_stack = []
        self._cut_stack = [False]
        self._memoization_cache = dict()

        self._last_node = None
        self._state = None
        self._lookahead = 0

        self._recursive_results = dict()
        self._recursive_eval = []
        self._recursive_head = []

    def _reset(self,
               text=None,
               filename=None,
               buffer_class=None,
               semantics=None,
               trace=None,
               comments_re=None,
               eol_comments_re=None,
               whitespace=None,
               ignorecase=None,
               nameguard=None,
               memoize_lookaheads=None,
               left_recursion=None,
               colorize=None,
               keywords=None,
               namechars='',
               **kwargs):
        if ignorecase is None:
            ignorecase = self.ignorecase
        if nameguard is None:
            nameguard = self.nameguard
        if memoize_lookaheads is not None:
            self.memoize_lookaheads = memoize_lookaheads
        if left_recursion is not None:
            self.left_recursion = left_recursion
        if trace is not None:
            self.trace = trace
        if semantics is not None:
            self.semantics = semantics
        if colorize is not None:
            self.colorize = colorize
        if keywords is not None:
            self.keywords = keywords
        if self.colorize:
            color.init()
        if namechars is not None:
            namechars = self.namechars

        self._initialize_caches()
        self._furthest_exception = None

        if isinstance(text, buffering.Buffer):
            buffer = text
        else:
            buffer_class = buffer_class or self.buffer_class
            buffer = buffer_class(
                text,
                filename=filename,
                comments_re=comments_re or self.comments_re,
                eol_comments_re=eol_comments_re or self.eol_comments_re,
                whitespace=notnone(whitespace, default=self.whitespace),
                ignorecase=ignorecase,
                nameguard=nameguard,
                namechars=namechars,
                **kwargs)
        self._buffer = buffer

    def _set_furthest_exception(self, e):
        if not self._furthest_exception or e.pos > self._furthest_exception.pos:
            self._furthest_exception = e

    def parse(self,
              text,
              rule_name='start',
              filename=None,
              buffer_class=None,
              semantics=None,
              trace=False,
              whitespace=None,
              **kwargs):
        try:
            self.parseinfo = kwargs.pop('parseinfo', self.parseinfo)
            self._reset(
                text=text,
                filename=filename,
                buffer_class=buffer_class,
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
            self._set_furthest_exception(e.nested)
            raise self._furthest_exception
        except FailedParse as e:
            self._set_furthest_exception(e)
            raise self._furthest_exception
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

    def _clear_cache(self):
        self._memoization_cache = dict()
        self._recursive_results = dict()

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

    def name_last_node(self, name):
        self.ast[name] = self.last_node

    def add_last_node_to_name(self, name):
        self.ast.setlist(name, self.last_node)

    def _push_ast(self):
        self._push_cst()
        self._ast_stack.append(AST())

    def _pop_ast(self):
        self._pop_cst()
        return self._ast_stack.pop()

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
            self.cst = self._copy_node(node)
        elif is_list(previous):
            previous.append(node)
        else:
            self.cst = [previous, node]

    def _extend_cst(self, node):
        if node is None:
            return
        previous = self.cst
        if previous is None:
            self.cst = self._copy_node(node)
        elif is_list(node):
            if is_list(previous):
                previous.extend(node)
            else:
                self.cst = [previous] + node
        elif is_list(previous):
            previous.append(node)
        else:
            self.cst = [previous, node]

    def _copy_node(self, node):
        if node is None:
            return None
        elif is_list(node):
            return node[:]
        else:
            return node

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

        def prune_cache(cache):
            prune_dict(cache, lambda k, _: k[0] < cutpos)

        prune_cache(self._memoization_cache)
        prune_cache(self._recursive_results)

    def _push_cut(self):
        self._cut_stack.append(False)

    def _pop_cut(self):
        return self._cut_stack.pop()

    def _enter_lookahead(self):
        self._lookahead += 1

    def _leave_lookahead(self):
        self._lookahead -= 1

    def _memoization(self):
        return self.memoize_lookaheads or self._lookahead == 0

    def _rulestack(self):
        stack = self.trace_separator.join(reversed(self._rule_stack))
        if max(len(s) for s in stack.splitlines()) > self.trace_length:
            stack = stack[:self.trace_length]
            stack = stack.rsplit(self.trace_separator, 1)[0]
            stack += self.trace_separator
        return stack

    def _find_rule(self, name):
        self._error(name, etype=FailedRef)
        return lambda: None  # makes static checkers happy

    def _find_semantic_rule(self, name):
        if self.semantics is None:
            return None, None

        postproc = getattr(self.semantics, '_postproc', None)
        if not callable(postproc):
            postproc = None

        rule = getattr(self.semantics, safe_name(name), None)
        if callable(rule):
            return rule, postproc

        rule = getattr(self.semantics, '_default', None)
        if callable(rule):
            return rule, postproc

        return None, postproc

    def _trace(self, msg, *params):
        if self.trace:
            msg = msg % params
            info(ustr(msg), file=sys.stderr)

    def _trace_event(self, event):
        if self.trace:
            fname = ''
            if self.trace_filename:
                fname = self._buffer.line_info().filename + '\n'
            self._trace('%s   \n%s%s \n',
                        event + self._rulestack(),
                        color.Style.DIM + fname,
                        color.Style.NORMAL + self._buffer.lookahead().rstrip('\r\n') +
                        color.Style.RESET_ALL
                        )

    def _trace_entry(self):
        self._trace_event(color.Fore.YELLOW + color.Style.BRIGHT + C_ENTRY)

    def _trace_success(self):
        self._trace_event(color.Fore.GREEN + color.Style.BRIGHT + C_SUCCESS)

    def _trace_failure(self):
        self._trace_event(color.Fore.RED + color.Style.BRIGHT + C_FAILURE)

    def _trace_recursion(self):
        self._trace_event(color.Fore.RED + color.Style.BRIGHT + C_RECURSION)

    def _trace_match(self, token, name=None, failed=False):
        if self.trace:
            fname = ''
            if self.trace_filename:
                fname = self._buffer.line_info().filename + '\n'
            name = '/%s/' % name if name else ''

            if not failed:
                fgcolor = color.Fore.GREEN + C_SUCCESS
            else:
                fgcolor = color.Fore.RED + C_FAILURE

            self._trace(
                color.Style.BRIGHT + fgcolor + "'%s' %s\n%s%s\n",
                token,
                name,
                color.Style.DIM + fname,
                color.Style.NORMAL + self._buffer.lookahead().rstrip('\r\n') +
                color.Style.RESET_ALL
            )

    def _error(self, item, etype=FailedParse):
        raise etype(
            self._buffer,
            list(reversed(self._rule_stack[:])),
            item
        )

    def _fail(self):
        self._error('fail')

    def _get_parseinfo(self, name, pos):
        endpos = self._pos
        return ParseInfo(
            self._buffer,
            name,
            pos,
            endpos,
            self._buffer.posline(pos),
            self._buffer.posline(endpos),
        )

    def _call(self, rule, name, params, kwparams):
        self._rule_stack.append(name)
        pos = self._pos
        try:
            self._trace_entry()

            self._last_node = None

            node, newpos, newstate = self._invoke_rule(rule, name, params, kwparams)

            self._goto(newpos)
            self._state = newstate
            self._add_cst_node(node)
            self._last_node = node

            self._trace_success()
            return node
        except FailedPattern:
            self._error('Expecting <%s>' % name)
        except FailedParse as e:
            self._goto(pos)
            self._set_furthest_exception(e)
            if isinstance(e, FailedLeftRecursion):
                self._trace_recursion()
            else:
                self._trace_failure()
            raise
        finally:
            self._rule_stack.pop()

    def _invoke_rule(self, rule, name, params, kwparams):
        cache = self._memoization_cache
        if name[0].islower():
            self._next_token()
        pos = self._pos

        key = (pos, rule, self._state)
        if key in cache:
            memo = cache[key]
            memo = self._left_recursion_check(name, key, memo)
            if isinstance(memo, Exception):
                raise memo
            return memo

        self._set_left_recursion_guard(name, key)
        self._push_ast()
        try:
            try:
                rule(self)

                node = self.ast
                if not node:
                    node = self.cst
                elif '@' in node:
                    node = node['@']  # override the AST
                elif self.parseinfo:
                    node.set_parseinfo(self._get_parseinfo(name, pos))

                node = self._invoke_semantic_rule(name, node, params, kwparams)
                result = (node, self._pos, self._state)

                result = self._left_recurse(rule, name, pos, key, result, params, kwparams)

                if self._memoization() and not self._in_recursive_loop():
                    cache[key] = result
                return result
            except FailedSemantics as e:
                self._error(ustr(e), FailedParse)
        except FailedParse as e:
            self._set_furthest_exception(e)
            if self._memoization():
                cache[key] = e
            raise
        finally:
            self._pop_ast()

    def _set_left_recursion_guard(self, name, key):
        exception = FailedLeftRecursion(
            self._buffer,
            list(reversed(self._rule_stack[:])),
            name
        )

        # Alessandro Warth et al say that we can deal with
        # direct and indirect left-recursion by seeding the
        # memoization cache with a parse failure.
        #
        #   http://www.vpri.org/pdf/tr2007002_packrat.pdf
        #
        if self._memoization():
            self._memoization_cache[key] = exception

    def _left_recursion_check(self, name, key, memo):
        if isinstance(memo, FailedLeftRecursion) and self.left_recursion:
            # At this point we know we've already seen this rule
            # at this position. Either we've got a potential
            # result from a previous pass that we can return, or
            # we make a note of the rule so that we can take
            # action as we unwind the rule stack.

            if key in self._recursive_results:
                memo = self._recursive_results[key]
            else:
                self._recursive_head.append(name)
        return memo

    def _in_recursive_loop(self):
        head = self._recursive_head
        return head and head[-1] in self._rule_stack

    def _left_recurse(self, rule, name, pos, key, result, params, kwparams):
        if self._memoization():
            self._recursive_results[key] = result

        # If the current name is in the head, then we've just
        # unwound to the highest rule in the recursion
        cache = self._memoization_cache
        last_pos = pos
        if (
            [name] == self._recursive_head[-1:] and
            self._recursive_head[-1:] != self._recursive_eval[-1:]
        ):
            # Repeatedly apply the rule until it can't consume any
            # more. We store the last good result each time. Prior
            # to doing so we reset the position and remove any
            # failures from the cache.
            last_result = result
            self._recursive_eval.append(name)
            while self._pos > last_pos:
                last_result = result
                last_pos = self._pos
                self._goto(pos)
                prune_dict(cache, lambda _, v: isinstance(v, FailedParse))
                try:
                    result = self._invoke_rule(rule, name, params, kwparams)
                except FailedParse:
                    pass

            result = last_result
            self._recursive_results = dict()
            self._recursive_head.pop()
            self._recursive_eval.pop()
        return result

    def _invoke_semantic_rule(self, name, node, params, kwparams):
        semantic_rule, postproc = self._find_semantic_rule(name)
        if semantic_rule:
            node = semantic_rule(node, *(params or ()), **(kwparams or {}))
        if postproc is not None:
            postproc(self, node)
        return node

    def _token(self, token):
        self._next_token()
        if self._buffer.match(token) is None:
            self._trace_match(token, failed=True)
            self._error(token, etype=FailedToken)
        self._trace_match(token)
        self._add_cst_node(token)
        self._last_node = token
        return token

    def _constant(self, literal):
        self._next_token()
        self._trace_match(literal)
        self._add_cst_node(literal)
        self._last_node = literal
        return literal

    def _pattern(self, pattern):
        token = self._buffer.matchre(pattern)
        if token is None:
            self._trace_match('', pattern, failed=True)
            self._error(pattern, etype=FailedPattern)
        self._trace_match(token, pattern)
        self._add_cst_node(token)
        self._last_node = token
        return token

    def _eof(self):
        return self._buffer.atend()

    def _eol(self):
        return self._buffer.ateol()

    def _check_eof(self):
        self._next_token()
        if not self._buffer.atend():
            self._error('Expecting end of text.')

    @contextmanager
    def _try(self):
        p = self._pos
        s = self._state
        ast_copy = self.ast.copy()
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

    @contextmanager
    def _ifnot(self):
        try:
            with self._if():
                yield
        except FailedParse:
            pass
        else:
            self._error('', etype=FailedLookahead)

    @contextmanager
    def _ignore(self):
        self._push_cst()
        try:
            self.cst = None
            yield
        finally:
            self._pop_cst()

    def _repeater(self, block, prefix=None):
        while True:
            self._push_cut()
            self._push_cst()
            try:
                p = self._pos
                with self._try():
                    if prefix:
                        with self._ignore():
                            prefix()
                            self._cut()

                    block()
                    cst = self.cst

                    if self._pos == p:
                        self._error('empty closure')
            except FailedCut:
                raise
            except FailedParse as e:
                if self._is_cut_set():
                    raise FailedCut(e)
                break
            finally:
                self._pop_cst()
                self._pop_cut()
            self._add_cst_node(cst)

    def _closure(self, block, sep=None):
        self._push_cst()
        try:
            self.cst = []
            with self._optional():
                with self._try():
                    block()
                self.cst = [self.cst]
                self._repeater(block, prefix=sep)
            cst = Closure(self.cst)
        finally:
            self._pop_cst()
        self._add_cst_node(cst)
        self.last_node = cst
        return cst

    def _positive_closure(self, block, sep=None):
        self._push_cst()
        try:
            self.cst = None
            with self._try():
                block()
            self.cst = [self.cst]
            self._repeater(block, prefix=sep)
            cst = Closure(self.cst)
        finally:
            self._pop_cst()
        self._add_cst_node(cst)
        self.last_node = cst
        return cst

    def _empty_closure(self):
        cst = Closure([])
        self._add_cst_node(cst)
        self.last_node = cst
        return cst

    def _check_name(self):
        name = ustr(self.last_node)
        if self.ignorecase or self._buffer.ignorecase:
            name = name.upper()
        if name in self.keywords:
            raise FailedKeywordSemantics('"%s" is a reserved word' % name)

    def _void(self):
        self.last_node = None
