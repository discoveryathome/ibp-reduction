"""Contributor hypothesis: demand-driven online sparse elimination.

A classical algorithm variant, not a novelty claim. Input rows are processed once;
existing pivots simplify each incoming row. Stop when the dependency closure of
all target integrals has pivots. Back-substitute only that closure. The frozen
initial engine remains in reducer.py for comparison.
"""
import time
from .families import FIELD,family,equations,targets
from .reducer import Arithmetic,encode,encode_row,priority

def online(name,policy,certificate=False):
    start=time.perf_counter();f=family(name);ar=Arithmetic(policy.get('reuse',True));nodes=[]
    def node(x):
        if not certificate:return -1
        nodes.append(x);return len(nodes)-1
    masters=set(f['masters']);wanted=set(targets(f))-masters
    inputs=list(equations(f,policy.get('seed','rectangular')))
    mode=policy.get('schedule','seed')
    if mode=='short':inputs.sort(key=lambda item:(len(item[2]),sum(max(x,0) for x in item[0]),item[0],item[1]))
    elif mode=='simple':inputs.sort(key=lambda item:(sum(max(x,0) for x in item[0]),sum(max(-x,0) for x in item[0]),len(item[2]),item[0],item[1]))
    elif mode=='target':inputs.sort(key=lambda item:(not bool(set(item[2])&wanted),len(item[2]),item[0],item[1]))
    initial_rows=sum(bool(r) for _,_,r in inputs)+(name=='bubble_equal_mass')
    initial_nnz=sum(len(r) for _,_,r in inputs)+(2 if name=='bubble_equal_mass' else 0)
    for _,_,r in inputs:
        for c in r.values():ar.observe(c)
    initial_terms=ar.max_terms;pivots={};processed=0;max_row=0;max_nnz=initial_nnz;constraints=0
    def axpy(left,li,right,ri,factor):
        out=left.copy()
        for k,v in right.items():
            x=ar.op('mul',factor,v)
            if k in out:x=ar.op('add',out[k],x)
            if x:out[k]=x
            else:out.pop(k,None)
        return out,node(dict(op='axpy',left=li,right=ri,factor=encode(factor)))
    def complete():
        seen=set();todo=list(wanted)
        while todo:
            a=todo.pop()
            if a in seen or a in masters:continue
            if a not in pivots:return False
            seen.add(a);todo.extend(k for k in pivots[a][0] if k!=a and k not in masters)
        return True
    if name=='bubble_equal_mass':
        inputs.insert(0,(None,None,{(0,1):FIELD.one,(1,0):-FIELD.one}))
    for a,j,row in inputs:
        if not row:continue
        processed+=1;rid=node(dict(op='symmetry')) if a is None else node(dict(op='input',seed=list(a),vector=j))
        while row:
            eligible=set(row)-masters
            if not eligible:
                constraints+=1;break
            col=max(eligible,key=lambda a:priority(a,policy.get('order','sector')))
            if col in pivots:
                pr,pid=pivots[col];row,rid=axpy(row,rid,pr,pid,-row[col])
                max_row=max(max_row,len(row));continue
            p=row[col]
            if p!=FIELD.one:
                row={k:ar.op('div',v,p) for k,v in row.items()}
                rid=node(dict(op='scale',row=rid,factor=encode(1/p)))
            pivots[col]=(row,rid);break
        max_row=max(max_row,len(row));max_nnz=max(max_nnz,initial_nnz+sum(len(r) for r,_ in pivots.values())+len(row))
        if complete():break
    solved={};visiting=set()
    def solve(a):
        if a in solved:return solved[a]
        if a not in pivots:raise ValueError(f'Unreduced {a}')
        if a in visiting:raise ValueError('Cycle')
        visiting.add(a);row,rid=pivots[a];row=row.copy()
        for k in list(row):
            if k==a or k in masters:continue
            pr,pid=solve(k);row,rid=axpy(row,rid,pr,pid,-row[k])
        visiting.remove(a);solved[a]=(row,rid);return row,rid
    outputs=[];unresolved=[]
    for a in sorted(wanted):
        try:
            row,rid=solve(a);outputs.append(dict(target=list(a),root=rid,row=encode_row(row)))
        except ValueError as e:unresolved.append(str(e))
    max_nnz=max(max_nnz,initial_nnz+sum(len(r) for r,_ in pivots.values())+sum(len(r) for r,_ in solved.values()))
    metrics=dict(input_rows=initial_rows,processed_rows=processed,input_nnz=initial_nnz,pivots=len(pivots),targets=len(targets(f)),masters=len(masters),reduced=len(outputs),success=not unresolved and not constraints,unresolved=unresolved,residual_master_constraints=constraints,
      arithmetic_operations=sum(ar.calls.values()),operation_counts=dict(ar.calls),attempted_operations=sum(ar.attempts.values()),cache_hits=ar.hits,cache_entries=len(ar.cache),peak_live_nnz=max_nnz,max_row_nnz=max(max_row,max((len(r) for r,_ in solved.values()),default=0)),initial_max_coefficient_terms=initial_terms,max_coefficient_terms=ar.max_terms,max_polynomial_degree=ar.max_degree,max_coefficient_bits=ar.max_bits,expression_growth_ratio=ar.max_terms/max(initial_terms,1),reduction_seconds=time.perf_counter()-start,fallback=False)
    return dict(version=1,family=name,policy=policy,nodes=nodes,outputs=outputs,metrics=metrics)
