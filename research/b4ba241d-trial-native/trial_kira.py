"""Native correctness replay for the three existing contributor-trial families.

Reuses PR #7's pinned exporter/importer; no source-file or checker modification.
Process-local exporter allowlist extension only; no tuning/performance claim.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import sys
import time

PREDECESSOR = 'd051133ed7c01652e21b53e34fcd5610051705a8'
NAMES = ('bubble_one_mass', 'triangle_two_mass', 'box_one_mass')
COUNTS = dict(zip(NAMES, (13, 14, 71)))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(project):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=project, text=True).strip()
    if revision != PREDECESSOR:
        raise ValueError('wrong predecessor commit')
    subprocess.run(['git', 'diff', '--exit-code', 'HEAD'], cwd=project, check=True,
                   stdout=subprocess.DEVNULL)
    sys.path.insert(0, str(project))
    from tools import export_kira_one_loop as exporter, check_kira as comparison
    from ibp import validator
    return exporter, comparison, validator


def inputs(exporter, name):
    if name not in NAMES:
        raise ValueError('not a contributor-trial family')
    original = exporter.NAMES
    try:
        exporter.NAMES = tuple(original) + NAMES
        return exporter.inputs(name)
    finally:
        exporter.NAMES = original


def integrals(text, name, n):
    rows = set()
    for line in text.splitlines():
        match = re.fullmatch(re.escape(name) + r'\[(-?\d+(?:,-?\d+)*)\](?:\s+#\s*(\d+))?', line.strip())
        if not match:
            raise ValueError('malformed integral list')
        a = tuple(map(int, match.group(1).split(',')))
        if len(a) != n or a in rows:
            raise ValueError('duplicate or wrong-dimensional integral')
        if match.group(2) is not None and int(match.group(2)) != sum(1 << i for i, x in enumerate(a) if x > 0):
            raise ValueError('incorrect sector annotation')
        rows.add(a)
    if not rows:
        raise ValueError('empty integral list')
    return rows


def geometry(files, name, comparison, validator):
    masses, distances, masters, rmax = validator.SPECS[name]
    n, S = len(masses), comparison.S
    f = json.loads(files['config/integralfamilies.yaml'])['integralfamilies']
    if len(f) != 1 or f[0]['name'] != name or f[0]['loop_momenta'] != ['k'] or f[0]['top_level_sectors'] != [(1 << n) - 1]:
        raise ValueError('wrong family, loop or sector')
    expected_momenta = ['k'] + ['k+p' + str(i) for i in range(1, n)]
    if [p for p, _ in f[0]['propagators']] != expected_momenta:
        raise ValueError('propagator momentum drift')
    for (_, value), expected in zip(f[0]['propagators'], masses):
        if not validator.exact_zero(comparison.expression(value) + expected):
            raise ValueError('propagator mass-sign/value drift')
    k = json.loads(files['config/kinematics.yaml'])['kinematics']
    momenta = ['p' + str(i) for i in range(1, n)]
    if k['incoming_momenta'] != momenta or k['outgoing_momenta'] != ['q']:
        raise ValueError('external momentum drift')
    eliminated, replacement = k['momentum_conservation']
    if eliminated != 'q' or replacement.replace(' ', '') != '+'.join(momenta) or 'symbol_to_replace_by_one' in k:
        raise ValueError('momentum elimination or numeric substitution drift')
    gram, pairs = S.zeros(n), set()
    for pair, value in k['scalarproduct_rules']:
        pair = tuple(pair)
        if pair in pairs or any(p not in momenta for p in pair) or len(pair) != 2:
            raise ValueError('invalid/duplicate scalar product')
        pairs.add(pair)
        i, j = (momenta.index(p) + 1 for p in pair)
        gram[i, j] = gram[j, i] = comparison.expression(value)
    if pairs != {(p, q) for i, p in enumerate(momenta) for q in momenta[i:]}:
        raise ValueError('incomplete scalar products')
    for i in range(n):
        for j in range(n):
            if not validator.exact_zero(gram[i, i] + gram[j, j] - 2 * gram[i, j] - distances[i][j]):
                raise ValueError('distance/Gram reconstruction drift')
    symbols = set().union(*(S.sympify(x).free_symbols for x in masses + [v for row in distances for v in row]))
    if k['kinematic_invariants'] != [[str(x), 2] for x in sorted(symbols, key=str)]:
        raise ValueError('generic invariant inventory drift')
    if integrals(files['masters'], name, n) != set(masters):
        raise ValueError('preferred master drift')
    job = json.loads(files['jobs.yaml'])['jobs'][0]['reduce_sectors']
    if job['reduce'] != [dict(sectors=[(1 << n) - 1], r=rmax, s=1)]:
        raise ValueError('seed region drift')


def certificate(project, name):
    return project / 'contributor-trial/certificates' / (name + '-online.json')


def check_family(project, directory, name, exporter, comparison, validator):
    expected = inputs(exporter, name)
    files = {relative: (directory / relative).read_text() for relative in expected}
    geometry(files, name, comparison, validator)
    if files != expected:
        raise ValueError('generated input differs from pinned exporter')
    cert = certificate(project, name)
    decoded = json.loads(cert.read_text())
    if integrals(files['targets'], name, len(validator.SPECS[name][0])) != {tuple(o['target']) for o in decoded['outputs']}:
        raise ValueError('requested target drift')
    for filename in ('masters', 'masters.final'):
        actual = integrals((directory / 'results' / name / filename).read_text(), name, len(validator.SPECS[name][0]))
        if actual != set(validator.SPECS[name][2]):
            raise ValueError('native master-set drift: ' + filename)
    export = directory / 'results' / name / 'kira_targets.kira'
    count = comparison.compare(export.read_text(), decoded)
    if count != COUNTS[name]:
        raise ValueError('wrong exact target count')
    return dict(exact_identities=count, masters=[list(a) for a in sorted(actual)],
                export_sha256=sha(export), certificate_sha256=sha(cert))


def limit_memory():
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))


def reject(function):
    try:
        function()
    except ValueError:
        return
    raise AssertionError('mutation was accepted')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--predecessor', type=Path, required=True)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--out', type=Path)
    group.add_argument('--check', type=Path)
    p.add_argument('--kira', type=Path)
    args = p.parse_args()
    project = args.predecessor.resolve()
    exporter, comparison, validator = load(project)
    if args.check:
        data = args.check.resolve()
        records = json.loads((data / 'runs.json').read_text())
        if [r['family'] for r in records] != list(NAMES):
            raise ValueError('missing, duplicate or reordered run')
        controls = 0
        for row in records:
            name, directory = row['family'], data / row['family']
            if row.get('returncode') != 0 or row.get('valid') is not True:
                raise ValueError('failed native run')
            actual = check_family(project, directory, name, exporter, comparison, validator)
            if any(row[k] != value for k, value in actual.items()) or row['log_sha256'] != sha(directory / 'run.log'):
                raise ValueError('receipt/evidence mismatch')
            cert = json.loads(certificate(project, name).read_text())
            text = (directory / 'results' / name / 'kira_targets.kira').read_text()
            reject(lambda: comparison.compare('', cert))
            reject(lambda: comparison.compare('\n\n'.join(text.strip().split('\n\n')[:-1]), cert))
            lines = text.splitlines()
            changed, count = re.subn(r'\*\((.+)\)$', r'*((\1)+1)', lines[1])
            if count != 1:
                raise ValueError('coefficient mutation did not apply')
            reject(lambda: comparison.compare('\n'.join([lines[0], changed, *lines[2:]]), cert))
            files = inputs(exporter, name)
            k = json.loads(files['config/kinematics.yaml'])
            k['kinematics']['scalarproduct_rules'][0][1] = '1+(' + k['kinematics']['scalarproduct_rules'][0][1] + ')'
            files['config/kinematics.yaml'] = json.dumps(k)
            reject(lambda: geometry(files, name, comparison, validator))
            controls += 4
        print(json.dumps(dict(valid=True, families=3, exact_identities=98, masters=8,
                              controls_rejected=controls, evidence_level='author-checked')))
        return
    if not args.kira:
        p.error('--out requires --kira')
    data, kira = args.out.resolve(), args.kira.resolve()
    data.mkdir(parents=True, exist_ok=False)
    records = []
    fermat = Path(os.environ['FERMATPATH']).resolve()
    for name in NAMES:
        directory = data / name
        files = inputs(exporter, name)
        geometry(files, name, comparison, validator)
        validator.check(json.loads(certificate(project, name).read_text()))
        for relative, text in files.items():
            path = directory / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        argv = ['/usr/bin/timeout', '--kill-after=5', '180', str(kira), '--parallel=1', 'jobs.yaml']
        row = dict(family=name, argv=argv, cwd=str(directory), kira_sha256=sha(kira), fermat_sha256=sha(fermat),
                   timeout_seconds=180, address_space_cap_bytes_per_process=2 * 1024**3,
                   input_sha256={relative: sha(directory / relative) for relative in files})
        start = time.perf_counter()
        try:
            with (directory / 'run.log').open('w') as log:
                process = subprocess.Popen(argv, cwd=directory, stdout=log, stderr=subprocess.STDOUT,
                                           preexec_fn=limit_memory)
                _, status, usage = os.wait4(process.pid, 0)
                process.returncode = os.waitstatus_to_exitcode(status)
            row.update(returncode=process.returncode, elapsed_seconds=time.perf_counter() - start,
                       user_seconds=usage.ru_utime, system_seconds=usage.ru_stime,
                       max_individual_process_rss_bytes=usage.ru_maxrss * 1024,
                       log_sha256=sha(directory / 'run.log'))
            if process.returncode:
                raise ValueError('native process failed')
            row.update(check_family(project, directory, name, exporter, comparison, validator), valid=True)
        except Exception as error:
            row.update(valid=False, error=type(error).__name__ + ': ' + str(error))
        records.append(row)
        (data / 'runs.json').write_text(json.dumps(records, indent=2) + '\n')
        print(json.dumps(row), flush=True)
        if not row['valid']:
            raise SystemExit(1)


if __name__ == '__main__':
    main()
