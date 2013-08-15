# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
import unittest
from grako.tool import genmodel


class GrammarTests(unittest.TestCase):
    def test_keywords_in_rule_names(self):
        grammar = '''
            start
                =
                whitespace
                ;

            whitespace
                =
                    {'x'}+
                ;
        '''
        m = genmodel('Keywords', grammar)
        m.parse('x')

    def test_update_ast(self):
        grammar = '''
            foo = name:"1" [ name: bar ] ;
            bar = { "2" } * ;
        '''
        m = genmodel('Keywords', grammar)
        ast = m.parse('1 2')
        self.assertEqual(ast.name, ['1', '2'])
        

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(GrammarTests)


def main():
    unittest.TextTestRunner(verbosity=2).run(suite())

if __name__ == '__main__':
    main()
