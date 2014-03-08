# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from grako.model import Node
from grako.codegen import ModelRenderer, CodeGenerator
import unittest


class Generator(CodeGenerator):
    def __init__(self):
        super(Generator, self).__init__()

    def _find_renderer(self, item):
        name = item.__class__.__name__
        return getattr(self, name, None)

    class Super(ModelRenderer):
        template = 'OK {sub}'

    class Sub(ModelRenderer):
        template = 'and OK too'


class Sub(Node):
    pass


class Super(Node):
    def __init__(self, ctx):
        super(Super, self).__init__(ctx)
        self.sub = Sub(self.ctx)


class TestCodegen(unittest.TestCase):
    def test_basic_codegen(self):
        model = Super(self)
        gen = Generator()
        result = gen.render(model)
        self.assertEqual('OK and OK too', result)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestCodegen)


def load_tests(loader, tests, pattern):
    tests = loader.loadTestsFromTestCase(TestCodegen)
    return tests
