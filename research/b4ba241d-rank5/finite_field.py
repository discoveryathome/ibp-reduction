"""Bounded rank-5 field reductions with expanded original-equation witnesses.

The solver compiles affine seed coefficients with SymPy. Witness replay uses a
separate direct AST evaluator over the original pinned text; no elimination.
"""

import argparse, ast, hashlib, json, math, re, time
from collections import Counter
from itertools import combinations_with_replacement
from pathlib import Path
import sympy as S
import identities as I

HERE=Path(__file__).resolve().parent
TARGET=(1,)*8+(0,0,-5)
CUT=(0,2,5,7)
SAMPLES=((2147483647,dict(d=23,m1=3,m2=5,m3=17,m4=23)),
         (2147483629,dict(d=61,m1=13,m2=71,m3=89,m4=101)))


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def model():
    trivial=frozenset(map(int,(HERE/'fixtures/trivialsector').read_text().strip().split(',')))
    masters=[tuple(map(int,l.split(','))) for l in (HERE/'fixtures/masters').read_text().splitlines()]
    if len(masters)!=113 or len(set(masters))!=113:raise ValueError('global master fixture drift')
    selected=frozenset(a for a in masters if all(a[i]>0 for i in CUT))
    if len(selected)!=27:raise ValueError('on-cut master convention drift')
    return trivial,selected


def seeds(mode):
    if mode not in ('tube','decreasing'):raise ValueError('unknown seed policy')
    if mode=='tube':
        result=[tuple(json.loads(l)) for l in (HERE/'fixtures/tube-rank5.jsonl').read_text().splitlines()]
        if len(result)!=589 or len(set(result))!=589:raise ValueError('tube fixture drift')
        return result
    trivial,_=model();result=[]
    for sector in range(256):
        if sector&165!=165 or sector in trivial:continue
        cap=max(1,5+sector.bit_count()-8+int(sector&~167==0))
        support=tuple((sector>>i)&1 for i in range(11));absent=[i for i,a in enumerate(support) if not a]
        for degree in range(cap+1):
            for monomial in combinations_with_replacement(absent,degree):
                counts=Counter(monomial);result.append(tuple(a-counts[i] for i,a in enumerate(support)))
    if len(result)!=876 or len(set(result))!=876:raise ValueError('Eq.18 reference count drift')
    return sorted(result)


def nonzero_integral(a,trivial):
    return all(a[i]>0 for i in CUT) and sum(1<<i for i,x in enumerate(a) if x>0) not in trivial


def compile_templates(prime,point):
    substitutions={x:point[str(x)] for x in (I.D,)+I.M};out=[]
    for row in I.source_templates():
        terms=[]
        for shift,expression in row.items():
            polynomial=S.Poly(expression.subs(substitutions),*I.A,domain=S.QQ)
            affine=[]
            for powers,c in polynomial.terms():
                if sum(powers)>1:raise ValueError('non-affine seed coefficient')
                value=int(c.p)*pow(int(c.q),-1,prime)%prime
                affine.append((-1 if sum(powers)==0 else powers.index(1),value))
            terms.append((shift,affine))
        out.append(terms)
    return out


def equation(seed,template,prime,trivial):
    row={}
    for shift,affine in template:
        c=sum(v if i<0 else v*seed[i] for i,v in affine)%prime
        if not c:continue
        a=tuple(x+y for x,y in zip(seed,shift))
        if not nonzero_integral(a,trivial):continue
        if any(x>0 for x in a[8:]):raise ValueError('positive ISP produced')
        row[a]=(row.get(a,0)+c)%prime
    return {a:c for a,c in row.items() if c}


def add_scaled(row,other,factor,prime):
    for key,value in other.items():
        result=(row.get(key,0)+factor*value)%prime
        if result:row[key]=result
        else:row.pop(key,None)


