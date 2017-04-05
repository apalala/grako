# -*- coding: utf-8 -*-
# Copyright (C) 2017      by Juancarlo Añez
# Copyright (C) 2012-2016 by Juancarlo Añez and Thomas Bragg
from __future__ import absolute_import, division, print_function, unicode_literals

from grako._config import __version__
from grako._config import __toolname__
from grako.tool import compile, parse, to_python_sourcecode
from grako.tool import main

assert __version__
assert __toolname__
assert compile
assert parse
assert to_python_sourcecode


if __name__ == '__main__':
    main()
