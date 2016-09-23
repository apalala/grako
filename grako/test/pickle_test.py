import unittest
import pickle

from grako.semantics import ModelBuilderSemantics
from grako.tool import genmodel


class PickleTest(unittest.TestCase):

    def test_synth_model(self):
        grammar = '''
            start::ASeq
                =
                values:aseq
                $
                ;

            aseq
                =
                {'a'}+
                ;
        '''

        m = genmodel('ASeq', grammar)
        model = m.parse('a a a', semantics=ModelBuilderSemantics())
        self.assertEqual('ASeq', type(model).__name__)

        p = pickle.dumps(model)
        new_model = pickle.loads(p)
        self.assertEqual('ASeq', type(new_model).__name__)

        self.assertEqual(model._ast, new_model._ast)
