"""Independent symbolic certificate checker.

Does NOT import the reducer, its row generator, zero test, or field arithmetic.
Inputs are derived again by directional differentiation in scalar products.
All equalities are polynomial identities over Q[d,s,t,m,u], never samples.
SymPy is a shared trusted algebra dependency (not a formally verified kernel).
"""
import json
from functools import lru_cache
from itertools import product
import sympy as S
D,s,t,m,u=S.symbols('d s t m u');SYMBOLS=(D,s,t,m,u)

SPECS={
 'tadpole':([m],[[0]],[(1,)],4),
 'bubble_massless':([0,0],[[0,s],[s,0]],[(1,1)],4),
 'bubble_equal_mass':([m,m],[[0,s],[s,0]],[(1,0),(1,1)],3),
 'triangle_one_mass':([0,0,0],[[0,0,s],[0,0,0],[s,0,0]],[(1,0,1)],4),
 'bubble_unequal_mass':([m,u],[[0,s],[s,0]],[(1,0),(0,1),(1,1)],4),
 'triangle_offshell':([0,0,0],[[0,s,u],[s,0,t],[u,t,0]],[(1,1,0),(1,0,1),(0,1,1),(1,1,1)],4),
 'box_massless':([0,0,0,0],[[0,0,s,0],[0,0,0,t],[s,0,0,0],[0,t,0,0]],[(1,0,1,0),(0,1,0,1),(1,1,1,1)],5),
}

SPECS.update({
 'bubble_one_mass':([0,m],[[0,s],[s,0]],[(0,1),(1,1)],5),
 'triangle_two_mass':([0,0,0],[[0,0,s],[0,0,t],[s,t,0]],[(1,0,1),(0,1,1)],4),
 'box_one_mass':([0,0,0,0],[[0,0,s,u],[0,0,0,t],[s,0,0,0],[u,t,0,0]],[(1,0,1,0),(0,1,0,1),(1,0,0,1),(1,1,1,1)],5),
})

@lru_cache(maxsize=20000)
def normal(x):return S.cancel(x)

def exact_zero(x):
    numerator,denominator=S.fraction(normal(x))
    if S.Poly(denominator,*SYMBOLS).is_zero:raise ValueError('Zero denominator')
    return S.Poly(numerator,*SYMBOLS,domain=S.QQ).is_zero

def decode(x):
    if not isinstance(x,list) or len(x)!=2:raise ValueError('Invalid rational function')
    def polynomial(terms):
        out=S.Integer(0)
        for powers,num,den in terms:
            if len(powers)!=5 or any(type(p)!=int or p<0 for p in powers):raise ValueError('Bad monomial')
            if type(num)!=int or type(den)!=int or den<=0:raise ValueError('Bad coefficient')
            out+=S.Rational(num,den)*S.prod(v**p for v,p in zip(SYMBOLS,powers))
        return out
    a,b=map(polynomial,x)
    if exact_zero(b):raise ValueError('Zero denominator')
    return normal(a/b)

def scaleless(a,masses,dist):
    active=[i for i in range(len(a)) if a[i]>0]
    return all(masses[i]==0 for i in active) and all(dist[i][j]==0 for i in active for j in active)

def input_row(name,a,j):
    if name == 'sunset_equal_mass_v1':
        from .two_loop_check import input_row as two_loop_input
        return two_loop_input(a,j)
    masses,dist,_,_=SPECS[name];n=len(masses)
    if len(a)!=n or any(type(v)!=int for v in a) or type(j)!=int or not 0<=j<n:raise ValueError('Bad seed')
    # k^2=x, k.r_i=y_i, r_0=0. Differentiate with vector k+r_j:
    # directional D_i = 2*(x+y_i+y_j+r_i.r_j).
    z=S.symbols('z:'+str(n));x=S.Symbol('x');y=(S.Integer(0),)+S.symbols('y1:'+str(n))
    substitutions={x:z[0]-masses[0]}
    for i in range(1,n):substitutions[y[i]]=(z[i]-z[0]-dist[0][i]-masses[i]+masses[0])/2
    row={tuple(a):D}
    for i in range(n):
        if not a[i]:continue
        # Rational(1,2) avoids a floating-point value even for all-integer distances.
        rij=S.sympify(dist[0][i]+dist[0][j]-dist[i][j])/2
        directional=S.expand((2*(x+y[i]+y[j]+rij)).subs(substitutions,simultaneous=True))
        for powers,coefficient in S.Poly(directional,*z).terms():
            b=tuple(a[k]+int(k==i)-powers[k] for k in range(n))
            row[b]=row.get(b,0)-a[i]*coefficient
    return {b:normal(c) for b,c in row.items() if not exact_zero(c) and not scaleless(b,masses,dist)}

