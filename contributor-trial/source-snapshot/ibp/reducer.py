"""Sparse exact Gaussian elimination with a replayable row-operation DAG."""
import time
from collections import Counter
from .families import FIELD, equations, family, targets

BASELINES = {
 'laporta': dict(seed='rectangular',order='sector',row='first',reuse=False),
 'sparse': dict(seed='rectangular',order='sector',row='short',reuse=False),
 'golden': dict(seed='golden',order='sector',row='short',reuse=False),
 'improved': dict(seed='improved',order='sector',row='short',reuse=False),
}

def encode(x):
    def poly(p):
        return [[list(m),int(c.numerator),int(c.denominator)] for m,c in sorted(p.terms())]
    return [poly(x.numer),poly(x.denom)]

def encode_row(row):
    return [[list(a),encode(c)] for a,c in sorted(row.items()) if c]

class Arithmetic:
    def __init__(self,reuse):
        self.reuse=reuse;self.cache={};self.attempts=Counter();self.calls=Counter();self.hits=0
        self.max_terms=0;self.max_degree=0;self.max_bits=0
    def op(self,kind,a,b):
        self.attempts[kind]+=1
        key=(kind,a,b)
        if self.reuse and key in self.cache:
            self.hits+=1;return self.cache[key]
        self.calls[kind]+=1
        x={'add':lambda:a+b,'mul':lambda:a*b,'div':lambda:a/b}[kind]()
        self.observe(x)
        if self.reuse and len(self.cache)<10000:self.cache[key]=x
        return x
    def observe(self,x):
        self.max_terms=max(self.max_terms,len(x.numer)+len(x.denom))
        self.max_degree=max(self.max_degree,max((sum(m) for p in [x.numer,x.denom] for m in p),default=0))
        self.max_bits=max(self.max_bits,max((max(abs(int(c.numerator)).bit_length(),int(c.denominator).bit_length()) for p in [x.numer,x.denom] for c in p.values()),default=0))

def priority(a,mode):
    sector=sum(x>0 for x in a);r=sum(max(x,0) for x in a);num=sum(max(-x,0) for x in a)
    if mode=='degree':return (r+num,sector,r,a)
    if mode=='dots':return (r-sector,sector,num,a)
    if mode=='reverse':return (sector,r,num,tuple(reversed(a)))
    return (sector,r,num,a)

def reduce(name,policy,certificate=True):
    started=time.perf_counter();f=family(name);ar=Arithmetic(policy['reuse']);nodes=[]
    def node(x):
        if not certificate:return -1
        nodes.append(x);return len(nodes)-1
    rows=[]
    for a,j,r in equations(f,policy['seed']):
        if r: rows.append([r,node(dict(op='input',seed=list(a),vector=j))])
    if name=='bubble_equal_mass':
        rows.append([{(0,1):FIELD.one,(1,0):-FIELD.one},node(dict(op='symmetry'))])
    input_rows=len(rows);input_nnz=sum(len(r) for r,_ in rows)
    for r,_ in rows:
        for c in r.values():ar.observe(c)
    initial_terms=ar.max_terms
    max_nnz=input_nnz;max_row=max(map(lambda r:len(r[0]),rows),default=0)
    masters=set(f['masters']); columns=sorted(set().union(*(set(r) for r,_ in rows))-masters,key=lambda a:priority(a,policy['order']),reverse=True)
    pivots={};selected=[]
    def axpy(left,li,right,ri,factor):
        out=left.copy()
        for k,v in right.items():
            x=ar.op('mul',factor,v)
            if k in out:x=ar.op('add',out[k],x)
            if x:out[k]=x
            else:out.pop(k,None)
        return out,node(dict(op='axpy',left=li,right=ri,factor=encode(factor)))
    for col in columns:
        candidates=[i for i,(r,_) in enumerate(rows) if col in r]
        if not candidates:continue
        if policy['row']=='first':idx=candidates[0]
        elif policy['row']=='short':idx=min(candidates,key=lambda i:(len(rows[i][0]),i))
        else:idx=min(candidates,key=lambda i:(sum(len(c.numer)+len(c.denom) for c in rows[i][0].values()),len(rows[i][0]),i))
        pivot,pid=rows.pop(idx);selected.append(pid);p=pivot[col]
        if p!=FIELD.one:
            pivot={k:ar.op('div',v,p) for k,v in pivot.items()}
            pid=node(dict(op='scale',row=pid,factor=encode(1/p)))
        pivots[col]=(pivot,pid)
        for i,(r,rid) in enumerate(rows):
            if col in r:rows[i]=list(axpy(r,rid,pivot,pid,-r[col]))
        # Retain all nonzero residuals, including possible master constraints.
        rows=[x for x in rows if x[0]]
        max_row=max(max_row,len(pivot),max((len(r) for r,_ in rows),default=0))
        max_nnz=max(max_nnz,sum(len(r) for r,_ in rows)+sum(len(r) for r,_ in pivots.values()))
    unresolved=[];solved={};visiting=set()
    def solve(a):
        nonlocal max_row,max_nnz
        if a in solved:return solved[a]
        if a not in pivots:raise ValueError(f'Unreduced nonmaster {a}')
        if a in visiting:raise ValueError('Cycle')
        visiting.add(a);r,rid=pivots[a];r=r.copy()
        for k in list(r):
            if k==a or k in masters:continue
            rr,ii=solve(k);r,rid=axpy(r,rid,rr,ii,-r[k])
        visiting.remove(a);solved[a]=(r,rid)
        max_row=max(max_row,len(r));max_nnz=max(max_nnz,sum(len(x) for x,_ in solved.values())+sum(len(x) for x,_ in pivots.values()))
        return r,rid
    outputs=[]
    for a in targets(f):
        if a in masters:continue
        try:
            r,rid=solve(a);outputs.append(dict(target=list(a),root=rid,row=encode_row(r)))
        except ValueError as e:unresolved.append(str(e))
    # A surviving relation on the designated masters signals an overcomplete basis.
    residual_master_constraints=len(rows)
    success=not unresolved and not residual_master_constraints
    metrics=dict(input_rows=input_rows,input_nnz=input_nnz,pivots=len(pivots),targets=len(targets(f)),
      reduced=len(outputs),masters=len(masters),success=success,unresolved=unresolved,
      residual_master_constraints=residual_master_constraints,arithmetic_operations=sum(ar.calls.values()),
      operation_counts=dict(ar.calls),attempted_operations=sum(ar.attempts.values()),cache_hits=ar.hits,
      cache_entries=len(ar.cache),peak_live_nnz=max_nnz,max_row_nnz=max_row,initial_max_coefficient_terms=initial_terms,
      max_coefficient_terms=ar.max_terms,max_polynomial_degree=ar.max_degree,max_coefficient_bits=ar.max_bits,
      expression_growth_ratio=ar.max_terms/max(initial_terms,1),reduction_seconds=time.perf_counter()-started)
    cert=dict(version=1,family=name,policy=policy,nodes=nodes,outputs=outputs,metrics=metrics)
    return cert
