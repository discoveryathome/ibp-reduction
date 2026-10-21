"""Deterministic training-only search and isolated, interleaved benchmark runs."""
import argparse,hashlib,json,math,os,platform,random,resource,statistics,subprocess,sys,time
from pathlib import Path
from .families import NAMES,family
from .reducer import BASELINES,reduce

SPACE={'seed':['rectangular','golden','improved'],'order':['sector','degree','dots','reverse'],
       'row':['first','short','complexity'],'reuse':[False,True]}
TRAIN=[n for n in NAMES if family(n)['split']=='train']
TEST=[n for n in NAMES if family(n)['split']=='test']

def dump(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def guarded(name,policy,certificate=False):
    c=reduce(name,policy,certificate)
    # Predeclared feasibility fallback is included in cost, never a free retry.
    if not c['metrics']['success'] and policy['seed']!='rectangular':
        first=c['metrics'];p=dict(policy,seed='rectangular');c=reduce(name,p,certificate)
        for k in ['arithmetic_operations','attempted_operations','reduction_seconds','input_rows','input_nnz','cache_hits']:
            c['metrics'][k]+=first[k]
        for k in ['peak_live_nnz','max_row_nnz','max_coefficient_terms','max_polynomial_degree','max_coefficient_bits','cache_entries','initial_max_coefficient_terms']:
            c['metrics'][k]=max(c['metrics'][k],first[k])
        for k,v in first['operation_counts'].items():c['metrics']['operation_counts'][k]=c['metrics']['operation_counts'].get(k,0)+v
        c['metrics']['fallback']=True;c['metrics']['failed_attempt']=first;c['requested_policy']=policy
    else:c['metrics']['fallback']=False
    c['metrics']['accounting_version']=2
    c['metrics']['expression_growth_ratio']=c['metrics']['max_coefficient_terms']/max(1,c['metrics']['initial_max_coefficient_terms'])
    return c

def search(out,budget=40,seed=20261020):
    rng=random.Random(seed);out=Path(out);out.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    baseline={f:guarded(f,BASELINES['sparse'])['metrics']['arithmetic_operations'] for f in TRAIN}
    tested=[];seen=set();initial=list(BASELINES.values())
    while len(tested)<budget:
        if initial:p=initial.pop(0).copy()
        elif len(tested)<10 or rng.random()<.25:p={k:rng.choice(v) for k,v in SPACE.items()}
        else:
            parents=sorted(tested,key=lambda x:x['score'])[:8]
            p=rng.choice(parents)['policy'].copy()
            for k in rng.sample(list(SPACE),rng.choice([1,1,2])):p[k]=rng.choice(SPACE[k])
        key=json.dumps(p,sort_keys=True)
        if key in seen:continue
        seen.add(key);runs={f:guarded(f,p)['metrics'] for f in TRAIN}
        success=all(x['success'] for x in runs.values())
        score=math.exp(statistics.mean(math.log(runs[f]['arithmetic_operations']/baseline[f]) for f in TRAIN)) if success else 1e99
        trial=dict(trial=len(tested),policy=p,score=score,runs=runs)
        tested.append(trial);print(f"trial {len(tested)}/{budget}: {score:.5f} {p}",flush=True)
        dump(out/'search.json',dict(seed=seed,budget=budget,train=TRAIN,held_out=TEST,objective='training geometric mean arithmetic ratio to sparse',trials=tested,seconds=time.perf_counter()-start))
    winner=min(tested,key=lambda x:(x['score'],json.dumps(x['policy'],sort_keys=True)))
    # Exactly check all training certificates before freeze/test.
    from .validator import check,prune
    checked=[]
    for f in TRAIN:
        c=prune(guarded(f,winner['policy'],True));checked.append(check(c));dump(out/'certificates'/f'{f}-train.json',c)
    frozen=dict(policy=winner['policy'],training_score=winner['score'],seed=seed,budget=budget,
      training=TRAIN,held_out=TEST,training_validation=checked,search_sha256=hashlib.sha256((out/'search.json').read_bytes()).hexdigest(),
      note='Frozen before held-out policy evaluation; benchmark-development baseline runs are disclosed in report. No family name enters policy.')
    dump(out/'frozen.json',frozen);print('FROZEN',frozen,flush=True)

def worker(args):
    p=json.loads(args.policy);start=time.perf_counter();cpu=time.process_time()
    c=guarded(args.family,p,bool(args.certificate));metrics=c['metrics']
    metrics['worker_seconds']=time.perf_counter()-start;metrics['cpu_seconds']=time.process_time()-cpu
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    metrics['peak_rss_bytes']=rss if sys.platform=='darwin' else rss*1024
    if args.certificate:
        from .validator import check,prune
        c=prune(c);t0=time.perf_counter();checked=check(c);checked['seconds']=time.perf_counter()-t0
        dump(args.certificate,c);metrics['validation']=checked
    print(json.dumps(metrics))

def isolated(f,p,timeout=90,certificate=None):
    command=[sys.executable,'-m','ibp.experiment','worker','--family',f,'--policy',json.dumps(p)]
    if certificate:command+=['--certificate',str(certificate)]
    t0=time.perf_counter()
    try:
        r=subprocess.run(command,capture_output=True,text=True,timeout=timeout,env=dict(os.environ,PYTHONHASHSEED='0'))
        if r.returncode:return dict(success=False,error=r.stderr[-2000:])
        result=json.loads(r.stdout);result['subprocess_wall_seconds']=time.perf_counter()-t0;return result
    except subprocess.TimeoutExpired:return dict(success=False,error=f'timeout {timeout}s')

def benchmark(out,repeats=3):
    out=Path(out);frozen=json.loads((out/'frozen.json').read_text());winner=frozen['policy']
    methods=dict(BASELINES,learned=winner,sparse_AA=BASELINES['sparse'],learned_no_reuse=dict(winner,reuse=False))
    dump(out/'evaluation-lock.json',dict(frozen_sha256=hashlib.sha256((out/'frozen.json').read_bytes()).hexdigest(),methods=methods,repeats=repeats,timeout=90))
    runs=[];started=time.perf_counter();rng=random.Random(89173)
    for repeat in range(repeats):
        for f in NAMES:
            order=list(methods);rng.shuffle(order)
            for method in order:
                print(f'run {repeat+1}/{repeats} {f} {method}',flush=True)
                result=isolated(f,methods[method]);runs.append(dict(method=method,instance=f,repeat=repeat,split=family(f)['split'],value=result.get('arithmetic_operations'),**result))
                dump(out/'runs.json',runs)
    checks=[]
    for f in NAMES:
        for method in ['sparse','learned']:
            path=out/'certificates'/f'{f}-{method}.json'
            result=isolated(f,methods[method],timeout=180,certificate=path)
            checks.append(dict(family=f,method=method,**result));print('certificate',f,method,result.get('validation',result.get('error')),flush=True)
    dump(out/'validation.json',checks)
    summary=[]
    for f in NAMES:
        for method in methods:
            rows=[r for r in runs if r['instance']==f and r['method']==method];valid=all(r['success'] for r in rows)
            entry=dict(instance=f,method=method,split=family(f)['split'],success=valid)
            if valid:
                if len({r['arithmetic_operations'] for r in rows})!=1:raise ValueError('Nondeterministic operation count')
                for k in ['arithmetic_operations','input_rows','input_nnz','targets','masters','peak_live_nnz','max_row_nnz','max_coefficient_terms','expression_growth_ratio','max_polynomial_degree','max_coefficient_bits','cache_hits','fallback']:
                    entry[k]=rows[0][k]
                for k in ['reduction_seconds','cpu_seconds','peak_rss_bytes']:
                    values=[r[k] for r in rows];entry[k]=statistics.median(values);entry[k+'_range']=[min(values),max(values)]
            summary.append(entry)
    dump(out/'summary.json',summary)
    info=dict(platform=platform.platform(),machine=platform.machine(),processor=platform.processor(),python=sys.version,
              sympy=__import__('sympy').__version__,cpu_count=os.cpu_count(),seconds=time.perf_counter()-started,
              note='Fresh sequential subprocesses; randomized method order within family/repeat; RSS includes interpreter/imports; no dedicated CPU isolation.')
    dump(out/'machine.json',info)
    print('COMPLETE',info,flush=True)

def reproduce(out):
    from .validator import check
    out=Path(out);count=0
    for p in sorted((out/'certificates').glob('*.json')):
        c=json.loads(p.read_text());print(p.name,check(c),flush=True);count+=1
    if not count:raise ValueError('Missing certificates')
    summary=json.loads((out/'summary.json').read_text());frozen=json.loads((out/'frozen.json').read_text())
    for f in NAMES:
        for method,policy in [('sparse',BASELINES['sparse']),('learned',frozen['policy'])]:
            m=guarded(f,policy)['metrics'];old=next(r for r in summary if r['instance']==f and r['method']==method)
            for key in ['arithmetic_operations','input_rows','peak_live_nnz','max_coefficient_terms','max_polynomial_degree','max_coefficient_bits']:
                if m[key]!=old[key]:raise ValueError(f'Metric mismatch {f} {method} {key}')
            if not m['success']:raise ValueError('Incomplete reduction')
    print(f'PASS: {count} exact certificates; sparse/learned deterministic costs reproduced on {len(NAMES)} families.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['search','benchmark','worker','reproduce']);p.add_argument('--out',default='results');p.add_argument('--budget',type=int,default=40);p.add_argument('--seed',type=int,default=20261020);p.add_argument('--repeats',type=int,default=3);p.add_argument('--family',choices=NAMES);p.add_argument('--policy');p.add_argument('--certificate');args=p.parse_args()
    if args.command=='worker':worker(args)
    elif args.command=='search':search(args.out,args.budget,args.seed)
    elif args.command=='benchmark':benchmark(args.out,args.repeats)
    else:reproduce(args.out)
