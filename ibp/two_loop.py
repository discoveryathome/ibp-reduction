"""Separate v1 two-loop equal-mass Euclidean vacuum sunset formulation.
D1=k1^2+m, D2=k2^2+m, D3=(k1-k2)^2+m; m is mass squared.
Canonical integral indices use the S3 changes of loop variables; scaleless loops vanish.
"""
from itertools import product
from .families import FIELD,d,m
TARGETS=[(1,1,1),(1,1,0),(2,1,1),(3,1,1),(2,2,1),(2,1,0),(2,2,0),(3,1,0),(1,1,-1),(2,1,-1),(2,2,-1)]
def specification():return dict(name='sunset_equal_mass_v1',masters=[(1,1,1),(1,1,0)],n=3,rmax=5,split='new-development')
def canonical(a):return tuple(sorted(a,reverse=True))
def equations(mode='rectangular'):
    # Each entry is (D1,D2,D3,constant/m) in k_j dot derivative_{k_i} D_l.
    contractions=[[(2,0,0,-2),(0,0,0,0),(1,-1,1,-1)],
                  [(1,1,-1,-1),(0,0,0,0),(1,-1,-1,1)],
                  [(0,0,0,0),(1,1,-1,-1),(-1,1,-1,1)],
                  [(0,0,0,0),(0,2,0,-2),(-1,1,1,-1)]]
    limit=4 if mode=='tight' else 5
    seeds=sorted({canonical(a) for a in product(range(-1,limit+1),repeat=3) if 2<=sum(x>0 for x in a) and sum(max(x,0) for x in a)<=limit and sum(max(-x,0) for x in a)<=1})
    for a in seeds:
        for j,terms in enumerate(contractions):
            row={a:d if j in (0,3) else FIELD.zero}
            for i,ai in enumerate(a):
                if not ai:continue
                for t,c in enumerate(terms[i]):
                    if not c:continue
                    b=list(a);b[i]+=1
                    if t<3:b[t]-=1
                    b=canonical(b)
                    if sum(x>0 for x in b)<2:continue
                    row[b]=row.get(b,FIELD.zero)-ai*c*(m if t==3 else FIELD.one)
            yield a,j,{b:FIELD.convert(c) for b,c in row.items() if c}
