# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


def main():
    import unittest
    from grako.test import bootstrap_test
    from grako.test import buffering_test
    from grako.test import ast_test
    from grako.test import grammar_test
    from grako.test import codegen_test
    from grako.test import parsing_test
    from grako.test import diagram_test

    suite = unittest.TestSuite(tests=[
        bootstrap_test.suite(),
        buffering_test.suite(),
        ast_test.suite(),
        grammar_test.suite(),
        codegen_test.suite(),
        parsing_test.suite(),
        grammar_test.suite(),
        diagram_test.suite(),
    ])

    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    main()
