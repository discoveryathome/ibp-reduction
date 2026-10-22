"""Prepare Kira 3 inputs for the frozen one-loop suite; does not run Kira."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ibp.families import NAMES, family, targets

KIRA_COMMIT = 'fb745431f97c8899a512e638da8598b0cfad7521'


def integral(name, indices):
    return name + '[' + ','.join(map(str, indices)) + ']'


def inputs(name):
    if name not in NAMES:
        raise ValueError('Only the seven frozen one-loop families are supported')
    f = family(name)
    momenta = ['p' + str(i) for i in range(1, f['n'])]
    rules = []
    for i in range(1, f['n']):
        for j in range(i, f['n']):
            dot = (f['distances'][0][i] + f['distances'][0][j] - f['distances'][i][j]) / 2
            rules.append([[momenta[i-1], momenta[j-1]], str(dot)])
    symbols = set()
    for value in f['masses'] + [x for row in f['distances'] for x in row]:
        symbols.update(map(str, value.as_expr().free_symbols))
    sector = (1 << f['n']) - 1
    masters = set(f['masters'])
    requested = [a for a in targets(f) if a not in masters]
    kinematics = {
        'incoming_momenta': momenta,
        'outgoing_momenta': ['q'] if momenta else [],
        'kinematic_invariants': [[s, 2] for s in sorted(symbols)],
        'scalarproduct_rules': rules,
    }
    if momenta:
        # Eliminate only the dummy momentum, leaving all propagator shifts independent.
        kinematics['momentum_conservation'] = ['q', '+'.join(momenta)]
    documents = {
        'config/integralfamilies.yaml': {'integralfamilies': [{
            'name': name,
            'loop_momenta': ['k'],
            'top_level_sectors': [sector],
            'propagators': [[('k' if i == 0 else 'k+p' + str(i)), str(-mass)]
                            for i, mass in enumerate(f['masses'])],
        }]},
        'config/kinematics.yaml': {'kinematics': kinematics},
        'jobs.yaml': {'jobs': [
            {'reduce_sectors': {
                'reduce': [{'sectors': [sector], 'r': f['rmax'], 's': 1}],
                'select_integrals': {'select_mandatory_list': [[name, 'targets']]},
                'preferred_masters': 'masters',
                'run_initiate': True,
                'run_triangular': True,
                'run_back_substitution': True,
            }},
            {'kira2file': {'target': [[name, 'targets']]}},
        ]},
    }
    # JSON is a YAML subset, so no additional YAML dependency is needed.
    files = {path: json.dumps(document, indent=2) + '\n' for path, document in documents.items()}
    files['targets'] = ''.join(integral(name, a) + '\n' for a in requested)
    files['masters'] = ''.join(integral(name, a) + '\n' for a in f['masters'])
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True, help='New output directory; existing directories are never overwritten.')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for name in NAMES:
        for relative, text in inputs(name).items():
            path = args.out / name / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            hashes[str(path.relative_to(args.out))] = hashlib.sha256(path.read_bytes()).hexdigest()
    sources = ['ibp/families.py', 'ibp/validator.py', 'tools/check_kira.py',
               'tools/export_kira_one_loop.py', 'requirements.txt']
    sources += ['results/certificates/' + name + '-sparse.json' for name in NAMES]
    manifest = {
        'scope': 'Seven frozen one-loop families; native Kira execution is not performed by this exporter.',
        'kira_commit': KIRA_COMMIT,
        'conventions': 'D_i=(k+r_i)^2+m_i; r_0=0, r_i=p_i; supplied Kira mass squared is -m_i. No Wick-rotation sign change.',
        'targets': 'All non-scaleless frozen targets excluding the explicitly listed masters (trivial identities).',
        'files_sha256': hashes,
        'sources_sha256': {s: hashlib.sha256((ROOT / s).read_bytes()).hexdigest() for s in sources},
    }
    (args.out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'directory': str(args.out), 'families': len(NAMES), 'files': len(hashes), 'solver_executed': False}))


if __name__ == '__main__':
    main()
