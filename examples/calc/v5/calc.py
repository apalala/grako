# this is calc.py
from __future__ import print_function
import sys
from calc_parser import CalcParser
from calc_model import CalcModelBuilderSemantics


def calc(text):
    parser = CalcParser(semantics=CalcModelBuilderSemantics())
    return parser.parse(text)


if __name__ == '__main__':
    text = open(sys.argv[1]).read()
    result = calc(text)
    print(text.strip(), '=', result)
