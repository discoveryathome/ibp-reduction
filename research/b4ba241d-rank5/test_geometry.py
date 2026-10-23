"""Check the separate field linear algebra and frozen seed/point boundaries."""
import json
import unittest

import geometry_verify as G


class GeometricReplayTests(unittest.TestCase):
    def test_field_inverse_and_singular_map(self):
        inverse,determinant=G.inverse([[1,2],[3,5]],101)
        self.assertEqual(inverse,[[96,2],[3,100]])
        self.assertEqual(determinant,100)
        with self.assertRaises(ValueError):G.inverse([[1,2],[2,4]],101)

    def test_restricted_momentum_parser(self):
        self.assertEqual(G.momentum('l1+l2-p4'),(1,1,0,0,0,-1))
        for text in ('f(l1)','l1*l2','p5','1'):
            with self.subTest(text=text),self.assertRaises(ValueError):G.momentum(text)

    def test_frozen_sample_and_basis_metadata(self):
        certificate=json.loads((G.HERE/'results/fields/tube-0.json').read_text())
        for key,value in [('sample',-1),('point',dict(certificate['point'],d=24)),('master_convention',[])]:
            mutant=dict(certificate,**{key:value})
            with self.subTest(key=key),self.assertRaises(ValueError):G.verify(mutant)


if __name__=='__main__':unittest.main()
