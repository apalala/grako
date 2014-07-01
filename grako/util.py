# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
import collections
import json
import datetime
import re
import codecs


PY3 = sys.version_info[0] >= 3

if PY3:
    strtype = str
else:
    strtype = basestring


def debug(*args, **kwargs):
    kwargs['file'] = sys.stderr
    print(*args, **kwargs)


def to_list(o):
    if o is None:
        return []
    elif isinstance(o, list):
        return o
    else:
        return [o]


def ustr(s):
    if PY3:
        return str(s)
    elif isinstance(s, str):
        return s.decode('utf-8')
    else:
        return unicode(s)


def udecode(s):
    if PY3:
        return str(s)
    else:
        if not isinstance(s, str):
            s = ustr(s)
        return s.decode('utf-8')


def __old__unescape(s):
    """
    Try to honor non-unicode escape sequences.
    """
    s = ustr(s)
    s = s.replace('\\"', '"')
    s = s.replace("\\'", "'")
    s = s.replace('\\a', '\a')
    s = s.replace('\\b', '\b')
    s = s.replace('\\f', '\f')
    s = s.replace('\\n', '\n')
    s = s.replace('\\r', '\r')
    s = s.replace('\\t', '\t')
    s = s.replace('\\v', '\v')
    if '\\' not in s:
        # leave alone
        return s
    elif PY3:
        return s.encode('utf-8').decode('unicode_escape')
    else:
        return unicode(s.encode('utf-8'), 'unicode_escape')


ESCAPE_SEQUENCE_RE = re.compile(
    r'''
    ( \\U........      # 8-digit Unicode escapes
    | \\u....          # 4-digit Unicode escapes
    | \\x..            # 2-digit Unicode escapes
    | \\[0-7]{1,3}     # Octal character escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''',
    re.UNICODE | re.VERBOSE
)


def eval_escapes(s):
    """
    Given a string, evaluate escape sequences starting with backslashes as
    they would be evaluated in Python source code. For a list of these
    sequences, see: https://docs.python.org/3/reference/lexical_analysis.html

    This is not the same as decoding the whole string with the 'unicode-escape'
    codec, because that provides no way to handle non-ASCII characters that are
    literally present in the string.
    """
    # by Rob Speer

    def decode_match(match):
        return codecs.decode(match.group(0), 'unicode-escape')

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)


def simplify_list(x):
    if isinstance(x, list) and len(x) == 1:
        return simplify_list(x[0])
    return x


def isiter(value):
    return (
        isinstance(value, collections.Iterable)
        and not isinstance(value, strtype)
    )


def trim(text, tabwidth=4):
    """
    Trim text of common, leading whitespace.

    Based on the trim algorithm of PEP 257:
        http://www.python.org/dev/peps/pep-0257/
    """
    if not text:
        return ''
    lines = text.expandtabs(tabwidth).splitlines()
    maxindent = len(text)
    indent = maxindent
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    trimmed = [lines[0].strip()] + [line[indent:].rstrip() for line in lines[1:]]
    i = 0
    while i < len(trimmed) and not trimmed[i]:
        i += 1
    return '\n'.join(trimmed[i:])


def indent(text, indent=1, multiplier=4):
    """ Indent the given block of text by indent*4 spaces
    """
    if text is None:
        return ''
    text = ustr(text)
    if indent >= 0:
        sindent = ' ' * multiplier * indent
        text = '\n'.join((sindent + t).rstrip() for t in text.splitlines())
    return text


def format_if(fmt, values):
    return fmt % values if values else ''


def notnone(value, default=None):
    return value if value is not None else default


def timestamp():
    return '.'.join('%2.2d' % t for t in datetime.datetime.utcnow().utctimetuple()[:-2])


def asjson(obj):
    if hasattr(obj, '__json__'):
        return obj.__json__()
    elif isinstance(obj, collections.Mapping):
        result = collections.OrderedDict()
        for k, v in obj.items():
            try:
                result[asjson(k)] = asjson(v)
            except TypeError:
                debug('Unhashable key?', type(k), str(k))
                raise
        return result
    elif isiter(obj):
        return [asjson(e) for e in obj]
    else:
        return obj


def asjsons(obj):
    return json.dumps(asjson(obj), indent=2)
