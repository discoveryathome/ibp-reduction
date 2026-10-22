"""Audit requested targets separately from seeds and generated IBP unknowns."""
import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ibp.families import NAMES, equations, family, targets
from ibp.trial import NEW
from ibp.validator import SPECS, scaleless
from ibp.two_loop_check import MASTERS, REQUIRED

FAMILIES = NAMES + NEW + ['sunset_equal_mass_v1']
SOURCES = ['ibp/families.py', 'ibp/trial.py', 'ibp/two_loop.py',
           'ibp/validator.py', 'ibp/two_loop_check.py', 'tools/audit_target_scope.py']


def profile(indices):
    """s counts negative index powers, not a universal tensor numerator degree."""
    unique = set(indices)
    counts = Counter(sum(max(-x, 0) for x in a) for a in unique)
    return {
        'unique_integrals': len(unique),
        's_histogram': {str(s): counts[s] for s in sorted(counts)},
        'max_s': max(counts, default=None),
        'max_dots': max((sum(max(x-1, 0) for x in a) for a in unique), default=None),
        'max_positive_sum': max((sum(max(x, 0) for x in a) for a in unique), default=None),
    }


def checker_domain(name):
    if name == 'sunset_equal_mass_v1':
        return set(REQUIRED) | set(MASTERS), set(MASTERS)
    masses, distances, masters, rmax = SPECS[name]
    allowed = {a for a in product(range(rmax+1), repeat=len(masses))
               if 0 < sum(a) <= rmax and not scaleless(a, masses, distances)}
    return allowed, set(masters)


def audit(name):
    f = family(name)
    requested = list(targets(f))
    expected, masters = checker_domain(name)
    if len(requested) != len(set(requested)) or set(requested) != expected:
        raise ValueError(f'{name}: producer/checker target mismatch or duplicate')
    if set(f['masters']) != masters or not masters <= expected:
        raise ValueError(f'{name}: producer/checker master mismatch')
    rows = list(equations(f, 'rectangular'))
    seeds = {a for a, _, _ in rows}
    unknowns = {a for _, _, row in rows for a in row}
    return {
        'family': name,
        'suite': 'initial' if name in NAMES else 'contributor-trial' if name in NEW else 'sunset-v1',
        'split': f['split'],
        'targets_including_masters': profile(requested),
        'non_master_targets': profile(set(requested) - masters),
        'masters': [list(a) for a in sorted(masters)],
        'negative_index_targets': [list(a) for a in sorted(requested) if min(a) < 0],
        'rectangular_seed_indices': profile(seeds),
        'generated_ibp_unknowns': profile(unknowns),
        'generated_ibp_rows': len(rows),
        'nonempty_generated_ibp_rows': sum(bool(row) for _, _, row in rows),
        'checker_target_and_master_sets_match': True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family', choices=FAMILIES, help='Default: all 11 local workloads.')
    parser.add_argument('--require-target-s', type=int,
                        help='Fail unless each selected family requests at least one target with this exact s.')
    args = parser.parse_args()
    if args.require_target_s is not None and args.require_target_s < 0:
        parser.error('--require-target-s must be nonnegative')
    rows = [audit(name) for name in ([args.family] if args.family else FAMILIES)]
    missing = [] if args.require_target_s is None else [
        row['family'] for row in rows
        if str(args.require_target_s) not in row['targets_including_masters']['s_histogram']]
    report = {
        'schema': 'ibp-target-scope/v1',
        'definition': 's(a)=sum_i max(-a_i,0); dots(a)=sum_i max(a_i-1,0).',
        'scope': 'Live local target/seed/IBP-index enumeration, not certificate replay or a tube-seeding performance experiment.',
        'seed_policy': 'rectangular; actual family equation generator, before elimination and any fallback',
        'generated_ibp_note': 'Only direct IBP rows, excluding separately inserted symmetry equations; unknowns are not requested targets.',
        'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES},
        'families': rows,
        'required_target_s': args.require_target_s,
        'families_missing_required_target_s': missing,
    }
    print(json.dumps(report, indent=2))
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
