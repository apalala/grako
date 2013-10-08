# -*- coding: utf-8 -*-
"""
The Grako test suite.
"""
from __future__ import print_function, division, absolute_import, unicode_literals

if __name__ == '__main__':
    import unittest
    from . import bootstrap_tests
    from . import buffering_test
    from . import grammar_tests

    bootstrap_tests.main()

    suite = unittest.TestSuite(tests=[
        buffering_test.suite(),
        grammar_tests.suite()
    ])

    unittest.TextTestRunner(verbosity=2).run(suite)
