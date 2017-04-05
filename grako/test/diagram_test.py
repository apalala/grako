# -*- coding: utf-8 -*-
# Copyright (C) 2017      by Juancarlo Añez
# Copyright (C) 2012-2016 by Juancarlo Añez and Thomas Bragg

# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import unittest
from grako.tool import compile


class DiagramTests(unittest.TestCase):

    def test_dot(self):
        grammar = '''
            start = "foo\\nbar" $;
        '''
        try:
            from grako.diagrams import draw
        except ImportError:
            return

        m = compile(grammar, 'Diagram')
        draw('tmp/diagram.png', m)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(DiagramTests)


def main():
    unittest.TextTestRunner(verbosity=2).run(suite())


if __name__ == '__main__':
    main()
