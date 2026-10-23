"""Run the four frozen trials sequentially with caps and complete receipts."""
import argparse, hashlib, json, os, resource, subprocess, sys, time
from pathlib import Path


def cap():resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);script=Path(__file__).with_name('finite_field.py').resolve();receipts=[]
    for sample in (0,1):
        for mode in ('tube','decreasing'):
            name=f'{mode}-{sample}';argv=['/usr/bin/timeout','--kill-after=5','120',sys.executable,str(script),'--mode',mode,'--sample',str(sample),'--out',str(out/(name+'.json'))]
            start=time.perf_counter()
            with (out/(name+'.log')).open('w') as log:
                process=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,preexec_fn=cap)
                _,status,usage=os.wait4(process.pid,0);process.returncode=os.waitstatus_to_exitcode(status)
            row=dict(mode=mode,sample=sample,argv=argv,returncode=process.returncode,elapsed_seconds=time.perf_counter()-start,
                     user_seconds=usage.ru_utime,system_seconds=usage.ru_stime,max_process_rss_bytes=usage.ru_maxrss*1024,
                     timeout_seconds=120,address_space_limit_bytes=2*1024**3,
                     solver_sha256=hashlib.sha256(script.read_bytes()).hexdigest())
            receipts.append(row);(out/'receipts.json').write_text(json.dumps(receipts,indent=2)+'\n');print(json.dumps(row),flush=True)
    raise SystemExit(0 if all(r['returncode']==0 for r in receipts) else 1)


if __name__=='__main__':main()
