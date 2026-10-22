"""Generate, exactly replay, and analytically cross-check the two-loop bridge."""
import copy,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from ibp.reducer import reduce
from ibp.contributor import online
from ibp.validator import check,decode,exact_zero,D,m
from ibp.two_loop import equations
from ibp.two_loop_check import input_row
OUT=ROOT/'research/readiness-20261021'
def main():
    for a,j,row in equations():
        other=input_row(a,j)
        if set(row)!=set(other) or any(not exact_zero(v.as_expr()-other[b]) for b,v in row.items()):raise ValueError('independent input mismatch')
    report=[]
    for name,fn,policy in [('sparse',reduce,dict(seed='rectangular',order='sector',row='short',reuse=True)),
      ('online',online,dict(seed='rectangular',order='dots',schedule='target',reuse=True))]:
        start=time.perf_counter();cert=fn('sunset_equal_mass_v1',policy,certificate=True)
        if not cert['metrics']['success']:raise ValueError(cert['metrics'])
        generated=time.perf_counter()-start;start=time.perf_counter();result=check(cert)
        rows={tuple(o['target']):{tuple(a):decode(c) for a,c in o['row']} for o in cert['outputs']}
        # Scaling of the sunset and factorized tadpole tensor control.
        if not exact_zero(rows[2,1,1].get((1,1,1),0)-(D-3)/(3*m)):raise ValueError('sunset scaling recurrence')
        if not exact_zero(rows[2,1,-1].get((1,1,0),0)+D/2):raise ValueError('numerator factorization')
        for mutate in ('missing','coefficient','seed'):
            bad=copy.deepcopy(cert)
            if mutate=='missing':bad['outputs'].pop()
            elif mutate=='coefficient':bad['outputs'][0]['row'][0][1][0][0][1]+=1
            else:next(n for n in bad['nodes'] if n['op']=='input')['vector']=4
            try:check(bad)
            except (ValueError,KeyError):pass
            else:raise ValueError('mutation accepted '+mutate)
        (OUT/f'two-loop-{name}.json').write_text(json.dumps(cert,indent=2)+'\n')
        report.append(dict(method=name,metrics=cert['metrics'],check=result,generation_seconds=generated,verification_seconds=time.perf_counter()-start,negative_controls=3))
        print(name,result,flush=True)
    (OUT/'two-loop-results.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
