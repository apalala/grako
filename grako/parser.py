# -*- coding: utf-8 -*-
# Copyright (C) 2017      by Juancarlo Añez
# Copyright (C) 2012-2016 by Juancarlo Añez and Thomas Bragg
from __future__ import absolute_import, division, print_function, unicode_literals

from grako.bootstrap import EBNFBootstrapParser
from grako.semantics import ASTSemantics, EBNFGrammarSemantics


class EBNFParser(EBNFBootstrapParser):
    def __init__(self, grammar_name=None, semantics=None, **kwargs):
        if semantics is None:
            semantics = ASTSemantics()
        super(EBNFParser, self).__init__(semantics=semantics, **kwargs)


class GrammarGenerator(EBNFBootstrapParser):
    def __init__(self, grammar_name=None, semantics=None, parseinfo=True, **kwargs):
        if semantics is None:
            semantics = EBNFGrammarSemantics(grammar_name)
        super(GrammarGenerator, self).__init__(
            semantics=semantics,
            parseinfo=parseinfo,
            **kwargs
        )
