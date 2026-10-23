"""Replay three frozen policies; check arithmetic/cache traces separately."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import resource
import signal
import sys
import time


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')


def proof_digest(certificate):
    value = {key: certificate[key] for key in ('nodes', 'outputs')}
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def replay(trace, metrics, decode, exact_zero):
    cache = {}; attempts = Counter(); calls = Counter()
    for event in trace:
        kind = event['kind']
        if kind not in ('add', 'mul', 'div'):
            raise ValueError('unknown arithmetic event')
        key = json.dumps([kind, event['a'], event['b']], sort_keys=True, separators=(',', ':'))
        executed = key not in cache
        if type(event['executed']) is not bool or event['executed'] != executed:
            raise ValueError('cache execution flag disagreement')
        attempts[kind] += 1
        actual = decode(event['result'])
        if executed:
            a, b = decode(event['a']), decode(event['b'])
            if kind == 'div' and exact_zero(b):
                raise ValueError('division by zero')
            expected = a+b if kind == 'add' else a*b if kind == 'mul' else a/b
            calls[kind] += 1
            if len(cache) < 10000:
                cache[key] = expected
        else:
            expected = cache[key]
        if not exact_zero(actual-expected):
            raise ValueError('trace arithmetic disagreement')
    expected = dict(arithmetic_operations=sum(calls.values()), operation_counts=dict(calls),
                    attempted_operations=sum(attempts.values()),
                    cache_hits=len(trace)-sum(calls.values()), cache_entries=len(cache))
    if any(metrics[key] != value for key, value in expected.items()):
        raise ValueError('trace counter disagreement')
    return dict(valid=True, **expected, attempted_by_kind=dict(attempts))


def timeout(signum, frame):
    raise TimeoutError('30-second policy replay cap')


def main():
    resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.out.exists():
        raise ValueError('fresh output directory required')
    a.out.mkdir(parents=True)
    sys.path.insert(0, str(a.source.resolve()))
    from ibp import reducer as R, contributor as C
    from ibp.validator import check, decode, exact_zero, prune
    candidate = json.loads(a.candidate.read_text())
    if hashlib.sha256(a.candidate.read_bytes()).hexdigest() != '399ddfacbdc7cef2d93771b03abb5a5e9bc3e928ce65df55b73589b2e3501212':
        raise ValueError('pinned candidate drift')
    check(candidate)
    inherited = json.loads((a.source/'research/readiness-20261021/two-loop-online.json').read_text())
    policies = (
        ('cached-sparse', 'batch', dict(R.BASELINES['sparse'], reuse=True), 425),
        ('inherited-online', 'online', inherited['policy'], 139),
        ('candidate-online', 'online', candidate['policy'], 107),
    )
    original = R.Arithmetic.op
    summary = {'candidate_sha256': hashlib.sha256(a.candidate.read_bytes()).hexdigest(), 'runs': []}
    signal.signal(signal.SIGALRM, timeout)
    for name, engine, policy, expected_count in policies:
        trace = []
        def observed(self, kind, left, right):
            before = sum(self.calls.values())
            result = original(self, kind, left, right)
            trace.append(dict(kind=kind, a=R.encode(left), b=R.encode(right),
                              result=R.encode(result), executed=sum(self.calls.values()) > before))
            return result
        started = time.perf_counter()
        try:
            R.Arithmetic.op = observed
            signal.alarm(30)
            certificate = (R.reduce if engine == 'batch' else C.online)(
                'sunset_equal_mass_v1', policy, certificate=True)
        except Exception as error:
            dump(a.out/f'{name}-partial-trace.json', trace)
            dump(a.out/'error.json', dict(method=name, error=repr(error)))
            raise
        finally:
            signal.alarm(0)
            R.Arithmetic.op = original
        elapsed = time.perf_counter()-started
        certificate = prune(certificate)
        dump(a.out/f'{name}.json', certificate)
        dump(a.out/f'{name}-trace.json', trace)
        validation = check(certificate)
        audited = replay(trace, certificate['metrics'], decode, exact_zero)
        if audited['arithmetic_operations'] != expected_count:
            raise ValueError('predeclared operation count mismatch')
        if name == 'candidate-online' and proof_digest(candidate) != proof_digest(certificate):
            raise ValueError('candidate DAG/output replay differs')
        rejected = []
        bad_trace = copy.deepcopy(trace)
        current = decode(bad_trace[0]['result'])
        bad_trace[0]['result'] = R.encode(R.FIELD.one if exact_zero(current) else R.FIELD.zero)
        bad_flag = copy.deepcopy(trace); bad_flag[0]['executed'] = not bad_flag[0]['executed']
        bad_metrics = dict(certificate['metrics'], arithmetic_operations=expected_count+1)
        for label, mutant, metrics in (
            ('arithmetic-result', bad_trace, certificate['metrics']),
            ('cache-flag', bad_flag, certificate['metrics']),
            ('operation-count', trace, bad_metrics),
        ):
            try:
                replay(mutant, metrics, decode, exact_zero)
            except ValueError:
                rejected.append(label)
            else:
                raise AssertionError('false trace accepted')
        row = dict(method=name, engine=engine, policy=policy, validation=validation,
                   operation_audit=audited, rejected_controls=rejected,
                   producer_seconds=elapsed, proof_sha256=proof_digest(certificate))
        summary['runs'].append(row)
        dump(a.out/'summary.json', summary)
        print(json.dumps(row), flush=True)


if __name__ == '__main__':
    main()
