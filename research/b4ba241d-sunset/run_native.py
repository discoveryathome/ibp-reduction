"""Run one unchanged sunset input fixture with bounded native resources."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cap():
    resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--kira', type=Path, required=True)
    a = p.parse_args()
    directory, kira = a.out.resolve(), a.kira.resolve()
    if directory.exists():
        raise ValueError('fresh trial directory required')
    shutil.copytree(a.input, directory)
    inputs = {str(f.relative_to(directory)): sha(f)
              for f in sorted(directory.rglob('*')) if f.is_file()}
    binary_hash = sha(kira)
    argv = ['/usr/bin/timeout', '--kill-after=5', '180', str(kira), '--parallel=1', 'jobs.yaml']
    started = time.perf_counter()
    with (directory/'run.log').open('w') as log:
        process = subprocess.Popen(argv, cwd=directory, stdout=log,
                                   stderr=subprocess.STDOUT, preexec_fn=cap)
        _, status, usage = os.wait4(process.pid, 0)
        process.returncode = os.waitstatus_to_exitcode(status)
    receipt = dict(argv=argv, returncode=process.returncode,
                   elapsed_seconds=time.perf_counter()-started,
                   user_seconds=usage.ru_utime, system_seconds=usage.ru_stime,
                   max_individual_process_rss_bytes=usage.ru_maxrss*1024,
                   timeout_seconds=180, address_space_limit_per_process=2*1024**3,
                   input_sha256=inputs, kira_sha256=binary_hash,
                   driver_sha256=sha(Path(__file__)),
                   binary_unchanged=sha(kira)==binary_hash,
                   scope='Execution receipt only; exact output/master checks are separate.')
    (directory/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt))
    raise SystemExit(process.returncode)


if __name__ == '__main__':
    main()
