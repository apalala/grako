# -*- coding: utf-8 -*-
"""
The Buffer class provides the functionality required by a parser-driven lexer.

Line analysis and caching are done so the parser can freely move with goto(p)
to any position in the parsed text, and still recover accurate information
about source lines and content.
"""
from __future__ import print_function, division, absolute_import, unicode_literals
# TODO: There could be a file buffer using random access
import re as regexp
import string
from bisect import bisect_left
from collections import namedtuple

__all__ = ['Buffer']

RETYPE = type(regexp.compile('.'))

PosLine = namedtuple('PosLine', ['pos', 'line'])
LineInfo = namedtuple('LineInfo', ['filename', 'line', 'col', 'start', 'text'])


class Buffer(object):
    def __init__(self, text,
                 filename=None,
                 whitespace=None,
                 comments_re=None,
                 ignorecase=False,
                 trace=False,
                 nameguard=True,
                 **kwargs):
        self.original_text = text
        self.text = text
        self.filename = filename if filename is not None else ''
        self.whitespace = set(whitespace
                              if whitespace is not None
                              else string.whitespace)
        self.comments_re = comments_re
        self.ignorecase = ignorecase
        self.trace = trace
        self.nameguard = nameguard
        self._fileinfo = self.get_fileinfo(text, filename)
        self._linecache = []
        self._linecount = 0
        self._pos = 0
        self._len = 0
        self._preprocess()
        self._len = len(self.text)
        self._build_line_cache()
        self._re_cache = {}

    def _preprocess(self):
        pass

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

    def peek(self, n):
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

    def eatwhitespace(self):
        p = self._pos
        le = self._len
        ws = self.whitespace
        while p < le and self.text[p] in ws:
            p += 1
        self._pos = p

    def eatcomments(self):
        if self.comments_re is not None:
            while self.matchre(self.comments_re, regexp.MULTILINE):
                pass

    def next_token(self):
        p = None
        while self._pos != p:
            p = self._pos
            self.eatcomments()
            self.eatwhitespace()

    def skip_to(self, c):
        p = self._pos
        le = self._len
        while p < le and self.text[p] != c:
            p += 1
        self._pos = p

    def skip_past(self, c):
        self.skip_to(c)
        self.next()

    def skip_to_eol(self):
        self.skip_to('\n')

    def is_space(self):
        return self.current() in self.whitespace

    def is_name_char(self):
        c = self.current()
        return c is not None and c.isalnum()

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
            check_nameguard = not (self.nameguard
                                   and token.isalnum()
                                   and self.is_name_char()
                                   )
            if check_nameguard:
                return token
        self.goto(p)

    def matchre(self, pattern, ignorecase=None):
        ignorecase = ignorecase if ignorecase is not None else self.ignorecase

        if isinstance(pattern, RETYPE):
            re = pattern
        elif pattern in self._re_cache:
            re = self._re_cache[pattern]
        else:
            re = regexp.compile(pattern,
                                regexp.MULTILINE |
                                (regexp.IGNORECASE if ignorecase else 0))
            self._re_cache[re] = re

        matched = re.match(self.text, self.pos)
        if matched:
            token = matched.group()
            self._pos += len(token)
            return token

    def get_fileinfo(self, text, filename):
        return [filename] * len(text.splitlines())

    def _build_line_cache(self):
        # The line cache holds the position of the last character
        # (counting from 0) in each line (counting from 1).  At the
        # head, we have an imaginary line 0 that ends at -1.
        cache = [PosLine(-1, 0)]
        n = 0
        for i, c in enumerate(self.text):
            if c == '\n':
                n += 1
                cache.append(PosLine(i, n))
        n += 1
        cache.append(PosLine(self._len - 1, n))
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
            return LineInfo(self.filename, nmax, 0, self._len, "")
        n = bisect_left(self._linecache, PosLine(pos, 0))
        start, line = self._linecache[n - 1]
        start = start + 1
        end = self._linecache[n].pos + 1
        text = self.text[start:end]
        col = pos - start
        return LineInfo(self.filename, line, col, start, text)

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
