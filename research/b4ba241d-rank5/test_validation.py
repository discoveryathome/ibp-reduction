"""Reject altered operators/certificates and replay the four archived witnesses."""

import argparse
import ast
import copy
import json
import math
from pathlib import Path
import re
import unittest

import finite_field as F
import identities as I

CERTIFICATES = Path(__file__).resolve().parent / 'results/fields'


class OperatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = I.source_templates()
        cls.derived, cls.determinant = I.derived_templates()

    def test_exact_bijective_match(self):
        matches = I.match_templates(self.source, self.derived)
        self.assertEqual(len({m['operator'] for m in matches}), 18)
        self.assertEqual(self.determinant, '512')

    def test_denominator_vectors_match_source_order(self):
        text = (I.HERE / 'fixtures/source-config/integralfamilies.yaml').read_text()
        source = re.findall(r'\[\s*"([^"]+)"\s*,\s*0\s*\]', text)
        names = ('l1', 'l2', 'p1', 'p2', 'p3', 'p4')
        expected = []
        for vector in I.VECTORS:
            self.assertTrue(all(c in (-1, 0, 1) for c in vector))
            expected.append(''.join(('+' if c > 0 else '-') + name
                                    for name, c in zip(names, vector) if c).lstrip('+'))
        self.assertEqual(source, expected)

    def test_massless_five_point_invariants(self):
        gram = I.external_gram()
        vectors = [I.S.eye(4)[:, i] for i in range(4)]
        vectors.append(-sum(vectors, I.S.zeros(4, 1)))
        for vector in vectors:
            self.assertEqual(I.S.expand((vector.T * gram * vector)[0]), 0)
        for i, invariant in enumerate((I.S.Integer(1), *I.M)):
            vector = vectors[i] + vectors[(i + 1) % 5]
            self.assertEqual(I.S.expand((vector.T * gram * vector)[0] - invariant), 0)

    def test_changed_shift_rejected(self):
        mutant = copy.deepcopy(self.source)
        old = min(mutant[0])
        shifted = (old[0] + 3,) + old[1:]
        self.assertNotIn(shifted, mutant[0])
        mutant[0][shifted] = mutant[0].pop(old)
        with self.assertRaises(ValueError):
            I.match_templates(mutant, self.derived)

    def test_missing_and_duplicate_operator_rejected(self):
        for mutant in (self.source[:-1], [self.source[0], *self.source[:-1]]):
            with self.subTest(count=len(mutant)), self.assertRaises(ValueError):
                I.match_templates(mutant, self.derived)

    def test_restricted_coefficient_parser(self):
        self.assertEqual(I.expression('a0/2 + 1'), I.A[0]/2 + 1)
        for text in ('f(a0)', 'a0.real', 'unknown', '1.5', 'a0**9', 'a0/0'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                I.expression(text)


class WitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificates = {
            (mode, sample): json.loads((CERTIFICATES / f'{mode}-{sample}.json').read_text())
            for mode in ('tube', 'decreasing') for sample in (0, 1)
        }

    def test_all_original_row_witnesses(self):
        for key, certificate in self.certificates.items():
            with self.subTest(case=key):
                self.assertTrue(F.verify(certificate)['valid'])

    def test_matching_fixed_master_coefficients(self):
        def coefficients(c):
            return {tuple(a): value for a, value in c['coefficients']}
        for sample in (0, 1):
            self.assertEqual(coefficients(self.certificates['tube', sample]),
                             coefficients(self.certificates['decreasing', sample]))

    def test_changed_master_coefficient_rejected(self):
        mutant = copy.deepcopy(self.certificates['tube', 0])
        value = mutant['coefficients'][0][1]
        mutant['coefficients'][0][1] = value + 1 if value < mutant['prime'] - 1 else value - 1
        with self.assertRaisesRegex(ValueError, 'witness disagreement'):
            F.verify(mutant)

    def test_changed_witness_weight_rejected(self):
        mutant = copy.deepcopy(self.certificates['tube', 0])
        value = mutant['witness'][0][1]
        mutant['witness'][0][1] = value + 1 if value < mutant['prime'] - 1 else value - 1
        with self.assertRaisesRegex(ValueError, 'witness disagreement'):
            F.verify(mutant)

    def test_omitted_original_row_rejected(self):
        mutant = copy.deepcopy(self.certificates['tube', 0])
        mutant['witness'].pop(0)
        with self.assertRaisesRegex(ValueError, 'witness disagreement'):
            F.verify(mutant)

    def test_duplicate_original_row_rejected(self):
        mutant = copy.deepcopy(self.certificates['tube', 0])
        mutant['witness'].insert(1, mutant['witness'][0])
        with self.assertRaisesRegex(ValueError, 'invalid witness entry'):
            F.verify(mutant)

    def test_metadata_mutations_rejected(self):
        original = self.certificates['tube', 0]
        changes = {
            'mode': 'unknown', 'sample': -1, 'prime': 101,
            'point': dict(original['point'], d=24), 'target': [0]*11,
            'seed_count': original['seed_count'] - 1,
            'raw_operator_rows': original['raw_operator_rows'] - 18,
            'source_template_sha256': '0'*64, 'master_fixture_sha256': '0'*64,
            'master_convention': original['master_convention'][:-1],
        }
        for field, value in changes.items():
            mutant = dict(original, **{field: value})
            with self.subTest(field=field), self.assertRaises(ValueError):
                F.verify(mutant)

    def test_separate_field_expression_evaluator(self):
        def evaluate(text):
            return F.evaluate(ast.parse(text, mode='eval').body, {'a0': 7}, 101)
        self.assertEqual(evaluate('a0/2 + 3'), 57)
        self.assertEqual(evaluate('2**-1'), 51)
        for text in ('f(a0)', 'a0.real', 'unknown', '1.5', 'a0**9', 'a0/0'):
            with self.subTest(text=text), self.assertRaises((ValueError, ZeroDivisionError)):
                evaluate(text)

    def test_decreasing_rank_cardinality(self):
        trivial, _ = F.model()
        expected = 0
        for sector in range(256):
            if sector & 165 != 165 or sector in trivial:
                continue
            positive = sector.bit_count()
            cap = max(1, 5 + positive - 8 + int(sector & ~167 == 0))
            expected += math.comb(11 - positive + cap, cap)
        self.assertEqual(expected, 876)
        self.assertEqual(len(F.seeds('decreasing')), expected)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificates', type=Path, default=CERTIFICATES)
    args, remaining = parser.parse_known_args()
    CERTIFICATES = args.certificates
    unittest.main(argv=[__file__, *remaining])
