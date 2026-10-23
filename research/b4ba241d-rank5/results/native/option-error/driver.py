"""One resource-capped native reference; output still needs coefficient checks."""
import argparse, hashlib, json, os, resource, subprocess, time
from pathlib import Path


def cap():
    resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory',type=Path,required=True);p.add_argument('--kira',type=Path,required=True)
    a=p.parse_args();directory=a.directory.resolve();kira=a.kira.resolve()
    if (directory/'receipt.json').exists() or (directory/'run.log').exists():raise ValueError('fresh trial required')
    argv=['/usr/bin/timeout','--kill-after=5','120',str(kira),'--parallel=1','--prime_user=2147483647',
          '--set_value=d=23','--set_value=s23=3','--set_value=s34=5','--set_value=s45=17','--set_value=s51=23','jobs.yaml']
    start=time.perf_counter()
    with (directory/'run.log').open('w') as log:
        process=subprocess.Popen(argv,cwd=directory,stdout=log,stderr=subprocess.STDOUT,preexec_fn=cap)
        _,status,usage=os.wait4(process.pid,0);process.returncode=os.waitstatus_to_exitcode(status)
    result=dict(argv=argv,returncode=process.returncode,elapsed_seconds=time.perf_counter()-start,
                user_seconds=usage.ru_utime,system_seconds=usage.ru_stime,
                max_individual_process_rss_bytes=usage.ru_maxrss*1024,
                address_space_limit_per_process=2*1024**3,timeout_seconds=120,
                kira_sha256=hashlib.sha256(kira.read_bytes()).hexdigest(),
                driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                scope='Native reference execution only; basis/coefficients require separate verification.')
    (directory/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
    raise SystemExit(process.returncode)


if __name__=='__main__':main()
