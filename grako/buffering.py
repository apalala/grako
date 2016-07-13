# -*- coding: utf-8 -*-
"""
The Buffer class provides the functionality required by a parser-driven lexer.

Line analysis and caching are done so the parser can freely move with goto(p)
to any position in the parsed text, and still recover accurate information
about source lines and content.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
from bisect import bisect_left
from collections import namedtuple

from grako.util import ustr, strtype, extend_list, re as regexp
from grako.util import WHITESPACE_RE, RE_FLAGS
from grako.exceptions import ParseError

# TODO: There could be a file buffer using random access

__all__ = ['Buffer']

RETYPE = type(regexp.compile('.'))


PosLine = namedtuple('PosLine', ['pos', 'line'])


LineInfo = namedtuple(
    'LineInfo',
    ['filename', 'line', 'col', 'start', 'end', 'text']
)


Comments = namedtuple('Comments', ['inline', 'eol'])


def _new_comments():
    return Comments([], [])


class Buffer(object):
    def __init__(self,
                 text,
                 filename=None,
                 whitespace=None,
                 tabwidth=None,
                 comments_re=None,
                 eol_comments_re=None,
                 ignorecase=False,
                 trace=False,
                 nameguard=None,
                 comment_recovery=False,
                 namechars='',
                 **kwargs):
        self.original_text = text
        self.text = ustr(text)
        self.filename = filename or ''

        self.whitespace = whitespace

        self.tabwidth = tabwidth
        self.comments_re = comments_re
        self.eol_comments_re = eol_comments_re
        self.ignorecase = ignorecase
        self.trace = True
        self.nameguard = (nameguard
                          if nameguard is not None
                          else bool(self.whitespace_re))
        self.comment_recovery = comment_recovery
        self.namechars = namechars
        self._namechar_set = set(namechars)
        if namechars:
            self.nameguard = True

        self._pos = 0
        self._len = 0
        self._linecount = 0
        self._line_index = []
        self._linecache = []
        self._comment_index = []
        self._re_cache = {}

        self._preprocess()
        self._postprocess()

    @property
    def whitespace(self):
        return self._whitespace

    @whitespace.setter
    def whitespace(self, value):
        self._whitespace = value
        self.whitespace_re = self.build_whitespace_re(value)

    @staticmethod
    def build_whitespace_re(whitespace):
        if whitespace is None:
            return WHITESPACE_RE
        elif isinstance(whitespace, RETYPE):
            return whitespace
        elif whitespace:
            if not isinstance(whitespace, strtype):
                # a list or a set?
                whitespace = ''.join(c for c in whitespace)
            return regexp.compile(
                '[%s]+' % regexp.escape(whitespace), RE_FLAGS
            )
        else:
            return None

    def _preprocess(self, *args, **kwargs):
        lines, index = self._preprocess_block(self.filename, self.text)
        self.text = ''.join(lines)
        self._line_index = index

    def _postprocess(self):
        self._build_line_cache()
        self._len = len(self.text)

    def _preprocess_block(self, name, block, **kwargs):
        if self.tabwidth is not None:
            block = block.replace('\t', ' ' * self.tabwidth)
        lines = self.split_block_lines(name, block)
        index = self._block_index(name, len(lines))
        return self.process_block(name, lines, index, **kwargs)

    def _block_index(self, name, n):
        return list(zip(n * [name], range(n)))

    def split_block_lines(self, name, block, **kwargs):
        return block.splitlines(True)

    def join_block_lines(self, lines):
        return ''.join(lines)

    def process_block(self, name, lines, index, **kwargs):
        return lines, index

    def include(self, lines, index, i, j, name, block, **kwargs):
        blines, bindex = self._preprocess_block(name, block, **kwargs)
        assert len(blines) == len(bindex)
        lines[i:j + 1] = blines
        index[i:j + 1] = bindex
        assert len(lines) == len(index)
        return j + len(blines)

    def include_file(self, source, name, lines, index, i, j):
        text, filename = self.get_include(source, name)
        return self.include(lines, index, i, i, filename, text)

    def get_include(self, source, filename):
        source = os.path.abspath(source)
        base = os.path.dirname(source)
        include = os.path.join(base, filename)
        try:
            with open(include) as f:
                return f.read(), include
        except IOError:
            raise ParseError('include not found: %s' % include)

    def replace_lines(self, i, j, name, block):
        lines = self.split_block_lines(name, self.text)
        index = list(self._line_index)

        endline = self.include(lines, index, i, j, name, block)

        self.text = self.join_block_lines(lines)
        self._line_index = index
        self._postprocess()

        newtext = self.join_block_lines(lines[j + 1:endline + 2])
        return endline, newtext

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, p):
        self.goto(p)

    @property
    def line(self):
        n = bisect_left(self._linecache, PosLine(self._pos, 0))
        return self._linecache[n - 1][1]

    @property
    def col(self):
        n = bisect_left(self._linecache, PosLine(self._pos, 0))
        start = self._linecache[n - 1][0]
        return self._pos - start - 1

    def atend(self):
        return self._pos >= self._len

    def ateol(self):
        return self.atend() or self.current() in '\r\n'

    def current(self):
        if self._pos >= self._len:
            return None
        return self.text[self._pos]

    def at(self, p):
        if p >= self._len:
            return None
        return self.text[p]

    def peek(self, n=1):
        return self.at(self._pos + n)

    def next(self):
        if self._pos >= self._len:
            return None
        c = self.text[self._pos]
        self._pos += 1
        return c

    def goto(self, p):
        self._pos = max(0, min(len(self.text), p))

    def move(self, n):
        self.goto(self.pos + n)

    def comments(self, p, clear=False):
        if not self.comment_recovery or not self._comment_index:
            return Comments([], [])

        n = self.line_info(p).line
        if n >= len(self._comment_index):
            return Comments([], [])

        eolcmm = []
        if n < len(self._comment_index):
            eolcmm = self._comment_index[n].eol
            if clear:
                self._comment_index[n].eol = []

        cmm = []
        while n >= 0 and self._comment_index[n].inline:
            cmm.insert(0, self._comment_index[n].inline)
            if clear:
                self._comment_index[n].inline = []
            n -= 1

        return Comments(cmm, eolcmm)

    def eat_whitespace(self):
        if self.whitespace_re is not None:
            while self.matchre(self.whitespace_re):
                pass

    def eat_comments(self):
        if self.comments_re is not None:
            while True:
                comment = self.matchre(self.comments_re)
                if not comment:
                    break
                if self.comment_recovery:
                    n = self.line
                    extend_list(self._comment_index, n, default=_new_comments)

                    index = self._comment_index[n]
                    if not index.inline or index.inline[-1] != comment:
                        index.inline.append(comment)

    def eat_eol_comments(self):
        if self.eol_comments_re is not None:
            while True:
                comment = self.matchre(self.eol_comments_re)
                if not comment:
                    break
                if self.comment_recovery:
                    n = self.line
                    extend_list(self._comment_index, n, default=_new_comments)

                    index = self._comment_index[n]
                    if not index.eol or index.eol[-1] != comment:
                        index.eol.append(comment)

    def next_token(self):
        p = None
        while self._pos != p:
            p = self._pos
            self.eat_eol_comments()
            self.eat_comments()
            self.eat_whitespace()

    def skip_to(self, c):
        p = self._pos
        le = self._len
        while p < le and self.text[p] != c:
            p += 1
        self.goto(p)
        return p

    def skip_past(self, c):
        self.skip_to(c)
        self.next()
        return self.pos

    def skip_to_eol(self):
        return self.skip_to('\n')

    def scan_space(self, offset=0):
        return (
            self.whitespace_re and
            self._scanre(self.whitespace_re, offset=offset) is not None
        )

    def is_space(self):
        return self.scan_space()

    def is_name_char(self, c):
        return c is not None and c.isalnum() or c in self._namechar_set

    def match(self, token, ignorecase=None):
        ignorecase = ignorecase if ignorecase is not None else self.ignorecase

        if token is None:
            return self.atend()

        p = self.pos
        if ignorecase:
            result = self.text[p:p + len(token)].lower() == token.lower()
        else:
            result = self.text[p:p + len(token)] == token

        if result:
            self.move(len(token))
            if not self.nameguard:
                return token
            else:
                partial_match = (
                    token.isalnum() and
                    token[0].isalpha() and
                    self.is_name_char(self.current())
                )
                if not partial_match:
                    return token
        self.goto(p)

    def matchre(self, pattern, ignorecase=None):
        matched = self._scanre(pattern, ignorecase=ignorecase)
        if matched:
            token = matched.group()
            self.move(len(token))
            return token

    def _scanre(self, pattern, ignorecase=None, offset=0):
        ignorecase = ignorecase if ignorecase is not None else self.ignorecase

        if isinstance(pattern, RETYPE):
            re = pattern
        elif pattern in self._re_cache:
            re = self._re_cache[pattern]
        else:
            flags = RE_FLAGS | (regexp.IGNORECASE if ignorecase else 0)
            re = regexp.compile(
                pattern,
                flags
            )
            self._re_cache[pattern] = re
        return re.match(self.text, self.pos + offset)

    def _build_line_cache(self):
        # The line cache holds the position of the last character
        # (counting from 0) in each line (counting from 1).  At the
        # head, we have an imaginary line 0 that ends at -1.
        lines = self.text.splitlines(True)
        i = -1
        n = 0
        cache = []
        for n, s in enumerate(lines):
            cache.append(PosLine(i, n))
            i += len(s)
        n += 1
        if lines and lines[-1][-1] in '\r\n':
            n += 1
        cache.append(PosLine(i, n))
        self._linecache = cache
        self._linecount = n

    @property
    def linecount(self):
        return self._linecount

    def line_info(self, pos=None):
        if pos is None:
            pos = self._pos

        nmax = len(self._linecache) - 1
        if pos >= self._len:
            return LineInfo(self.filename, nmax, 0, self._len, self._len, '')

        n = bisect_left(self._linecache, PosLine(pos, 0))
        start, line = self._linecache[n - 1]
        start = start + 1
        end = self._linecache[n].pos + 1
        col = pos - start

        text = self.text[start:end]
        n = min(len(self._line_index) - 1, line)
        filename, line = self._line_index[n]

        return LineInfo(filename, line, col, start, end, text)

    def lookahead(self):
        if self.atend():
            return ''
        info = self.line_info()
        text = info.text[info.col:info.col + 1 + 80]
        text = text.split('\n')[0]
        return '<%d:%d>%s' % (info.line + 1, info.col + 1, text)

    def get_line(self, n=None):
        if n is None:
            n = self.line
        start, line = self._linecache[n][:2]
        assert line == n
        end, _ = self._linecache[n + 1]
        return self.text[start + 1:end]
