# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import functools

from grako import tool
from grako import _version
from grako.codegen import pythoncg

__version__ = _version.__version__

genmodel = tool.genmodel
gencode = functools.partial(tool.gencode, codegen=pythoncg)


def main():
    tool.main(codegen=pythoncg, outer_version='')

if __name__ == '__main__':
    main()
