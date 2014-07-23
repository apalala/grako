# -*- coding: utf-8 -*-
"""
Parse and translate an EBNF grammar into a Python parser for
the described language.
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import codecs
import argparse
import os
import pickle
import sys

from grako._version import __version__
from grako.util import eval_escapes
from grako.exceptions import GrakoException
from grako.parser import GrakoGrammarGenerator

# we hook the tool to the Python code generator as the default
from grako.codegen import pythoncg

DESCRIPTION = (
    'Grako (for "grammar compiler") takes grammars'
    ' in a variation of EBNF as input, and outputs a memoizing'
    ' PEG/Packrat parser in Python.'
)


argparser = argparse.ArgumentParser(prog='grako',
                                    description=DESCRIPTION
                                    )
argparser.add_argument('-b', '--binary',
                       help='generate a pickled grammar model (requires --output)',
                       action='store_true'
                       )
argparser.add_argument('-d', '--draw',
                       help='generate a diagram of the grammar (requires --output)',
                       action='store_true'
                       )
argparser.add_argument('filename',
                       metavar='GRAMMAR',
                       help='The filename of the Grako grammar'
                       )
argparser.add_argument('-m', '--name',
                       nargs=1,
                       metavar='NAME',
                       help='Name for the grammar (defaults to GRAMMAR base name)'
                       )
argparser.add_argument('-n', '--no-nameguard',
                       help='allow tokens that are prefixes of others',
                       dest="nameguard",
                       action='store_false',
                       default=True
                       )
argparser.add_argument('-o', '--output',
                       metavar='FILE',
                       help='output file (default is stdout)'
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
                       metavar='CHARACTERS',
                       help='characters to skip during parsing (use "" to disable)',
                       default=None
                       )


def genmodel(name, grammar, trace=False, filename=None):
    parser = GrakoGrammarGenerator(name, trace=trace)
    return parser.parse(grammar, filename=filename)


def gencode(name, grammar, trace=False, filename=None, codegen=pythoncg):
    model = genmodel(name, grammar, trace=trace, filename=filename)
    return codegen(model)


def _error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main(codegen=pythoncg, outer_version=''):
    argparser.add_argument('-v', '--version',
                        help='provide version information and exit',
                        action='version',
                        version=outer_version + 'Grako ' + __version__
                        )
    try:
        args = argparser.parse_args()
    except Exception as e:
        _error(str(e))
        sys.exit(2)

    binary = args.binary
    filename = args.filename
    name = args.name
    nameguard = args.nameguard
    draw = args.draw
    outfile = args.output
    pretty = args.pretty
    trace = args.trace
    whitespace = args.whitespace

    if whitespace:
        whitespace = eval_escapes(args.whitespace)

    if binary and not outfile:
        _error('--binary requires --outfile')
        sys.exit(2)

    if draw and not outfile:
        _error('--draw requires --outfile')
        sys.exit(2)

    if sum((binary, draw, pretty)) > 1:
        _error('either --binary or --draw or --pretty')
        sys.exit(2)

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
        model.whitespace = whitespace
        model.nameguard = nameguard

        if binary:
            result = pickle.dumps(model, protocol=2)
        elif pretty:
            result = str(model)
        else:
            result = codegen(model)

        if draw:
            from grako import diagrams
            diagrams.draw(outfile, model)
        elif outfile:
            with codecs.open(outfile, 'w', encoding='utf-8') as f:
                f.write(result)
        else:
            print(result)
    except GrakoException as e:
        _error(e)
        sys.exit(1)

if __name__ == '__main__':
    main()