def reduce(mode,sample):
    start=time.perf_counter();prime,point=SAMPLES[sample]
    if prime<2 or any(prime%q==0 for q in range(2,math.isqrt(prime)+1)):raise ValueError('non-prime')
    trivial,masters=model();seed_list=seeds(mode);templates=compile_templates(prime,point)
    equations=[];variables=set(masters)|{TARGET}
    for i,seed in enumerate(seed_list):
        for j,template in enumerate(templates):
            row=equation(seed,template,prime,trivial)
            if row:equations.append((18*i+j,row));variables.update(row)
    def order(a):
        t=sum(x>0 for x in a);sector=sum(1<<i for i,x in enumerate(a) if x>0)
        return (a not in masters,t,sector,sum(max(x,0) for x in a),sum(-x for x in a if x<0),a)
    columns=sorted(variables,key=order);ids={a:i for i,a in enumerate(columns)}
    records=[(rid,{ids[a]:c for a,c in row.items()}) for rid,row in equations]
    records.sort(key=lambda item:(max(item[1]),len(item[1]),item[0]))
    generated=time.perf_counter();pivots={};derivations=[]
    for rid,row in records:
        deps=[]
        while row:
            pivot=max(row)
            if columns[pivot] in masters:raise ValueError('nonzero relation among frozen masters')
            if pivot not in pivots:
                inverse=pow(row[pivot],-1,prime);normalized={k:v*inverse%prime for k,v in row.items()}
                number=len(derivations);derivations.append((rid,inverse,deps));pivots[pivot]=(normalized,number)
                break
            existing,number=pivots[pivot];factor=row[pivot];deps.append((number,factor))
            add_scaled(row,existing,-factor,prime)
    residual={ids[TARGET]:1};weights={}
    while True:
        reducible=[key for key in residual if key in pivots]
        if not reducible:break
        pivot=max(reducible);row,number=pivots[pivot];factor=residual[pivot]
        weights[number]=(weights.get(number,0)+factor)%prime
        add_scaled(residual,row,-factor,prime)
    survivors=[columns[k] for k in residual if columns[k] not in masters]
    if survivors:raise ValueError('non-master target survivors: '+str(survivors[:8]))
    witness={}
    for number in range(len(derivations)-1,-1,-1):
        weight=weights.get(number,0)
        if not weight:continue
        rid,inverse,deps=derivations[number];factor=weight*inverse%prime
        witness[rid]=(witness.get(rid,0)+factor)%prime
        for earlier,scale in deps:weights[earlier]=(weights.get(earlier,0)-factor*scale)%prime
    result=dict(mode=mode,sample=sample,prime=prime,point=point,target=list(TARGET),
                seed_count=len(seed_list),raw_operator_rows=len(seed_list)*18,nonzero_equations=len(equations),
                variables=len(columns),pivots=len(pivots),global_free_columns=len(columns)-len(pivots),
                master_convention=[list(a) for a in sorted(masters)],
                coefficients=[[list(columns[k]),v] for k,v in sorted(residual.items())],
                witness=[[rid,value] for rid,value in sorted(witness.items()) if value],
                generation_seconds=generated-start,solve_and_witness_seconds=time.perf_counter()-generated,
                source_template_sha256=sha(HERE/'fixtures/IBP_LI'),master_fixture_sha256=sha(HERE/'fixtures/masters'),
                scope='One target at one finite-field point; not an algebraic or performance claim.')
    return result


def raw_templates():
    rows=[]
    for block in re.split(r'\n\s*\n',(HERE/'fixtures/IBP_LI').read_text().strip()):
        row=[]
        for line in block.splitlines():
            m=re.fullmatch(r'doublePentagon\[(-?\d+(?:,-?\d+)*)\]\*\((.+)\)',line.strip())
            if not m:raise ValueError('malformed original template')
            row.append((tuple(map(int,m.group(1).split(','))),ast.parse(m.group(2).replace('^','**'),mode='eval').body))
        rows.append(row)
    if len(rows)!=18:raise ValueError('template count drift')
    return rows


