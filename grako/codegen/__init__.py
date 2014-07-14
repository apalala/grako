# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from grako.exceptions import CodegenError
from grako.codegen.cgbase import *  # noqa
from grako.codegen import python


def codegen(model, target='python'):
    if target.lower() == 'python':
        return python.codegen(model)
    else:
        raise CodegenError('Unknown target language: %s' % target)
