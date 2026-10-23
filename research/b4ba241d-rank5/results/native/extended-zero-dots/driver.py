"""One predeclared600s continuation; preserve scientific inputs byte-for-byte."""
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
    p.add_argument('--task', type=Path, required=True)
    a = p.parse_args(); directory = a.out.resolve(); kira = a.kira.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    names = ('jobs.yaml', 'masters', 'targets', 'config/integralfamilies.yaml', 'config/kinematics.yaml')
    for name in names:
        destination = directory/name; destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(a.input/name, destination)
    original = json.loads((a.input/'receipt.json').read_text())
    if sha(kira) != original['kira_sha256']:
        raise ValueError('native executable drift')
    argv = ['/usr/bin/timeout', '--kill-after=5', '600', str(kira), '--parallel=1', '--prime=2147483647',
            '--set_value=d=23', '--set_value=s23=3', '--set_value=s34=5',
            '--set_value=s45=17', '--set_value=s51=23', 'jobs.yaml']
    if argv[:2] != original['argv'][:2] or argv[3:] != original['argv'][3:]:
        raise ValueError('only the wall limit may change')
    frozen = dict(argv=argv, original_argv=original['argv'],
                  input_sha256={name: sha(directory/name) for name in names},
                  kira_sha256=sha(kira), driver_sha256=sha(Path(__file__)),
                  task_sha256=sha(a.task), timeout_seconds=600,
                  address_space_limit_per_process=2*1024**3,
                  scope='Explicit resource-only continuation after archived120s timeouts; no timing or generic algebraic claim.')
    (directory/'PRE_RUN.json').write_text(json.dumps(frozen, indent=2)+'\n')
    shutil.copyfile(__file__, directory/'driver.py')
    shutil.copyfile(a.task, directory/'PREDECLARED_TASK.md')
    started = time.perf_counter()
    with (directory/'run.log').open('w') as log:
        process = subprocess.Popen(argv, cwd=directory, stdout=log,
                                   stderr=subprocess.STDOUT, preexec_fn=cap)
        _, status, usage = os.wait4(process.pid, 0)
        process.returncode = os.waitstatus_to_exitcode(status)
    result = dict(frozen, returncode=process.returncode, elapsed_seconds=time.perf_counter()-started,
                  user_seconds=usage.ru_utime, system_seconds=usage.ru_stime,
                  max_individual_process_rss_bytes=usage.ru_maxrss*1024,
                  binary_unchanged=sha(kira)==frozen['kira_sha256'])
    (directory/'receipt.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result)); raise SystemExit(process.returncode)


if __name__ == '__main__':
    main()
