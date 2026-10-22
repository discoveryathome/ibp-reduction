"""Fail-closed, exact same-target comparison with the saved Kira text export."""
import argparse,ast,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import sympy as S
from ibp.validator import check,decode,exact_zero,D,m
OUT=ROOT/'research/readiness-20261021'
def expression(text):
    def visit(n):
        if isinstance(n,ast.Constant) and type(n.value)==int:return S.Integer(n.value)
        if isinstance(n,ast.Name) and n.id in ('d','m'):return {'d':D,'m':m}[n.id]
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.USub,ast.UAdd)):
            return -visit(n.operand) if isinstance(n.op,ast.USub) else visit(n.operand)
        if isinstance(n,ast.BinOp):
            a,b=visit(n.left),visit(n.right)
            if isinstance(n.op,ast.Add):return a+b
            if isinstance(n.op,ast.Sub):return a-b
            if isinstance(n.op,ast.Mult):return a*b
            if isinstance(n.op,ast.Div):return a/b
            if isinstance(n.op,ast.Pow) and b.is_Integer and abs(b)<=16:return a**b
        raise ValueError('unsupported coefficient expression')
    return visit(ast.parse(text.replace('^','**'),mode='eval').body)
def compare(text,certificate):
    check(certificate)
    expected={tuple(o['target']):{tuple(a):decode(c) for a,c in o['row']} for o in certificate['outputs']}
    actual={}
    for block in text.strip().split('\n\n'):
        row={};target=None
        for line in block.splitlines():
            match=re.fullmatch(r'sunset\[(-?\d+),(-?\d+),(-?\d+)\]\*\((.+)\)',line.strip())
            if not match:raise ValueError('malformed/empty Kira export')
            a=tuple(map(int,match.groups()[:3]));coefficient=expression(match.group(4))
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
    p=argparse.ArgumentParser();p.add_argument('--export',type=Path,default=OUT/'kira/kira_targets.kira');args=p.parse_args()
    text=args.export.read_text();rows=[]
    for method in ('sparse','online'):
        file=OUT/f'two-loop-{method}.json';rows.append(dict(method=method,exact_identities=compare(text,json.loads(file.read_text())),certificate_sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
    print(json.dumps(dict(valid=True,export_sha256=hashlib.sha256(args.export.read_bytes()).hexdigest(),rows=rows,
      scope='Exact rational identities in d and nonzero squared mass m; same nine targets and two masters, not a production speed comparison.'),indent=2))
if __name__=='__main__':main()
