"""Frozen one-loop Euclidean families; masses are squared masses.
I(a) = integral d^d k / product_i ((k+r_i)^2 + m_i)^a_i.
Distances S_ij=(r_i-r_j)^2. d and all named invariants remain symbolic.
"""
from itertools import product
from sympy import QQ
FIELD = QQ.frac_field('d', 's', 't', 'm', 'u')
d, s, t, m, u = FIELD.gens

def family(name):
    if name == 'sunset_equal_mass_v1':
        from .two_loop import specification
        return specification()
    specs = {
        'tadpole': ([m], [[0]], [(1,)], 4, 'control'),
        'bubble_massless': ([0,0], [[0,s],[s,0]], [(1,1)], 4, 'train'),
        'bubble_equal_mass': ([m,m], [[0,s],[s,0]], [(1,0),(1,1)], 3, 'train'),
        'triangle_one_mass': ([0,0,0], [[0,0,s],[0,0,0],[s,0,0]], [(1,0,1)], 4, 'train'),
        'bubble_unequal_mass': ([m,u], [[0,s],[s,0]], [(1,0),(0,1),(1,1)], 4, 'test'),
        'triangle_offshell': ([0,0,0], [[0,s,u],[s,0,t],[u,t,0]], [(1,1,0),(1,0,1),(0,1,1),(1,1,1)], 4, 'test'),
        'box_massless': ([0,0,0,0], [[0,0,s,0],[0,0,0,t],[s,0,0,0],[0,t,0,0]], [(1,0,1,0),(0,1,0,1),(1,1,1,1)], 5, 'test'),
    }
    specs.update({
        'bubble_one_mass': ([0,m], [[0,s],[s,0]], [(0,1),(1,1)], 5, 'trial-test'),
        'triangle_two_mass': ([0,0,0], [[0,0,s],[0,0,t],[s,t,0]], [(1,0,1),(0,1,1)], 4, 'trial-test'),
        'box_one_mass': ([0,0,0,0], [[0,0,s,u],[0,0,0,t],[s,0,0,0],[u,t,0,0]], [(1,0,1,0),(0,1,0,1),(1,0,0,1),(1,1,1,1)], 5, 'trial-test'),
    })
    masses, distances, masters, rmax, split = specs[name]
    # Equal masses: a translation/reflection identifies the two tadpoles.
    return dict(name=name, masses=list(map(FIELD.convert,masses)),
                distances=[[FIELD.convert(x) for x in row] for row in distances],
                masters=masters, rmax=rmax, split=split, n=len(masses))

NAMES = ['tadpole','bubble_massless','bubble_equal_mass','triangle_one_mass',
         'bubble_unequal_mass','triangle_offshell','box_massless']

def zero(a,f):
    support=[i for i,x in enumerate(a) if x>0]
    return not support or (all(not f['masses'][i] for i in support) and
        all(not f['distances'][i][j] for i in support for j in support))

def indices(n,rmax,numerators=0):
    for a in product(range(-numerators,rmax+1),repeat=n):
        if 0<sum(max(x,0) for x in a)<=rmax and sum(max(-x,0) for x in a)<=numerators:
            yield a

def targets(f):
    if f['name'] == 'sunset_equal_mass_v1':
        from .two_loop import TARGETS
        return TARGETS
    return [a for a in indices(f['n'],f['rmax']) if not zero(a,f)]

def seeds(f, mode='rectangular'):
    seed_rmax=f['rmax']-1 if mode=='tight' else f['rmax']
    for a in indices(f['n'],seed_rmax,1):
        if zero(a,f): continue
        dots=sum(max(x-1,0) for x in a)
        num=sum(max(-x,0) for x in a)
        lines=sum(x>0 for x in a)
        if mode=='golden' and dots>f['rmax']-f['n']: continue
        if mode=='improved' and (dots>f['rmax']-f['n'] or num>max(0,lines-2)): continue
        yield a

def equations(f,mode='rectangular'):
    if f['name'] == 'sunset_equal_mass_v1':
        from .two_loop import equations as two_loop_equations
        yield from two_loop_equations(mode)
        return
    for a in seeds(f,mode):
        for j in range(f['n']):
            row={a:d-sum(a)}
            for i,ai in enumerate(a):
                if not ai: continue
                b=list(a);b[i]+=1;b[j]-=1;b=tuple(b)
                row[b]=row.get(b,FIELD.zero)-ai
                b=list(a);b[i]+=1;b=tuple(b)
                c=ai*(f['masses'][i]+f['masses'][j]+f['distances'][i][j])
                row[b]=row.get(b,FIELD.zero)+c
            yield a,j,{b:FIELD.convert(c) for b,c in row.items() if c and not zero(b,f)}
