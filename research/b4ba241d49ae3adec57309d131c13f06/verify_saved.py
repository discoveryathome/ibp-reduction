"""Author replay of archived native exports, source bindings, and failure controls."""

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from run_native import PREDECESSOR, FAMILIES, check_family, digest, master_set

HERE = Path(__file__).resolve().parent


def reject(label, function):
    try:
        function()
    except (ValueError, OSError):
        return label
    raise AssertionError('invalid evidence accepted: ' + label)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--predecessor', type=Path, required=True)
    parser.add_argument('--data', type=Path, default=HERE / 'native')
    args = parser.parse_args()
    project, data = args.predecessor.resolve(), args.data.resolve()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=project, text=True).strip()
    if revision != PREDECESSOR:
        raise ValueError('wrong predecessor commit')
    subprocess.run(['git', 'diff', '--exit-code', 'HEAD'], cwd=project, check=True,
                   stdout=subprocess.DEVNULL)
    sys.path.insert(0, str(project))
    from tools.check_kira import compare, expression
    from ibp.validator import exact_zero, D, m

    manifest = json.loads((data / 'manifest.json').read_text())
    for directory, key in ((project, 'sources_sha256'), (data, 'files_sha256')):
        for relative, expected in manifest[key].items():
            if digest(directory / relative) != expected:
                raise ValueError('changed bound source/input: ' + relative)
    receipts = json.loads((data / 'run-receipts.json').read_text())
    if len(receipts) != len(FAMILIES) or {r['family'] for r in receipts} != set(FAMILIES):
        raise ValueError('missing or duplicate family receipt')
    checks = []
    for row in receipts:
        name = row['family']
        actual = check_family(project, data / name, name, compare)
        if row.get('returncode') != 0 or row.get('valid') is not True:
            raise ValueError('failed native run: ' + name)
        for key, value in actual.items():
            if row[key] != value:
                raise ValueError('receipt differs from evidence: ' + name + '/' + key)
        if digest(data / name / 'run.log') != row['log_sha256']:
            raise ValueError('native run log changed: ' + name)
        checks.append(dict(family=name, **actual))
    if sum(r['exact_identities'] for r in checks) != 115:
        raise ValueError('wrong total identity count')

    # Analytic IBP control: I_a/I_1 = product((2j-d)/(2jm), j=1..a-1).
    text = (data / 'tadpole/results/tadpole/kira_targets.kira').read_text()
    ratio = 1
    for a in range(2, 5):
        ratio *= (2 * (a - 1) - D) / (2 * (a - 1) * m)
        block = next(b for b in text.strip().split('\n\n') if b.startswith(f'tadpole[{a}]*(-1)'))
        coefficient = re.fullmatch(r'tadpole\[1\]\*\((.+)\)', block.splitlines()[1]).group(1)
        if not exact_zero(expression(coefficient) - ratio):
            raise ValueError('analytic tadpole ratio differs')

    controls = []
    for bad in ('', '\n', 'tadpole[1] # 0\n', 'tadpole[1]\ntadpole[1] # 1\n'):
        controls.append(reject('invalid master metadata: ' + repr(bad), lambda: master_set(bad)))
    certificate = json.loads((project / 'results/certificates/tadpole-sparse.json').read_text())
    controls.append(reject('empty export', lambda: compare('', certificate)))
    blocks = text.strip().split('\n\n')
    controls.append(reject('missing target', lambda: compare('\n\n'.join(blocks[:-1]), certificate)))
    controls.append(reject('duplicate target', lambda: compare('\n\n'.join([*blocks, blocks[0]]) + '\n', certificate)))
    lines = text.splitlines()
    changed, count = re.subn(r'\*\((.+)\)$', r'*((\1)+(d-4)*(d-6)*(d-8))', lines[1])
    if count != 1:
        raise ValueError('coefficient mutation did not apply')
    mutated = '\n'.join([lines[0], changed, *lines[2:]])
    controls.append(reject('coefficient error invisible at d=4,6,8', lambda: compare(mutated, certificate)))
    with tempfile.TemporaryDirectory(dir=HERE) as tmp:
        directory = Path(tmp) / 'tadpole'
        shutil.copytree(data / 'tadpole', directory)
        final = directory / 'results/tadpole/masters.final'
        final.write_text('tadpole[2] # 1\n')
        controls.append(reject('wrong native final basis', lambda: check_family(project, directory, 'tadpole', compare)))
        final.unlink()
        controls.append(reject('missing native final basis', lambda: check_family(project, directory, 'tadpole', compare)))

    print(json.dumps(dict(valid=True, evidence_level='author-checked', families=checks,
                          exact_identities=115, analytic_tadpole_ratios=3,
                          controls_rejected=controls), indent=2))


if __name__ == '__main__':
    main()
