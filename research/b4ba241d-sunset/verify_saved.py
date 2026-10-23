"""Exact native/certificate comparison and independent saved-cost trace replay."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

import audit_cost

HERE = Path(__file__).resolve().parent
MASTERS = {(1, 1, 1), (1, 1, 0)}


def master_set(path):
    result = set()
    for line in path.read_text().splitlines():
        match = re.fullmatch(r'sunset\[(-?\d+),(-?\d+),(-?\d+)\](?:\s*#\s*\d+)?', line.strip())
        if not match:
            raise ValueError('malformed native master list')
        integral = tuple(map(int, match.groups()))
        if integral in result:
            raise ValueError('duplicate native master')
        result.add(integral)
    if result != MASTERS:
        raise ValueError('native master convention disagreement')
    return result


def rejected(call, name):
    try:
        call()
    except (ValueError, AssertionError, IndexError, KeyError):
        return name
    raise AssertionError('false control accepted: '+name)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, default=HERE.parents[1])
    p.add_argument('--native', type=Path, default=HERE/'results/native')
    p.add_argument('--cost', type=Path, default=HERE/'results/cost')
    p.add_argument('--candidate', type=Path, default=HERE/'fixtures/best.json')
    a = p.parse_args()
    bindings = json.loads((HERE/'SOURCES.json').read_text())
    for name, expected in bindings['project_files_sha256'].items():
        if hashlib.sha256((a.source/name).read_bytes()).hexdigest() != expected:
            raise ValueError('project source drift: '+name)
    if hashlib.sha256(a.candidate.read_bytes()).hexdigest() != bindings['candidate_sha256']:
        raise ValueError('candidate fixture drift')
    receipt = json.loads((a.native/'receipt.json').read_text())
    if receipt['returncode'] != 0 or not receipt['binary_unchanged'] or receipt['kira_sha256'] != bindings['native_binary_sha256']:
        raise ValueError('native execution receipt disagreement')
    for name, expected in receipt['input_sha256'].items():
        if hashlib.sha256((a.native/name).read_bytes()).hexdigest() != expected:
            raise ValueError('native input drift: '+name)
    sys.path.insert(0, str(a.source.resolve()))
    from ibp.validator import check, decode, exact_zero
    spec = importlib.util.spec_from_file_location('sunset_comparator', a.source/'tools/check_kira.py')
    comparator = importlib.util.module_from_spec(spec); spec.loader.exec_module(comparator)
    native = a.native/'results/sunset'
    for name in ('masters', 'masters.final'):
        master_set(native/name)
    text = (native/'kira_targets.kira').read_text()
    candidate = json.loads(a.candidate.read_text())
    certificates = [('predecessor-best', candidate)] + [
        (method, json.loads((a.cost/f'{method}.json').read_text()))
        for method in ('cached-sparse', 'inherited-online', 'candidate-online')]
    comparisons = []
    for name, certificate in certificates:
        if comparator.compare(text, certificate) != 9:
            raise ValueError('nine distinct targets required')
        comparisons.append(dict(method=name, exact_identities=9,
                                proof_nodes=len(certificate['nodes'])))
    if audit_cost.proof_digest(candidate) != audit_cost.proof_digest(certificates[-1][1]):
        raise ValueError('candidate proof/output replay disagreement')
    costs = []
    for name, certificate in certificates[1:]:
        trace = json.loads((a.cost/f'{name}-trace.json').read_text())
        costs.append(dict(method=name, **audit_cost.replay(trace, certificate['metrics'], decode, exact_zero)))
    blocks = text.strip().split('\n\n')
    lines = text.splitlines()
    for i, line in enumerate(lines):
        match = re.fullmatch(r'sunset\[(-?\d+),(-?\d+),(-?\d+)\]\*\((.+)\)', line.strip())
        if match and tuple(map(int, match.groups()[:3])) in MASTERS:
            lines[i] = line[:line.index('*')] + '*((%s)+1)' % match.group(4)
            break
    else:
        raise ValueError('no native master coefficient to mutate')
    bad_basis = text.replace('sunset[1,1,0]', 'sunset[2,0,0]')
    controls = []
    for label, mutant in (
        ('empty-export', ''), ('missing-target', '\n\n'.join(blocks[:-1])),
        ('duplicate-target', text.strip()+'\n\n'+blocks[0]),
        ('master-coefficient', '\n'.join(lines)), ('wrong-master-basis', bad_basis),
        ('executable-expression', text.replace('*(', '*(f(d)+', 1)),
        ('target-normalization', text.replace('*(-1)', '*(-2)', 1)),
    ):
        controls.append(rejected(lambda mutant=mutant: comparator.compare(mutant, candidate), label))
    mutant = copy.deepcopy(candidate); mutant['outputs'].pop()
    controls.append(rejected(lambda: check(mutant), 'missing-certificate-target'))
    mutant = copy.deepcopy(candidate); mutant['outputs'][0]['row'][0][1][0][0][1] += 1
    controls.append(rejected(lambda: check(mutant), 'certificate-coefficient'))
    print(json.dumps(dict(valid=True, distinct_native_targets=9, masters=2,
                         comparisons=comparisons, cost_audits=costs,
                         rejected_controls=controls,
                         scope='Exact generic d,m identities and specified field-operation/cache counts; not independent physics review or a timing claim.'), indent=2))


if __name__ == '__main__':
    main()
