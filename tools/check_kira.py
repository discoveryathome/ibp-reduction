"""Fail-closed, exact same-target comparison with the saved Kira text export."""
import argparse,ast,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import sympy as S
from ibp.validator import check,decode,exact_zero,SYMBOLS
OUT=ROOT/'research/readiness-20261021'
SYMBOL_MAP={str(symbol):symbol for symbol in SYMBOLS}
def expression(text):
    def visit(n):
        if isinstance(n,ast.Constant) and type(n.value)==int:return S.Integer(n.value)
        if isinstance(n,ast.Name) and n.id in SYMBOL_MAP:return SYMBOL_MAP[n.id]
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.USub,ast.UAdd)):
            return -visit(n.operand) if isinstance(n.op,ast.USub) else visit(n.operand)
        if isinstance(n,ast.BinOp):
            a,b=visit(n.left),visit(n.right)
            if isinstance(n.op,ast.Add):return a+b
            if isinstance(n.op,ast.Sub):return a-b
            if isinstance(n.op,ast.Mult):return a*b
            if isinstance(n.op,ast.Div):
                if exact_zero(b):raise ValueError('zero denominator')
                return a/b
            if isinstance(n.op,ast.Pow) and b.is_Integer and abs(b)<=16:
                if b<0 and exact_zero(a):raise ValueError('zero denominator')
                return a**b
        raise ValueError('unsupported coefficient expression')
    return visit(ast.parse(text.replace('^','**'),mode='eval').body)
def compare(text,certificate):
    check(certificate)
    name='sunset' if certificate['family']=='sunset_equal_mass_v1' else certificate['family']
    pattern=re.compile(re.escape(name)+r'\[(-?\d+(?:,-?\d+)*)\]\*\((.+)\)')
    expected={tuple(o['target']):{tuple(a):decode(c) for a,c in o['row']} for o in certificate['outputs']}
    actual={}
    for block in text.strip().split('\n\n'):
        row={};target=None
        for line in block.splitlines():
            match=pattern.fullmatch(line.strip())
            if not match:raise ValueError('malformed/empty Kira export')
            a=tuple(map(int,match.group(1).split(',')));coefficient=expression(match.group(2))
            if a in row:raise ValueError('duplicate integral')
            if target is None:
                target=a
                if coefficient!=-1:raise ValueError('unexpected target normalization')
            row[a]=coefficient
        if target in actual:raise ValueError('duplicate target')
        actual[target]=row
    if set(actual)!=set(expected):raise ValueError('incomplete/wrong target set')
    for target,row in expected.items():
        if set(row)!=set(actual[target]):raise ValueError('different master basis')
        for a,c in row.items():
            if not exact_zero(c+actual[target][a]):raise ValueError(('coefficient disagreement',target,a))
    return len(actual)
def main():
    p=argparse.ArgumentParser();p.add_argument('--export',type=Path,default=OUT/'kira/kira_targets.kira')
    p.add_argument('--certificate',type=Path,help='Compare a specific exact certificate; defaults to both saved sunset certificates.')
    args=p.parse_args()
    text=args.export.read_text();rows=[]
    files=[args.certificate] if args.certificate else [OUT/f'two-loop-{method}.json' for method in ('sparse','online')]
    for file in files:
        cert=json.loads(file.read_text())
        row=dict(certificate=str(file.relative_to(ROOT) if file.is_relative_to(ROOT) else file),family=cert['family'],exact_identities=compare(text,cert),certificate_sha256=hashlib.sha256(file.read_bytes()).hexdigest())
        if not args.certificate:row['method']=file.stem.removeprefix('two-loop-')
        rows.append(row)
    print(json.dumps(dict(valid=True,export_sha256=hashlib.sha256(args.export.read_bytes()).hexdigest(),rows=rows,
      scope='Exact rational identities at generic kinematics; full non-master target set and prescribed basis, not a production speed comparison.'),indent=2))
if __name__=='__main__':main()
