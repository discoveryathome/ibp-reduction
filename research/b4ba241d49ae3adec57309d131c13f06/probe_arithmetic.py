"""Replay the project's existing arithmetic probe without rewriting its saved result.

Credit: tools/probe_kira_arithmetic.py at the pinned project/predecessor commits.
The finite diagnostic compares upstream code to unsigned __int128, not a proof.
"""

import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import tempfile

KIRA = 'fb745431f97c8899a512e638da8598b0cfad7521'
PROJECT = 'd051133ed7c01652e21b53e34fcd5610051705a8'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--predecessor', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    project, source = args.predecessor.resolve(), args.source.resolve()
    for path, expected in ((project, PROJECT), (source, KIRA)):
        actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=path, text=True).strip()
        if actual != expected:
            raise ValueError('wrong source commit: ' + str(path))
        subprocess.run(['git', 'diff', '--exit-code', 'HEAD'], cwd=path, check=True,
                       stdout=subprocess.DEVNULL)
    probe_file = project / 'tools/probe_kira_arithmetic.py'
    probe = runpy.run_path(str(probe_file))['PROBE']
    # Linux uint64_t is unsigned long, unlike the original Apple probe's ULLs.
    probe = probe.replace('{0ULL,1ULL,m-1}', '{uint64_t{0},uint64_t{1},m-1}')
    config = (source / 'build/src/pyred/config.h').read_text()
    rows = []
    with tempfile.TemporaryDirectory(dir=args.out.parent) as tmp:
        directory = Path(tmp)
        (directory / 'pyred').mkdir()
        (directory / 'probe.cpp').write_text(probe)
        for mode in ('release', 'integer'):
            cfg = config.replace('#define VALGRIND', '#undef VALGRIND')
            if mode == 'integer':
                cfg = cfg.replace('#undef VALGRIND', '#define VALGRIND')
            (directory / 'pyred/config.h').write_text(cfg)
            argv = ['c++', '-std=c++17', '-O2', '-I' + str(directory), '-I' + str(source / 'src'),
                    str(directory / 'probe.cpp'), str(source / 'src/pyred/coeff_helper.cpp'),
                    '-o', str(directory / 'probe')]
            subprocess.run(argv, check=True)
            row = json.loads(subprocess.check_output([str(directory / 'probe')], text=True))
            rows.append(dict(mode=mode, **row))
    result = dict(kira_commit=KIRA, predecessor_commit=PROJECT,
                  probe_source_sha256=hashlib.sha256(probe_file.read_bytes()).hexdigest(),
                  cpp_probe_sha256=hashlib.sha256(probe.encode()).hexdigest(),
                  harness_adjustment='Explicit uint64_t initializer-list constants; upstream arithmetic unchanged.',
                  coefficient_source_sha256=hashlib.sha256((source / 'src/pyred/coeff_helper.cpp').read_bytes()).hexdigest(),
                  rows=rows, scope='Fixed-seed 100009-case diagnostic per mode, not exhaustive correctness.')
    with args.out.open('x') as out:
        out.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    if any(row['failures'] for row in rows):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
