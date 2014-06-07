# -*- coding: utf-8 -*-
"""
Parse and translate an EBNF grammar into a Python parser for
the described language.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import codecs
import argparse
import os
import pickle
import sys

from .exceptions import GrakoException
from .parser import GrakoGrammarGenerator

DESCRIPTION = ('Grako (for grammar compiler) takes grammars'
               ' in a variation of EBNF as input, and outputs a memoizing'
               ' PEG parser in Python.'
               )


argparser = argparse.ArgumentParser(prog='grako',
                                    description=DESCRIPTION
                                    )
argparser.add_argument('-b', '--binary',
                       help='generate a pickled grammar model instead of a parser',
                       action='store_true'
                       )
argparser.add_argument('-d', '--draw',
                       help='generate a diagram of the grammar (requires --outfile)',
                       action='store_true'
                       )
argparser.add_argument('filename',
                       metavar='grammar',
                       help='The filename of the grammar to gencode( a parser for'
                       )
argparser.add_argument('-n', '--no-nameguard',
                       help='do not protect alphanumeric tokens that are prefixes of others',
                       dest="nameguard", action='store_false', default=True
                       )
argparser.add_argument('-m', '--name',
                       nargs=1,
                       metavar='name',
                       help="An optional name for the grammar. It defaults to the basename of the grammar file's name"
                       )
argparser.add_argument('-o', '--outfile',
                       metavar='outfile',
                       help='specify where the output should go (default is stdout)'
                       )
argparser.add_argument('-p', '--pretty',
                       help='prettify the input grammar',
                       action='store_true'
                       )
argparser.add_argument('-t', '--trace',
                       help='produce verbose parsing output',
                       action='store_true'
                       )
argparser.add_argument('-w', '--whitespace',
                       metavar='characters',
                       help='whitespace characters (use empty string to disable automatic whitespace)',
                       )


def genmodel(name, grammar, trace=False, filename=None):
    parser = GrakoGrammarGenerator(name, trace=trace)
    return parser.parse(grammar, filename=filename)


def gencode(name, grammar, trace=False, filename=None):
    model = genmodel(name, grammar, trace=trace, filename=filename)
    return model.render()


def main():
    import logging
    logging.basicConfig(format='%(levelname)s: %(message)s')
    log = logging.getLogger()
    try:
        args = argparser.parse_args()
    except Exception as e:
        print(e)
        sys.exit(1)

    binary = args.binary
    filename = args.filename
    name = args.name
    nameguard = args.nameguard
    draw = args.draw
    outfile = args.outfile
    pretty = args.pretty
    trace = args.trace
    whitespace = args.whitespace

    if binary and not outfile:
        log.error('--binary requires --outfile')
        sys.exit(1)

    if draw and not outfile:
        log.error('--draw requires --outfile')
        sys.exit(1)

    if sum((binary, draw, pretty)) > 1:
        log.error('either --binary or --draw or --pretty')
        sys.exit(1)

    if name is None:
        name = os.path.splitext(os.path.basename(filename))[0]

    if outfile and os.path.isfile(outfile):
        os.unlink(outfile)

    grammar = codecs.open(filename, 'r', encoding='utf-8').read()

    if outfile:
        dirname = os.path.dirname(outfile)
        if dirname and not os.path.isdir(dirname):
            os.makedirs(dirname)

    try:
        model = genmodel(name, grammar, trace=trace, filename=filename)
        model.whitespace = repr(whitespace)
        model.nameguard = repr(nameguard)

        if binary:
            result = pickle.dumps(model, protocol=2)
        elif pretty:
            result = str(model)
        else:
            result = model.render()

        if draw:
            from . import diagrams
            diagrams.draw(outfile, model)
        elif outfile:
            with codecs.open(outfile, 'w', encoding='utf-8') as f:
                f.write(result)
        else:
            print(result)
    except GrakoException as e:
        log.error(str(e))

if __name__ == '__main__':
    main()
