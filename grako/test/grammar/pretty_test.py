# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from grako.util import trim
from grako.tool import genmodel


class PrettyTests(unittest.TestCase):

    def test_pretty(self):
        grammar = '''\
            start = lisp ;
            lisp = sexp | list | symbol;
            sexp::SExp = '(' cons:lisp '.' ~ cdr:lisp ')' ;
            list::List = '(' elements:{sexp}* ')' ;
            symbol::Symbol = value:/[^\s().]+/ ;
        '''

        pretty = trim('''\
            start
                =
                lisp
                ;


            lisp
                =
                sexp | list | symbol
                ;


            sexp::SExp
                =
                '(' cons:lisp '.' ~ cdr:lisp ')'
                ;


            list::List
                =
                '(' elements:{sexp} ')'
                ;


            symbol::Symbol
                =
                value:/[^\s().]+/
                ;
        ''')

        pretty_lean = trim('''\
            start
                =
                lisp
                ;


            lisp
                =
                sexp | list | symbol
                ;


            sexp
                =
                '(' lisp '.' ~ lisp ')'
                ;


            list
                =
                '(' {sexp} ')'
                ;


            symbol
                =
                /[^\s().]+/
                ;
        ''')

        model = genmodel(grammar=grammar)

        self.assertEqual(pretty, model.pretty())
        self.assertEqual(str(model), model.pretty())

        self.assertEqual(pretty_lean, model.pretty_lean())
