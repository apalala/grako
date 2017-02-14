# -*- coding: utf-8 -*-
# Copyright (C) 2017      by Juancarlo Añez
# Copyright (C) 2012-2016 by Juancarlo Añez and Thomas Bragg
from __future__ import absolute_import, division, print_function, unicode_literals

from grako.exceptions import CodegenError
from grako.codegen.cgbase import *  # noqa


def codegen(model, target='python'):
    if target.lower() == 'python':
        from grako.codegen import python
        return python.codegen(model)
    else:
        raise CodegenError('Unknown target language: %s' % target)
