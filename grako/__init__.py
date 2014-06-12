# -*- coding: utf-8 -*-
"""
Parse and translate an EBNF grammar into a Python parser for
the described language.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from grako import tool

genmodel = tool.genmodel
gencode = tool.gencode


def main():
    tool.main()

if __name__ == '__main__':
    main()
