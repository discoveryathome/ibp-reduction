"""Independent derivation of sunset IBP inputs by symbolic directional differentiation.
Shares SymPy with the other checker, but not the producer's contraction table.
"""
import sympy as S
from .validator import D,m,normal,exact_zero
MASTERS=[(1,1,1),(1,1,0)]
REQUIRED=[(2,1,1),(3,1,1),(2,2,1),(2,1,0),(2,2,0),(3,1,0),(1,1,-1),(2,1,-1),(2,2,-1)]
def input_row(a,j):
    if len(a)!=3 or any(type(x)!=int or not -2<=x<=7 for x in a) or type(j)!=int or not 0<=j<4:raise ValueError('sunset seed')
    x,y,z=S.symbols('k1sq k2sq k1dotk2');p=S.symbols('P1:4');i,v=divmod(j,2)
    # Directional changes of scalar products under k_i -> k_i + epsilon*k_v.
    directions=[(2*x,0,z),(2*z,0,y),(0,2*z,x),(0,2*y,z)]
    propagators=(x+m,y+m,x+y-2*z+m);subs={x:p[0]-m,y:p[1]-m,z:(p[0]+p[1]-p[2]-m)/2}
    row={tuple(sorted(a,reverse=True)):D if i==v else S.Integer(0)}
    for ell,denom in enumerate(propagators):
        deriv=sum(S.diff(denom,w)*delta for w,delta in zip((x,y,z),directions[j]));deriv=S.expand(deriv.subs(subs,simultaneous=True))
        for powers,c in S.Poly(deriv,*p).terms():
            b=tuple(sorted((a[k]+int(k==ell)-powers[k] for k in range(3)),reverse=True))
            if sum(q>0 for q in b)<2:continue
            row[b]=row.get(b,0)-a[ell]*c
    return {b:normal(c) for b,c in row.items() if not exact_zero(c)}
