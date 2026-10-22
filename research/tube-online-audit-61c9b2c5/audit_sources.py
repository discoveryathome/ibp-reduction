"""Recompute SAILIR source/CSV findings without executing upstream code."""
import argparse
import ast
import csv
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent


def integral(text):
    start = text.index('[')
    value = ast.literal_eval(text[start:])
    if not isinstance(value, list) or len(value) != 7 or any(type(a) is not int for a in value):
        raise ValueError('Invalid integral index data')
    return tuple(value)


def summarize(source):
    manifest = json.loads((HERE/'sailir-sources.json').read_text())
    for name, expected in manifest['files'].items():
        if hashlib.sha256((source/name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Source fingerprint mismatch: {name}')
    sailir = list(csv.DictReader((source/'results/sailir_benchmark.csv').open()))
    kira = list(csv.DictReader((source/'results/kira_benchmark.csv').open()))
    if len(sailir) != 19 or len(kira) != 19:
        raise ValueError('Unexpected published CSV coverage')
    comparison = {integral(row['integral']): row for row in kira}
    if len(comparison) != 19 or set(comparison) != {integral(x['integral']) for x in sailir}:
        raise ValueError('CSV target coverage does not match')
    cases = []
    for row in sailir:
        index = integral(row['integral'])
        r, s, dots = int(row['r']), int(row['s']), int(row['d'])
        if ((r, s, dots) != (sum(max(a, 0) for a in index), sum(max(-a, 0) for a in index),
                            sum(max(a-1, 0) for a in index[:6]))):
            raise ValueError('CSV labels disagree with the integral')
        if not (10 <= r <= 13 and 4 <= s <= 7):
            continue
        other = comparison[index]
        if (r, s, dots) != tuple(int(other[k]) for k in ('r', 's', 'd')):
            raise ValueError('Kira labels disagree')
        target_file = source/f'scripts/kira/integrals-{r}.{s}.{dots}'
        if integral(target_file.read_text().strip()) != index:
            raise ValueError('Kira target file disagrees with its CSV')
        kira_memory = Fraction(other['peak_memory_kb']) / 1024
        cases.append(dict(
            r=r, s=s, dots=dots, integral=list(index),
            sailir_recorded_elapsed_seconds=row['time_s'],
            sailir_ideal_parallel_seconds=row['ideal_parallel_time_s'],
            sailir_jobs=int(row['total_jobs']),
            sailir_peak_raw_worker_mib=row['max_worker_memory_raw_mb'],
            sailir_peak_per_cpu_worker_mib=row['max_worker_memory_per_cpu_mb'],
            sailir_orchestrator_mib=row['orchestrator_memory_mb'],
            kira_seconds=other['total_time_s'], kira_peak_mib=float(kira_memory),
            ideal_time_ratio=float(Fraction(row['ideal_parallel_time_s'])/Fraction(other['total_time_s'])),
            elapsed_time_ratio=float(Fraction(row['time_s'])/Fraction(other['total_time_s'])),
            raw_worker_memory_ratio=float(Fraction(row['max_worker_memory_raw_mb'])/kira_memory),
            per_cpu_worker_memory_ratio=float(Fraction(row['max_worker_memory_per_cpu_mb'])/kira_memory)))
    if {(x['r'], x['s']) for x in cases} != {(r, s) for r in range(10, 14) for s in range(4, 8)}:
        raise ValueError('Paper 16-case grid is incomplete')
    shell = (source/'scripts/kira/run_benchmark_s7.sh').read_text()
    job = (source/'scripts/kira/jobs_benchmark.yaml').read_text()
    selections = re.findall(r'\[\s*(integrals-[0-9.]+)\s*\]', job)
    if selections != ['integrals-13.7.7'] or 'cp -f "integrals-${spec}" integrals' not in shell:
        raise ValueError('Kira wrapper finding needs re-audit')
    numeric_references = re.findall(r'numerical_points:\s*(\S+)', job)
    if numeric_references != ['numerics']:
        raise ValueError('Numerical point reference changed')
    if 'scripts/kira/numerics' in manifest['tree_paths'] or (source/'scripts/kira/numerics').exists():
        raise ValueError('Source snapshot now contains numerics; re-audit the absence claim')
    log = (source/'results/training_log/train.log').read_text()
    epochs = re.findall(r'^Epoch (\d+)/30 \(([0-9.]+)s\):$', log, re.M)
    if [int(i) for i, _ in epochs] != list(range(1, 31)):
        raise ValueError('Training log does not contain the expected 30 epochs')
    counts = re.search(r'^Train: (\d+), Val: (\d+)$', log, re.M)
    if counts is None:
        raise ValueError('Missing training sample counts')
    memory_counterexamples = [[x['r'], x['s']] for x in cases
                             if x['per_cpu_worker_memory_ratio'] < 1 < x['raw_worker_memory_ratio']]
    return dict(
        source_commit=manifest['commit'], checked_source_files=len(manifest['files']),
        upstream_code_executed=False, csv_rows_each=19, paper_cases=len(cases), cases=cases,
        sum_recorded_elapsed_values_seconds=str(sum(Fraction(x['sailir_recorded_elapsed_seconds']) for x in cases)),
        sum_ideal_parallel_values_seconds=str(sum(Fraction(x['sailir_ideal_parallel_seconds']) for x in cases)),
        jobs_across_paper_cases=sum(x['sailir_jobs'] for x in cases),
        per_cpu_below_kira_but_raw_worker_above_kira=memory_counterexamples,
        training=dict(epochs=30, epoch_duration_sum_seconds=str(sum(Fraction(t) for _, t in epochs)),
                      train_samples=int(counts[1]), validation_samples=int(counts[2]),
                      logged_device='cuda', note='Reported epoch times; no local training or CPU extrapolation.'),
        static_findings=dict(kira_wrapper_copies='integrals', kira_yaml_selects=selections,
                             numerical_point_file='scripts/kira/numerics', numerical_point_file_missing=True),
        limitations=['Source-data audit, not a replication of either solver or the published timings.',
                     'Sums of reported run durations are not CPU-hours or elapsed time of this donation.',
                     'Maximum per-CPU worker memory, raw worker peak and aggregate concurrent memory differ.',
                     'Original worker DAGs, total CPU-seconds and aggregate simultaneous RSS are not in the CSVs.'],
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sailir-source', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = json.dumps(summarize(args.sailir_source), indent=2) + '\n'
    if args.output:
        args.output.write_text(result)
    else:
        print(result, end='')
