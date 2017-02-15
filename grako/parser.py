# -*- coding: utf-8 -*-
# Copyright (C) 2017      by Juancarlo Añez
# Copyright (C) 2012-2016 by Juancarlo Añez and Thomas Bragg
"""
Implements parsing of Grako's EBNF idiom for grammars, and grammar model
creation using the .grammars module.

GrakoParserRoot is the bootstrap parser. It uses the facilities of parsing.Parser
as generated parsers do, but it does not conform to the patterns in the generated
code. Why? Because having Grako bootstrap itself from its grammar would be cool,
but very bad engineering. GrakoParserRoot is hand-crafted.

The GrammarGenerator class, a descendant of GrakoParserRoot constructs
a model of the grammar using semantic actions the model elements defined
in the .grammars module.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from grako.buffering import Buffer
from grako.bootstrap import EBNFBootstrapParser
from grako.grammars import GrakoContext
from grako.grammars import EBNFBuffer
from grako.semantics import GrakoASTSemantics, GrakoSemantics

__all__ = ['EBNFParser', 'GrammarGenerator']


class EBNFParserBase(EBNFBootstrapParser, GrakoContext):
    def parse(self, text, *args, **kwargs):
        if not isinstance(text, Buffer):
            text = EBNFBuffer(text, **kwargs)
        return super(EBNFParserBase, self).parse(text, *args, **kwargs)


class EBNFParser(EBNFParserBase):
    def __init__(self, grammar_name=None, semantics=None, **kwargs):
        if semantics is None:
            semantics = GrakoASTSemantics()
        super(EBNFParser, self).__init__(semantics=semantics, **kwargs)


class GrammarGenerator(EBNFParserBase):
    def __init__(self, grammar_name=None, semantics=None, parseinfo=True, **kwargs):
        if semantics is None:
            semantics = GrakoSemantics(grammar_name)
        super(GrammarGenerator, self).__init__(
            semantics=semantics,
            parseinfo=True,
            **kwargs
        )