def check(cert):
    if cert.get('version')!=1 or cert.get('family') not in set(SPECS)|{'sunset_equal_mass_v1'}:raise ValueError('Unknown certificate')
    name=cert['family']
    if name == 'sunset_equal_mass_v1':
        from .two_loop_check import MASTERS, REQUIRED
        masters=set(MASTERS);required=set(REQUIRED)
    else:
        masses,dist,masters,rmax=SPECS[name];masters=set(masters);n=len(masses)
        required={a for a in product(range(rmax+1),repeat=n) if 0<sum(a)<=rmax and not scaleless(a,masses,dist)}-masters
    outputs=cert['outputs']
    if len(outputs)!=len(required) or {tuple(o['target']) for o in outputs}!=required:raise ValueError('Incomplete/duplicate targets')
    nodes=cert['nodes'];live={};refs=[0]*len(nodes)
    for i,node in enumerate(nodes):
        for key in ('left','right','row'):
            if key in node:
                j=node[key]
                if type(j)!=int or not 0<=j<i:raise ValueError('Invalid DAG reference')
                refs[j]+=1
    roots={o['root'] for o in outputs}
    if any(type(i)!=int or not 0<=i<len(nodes) for i in roots):raise ValueError('Invalid root')
    for i in roots:refs[i]+=1
    for i,node in enumerate(nodes):
        op=node['op']
        if op=='input':r=input_row(name,node['seed'],node['vector'])
        elif op=='symmetry':
            if name!='bubble_equal_mass':raise ValueError('Unsupported symmetry')
            r={(0,1):S.Integer(1),(1,0):S.Integer(-1)}
        elif op=='scale':
            factor=decode(node['factor'])
            if exact_zero(factor):raise ValueError('Singular row scaling')
            r={a:normal(c*factor) for a,c in live[node['row']].items()}
        elif op=='axpy':
            r=live[node['left']].copy();factor=decode(node['factor'])
            for a,c in live[node['right']].items():
                value=normal(r.get(a,0)+factor*c)
                if exact_zero(value):r.pop(a,None)
                else:r[a]=value
        else:raise ValueError('Unknown proof operation')
        if refs[i]:live[i]=r
        for key in ('left','right','row'):
            if key in node:
                j=node[key];refs[j]-=1
                if not refs[j]:live.pop(j,None)
    for out in outputs:
        a=tuple(out['target']);r=live[out['root']]
        advertised={tuple(k):decode(v) for k,v in out['row']}
        if len(advertised)!=len(out['row']):raise ValueError('Duplicate integral')
        if not exact_zero(advertised.get(a,0)-1):raise ValueError('Target not normalized')
        if set(advertised)-masters-{a}:raise ValueError('Unreduced integral in result')
        for k in set(r)|set(advertised):
            if not exact_zero(r.get(k,0)-advertised.get(k,0)):raise ValueError('Certificate/result mismatch')
    return dict(valid=True,family=name,identities=len(outputs),proof_nodes=len(nodes),arithmetic='exact rational polynomial identities')

def prune(cert):
    """Only serialization cleanup; checker also accepts the unpruned DAG."""
    wanted=set();nodes=cert['nodes']
    def visit(i):
        if i in wanted:return
        wanted.add(i)
        for key in ('left','right','row'):
            if key in nodes[i]:visit(nodes[i][key])
    for o in cert['outputs']:visit(o['root'])
    ordered=sorted(wanted);mapping={old:new for new,old in enumerate(ordered)}
    result=[]
    for old in ordered:
        node=nodes[old].copy()
        for key in ('left','right','row'):
            if key in node:node[key]=mapping[node[key]]
        result.append(node)
    cert['nodes']=result
    for o in cert['outputs']:o['root']=mapping[o['root']]
    return cert

if __name__=='__main__':
    import sys
    print(json.dumps(check(json.load(open(sys.argv[1]))),indent=2))
