"""Exact unimodular loop change reconciles16 designated entries with15."""
import argparse
import ast
import json
from pathlib import Path

import verify_saved as V

SOURCE=(1,0,1,0,0,1,0)
DESTINATION=(0,1,1,1,0,0,0)
CHANGE=((0,-1),(-1,0))


def momentum(text):
    names={name:tuple(int(i==j) for i in range(4))
           for j,name in enumerate(('k1','k2','p1','p3'))}
    def visit(node):
        if isinstance(node,ast.Name) and node.id in names:return names[node.id]
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):
            return tuple(-v for v in visit(node.operand))
        if isinstance(node,ast.BinOp) and isinstance(node.op,(ast.Add,ast.Sub)):
            a,b=visit(node.left),visit(node.right);sign=-1 if isinstance(node.op,ast.Sub) else 1
            return tuple(x+sign*y for x,y in zip(a,b))
        raise ValueError('unsupported linear momentum')
    return visit(ast.parse(text,mode='eval').body)


def prove(propagators,change=CHANGE):
    if len(propagators)!=7 or any(mass!=0 for _,mass in propagators):
        raise ValueError('fixed seven massless forms required')
    determinant=change[0][0]*change[1][1]-change[0][1]*change[1][0]
    if abs(determinant)!=1:raise ValueError('loop change must be unimodular')
    vectors=[momentum(text) for text,_ in propagators];mapped=[0]*7;records=[]
    for i,power in enumerate(SOURCE):
        if not power:continue
        vector=vectors[i]
        transformed=tuple(sum(vector[k]*change[k][j] for k in range(2)) for j in range(2))+vector[2:]
        matches=[(j,sign) for j,candidate in enumerate(vectors) for sign in (1,-1)
                 if transformed==tuple(sign*x for x in candidate)]
        if len(matches)!=1:raise ValueError('active denominator has no unique signed match')
        j,sign=matches[0];mapped[j]+=power
        records.append(dict(source_position=i+1,target_position=j+1,sign=sign,
                            source_vector=list(vector),transformed_vector=list(transformed)))
    if tuple(mapped)!=DESTINATION:raise ValueError('claimed integral relation does not follow')
    return dict(valid=True,source_integral=list(SOURCE),destination_integral=list(DESTINATION),
                old_loop_momenta=['-new_k2','-new_k1'],loop_matrix=[list(x) for x in change],
                determinant=determinant,absolute_measure_jacobian=1,active_denominator_matches=records,
                statement='I[1,0,1,0,0,1,0] = I[0,1,1,1,0,0,0]',
                domain='Exact momentum-form equality; generic d and external kinematics, assuming invariant dimensionally regularized loop integration.',
                limitation='This one redundancy reconciles the two lists; it does not establish independence/minimality of the remaining15.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native',type=Path,default=V.HERE/'native')
    p.add_argument('--out',type=Path)
    a=p.parse_args()
    if a.out and a.out.exists():raise ValueError('fresh proof output required')
    family=json.loads((a.native/'config/integralfamilies.yaml').read_text())['integralfamilies'][0]
    if family['loop_momenta']!=['k1','k2']:raise ValueError('loop basis drift')
    proof=prove(family['propagators'])
    actual=V.integral_set(a.native/'results/trianglebox/masters')
    final=V.integral_set(a.native/'results/trianglebox/masters.final')
    preferred=V.integral_set(a.native/'masters')
    if actual!=final or preferred-actual!={SOURCE} or actual-preferred or DESTINATION not in actual:
        raise ValueError('native/designated lists do not match the proved reconciliation')
    rejected=[]
    for name,propagators,change in (
        ('missing-loop-swap',family['propagators'],((1,0),(0,1))),
        ('nonunit-Jacobian',family['propagators'],((0,-2),(-1,0))),
        ('changed-active-momentum',[*family['propagators'][:5],['k2+p1',0],family['propagators'][6]],CHANGE),
    ):
        try:prove(propagators,change)
        except ValueError:rejected.append(name)
        else:raise AssertionError('false loop relation accepted')
    proof['rejected_controls']=rejected
    proof['paper_to_native']=[[list(x),list(DESTINATION if x==SOURCE else x)] for x in sorted(preferred)]
    if a.out:a.out.write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof,indent=2))


if __name__=='__main__':main()