def evaluate(node,values,p):
    if isinstance(node,ast.Constant) and type(node.value) is int:return node.value%p
    if isinstance(node,ast.Name) and node.id in values:return values[node.id]%p
    if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
        return evaluate(node.operand,values,p)*(-1 if isinstance(node.op,ast.USub) else 1)%p
    if isinstance(node,ast.BinOp):
        a=evaluate(node.left,values,p)
        if isinstance(node.op,ast.Pow):
            exponent=node.right
            sign=-1 if isinstance(exponent,ast.UnaryOp) and isinstance(exponent.op,ast.USub) else 1
            if isinstance(exponent,ast.UnaryOp) and isinstance(exponent.op,(ast.USub,ast.UAdd)):exponent=exponent.operand
            if not isinstance(exponent,ast.Constant) or type(exponent.value) is not int or abs(exponent.value)>8:raise ValueError('invalid coefficient exponent')
            return pow(a,sign*exponent.value,p)
        b=evaluate(node.right,values,p)
        if isinstance(node.op,ast.Add):return (a+b)%p
        if isinstance(node.op,ast.Sub):return (a-b)%p
        if isinstance(node.op,ast.Mult):return a*b%p
        if isinstance(node.op,ast.Div):return a*pow(b,-1,p)%p
    raise ValueError('unsupported original coefficient')


def verify(certificate):
    mode,sample=certificate['mode'],certificate['sample']
    if mode not in ('tube','decreasing') or type(sample) is not int or sample not in (0,1):raise ValueError('invalid policy/sample metadata')
    prime,point=SAMPLES[sample]
    if certificate['prime']!=prime or certificate['point']!=point or tuple(certificate['target'])!=TARGET:raise ValueError('sample/target drift')
    if certificate['source_template_sha256']!=sha(HERE/'fixtures/IBP_LI') or certificate['master_fixture_sha256']!=sha(HERE/'fixtures/masters'):raise ValueError('fixture drift')
    seed_list=seeds(mode);trivial,masters=model();templates=raw_templates();total={};seen=set()
    if certificate['seed_count']!=len(seed_list) or certificate['raw_operator_rows']!=18*len(seed_list):raise ValueError('seed/row metadata drift')
    if certificate['master_convention']!=[list(a) for a in sorted(masters)]:raise ValueError('declared master convention drift')
    for rid,weight in certificate['witness']:
        if type(rid) is not int or rid in seen or not 0<=rid<18*len(seed_list) or type(weight) is not int or not 0<weight<prime:raise ValueError('invalid witness entry')
        seen.add(rid);seed=seed_list[rid//18];values={**point,**{f'a{i}':a for i,a in enumerate(seed)}}
        for shift,tree in templates[rid%18]:
            c=evaluate(tree,values,prime)*weight%prime
            a=tuple(x+y for x,y in zip(seed,shift))
            if c and all(a[i]>0 for i in CUT) and sum(1<<i for i,x in enumerate(a) if x>0) not in trivial:
                total[a]=(total.get(a,0)+c)%prime
    expected={TARGET:1};seen=set()
    for a,c in certificate['coefficients']:
        a=tuple(a)
        if len(a)!=11 or any(type(x) is not int for x in a) or a not in masters or a in seen or type(c) is not int or not 0<c<prime:raise ValueError('invalid master coefficient')
        seen.add(a);expected[a]=(expected.get(a,0)-c)%prime
    total={a:c for a,c in total.items() if c};expected={a:c for a,c in expected.items() if c}
    if total!=expected:raise ValueError('original-row witness disagreement')
    return dict(valid=True,mode=mode,sample=sample,seed_count=len(seed_list),masters_used=len(certificate['coefficients']),original_rows_used=len(certificate['witness']))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=('tube','decreasing'));p.add_argument('--sample',type=int,choices=(0,1))
    p.add_argument('--out',type=Path);p.add_argument('--verify',type=Path)
    a=p.parse_args()
    if a.verify:
        print(json.dumps(verify(json.loads(a.verify.read_text()))));return
    if a.mode is None or a.sample is None or a.out is None:p.error('mode, sample and new out are required')
    if a.out.exists():raise ValueError('fresh certificate path required')
    result=reduce(a.mode,a.sample);checked=verify(result)
    with a.out.open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({**checked,'generation_seconds':result['generation_seconds'],'solve_seconds':result['solve_and_witness_seconds']}))


if __name__=='__main__':main()
