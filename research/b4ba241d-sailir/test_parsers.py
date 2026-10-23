"""Keep numerical coefficients, image coverage and momentum forms restricted."""
from fractions import Fraction
import unittest

import basis_relation as B
import verify_saved as V


class ParserTests(unittest.TestCase):
    def test_rational_coefficients_and_poles(self):
        self.assertEqual(V.rational('-(3+1)/8 + 2^(-1)'),0)
        self.assertEqual(V.field(Fraction(1,2)),505)
        with self.assertRaises(ValueError):V.field(Fraction(1,1009))
        for text in ('f(1)','d','1.5','True','2**17'):
            with self.subTest(text=text),self.assertRaises(ValueError):V.rational(text)

    def test_export_requires_normalization_and_declared_masters(self):
        target=V.TARGET;master=(1,1,1,1,1,1,0)
        name=lambda a:'trianglebox['+','.join(map(str,a))+']'
        text=name(target)+'*(-1)\n'+name(master)+'*(1/2)'
        self.assertEqual(V.parse(text,{master}),{target:{master:Fraction(1,2)}})
        with self.assertRaises(ValueError):V.parse(text,set())
        with self.assertRaises(ValueError):V.parse(text.replace('*(-1)','*(-2)'),{master})

    def test_linear_momentum_parser(self):
        self.assertEqual(B.momentum('k2-p1'),(0,1,-1,0))
        for text in ('f(k1)','k1*k2','p2','1'):
            with self.subTest(text=text),self.assertRaises(ValueError):B.momentum(text)


if __name__=='__main__':unittest.main()
