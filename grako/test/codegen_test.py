# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

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


class Sub(object):
    pass


class Super(object):
    def __init__(self):
        self.sub = Sub()


class TestCodegen(unittest.TestCase):
    def test_basic_codegen(self):
        model = Super()
        gen = Generator()
        result = gen.render(model)
        self.assertEqual('OK and OK too', result)

def load_tests(loader, tests, pattern):
    tests = loader.loadTestsFromTestCase(TestCodegen)
    return tests
