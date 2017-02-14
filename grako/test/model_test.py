# -*- coding: utf-8 -*-
# Copyright (C) 2017      by Juancarlo Añez
# Copyright (C) 2012-2016 by Juancarlo Añez and Thomas Bragg
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from grako.objectmodel import Node


class ModelTests(unittest.TestCase):
    def test_node_kwargs(self):
        class Atom(Node):
            def __init__(self, arguments=None, symbol=None, **_kwargs_):
                super(Atom, self).__init__(
                    arguments=arguments,
                    symbol=symbol,
                    **_kwargs_
                )

        atom = Atom(symbol='foo', ast={})
        self.assertIsNotNone(atom.symbol)
        self.assertEqual(atom.symbol, 'foo')

        atom = Atom(symbol='foo')
        self.assertIsNotNone(atom.symbol)
        self.assertEqual(atom.symbol, 'foo')
