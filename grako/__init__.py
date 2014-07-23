# -*- coding: utf-8 -*-
"""
Parse and translate an EBNF grammar into a Python parser for
the described language.
"""
from __future__ import absolute_import, division, print_function, unicode_literals
from grako import tool
from grako import _version

__version__ = _version.__version__

genmodel = tool.genmodel
gencode = tool.gencode


def main():
    tool.main()

if __name__ == '__main__':
    main()
