"""Run the pinned PR #7 inputs; retain failures and check exact identities/masters.

Uses the predecessor's exporter and comparator without modifying either. Timings
are execution receipts, not a performance benchmark. Linux only (wait4/GNU timeout).
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
FAMILIES = ('tadpole', 'bubble_massless', 'bubble_equal_mass', 'triangle_one_mass',
            'bubble_unequal_mass', 'triangle_offshell', 'box_massless')
LIMIT_BYTES = 2 * 1024**3


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def master_set(text):
    result = set()
    for line in text.splitlines():
        match = re.fullmatch(r'([A-Za-z_][A-Za-z_0-9]*)\[(-?\d+(?:,-?\d+)*)\](?:\s+#\s*(\d+))?', line.strip())
        if not match:
            raise ValueError('malformed master entry')
        name, indices, sector = match.groups()
        values = tuple(map(int, indices.split(',')))
        if sector is not None and int(sector) != sum(1 << i for i, a in enumerate(values) if a > 0):
            raise ValueError('incorrect master sector annotation')
        integral = name + '[' + ','.join(map(str, values)) + ']'
        if integral in result:
            raise ValueError('duplicate master')
        result.add(integral)
    if not result:
        raise ValueError('empty master list')
    return result


def check_family(project, directory, name, compare):
    expected = master_set((directory / 'masters').read_text())
    for filename in ('masters', 'masters.final'):
        actual = master_set((directory / 'results' / name / filename).read_text())
        if actual != expected:
            raise ValueError(f'{filename} differs: expected {sorted(expected)}, got {sorted(actual)}')
    certificate = project / 'results' / 'certificates' / (name + '-sparse.json')
    export = directory / 'results' / name / 'kira_targets.kira'
    count = compare(export.read_text(), json.loads(certificate.read_text()))
    return dict(exact_identities=count, masters=sorted(actual),
                export_sha256=digest(export), certificate_sha256=digest(certificate))


def limit_memory():
    # Inherited by Kira and its one Fermat worker; this is a per-process cap.
    resource.setrlimit(resource.RLIMIT_AS, (LIMIT_BYTES, LIMIT_BYTES))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--predecessor', type=Path, required=True)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--kira', type=Path, required=True)
    parser.add_argument('--families', nargs='+', choices=FAMILIES, default=list(FAMILIES))
    args = parser.parse_args()
    project, inputs, kira = args.predecessor.resolve(), args.inputs.resolve(), args.kira.resolve()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=project, text=True).strip()
    if revision != PREDECESSOR:
        raise ValueError('wrong predecessor commit')
    subprocess.run(['git', 'diff', '--exit-code', 'HEAD'], cwd=project, check=True, stdout=subprocess.DEVNULL)
    sys.path.insert(0, str(project))
    from tools.check_kira import compare
    from tools.export_kira_one_loop import inputs as original_inputs

    manifest = json.loads((inputs / 'manifest.json').read_text())
    for path, expected in manifest['sources_sha256'].items():
        if digest(project / path) != expected:
            raise ValueError('predecessor source changed: ' + path)
    for name in FAMILIES:
        for relative, text in original_inputs(name).items():
            if (inputs / name / relative).read_bytes() != text.encode():
                raise ValueError('generated input changed: ' + name + '/' + relative)

    receipt_path = inputs / 'run-receipts.json'
    receipts = json.loads(receipt_path.read_text()) if receipt_path.exists() else []
    completed = {row['family'] for row in receipts}
    if len(set(args.families)) != len(args.families) or completed.intersection(args.families):
        raise ValueError('duplicate trial: generate a fresh input tree instead')
    fermat = Path(os.environ['FERMATPATH']).resolve()
    for name in args.families:
        directory = inputs / name
        argv = ['/usr/bin/timeout', '--kill-after=5', '180', str(kira), '--parallel=1', 'jobs.yaml']
        row = dict(family=name, predecessor=revision, argv=argv, cwd=str(directory),
                   kira_sha256=digest(kira), fermat_sha256=digest(fermat),
                   timeout_seconds=180, address_space_limit_bytes_per_process=LIMIT_BYTES)
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
                       resource_scope='wait4: timeout and reaped descendants; RSS is a maximum, not an aggregate.',
                       log_sha256=digest(directory / 'run.log'))
            if process.returncode:
                raise ValueError('native process failed: ' + str(process.returncode))
            row.update(check_family(project, directory, name, compare), valid=True)
        except Exception as error:
            row.update(valid=False, error=type(error).__name__ + ': ' + str(error))
        receipts.append(row)
        receipt_path.write_text(json.dumps(receipts, indent=2) + '\n')
        print(json.dumps(row), flush=True)
        if not row['valid']:
            raise SystemExit(1)


if __name__ == '__main__':
    main()
