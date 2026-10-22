"""One-loop input checks and synthetic parser controls; never execute native Kira."""
import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from itertools import product
from pathlib import Path

import sympy as S

from ibp.validator import SPECS, SYMBOLS, decode, scaleless
from tools.check_kira import compare, expression
from tools.export_kira_one_loop import inputs

ROOT = Path(__file__).resolve().parents[1]
COUNTS = {
    'tadpole': 3,
    'bubble_massless': 5,
    'bubble_equal_mass': 7,
    'triangle_one_mass': 9,
    'bubble_unequal_mass': 11,
    'triangle_offshell': 18,
    'box_massless': 62,
}


def integral(name, indices):
    return name + '[' + ','.join(map(str, indices)) + ']'


def synthetic_export(certificate):
    """Translate saved rows into Kira syntax, not independent solver evidence."""
    blocks = []
    for output in certificate['outputs']:
        target = output['target']
        row = {tuple(a): decode(c) for a, c in output['row']}
        ordered = [tuple(target)] + [a for a in row if a != tuple(target)]
        blocks.append('\n'.join(
            integral(certificate['family'], a) + '*(' +
            str(-row[a]).replace('**', '^') + ')' for a in ordered))
    return '\n\n'.join(blocks) + '\n'


class OneLoopInputsTests(unittest.TestCase):
    def parse_integrals(self, text, name, dimension):
        result = []
        for line in text.splitlines():
            match = re.fullmatch(re.escape(name) + r'\[(-?\d+(?:,-?\d+)*)\]', line)
            self.assertIsNotNone(match, line)
            indices = tuple(map(int, match[1].split(',')))
            self.assertEqual(len(indices), dimension)
            result.append(indices)
        self.assertEqual(len(result), len(set(result)), 'duplicate integral')
        return set(result)

    def test_geometry_and_generic_invariants_against_validator_specs(self):
        for name in COUNTS:
            masses, distances, _, _ = SPECS[name]
            with self.subTest(family=name):
                files = inputs(name)
                families = json.loads(files['config/integralfamilies.yaml'])['integralfamilies']
                self.assertEqual(len(families), 1)
                family = families[0]
                n = len(masses)
                self.assertEqual(family['name'], name)
                self.assertEqual(family['loop_momenta'], ['k'])
                self.assertEqual(family['top_level_sectors'], [(1 << n) - 1])
                self.assertEqual([p for p, _ in family['propagators']],
                                 ['k'] + ['k+p' + str(i) for i in range(1, n)])
                exported_masses = [S.sympify(m) for _, m in family['propagators']]
                self.assertEqual(exported_masses, [-S.sympify(m) for m in masses])

                kinematics = json.loads(files['config/kinematics.yaml'])['kinematics']
                momenta = ['p' + str(i) for i in range(1, n)]
                self.assertEqual(kinematics['incoming_momenta'], momenta)
                self.assertNotIn('symbol_to_replace_by_one', kinematics)
                if momenta:
                    self.assertEqual(kinematics['outgoing_momenta'], ['q'])
                    eliminated, replacement = kinematics['momentum_conservation']
                    self.assertEqual(eliminated, 'q')
                    self.assertEqual(S.expand(S.sympify(replacement) -
                                              sum(S.Symbol(p) for p in momenta)), 0)
                else:
                    self.assertEqual(kinematics['outgoing_momenta'], [])
                    self.assertNotIn('momentum_conservation', kinematics)
                rules = kinematics['scalarproduct_rules']
                expected_pairs = {(p, q) for i, p in enumerate(momenta) for q in momenta[i:]}
                self.assertEqual({tuple(pair) for pair, _ in rules}, expected_pairs)
                self.assertEqual(len(rules), len(expected_pairs))
                gram = S.zeros(n)
                for (p, q), value in rules:
                    i, j = momenta.index(p) + 1, momenta.index(q) + 1
                    gram[i, j] = gram[j, i] = S.sympify(value)
                for i, j in product(range(n), repeat=2):
                    reconstructed = gram[i, i] + gram[j, j] - 2 * gram[i, j]
                    self.assertEqual(S.cancel(reconstructed - distances[i][j]), 0, (i, j))
                symbols = set().union(*(S.sympify(x).free_symbols for x in
                                        masses + [x for row in distances for x in row]))
                self.assertEqual(kinematics['kinematic_invariants'],
                                 [[str(symbol), 2] for symbol in sorted(symbols, key=str)])
                exported_symbols = set().union(*(x.free_symbols for x in exported_masses + list(gram)))
                self.assertEqual(exported_symbols, symbols)

    def test_targets_basis_and_jobs_against_validator_specs(self):
        for name in COUNTS:
            masses, distances, masters, rmax = SPECS[name]
            with self.subTest(family=name):
                files = inputs(name)
                n = len(masses)
                required = {a for a in product(range(rmax + 1), repeat=n)
                            if 0 < sum(a) <= rmax and not scaleless(a, masses, distances)} - set(masters)
                self.assertEqual(len(required), COUNTS[name])
                self.assertEqual(self.parse_integrals(files['targets'], name, n), required)
                self.assertEqual(self.parse_integrals(files['masters'], name, n), set(masters))
                jobs = json.loads(files['jobs.yaml'])['jobs']
                self.assertEqual(len(jobs), 2)
                reduction = jobs[0]['reduce_sectors']
                self.assertEqual(reduction['reduce'], [{'sectors': [(1 << n) - 1], 'r': rmax, 's': 1}])
                self.assertEqual(reduction['select_integrals'], {'select_mandatory_list': [[name, 'targets']]})
                self.assertEqual(reduction['preferred_masters'], 'masters')
                for flag in ('run_initiate', 'run_triangular', 'run_back_substitution'):
                    self.assertIs(reduction[flag], True)
                self.assertEqual(jobs[1], {'kira2file': {'target': [[name, 'targets']]}})

    def test_cli_writes_all_seven_families_without_running_solver(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / 'inputs'
            command = [sys.executable, str(ROOT / 'tools/export_kira_one_loop.py'), '--out', str(out)]
            run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
            report = json.loads(run.stdout)
            self.assertEqual(report['families'], 7)
            self.assertEqual(report['files'], 35)
            self.assertIs(report['solver_executed'], False)
            self.assertEqual({p.name for p in out.iterdir() if p.is_dir()}, set(COUNTS))
            hashes = {}
            for name in COUNTS:
                for relative, expected in inputs(name).items():
                    path = out / name / relative
                    self.assertEqual(path.read_text(), expected)
                    hashes[str(path.relative_to(out))] = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(json.loads((out / 'manifest.json').read_text())['files_sha256'], hashes)
            manifest_before = (out / 'manifest.json').read_bytes()
            repeated = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(repeated.returncode, 0)
            self.assertEqual((out / 'manifest.json').read_bytes(), manifest_before)


class SyntheticOneLoopComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificates = {name: json.loads((ROOT / 'results/certificates' / (name + '-sparse.json')).read_text())
                            for name in COUNTS}
        cls.tadpole = cls.certificates['tadpole']
        cls.text = synthetic_export(cls.tadpole)

    def test_synthetic_exports_of_all_seven_sparse_certificates(self):
        for name, certificate in self.certificates.items():
            with self.subTest(family=name):
                text = synthetic_export(certificate)
                for output, block in zip(certificate['outputs'], text.strip().split('\n\n')):
                    self.assertEqual(block.splitlines()[0], integral(name, output['target']) + '*(-1)')
                self.assertEqual(compare(text, certificate), COUNTS[name])

    def test_cli_with_analytic_tadpole_control(self):
        # Gamma-function recurrence, written independently of encoded certificate rows.
        text = ('tadpole[2]*(-1)\ntadpole[1]*((2-d)/(2*m))\n\n'
                'tadpole[3]*(-1)\ntadpole[1]*((2-d)*(4-d)/(8*m^2))\n\n'
                'tadpole[4]*(-1)\ntadpole[1]*((2-d)*(4-d)*(6-d)/(48*m^3))\n')
        with tempfile.TemporaryDirectory() as temporary:
            export = Path(temporary) / 'synthetic-analytic-tadpole.kira'
            export.write_text(text)
            command = [sys.executable, str(ROOT / 'tools/check_kira.py'),
                       '--certificate', str(ROOT / 'results/certificates/tadpole-sparse.json'),
                       '--export', str(export)]
            run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(run.stdout)['rows'][0]['exact_identities'], 3)
            export.write_text(text.replace('(2-d)', '(3-d)', 1))
            self.assertNotEqual(subprocess.run(command, cwd=ROOT, capture_output=True).returncode, 0)

    def test_synthetic_wrong_coefficients_including_sample_invisible_error(self):
        d = SYMBOLS[0]
        perturbation = (d - 4) * (d - 6) * (d - 8)
        self.assertTrue(all(perturbation.subs(d, sample) == 0 for sample in (4, 6, 8)))
        self.assertNotEqual(S.expand(perturbation), 0)
        lines = self.text.splitlines()
        prefix, coefficient = lines[1].split('*(', 1)
        for error in ('1', '(d-4)*(d-6)*(d-8)'):
            with self.subTest(error=error):
                altered = lines.copy()
                altered[1] = prefix + '*((' + coefficient[:-1] + ')+(' + error + '))'
                with self.assertRaisesRegex(ValueError, 'coefficient disagreement'):
                    compare('\n'.join(altered), self.tadpole)

    def test_synthetic_malformed_targets_families_dimensions_and_basis(self):
        blocks = self.text.strip().split('\n\n')
        lines = blocks[0].splitlines()
        wrong_dimension = lines[0].replace(']', ',0]', 1)
        wrong_master = lines[1].replace('tadpole[1]', 'tadpole[99]')
        controls = {
            'empty': '',
            'missing target': '\n\n'.join(blocks[1:]),
            'duplicate target': self.text + '\n' + blocks[0],
            'duplicate master': '\n'.join(lines + [lines[1]]) + '\n\n' + '\n\n'.join(blocks[1:]),
            'wrong family': self.text.replace('tadpole[', 'bubble_massless['),
            'wrong dimension': self.text.replace(lines[0], wrong_dimension, 1),
            'invalid basis': self.text.replace(lines[1], wrong_master, 1),
            'extra zero basis term': blocks[0] + '\ntadpole[99]*(0)\n\n' + '\n\n'.join(blocks[1:]),
            'wrong target normalization': self.text.replace('*(-1)', '*(1)', 1),
            'master before target': '\n'.join(reversed(lines)) + '\n\n' + '\n\n'.join(blocks[1:]),
        }
        for label, text in controls.items():
            with self.subTest(control=label), self.assertRaises(ValueError):
                compare(text, self.tadpole)

    def test_synthetic_export_cannot_validate_a_tampered_certificate(self):
        certificate = copy.deepcopy(self.tadpole)
        certificate['outputs'][0]['row'][0][1][0][0][1] += 1
        with self.assertRaisesRegex(ValueError, 'Certificate/result mismatch'):
            compare(synthetic_export(certificate), certificate)

    def test_generic_exact_expression_symbols_and_arithmetic(self):
        d, s, t, m, u = SYMBOLS
        expected = (d + s - t) / (m + u) + s**2 / 2 - 1 / (u**2)
        self.assertEqual(S.cancel(expression('(+d+s-t)/(m+u)+s^2/2-u^-2') - expected), 0)
        self.assertEqual(expression('d+s+t+m+u').free_symbols, set(SYMBOLS))

    def test_synthetic_coefficients_reject_unsafe_or_inexact_expressions(self):
        for value in ('abs(d)', '__import__("os")', 'unknown', 'pi', '1.0', 'True',
                      '1/0', '1/(s-s)', '0^(-1)', 'd^s', 'd[0]', 'd.real'):
            with self.subTest(expression=value), self.assertRaises(ValueError):
                compare(self.text.replace('*(-1)', '*(-1+0*(' + value + '))', 1), self.tadpole)

    def test_synthetic_coefficients_reject_algebraically_zero_denominators(self):
        # Structural equality misses this zero; SymPy otherwise erases 0/zero.
        denominator = '((s^2-1)/(s-1)-s-1)'
        for value in ('0/' + denominator, '0*' + denominator + '^(-1)'):
            with self.subTest(expression=value), self.assertRaises(ValueError):
                compare(self.text.replace('*(-1)', '*(-1+(' + value + '))', 1), self.tadpole)


if __name__ == '__main__':
    unittest.main()
