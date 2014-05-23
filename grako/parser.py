# -*- coding: utf-8 -*-
"""
Implements parsing of Grako's EBNF idiom for grammars, and grammar model
creation using the .grammars module.

GrakoParserRoot is the bootstrap parser. It uses the facilities of parsing.Parser
as generated parsers do, but it does not conform to the patterns in the generated
code. Why? Because having Grako bootstrap itself from its grammar would be cool,
but very bad engineering. GrakoParserRoot is hand-crafted.

The GrakoGrammarGenerator class, a descendant of GrakoParserRoot constructs
a model of the grammar using semantic actions the model elements defined
in the .grammars module.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .exceptions import ParseError
from .buffering import Buffer
from .semantics import GrakoASTSemantics, GrakoSemantics
from .bootstrap import GrakoBootstrapParser

__all__ = ['GrakoParser', 'GrakoGrammarGenerator']

COMMENTS_RE = r'\(\*(?:.|\n)*?\*\)'


class GrakoBuffer(Buffer):
    def process_block(self, name, lines, index, **kwargs):
        # search for pragmas of the form
        # .. pragma_name :: params

        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith('..'):
                name, arg = line.split('..')[1], ''
                if '::' in name:
                    name, arg = name.split('::')
                name, arg = name.strip(), arg.strip()
                i = self.pragma(name, arg, lines, index, i)
            else:
                i += 1
        return lines, index

    def pragma(self, name, arg, lines, index, i):
        # we only recognize the 'include' pragama
        if name == 'include':
            return self.include_file(arg, lines, index, i, i)
        else:
            raise ParseError('Unknown pragma: %s' % name)


class GrakoParserBase(GrakoBootstrapParser):

    def parse(self, text, rule='grammar', filename=None, **kwargs):
        if not isinstance(text, Buffer):
            text = GrakoBuffer(text, comments_re=COMMENTS_RE, **kwargs)
        return super(GrakoParserBase, self).parse(
            text,
            rule,
            filename=filename,
            **kwargs
        )


class GrakoParser(GrakoParserBase):
    def __init__(self, grammar_name, semantics=None, **kwargs):
        if semantics is None:
            semantics = GrakoASTSemantics()
        super(GrakoParser, self).__init__(semantics=semantics, **kwargs)


class GrakoGrammarGenerator(GrakoParserBase):
    def __init__(self, grammar_name, semantics=None, **kwargs):
        if semantics is None:
            semantics = GrakoSemantics(grammar_name)
        super(GrakoGrammarGenerator, self).__init__(semantics=semantics, **kwargs)
