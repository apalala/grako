# -*- coding: utf-8 -*-
# Copyright (C) 2017      by Juancarlo Añez
# Copyright (C) 2012-2016 by Juancarlo Añez and Thomas Bragg
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys

import grako
from grako.codegen import codegen
import regex_parser

PARSER_FILENAME = 'genparser.py'


def main():
    grammar = regex_parser.translate('(a|b)*')
    model = grako.compile(grammar, 'Regexp')
    model.parse('aaabbaba', 'S0')
    try:
        model.parse('aaaCbbaba', 'S0')
        raise Exception('Should not have parsed!')
    except grako.exceptions.FailedParse:
        pass
    print('Grammar:', file=sys.stderr)
    print(grammar)
    sys.stdout.flush()
    with open(PARSER_FILENAME, 'w') as f:
        f.write(codegen(model))
    print('Generated parser saved as:', PARSER_FILENAME, file=sys.stderr)
    print(file=sys.stderr)


if __name__ == '__main__':
    main()
