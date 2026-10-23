"""Replay the frozen field witnesses from geometry,without SymPy or IBP text."""
import argparse
import ast
import copy
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import resource
import time

HERE=Path(__file__).resolve().parent
CUT=(0,2,5,7)
TARGET=(1,)*8+(0,0,-5)
SAMPLES=((2147483647,dict(d=23,m1=3,m2=5,m3=17,m4=23)),
         (2147483629,dict(d=61,m1=13,m2=71,m3=89,m4=101)))


def inverse(matrix,p):
    n=len(matrix);a=[list(row)+[int(i==j) for j in range(n)] for i,row in enumerate(matrix)];det=1
    if any(len(row)!=n for row in matrix):raise ValueError('square matrix required')
    for j in range(n):
        pivot=next((i for i in range(j,n) if a[i][j]%p),None)
        if pivot is None:raise ValueError('singular geometric map')
        if pivot!=j:a[j],a[pivot]=a[pivot],a[j];det=-det
        value=a[j][j]%p;det=det*value%p;scale=pow(value,-1,p)
        a[j]=[x*scale%p for x in a[j]]
        for i in range(n):
            if i!=j:
                factor=a[i][j];a[i]=[(x-factor*y)%p for x,y in zip(a[i],a[j])]
    return [row[n:] for row in a],det%p


def momentum(text):
    names={name:tuple(int(i==j) for i in range(6)) for j,name in enumerate(('l1','l2','p1','p2','p3','p4'))}
    def visit(node):
        if isinstance(node,ast.Name) and node.id in names:return names[node.id]
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):return tuple(-x for x in visit(node.operand))
        if isinstance(node,ast.BinOp) and isinstance(node.op,(ast.Add,ast.Sub)):
            a,b=visit(node.left),visit(node.right);sign=-1 if isinstance(node.op,ast.Sub) else 1
            return tuple(x+sign*y for x,y in zip(a,b))
        raise ValueError('unsupported geometric momentum')
    return visit(ast.parse(text,mode='eval').body)


