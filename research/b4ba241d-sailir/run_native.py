"""One fixed native preflight; generate18 requests from the frozen episode."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import time

TARGET = (1,2,1,1,1,1,-3)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n')


def cap():
    resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--episode',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--kira',type=Path,required=True)
    a=p.parse_args(); directory=a.out.resolve(); kira=a.kira.resolve()
    if directory.exists():raise ValueError('fresh native output directory required')
    if sha(kira)!='9d49f623f144ee90c3eb2f50290b180b93c5c85e9ca1272092cecb065eb47066':
        raise ValueError('pinned native binary drift')
    source_hashes={name:sha(a.source/name) for name in (
        'scripts/kira/config/integralfamilies.yaml','scripts/kira/config/kinematics.yaml','sailir/ibp_env.py')}
    if source_hashes['scripts/kira/config/integralfamilies.yaml']!='dc34f0fa1f8a36422e464439458dcdb6a823eb49589bb503b645a8d28d9c9134' or source_hashes['scripts/kira/config/kinematics.yaml']!='018b41681f6da3f961b0e10afa51e15900eaaef60ef10295c03771be8dc72b30':
        raise ValueError('pinned geometry source drift')
    episode=json.loads(a.episode.read_text())
    if episode['prime']!=1009 or episode['kinematics']!=dict(d=41,m1=1,m2=31,m3=47) or episode['initial']!=[[list(TARGET),1]]:
        raise ValueError('episode convention drift')
    requests={TARGET}|{tuple(index) for index,_ in episode['final']}
    if len(episode['final'])!=17 or len(requests)!=18 or any(len(x)!=7 or any(type(a) is not int for a in x) or sum(max(a,0) for a in x)>7 for x in requests):
        raise ValueError('frozen18-target set drift')
    paper=None
    for node in ast.parse((a.source/'sailir/ibp_env.py').read_text()).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAPER_MASTERS' for t in node.targets):
            value=node.value
            if not isinstance(value,ast.Call) or not isinstance(value.func,ast.Name) or value.func.id!='frozenset' or len(value.args)!=1:
                raise ValueError('nonliteral paper master convention')
            paper={tuple(x) for x in ast.literal_eval(value.args[0])}
    if paper is None or len(paper)!=16 or any(len(x)!=7 or any(type(a) is not int for a in x) for x in paper):
        raise ValueError('paper16-master fixture drift')
    (directory/'config').mkdir(parents=True,exist_ok=False)
    family=dict(integralfamilies=[dict(name='trianglebox',loop_momenta=['k1','k2'],top_level_sectors=[63],
        propagators=[[x,0] for x in ['k1','k2','k1+k2','k1+p1','k2+p3','k2-p1','k1+p3']])])
    kinematics=dict(kinematics=dict(incoming_momenta=['p1','p2'],outgoing_momenta=['p3'],
        momentum_conservation=['p3','p1+p2'],kinematic_invariants=[['m1',2],['m2',2],['m3',2]],
        scalarproduct_rules=[[[x,x],m] for x,m in [('p1','m1'),('p2','m2'),('p3','m3')]],symbol_to_replace_by_one='m1'))
    jobs=dict(jobs=[dict(reduce_sectors=dict(reduce=[dict(topologies=['trianglebox'],sectors=[63],r=7,s=3)],
        select_integrals=dict(select_mandatory_list=[['trianglebox','targets']]),preferred_masters='masters',
        run_initiate=True,run_triangular=True,run_back_substitution=True)),dict(kira2file=dict(target=[['trianglebox','targets']]))])
    dump(directory/'config/integralfamilies.yaml',family);dump(directory/'config/kinematics.yaml',kinematics);dump(directory/'jobs.yaml',jobs)
    for name,rows in [('targets',requests),('masters',paper)]:
        (directory/name).write_text(''.join('trianglebox['+','.join(map(str,x))+']\n' for x in sorted(rows)))
    inputs={str(f.relative_to(directory)):sha(f) for f in sorted(directory.rglob('*')) if f.is_file()}
    argv=['/usr/bin/timeout','--kill-after=5','180',str(kira),'--parallel=1','--prime=1009',
          '--set_value=d=41','--set_value=m2=31','--set_value=m3=47','jobs.yaml']
    frozen=dict(argv=argv,input_sha256=inputs,source_sha256=source_hashes,episode_sha256=sha(a.episode),
                driver_sha256=sha(Path(__file__)),kira_sha256=sha(kira),requests=18,paper_preferred_masters=16,
                point=dict(d=41,m1=1,m2=31,m3=47),comparison_prime=1009,
                native_coefficient_domain='Exact rational specialization; coefficients compared modulo1009 separately.',
                timeout_seconds=180,address_space_limit_per_process=2*1024**3)
    dump(directory/'PRE_RUN.json',frozen);shutil.copyfile(__file__,directory/'driver.py')
    started=time.perf_counter()
    with (directory/'run.log').open('w') as log:
        process=subprocess.Popen(argv,cwd=directory,stdout=log,stderr=subprocess.STDOUT,preexec_fn=cap)
        _,status,usage=os.wait4(process.pid,0);process.returncode=os.waitstatus_to_exitcode(status)
    result=dict(frozen,returncode=process.returncode,elapsed_seconds=time.perf_counter()-started,
                user_seconds=usage.ru_utime,system_seconds=usage.ru_stime,
                max_individual_process_rss_bytes=usage.ru_maxrss*1024,binary_unchanged=sha(kira)==frozen['kira_sha256'])
    dump(directory/'receipt.json',result);print(json.dumps(result));raise SystemExit(process.returncode)


if __name__=='__main__':main()
