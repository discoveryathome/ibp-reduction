"""Timed contributor trial: small structural search, frozen new-family tests."""
import argparse,hashlib,json,math,os,platform,random,resource,statistics,subprocess,sys,time
from pathlib import Path
from .families import NAMES
from .reducer import BASELINES,Arithmetic
from .experiment import guarded,dump
from .contributor import online
DEV=['bubble_massless','bubble_equal_mass','triangle_one_mass']
NEW=['bubble_one_mass','triangle_two_mass','box_one_mass']

def worker(args):
    policy=json.loads(args.policy)
    profile={'trivial':0,'nontrivial':0};original_op=Arithmetic.op
    def profiled(ar,kind,a,b):
        before=ar.calls[kind];value=original_op(ar,kind,a,b)
        if ar.calls[kind]>before:
            trivial=(kind=='add' and (not a or not b or a==-b)) or (kind=='mul' and (a in (0,1,-1) or b in (0,1,-1))) or (kind=='div' and (not a or b in (1,-1) or a==b or a==-b))
            profile['trivial' if trivial else 'nontrivial']+=1
        return value
    Arithmetic.op=profiled
    t=time.perf_counter();cpu=time.process_time()
    c=online(args.family,policy,bool(args.certificate)) if args.engine=='online' else guarded(args.family,policy,bool(args.certificate))
    m=c['metrics'];m['nontrivial_arithmetic_operations']=profile['nontrivial'];m['trivial_arithmetic_operations']=profile['trivial'];m['worker_seconds']=time.perf_counter()-t;m['cpu_seconds']=time.process_time()-cpu
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;m['peak_rss_bytes']=rss if sys.platform=='darwin' else 1024*rss
    if args.certificate and m['success']:
        from .validator import check,prune
        c=prune(c);t=time.perf_counter();m['validation']=check(c);m['validation']['seconds']=time.perf_counter()-t;dump(args.certificate,c)
    print(json.dumps(m))

def run(f,engine,policy,timeout=60,certificate=None):
    cmd=[sys.executable,'-m','ibp.trial','worker','--family',f,'--engine',engine,'--policy',json.dumps(policy)]
    if certificate:cmd+=['--certificate',str(certificate)]
    start=time.perf_counter()
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout,env=dict(os.environ,PYTHONHASHSEED='0'))
        if p.returncode:return dict(success=False,error=p.stderr[-2000:],subprocess_seconds=time.perf_counter()-start)
        return dict(json.loads(p.stdout),subprocess_seconds=time.perf_counter()-start)
    except subprocess.TimeoutExpired:return dict(success=False,error=f'timeout after {timeout}s',subprocess_seconds=time.perf_counter()-start)

def explore(out):
    start=time.perf_counter();base={};trials=[]
    for f in DEV:
        base[f]=run(f,'batch',dict(BASELINES['sparse'],seed='tight',reuse=True));print('cached tight baseline',f,base[f].get('arithmetic_operations'),flush=True)
    for schedule in ['seed','short','simple','target']:
        for order in ['sector','dots']:
            policy=dict(seed='rectangular',reuse=True,schedule=schedule,order=order)
            runs={f:run(f,'online',policy) for f in DEV}
            good=all(m['success'] for m in runs.values())
            score=math.exp(statistics.mean(math.log(runs[f]['arithmetic_operations']/base[f]['arithmetic_operations']) for f in DEV)) if good else 1e99
            trials.append(dict(policy=policy,runs=runs,score=score));print('H1',policy,'score',score,flush=True)
            dump(out/'exploration.json',dict(dev=DEV,new=NEW,baseline=base,trials=trials,seconds=time.perf_counter()-start))
    best=min(trials,key=lambda t:t['score'])
    checks=[]
    for f in DEV:
        c=run(f,'online',best['policy'],certificate=out/'certificates'/f'{f}-dev.json',timeout=120)
        if not c.get('validation',{}).get('valid'):raise ValueError(c)
        checks.append(c)
    frozen=dict(policy=best['policy'],training_score=best['score'],dev=DEV,new=NEW,checks=checks,
       code_sha256=hashlib.sha256(Path('ibp/contributor.py').read_bytes()).hexdigest(),
       exploration_sha256=hashlib.sha256((out/'exploration.json').read_bytes()).hexdigest(),
       frozen_at=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat())
    dump(out/'frozen.json',frozen);print('FROZEN',best['policy'],flush=True)

def evaluate(out):
    frozen=json.loads((out/'frozen.json').read_text());initial=json.loads(Path('results/frozen.json').read_text())
    methods={'cached_sparse':('batch',dict(BASELINES['sparse'],reuse=True)),
             'cached_tight':('batch',dict(BASELINES['sparse'],seed='tight',reuse=True)),
             'initial_learned':('batch',initial['policy']),
             'online':('online',frozen['policy'])}
    # These are a development regression and three untouched family cases.
    cases=['box_massless']+NEW;rng=random.Random(52981);rows=[]
    dump(out/'evaluation-lock.json',dict(cases=cases,methods=methods,repeats=3,
      frozen_sha256=hashlib.sha256((out/'frozen.json').read_bytes()).hexdigest(),
      note='box_massless is exposed development regression; the other three were not evaluated during trial policy selection.'))
    for rep in range(3):
        for f in cases:
            order=list(methods);rng.shuffle(order)
            for name in order:
                engine,policy=methods[name];print('TEST',rep,f,name,flush=True)
                row=run(f,engine,policy,timeout=90)
                rows.append(dict(instance=f,method=name,repeat=rep,**row));dump(out/'runs.json',rows)
    checks=[]
    for f in cases:
        for name in methods:
            engine,policy=methods[name];print('CHECK',f,name,flush=True)
            m=run(f,engine,policy,timeout=180,certificate=out/'certificates'/f'{f}-{name}.json')
            checks.append(dict(instance=f,method=name,**m));dump(out/'validation.json',checks)
    summary=[]
    for f in cases:
        for method in methods:
            subset=[r for r in rows if r['instance']==f and r['method']==method]
            entry=dict(instance=f,method=method,success=all(x['success'] for x in subset))
            if entry['success']:
                assert len({r['arithmetic_operations'] for r in subset})==1
                for k in ['arithmetic_operations','nontrivial_arithmetic_operations','trivial_arithmetic_operations','attempted_operations','cache_hits','input_rows','input_nnz','processed_rows','targets','masters','peak_live_nnz','max_row_nnz','max_coefficient_terms','max_polynomial_degree','max_coefficient_bits','fallback']:
                    entry[k]=subset[0].get(k)
                for k in ['reduction_seconds','cpu_seconds','peak_rss_bytes']:
                    values=[r[k] for r in subset];entry[k]=statistics.median(values);entry[k+'_range']=[min(values),max(values)]
            summary.append(entry)
    dump(out/'summary.json',summary);print('EVALUATION COMPLETE',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['worker','explore','evaluate']);parser.add_argument('--out',default='contributor-trial');parser.add_argument('--family');parser.add_argument('--engine');parser.add_argument('--policy');parser.add_argument('--certificate');args=parser.parse_args();out=Path(args.out)
    if args.command=='worker':worker(args)
    elif args.command=='explore':explore(out)
    else:evaluate(out)