def operators(prime,point,family=None):
    # Solve massless p1..p5,adjacent invariants,and p5=-p1-p2-p3-p4.
    pairs=list(combinations(range(4),2))
    vectors=((1,1,0,0),(0,1,1,0),(0,0,1,1),(1,1,1,0),(0,1,1,1),(1,1,1,1))
    equations=[[2*v[i]*v[j] for i,j in pairs] for v in vectors]
    inv,_=inverse(equations,prime);rhs=[1,point['m1'],point['m2'],point['m3'],point['m4'],0]
    values=[sum(x*y for x,y in zip(row,rhs))%prime for row in inv]
    external=[[0]*4 for _ in range(4)]
    for (i,j),value in zip(pairs,values):external[i][j]=external[j][i]=value
    _,gram_det=inverse(external,prime)
    def constant(x):return [0]*11+[x%prime]
    def variable(i):a=[0]*12;a[i]=1;return a
    gram=[[constant(0) for _ in range(6)] for _ in range(6)]
    gram[0][0]=variable(0);gram[1][1]=variable(1);gram[0][1]=gram[1][0]=variable(2)
    for i in range(4):
        gram[0][i+2]=gram[i+2][0]=variable(i+3)
        gram[1][i+2]=gram[i+2][1]=variable(i+7)
        for j in range(4):gram[i+2][j+2]=constant(external[i][j])
    def dot(left,right,g):
        return [sum(left[i]*right[j]*g[i][j][k] for i in range(6) for j in range(6))%prime for k in range(12)]
    if family is None:family=json.loads((HERE/'results/native/zero-dots/config/integralfamilies.yaml').read_text())['integralfamilies'][0]
    if len(family['propagators'])!=11 or family['cut_propagators']!=[1,3,6,8] or any(m!=0 for _,m in family['propagators']):raise ValueError('frozen geometric family drift')
    forms=[momentum(text) for text,_ in family['propagators']]
    denominators=[dot(v,v,gram) for v in forms]
    inv,det=inverse([row[:11] for row in denominators],prime)
    constants=[row[11] for row in denominators]
    primitive=[row+[-sum(x*y for x,y in zip(row,constants))%prime] for row in inv]
    converted=[[[sum(gram[i][j][k]*primitive[k][l] for k in range(11))%prime for l in range(12)] for j in range(6)] for i in range(6)]
    for i in range(6):
        for j in range(6):converted[i][j][11]=(converted[i][j][11]+gram[i][j][11])%prime
    def template(divergence,deltas):
        terms=[((0,)*11,-1,divergence%prime)] if divergence%prime else []
        for j,delta in enumerate(deltas):
            for k,value in enumerate(delta):
                if value:
                    shift=[0]*11;shift[j]+=1
                    if k<11:shift[k]-=1
                    terms.append((tuple(shift),j,-value%prime))
        return terms
    result={}
    unit=[[int(i==j) for i in range(6)] for j in range(6)]
    for loop in range(2):
        for direction in range(6):
            deltas=[[2*v[loop]*x%prime for x in dot(v,unit[direction],converted)] for v in forms]
            result[f'IBP_l{loop+1}_q{direction}']=template(point['d'] if loop==direction else 0,deltas)
    for i,j in pairs:
        deltas=[]
        for v in forms:
            change=[0]*6
            change[j+2]=sum(v[k+2]*external[i][k] for k in range(4))%prime
            change[i+2]=-sum(v[k+2]*external[j][k] for k in range(4))%prime
            deltas.append([2*x%prime for x in dot(v,change,converted)])
        result[f'LI_p{i+1}_p{j+1}']=template(0,deltas)
    matching=json.loads((HERE/'identities.json').read_text())['matches']
    if {x['operator'] for x in matching}!=set(result) or sorted(x['source_index'] for x in matching)!=list(range(18)):
        raise ValueError('operator bijection drift')
    ordered=[]
    for item in sorted(matching,key=lambda x:x['source_index']):
        scale=Fraction(item['normalization']);factor=scale.numerator*pow(scale.denominator,-1,prime)%prime
        if not factor:raise ValueError('zero operator normalization')
        ordered.append([(shift,index,value*factor%prime) for shift,index,value in result[item['operator']]])
    return ordered,dict(denominator_map_determinant_mod_prime=det,external_gram_determinant_mod_prime=gram_det)


def compositions(total,slots):
    if slots==1:yield (total,);return
    for first in range(total+1):
        for rest in compositions(total-first,slots-1):yield (first,)+rest


def seed_set(width,trivial):
    result=set()
    for sector in range(256):
        if sector&165!=165 or sector in trivial:continue
        support=[(sector>>i)&1 for i in range(11)];absent=[i for i,x in enumerate(support) if not x]
        cap=max(1,width+sum(support)-8+int(sector&~167==0))
        for degree in range(cap+1):
            for powers in compositions(degree,len(absent)):
                seed=support.copy()
                for i,value in zip(absent,powers):seed[i]=-value
                result.add(tuple(seed))
    return result


