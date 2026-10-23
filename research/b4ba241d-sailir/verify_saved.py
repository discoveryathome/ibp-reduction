"""Replay18 native images and the fixed SAILIR episode over F_1009."""
import argparse
import ast
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
TARGET=(1,2,1,1,1,1,-3)
PRIME=1009
NAME=r'trianglebox\[(-?\d+(?:,-?\d+){6})\]'


def rational(text):
    def visit(node):
        if isinstance(node,ast.Constant) and type(node.value) is int:return Fraction(node.value)
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            return visit(node.operand)*(-1 if isinstance(node.op,ast.USub) else 1)
        if isinstance(node,ast.BinOp):
            a,b=visit(node.left),visit(node.right)
            if isinstance(node.op,ast.Add):return a+b
            if isinstance(node.op,ast.Sub):return a-b
            if isinstance(node.op,ast.Mult):return a*b
            if isinstance(node.op,ast.Div):return a/b
            if isinstance(node.op,ast.Pow) and b.denominator==1 and abs(b)<=16:return a**b.numerator
        raise ValueError('unsupported native coefficient')
    return visit(ast.parse(text.replace('^','**'),mode='eval').body)


def field(value):
    if value.denominator%PRIME==0:raise ValueError('native denominator pole modulo1009')
    return value.numerator*pow(value.denominator,-1,PRIME)%PRIME


def integral_set(path):
    result=set()
    for line in path.read_text().splitlines():
        match=re.fullmatch(NAME+r'(?:\s*#\s*\d+)?',line.strip())
        if not match:raise ValueError('malformed integral list')
        a=tuple(map(int,match.group(1).split(',')))
        if a in result:raise ValueError('duplicate integral list entry')
        result.add(a)
    if not result:raise ValueError('empty integral list')
    return result


def parse(text,masters):
    if not text.strip():raise ValueError('empty native export')
    images={}
    for block in re.split(r'\n\s*\n',text.strip()):
        terms=[]
        for line in block.splitlines():
            match=re.fullmatch(NAME+r'\*\((.+)\)',line.strip())
            if not match:raise ValueError('malformed native export')
            terms.append((tuple(map(int,match.group(1).split(','))),rational(match.group(2))))
        target,normalization=terms[0]
        if target in images:raise ValueError('duplicate native target')
        if len(terms)==1 and target in masters and normalization==1:
            images[target]={target:Fraction(1)};continue
        if normalization!=-1:raise ValueError('native target normalization')
        image={};seen={target}
        for a,c in terms[1:]:
            if a in seen:raise ValueError('duplicate integral in native row')
            if a not in masters:raise ValueError('unreduced native integral')
            seen.add(a)
            if c:image[a]=c
        images[target]=image
    return images


