# -*- coding: utf-8 -*-
"""
This awkward set of tests tries to make Grako bang its head against iself.
"""
from __future__ import print_function, division, absolute_import, unicode_literals
import sys
sys.path.append('tmp')
import os
import shutil
import json
import pickle
import unittest
from grako.model import NodeTraverser
from grako.semantics import GrakoSemantics
from grako.bootstrap import (GrakoParser,
                             GrakoGrammarGenerator,
                             COMMENTS_RE
                             )


class BootstrapTests(unittest.TestCase):

    def test_bootstrap(self):
        print()

        if os.path.isfile('tmp/00.ast'):
            shutil.rmtree('tmp')
        if not os.path.isdir('tmp'):
            os.mkdir('tmp')
        print('-' * 20, 'phase 00 - parse using the bootstrap grammar')
        with open('etc/grako.ebnf') as f:
            text = str(f.read())
        g = GrakoParser('Grako', parseinfo=False)
        grammar0 = g.parse(text)
        ast0 = json.dumps(grammar0, indent=2)
        with open('tmp/00.ast', 'w') as f:
            f.write(ast0)

        print('-' * 20, 'phase 01 - parse with parser generator')
        with open('etc/grako.ebnf') as f:
            text = str(f.read())
        g = GrakoGrammarGenerator('Grako', parseinfo=False)
        g.parse(text, trace=False)

        generated_grammar1 = str(g.ast['grammar'])
        with open('tmp/01.ebnf', 'w') as f:
            f.write(generated_grammar1)

        print('-' * 20, 'phase 02 - parse previous output with the parser generator')
        with open('tmp/01.ebnf', 'r') as f:
            text = str(f.read())
        g = GrakoGrammarGenerator('Grako')
        g.parse(text, trace=False)
        generated_grammar2 = str(g.ast['grammar'])
        with open('tmp/02.ebnf', 'w') as f:
            f.write(generated_grammar2)
        self.assertEqual(generated_grammar2, generated_grammar1)

        print('-' * 20, 'phase 03 - repeat')
        with open('tmp/02.ebnf') as f:
            text = f.read()
        g = GrakoParser('Grako', parseinfo=False)
        ast3 = g.parse(text)
        with open('tmp/03.ast', 'w') as f:
            f.write(json.dumps(ast3, indent=2))

        print('-' * 20, 'phase 04 - repeat')
        with open('tmp/02.ebnf') as f:
            text = f.read()
        g = GrakoGrammarGenerator('Grako')
        g.parse(text)
        parser = g.ast['grammar']
    #    pprint(parser.first_sets, indent=2, depth=3)
        generated_grammar4 = str(parser)
        with open('tmp/04.ebnf', 'w') as f:
            f.write(generated_grammar4)
        self.assertEqual(generated_grammar4, generated_grammar2)

        print('-' * 20, 'phase 05 - parse using the grammar model')
        with open('tmp/04.ebnf') as f:
            text = f.read()
        ast5 = parser.parse(text)
        with open('tmp/05.ast', 'w') as f:
            f.write(json.dumps(ast5, indent=2))

        print('-' * 20, 'phase 06 - generate parser code')
        gencode6 = parser.codegen()
        with open('tmp/g06.py', 'w') as f:
            f.write(gencode6)

        print('-' * 20, 'phase 07 - import generated code')
        from g06 import GrakoParser as GenParser  # @UnresolvedImport

        print('-' * 20, 'phase 08 - compile using generated code')
        parser = GenParser(trace=False)
        result = parser.parse(text, 'grammar')
        self.assertEqual(result, parser.ast['grammar'])
        ast8 = parser.ast['grammar']
        json8 = json.dumps(ast8, indent=2)
        open('tmp/08.ast', 'w').write(json8)
        self.assertEqual(ast5, ast8)

        print('-' * 20, 'phase 09 - Generate parser with semantics')
        with open('etc/grako.ebnf') as f:
            text = f.read()
        parser = GrakoGrammarGenerator('Grako')
        g9 = parser.parse(text)
        generated_grammar9 = str(g9)
        with open('tmp/09.ebnf', 'w') as f:
            f.write(generated_grammar9)
        self.assertEqual(generated_grammar9, generated_grammar1)

        print('-' * 20, 'phase 10 - Parse with a model using a semantics')
        g10 = g9.parse(text,
                    start_rule='grammar',
                    semantics=GrakoSemantics('Grako'),
                    comments_re=COMMENTS_RE
                    )
        generated_grammar10 = str(g10)
        with open('tmp/10.ebnf', 'w') as f:
            f.write(generated_grammar10)
        gencode10 = g10.codegen()
        with open('tmp/g10.py', 'w') as f:
            f.write(gencode10)

        print('-' * 20, 'phase 11 - Pickle the model and try again.')
        with open('tmp/11.grako', 'wb') as f:
            pickle.dump(g10, f, protocol=2)
        with open('tmp/11.grako', 'rb') as f:
            g11 = pickle.load(f)
        r11 = g11.parse(text,
                        start_rule='grammar',
                        semantics=GrakoSemantics('Grako'),
                        comments_re=COMMENTS_RE
                        )
        with open('tmp/11.ebnf', 'w') as f:
            f.write(str(110))
        gencode11 = r11.codegen()
        with open('tmp/g11.py', 'w') as f:
            f.write(gencode11)

        print('-' * 20, 'phase 12 - Traverser')

        class PrintNameTraverser(NodeTraverser):
            def __init__(self):
                self.traversed = []

            def traverse(self, o):
                self.traversed.append(o.__class__.__name__)
                super(PrintNameTraverser, self).traverse(o)

        v = PrintNameTraverser()
        v.traverse(g11)
        with open('tmp/12.txt', 'w') as f:
            f.write('\n'.join(v.traversed))

        print('-' * 20, 'phase 13 - Graphics')
        try:
            from grako.diagrams import draw
        except:
            print('PyGraphViz not found!')
        else:
            draw('tmp/13.png', g11)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BootstrapTests)


def main():
    unittest.TextTestRunner(verbosity=2).run(suite())

if __name__ == '__main__':
    main()