def verify(certificate,family=None):
    sample=certificate['sample'];mode=certificate['mode']
    if type(sample) is not int or sample not in (0,1) or mode not in ('tube','decreasing'):raise ValueError('scope drift')
    prime,point=SAMPLES[sample]
    if certificate['prime']!=prime or certificate['point']!=point or tuple(certificate['target'])!=TARGET:raise ValueError('point/target drift')
    trivial=set(map(int,(HERE/'fixtures/trivialsector').read_text().strip().split(',')))
    global_masters=[tuple(map(int,line.split(','))) for line in (HERE/'fixtures/masters').read_text().splitlines()]
    masters={a for a in global_masters if all(a[i]>0 for i in CUT)}
    if len(global_masters)!=113 or len(set(global_masters))!=113 or len(masters)!=27:raise ValueError('master convention drift')
    if certificate['master_convention']!=[list(a) for a in sorted(masters)]:raise ValueError('declared master convention drift')
    if mode=='tube':
        seeds=[tuple(json.loads(line)) for line in (HERE/'fixtures/tube-rank5.jsonl').read_text().splitlines()]
        base=seed_set(4,trivial);rebuilt=base|{a[:10]+(a[10]-1,) for a in base}
        if len(base)!=358 or len(rebuilt)!=589 or seeds!=sorted(rebuilt):raise ValueError('tube seed fixture disagrees with geometric replay policy')
    else:
        seeds=sorted(seed_set(5,trivial))
        if len(seeds)!=876:raise ValueError('decreasing-rank policy drift')
    if certificate['seed_count']!=len(seeds):raise ValueError('seed count drift')
    templates,geometry=operators(prime,point,family);total={};seen=set()
    for rid,weight in certificate['witness']:
        if type(rid) is not int or rid in seen or not 0<=rid<18*len(seeds) or type(weight) is not int or not 0<weight<prime:raise ValueError('invalid witness entry')
        seen.add(rid);seed=seeds[rid//18]
        for shift,index,value in templates[rid%18]:
            coefficient=weight*value*(1 if index<0 else seed[index])%prime
            a=tuple(x+y for x,y in zip(seed,shift))
            if not coefficient or not all(a[i]>0 for i in CUT) or sum(1<<i for i,x in enumerate(a) if x>0) in trivial:continue
            if any(x>0 for x in a[8:]):raise ValueError('positive auxiliary index generated')
            total[a]=(total.get(a,0)+coefficient)%prime
    expected={TARGET:1};seen=set()
    for a,value in certificate['coefficients']:
        a=tuple(a)
        if any(type(x) is not int for x in a) or a not in masters or a in seen or type(value) is not int or not 0<value<prime:raise ValueError('invalid master coefficient')
        seen.add(a);expected[a]=(expected.get(a,0)-value)%prime
    if {a:c for a,c in total.items() if c}!={a:c for a,c in expected.items() if c}:raise ValueError('geometric witness disagreement')
    return dict(valid=True,mode=mode,sample=sample,seed_count=len(seeds),original_rows=len(certificate['witness']),**geometry)


def main():
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise ValueError('fresh verification report required')
    results=[];controls=[];started=time.perf_counter()
    for mode in ('tube','decreasing'):
        for sample in (0,1):
            certificate=json.loads((HERE/f'results/fields/{mode}-{sample}.json').read_text());results.append(verify(certificate))
    base=json.loads((HERE/'results/fields/tube-0.json').read_text())
    for label,kind in [('master-coefficient','coefficient'),('witness-weight','weight'),('omitted-row','omit')]:
        mutant=copy.deepcopy(base)
        if kind=='coefficient':mutant['coefficients'][0][1]=mutant['coefficients'][0][1]%(base['prime']-1)+1
        elif kind=='weight':mutant['witness'][0][1]=mutant['witness'][0][1]%(base['prime']-1)+1
        else:mutant['witness'].pop(0)
        try:verify(mutant)
        except ValueError:controls.append(label)
        else:raise AssertionError('altered witness accepted')
    wrong_geometry=json.loads((HERE/'results/native/zero-dots/config/integralfamilies.yaml').read_text())['integralfamilies'][0]
    wrong_geometry['propagators'][6][0]='l1+l2+p4'
    try:verify(base,wrong_geometry)
    except ValueError:controls.append('changed-geometric-momentum')
    else:raise AssertionError('changed geometric momentum accepted')
    result=dict(valid=True,method='Standard-library finite-field Gram constraints,affine inverse and direct momentum differentiation;no SymPy or published coefficient parser.',
                cases=results,rejected_controls=controls,elapsed_seconds=time.perf_counter()-started,
                shared_inputs=['frozen geometry and dimensional-regularization axioms','operator label/normalization bijection','cut/trivial-sector conventions','source master list','existing known witnesses'],
                scope='Same-author verification of four existing field target identities;not a new holdout,independent-person review,rank proof or generic target reconstruction.')
    a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