def compare(images,masters,episode):
    if episode['prime']!=PRIME or episode['kinematics']!=dict(d=41,m1=1,m2=31,m3=47) or episode['initial']!=[[list(TARGET),1]]:
        raise ValueError('episode point/target drift')
    residual=episode['final'];required={TARGET}|{tuple(a) for a,c in residual}
    if len(residual)!=17 or len(required)!=18 or any(len(a)!=7 or any(type(v) is not int for v in a) or type(c) is not int or not 0<c<PRIME for a,c in residual):
        raise ValueError('invalid17-term episode')
    if set(images)-required:raise ValueError('unexpected native target')
    complete=copy.deepcopy(images)
    for target in required:
        if target not in complete:
            if target not in masters:raise ValueError('missing requested native image')
            complete[target]={target:Fraction(1)}
        if set(complete[target])-masters:raise ValueError('undeclared native master')
        if target in masters and complete[target]!={target:Fraction(1)}:
            raise ValueError('nonidentity image for actual native master')
    difference={}
    for target,coefficient in [(TARGET,1)]+[(tuple(a),-c) for a,c in residual]:
        for master,value in complete[target].items():
            difference[master]=(difference.get(master,0)+coefficient*field(value))%PRIME
    difference={a:c for a,c in difference.items() if c}
    if difference:raise ValueError('native episode identity disagreement: '+str(difference))
    return complete


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native',type=Path,default=HERE/'native')
    p.add_argument('--episode',type=Path,default=HERE/'data/worked-episode.json')
    p.add_argument('--out',type=Path)
    a=p.parse_args()
    if a.out and a.out.exists():raise ValueError('fresh result path required')
    receipt=json.loads((a.native/'receipt.json').read_text())
    if receipt['returncode']!=0 or not receipt['binary_unchanged'] or receipt['kira_sha256']!='9d49f623f144ee90c3eb2f50290b180b93c5c85e9ca1272092cecb065eb47066' or receipt['point']!=dict(d=41,m1=1,m2=31,m3=47) or receipt['comparison_prime']!=PRIME:
        raise ValueError('native execution binding disagreement')
    sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    if sha(a.episode)!=receipt['episode_sha256']:raise ValueError('episode fingerprint drift')
    for name,expected in receipt['input_sha256'].items():
        if sha(a.native/name)!=expected:raise ValueError('native input fingerprint drift')
    directory=a.native/'results/trianglebox';masters=integral_set(directory/'masters')
    if masters!=integral_set(directory/'masters.final'):raise ValueError('native master files disagree')
    episode=json.loads(a.episode.read_text());requests={TARGET}|{tuple(x) for x,c in episode['final']}
    if integral_set(a.native/'targets')!=requests:raise ValueError('requested native targets disagree')
    preferred=integral_set(a.native/'masters')
    if len(preferred)!=16:raise ValueError('preferred paper master count drift')
    text=(directory/'kira_targets.kira').read_text();images=parse(text,masters)
    complete=compare(images,masters,episode);rejected=[]
    def reject(label,call):
        try:call()
        except (ValueError,ZeroDivisionError):rejected.append(label)
        else:raise AssertionError('false control accepted: '+label)
    reject('empty-export',lambda:parse('',masters))
    reject('duplicate-target',lambda:parse(text.strip()+'\n\n'+re.split(r'\n\s*\n',text.strip())[0],masters))
    reject('target-normalization',lambda:parse(text.replace('*(-1)','*(-2)',1),masters))
    reject('executable-coefficient',lambda:parse(text.replace('*(', '*(f(1)+',1),masters))
    missing=next(x for x in requests if x not in masters);incomplete=dict(images);incomplete.pop(missing)
    reject('missing-image',lambda:compare(incomplete,masters,episode))
    master=next(iter(masters));changed=copy.deepcopy(complete)
    changed[TARGET][master]=changed[TARGET].get(master,Fraction(0))+1
    reject('changed-target-image',lambda:compare(changed,masters,episode))
    residual=tuple(episode['final'][0][0]);changed=copy.deepcopy(complete)
    changed[residual][master]=changed[residual].get(master,Fraction(0))+1
    reject('changed-residual-image',lambda:compare(changed,masters,episode))
    pole=Fraction(1,PRIME);reject('modular-denominator-pole',lambda:field(pole))
    changed_episode=copy.deepcopy(episode);changed_episode['prime']=1013
    reject('changed-prime',lambda:compare(images,masters,changed_episode))
    used=set().union(*(set(image) for image in complete.values()));used_master=next(iter(used))
    reject('undeclared-master',lambda:compare(images,masters-{used_master},episode))
    encoded=[[list(target),[[list(m),str(c),field(c)] for m,c in sorted(image.items())],
              'explicit' if target in images else 'native-master-identity'] for target,image in sorted(complete.items())]
    result=dict(valid=True,prime=PRIME,point=receipt['point'],requested_images=18,explicit_images=len(images),
                actual_master_count=len(masters),actual_masters=[list(x) for x in sorted(masters)],
                preferred_paper_basis_equal=masters==preferred,
                native_only_masters=[list(x) for x in sorted(masters-preferred)],
                paper_only_masters=[list(x) for x in sorted(preferred-masters)],
                images=encoded,rejected_controls=rejected,
                scope='One native rational specialization checks one17-term episode identity modulo1009;no learned-policy,generic reconstruction or benchmark claim.')
    if a.out:a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('images','actual_masters','native_only_masters','paper_only_masters')},indent=2))


if __name__=='__main__':main()
