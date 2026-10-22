"""Coverage controls distinguish requested targets from internal numerator indices."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from tools.audit_target_scope import FAMILIES, audit, main, profile

ROOT = Path(__file__).resolve().parents[1]


class TargetScopeTests(unittest.TestCase):
    def test_dots_and_negative_indices_are_distinct(self):
        self.assertEqual(profile([(3, 1, -2), (3, 1, -2), (1, 1, 0)]), {
            'unique_integrals': 2, 's_histogram': {'0': 1, '2': 1},
            'max_s': 2, 'max_dots': 2, 'max_positive_sum': 4})
        self.assertEqual(profile([])['max_s'], None)
        rank_twenty = profile([(1,) * 8 + (-8, -6, -6)])
        self.assertEqual((rank_twenty['max_s'], rank_twenty['max_dots']), (20, 0))
        dotted = profile([(5, 4)])
        self.assertEqual((dotted['max_s'], dotted['max_dots']), (0, 7))

    def test_all_ten_one_loop_target_sets_have_no_negative_indices(self):
        counts = {'tadpole': 4, 'bubble_massless': 6, 'bubble_equal_mass': 9,
                  'triangle_one_mass': 10, 'bubble_unequal_mass': 14,
                  'triangle_offshell': 22, 'box_massless': 65, 'bubble_one_mass': 15,
                  'triangle_two_mass': 16, 'box_one_mass': 75}
        self.assertCountEqual(FAMILIES, [*counts, 'sunset_equal_mass_v1'])
        for name, count in counts.items():
            with self.subTest(family=name):
                row = audit(name)
                self.assertEqual(row['targets_including_masters']['s_histogram'], {'0': count})
                self.assertEqual(row['negative_index_targets'], [])
                self.assertTrue(row['checker_target_and_master_sets_match'])

    def test_generated_negative_indices_do_not_become_targets(self):
        row = audit('bubble_equal_mass')
        self.assertEqual(row['targets_including_masters']['max_s'], 0)
        self.assertEqual(row['rectangular_seed_indices']['max_s'], 1)
        self.assertEqual(row['generated_ibp_unknowns']['max_s'], 2)
        self.assertEqual(row['generated_ibp_rows'], 30)

    def test_sunset_is_separate_and_only_requests_s_zero_and_one(self):
        row = audit('sunset_equal_mass_v1')
        self.assertEqual(row['suite'], 'sunset-v1')
        self.assertEqual(row['targets_including_masters']['s_histogram'], {'0': 8, '1': 3})
        self.assertEqual(row['non_master_targets']['s_histogram'], {'0': 6, '1': 3})
        self.assertEqual(row['negative_index_targets'], [[1, 1, -1], [2, 1, -1], [2, 2, -1]])
        self.assertEqual(row['rectangular_seed_indices']['unique_integrals'], 16)
        self.assertEqual(row['generated_ibp_rows'], 64)
        self.assertEqual(row['generated_ibp_unknowns']['max_s'], 2)

    def test_drift_from_checker_target_domain_is_rejected(self):
        for changed in [[(1,), (2,), (3,)], [(1,), (2,), (3,), (4,), (4,)],
                        [(1,), (2,), (3,), (4,), (1, -2)]]:
            with self.subTest(targets=changed), patch('tools.audit_target_scope.targets', return_value=changed):
                with self.assertRaisesRegex(ValueError, 'target mismatch or duplicate'):
                    audit('tadpole')

    def test_master_drift_is_rejected(self):
        from ibp.families import family
        f = family('tadpole')
        f['masters'] = [(2,)]
        with patch('tools.audit_target_scope.family', return_value=f):
            with self.assertRaisesRegex(ValueError, 'master mismatch'):
                audit('tadpole')

    def test_cli_claim_gate_uses_requested_target_s_only(self):
        cases = [('bubble_equal_mass', 0, 0), ('bubble_equal_mass', 1, 1),
                 ('sunset_equal_mass_v1', 1, 0), ('sunset_equal_mass_v1', 2, 1)]
        for family, rank, status in cases:
            with self.subTest(family=family, s=rank):
                run = subprocess.run([sys.executable, str(ROOT / 'tools/audit_target_scope.py'),
                                      '--family', family, '--require-target-s', str(rank)],
                                     cwd=ROOT, text=True, capture_output=True)
                self.assertEqual(run.returncode, status, run.stderr)
                report = json.loads(run.stdout)
                self.assertEqual(report['families_missing_required_target_s'], [family] if status else [])

    def test_cli_requires_exact_s_even_when_larger_s_exists(self):
        synthetic = {'family': 'tadpole',
                     'targets_including_masters': {'s_histogram': {'0': 1, '2': 1}}}
        output = io.StringIO()
        with patch('tools.audit_target_scope.audit', return_value=synthetic), \
                patch('sys.argv', ['audit_target_scope.py', '--family', 'tadpole', '--require-target-s', '1']), \
                redirect_stdout(output):
            self.assertEqual(main(), 1)
        self.assertEqual(json.loads(output.getvalue())['families_missing_required_target_s'], ['tadpole'])

    def test_cli_all_families_requires_every_workload(self):
        run = subprocess.run([sys.executable, str(ROOT / 'tools/audit_target_scope.py'),
                              '--require-target-s', '1'], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(run.returncode, 1, run.stderr)
        report = json.loads(run.stdout)
        self.assertEqual(len(report['families']), 11)
        self.assertCountEqual(report['families_missing_required_target_s'], FAMILIES[:-1])


if __name__ == '__main__':
    unittest.main()
