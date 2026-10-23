"""Derive the double-pentagon's 12 IBP/6 LI templates from momentum geometry.

Source data: Berman et al., tube_seeding ec955d46f26ef497ca5ee7053f6f0286efb7971b.
No upstream code is imported/executed. Equality is symbolic, not sampled.
"""

import argparse
import ast
import hashlib
from itertools import combinations
import json
from pathlib import Path
import re
import sympy as S

HERE = Path(__file__).resolve().parent
A = S.symbols('a0:11')
D = S.Symbol('d')
M = S.symbols('m1:5')
SYMBOLS = (D,) + M + A
ZERO = (0,) * 11
VECTORS = ((1,0,0,0,0,0), (1,0,1,0,0,0), (1,0,1,1,0,0),
           (0,1,0,0,0,0), (0,1,0,0,1,0), (1,1,1,1,1,0),
           (1,1,0,0,0,-1), (1,1,0,0,0,0), (0,1,1,0,0,0),
           (0,1,0,1,0,0), (0,1,0,0,0,1))


def expression(text):
    names = {str(x): x for x in SYMBOLS}
    def visit(n):
        if isinstance(n, ast.Constant) and type(n.value) is int:
            return S.Integer(n.value)
        if isinstance(n, ast.Name) and n.id in names:
            return names[n.id]
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)):
            return visit(n.operand) * (-1 if isinstance(n.op, ast.USub) else 1)
        if isinstance(n, ast.BinOp):
            left, right = visit(n.left), visit(n.right)
            if isinstance(n.op, ast.Add): return left + right
            if isinstance(n.op, ast.Sub): return left - right
            if isinstance(n.op, ast.Mult): return left * right
            if isinstance(n.op, ast.Div) and right != 0: return left / right
            if isinstance(n.op, ast.Pow) and right.is_Integer and abs(right) <= 8: return left**right
        raise ValueError('unsupported coefficient syntax')
    return S.expand(visit(ast.parse(text.replace('^', '**'), mode='eval').body))


def source_templates():
    rows = []
    text = (HERE / 'fixtures/IBP_LI').read_text()
    for block in re.split(r'\n\s*\n', text.strip()):
        row = {}
        for line in block.splitlines():
            match = re.fullmatch(r'doublePentagon\[(-?\d+(?:,-?\d+)*)\]\*\((.+)\)', line.strip())
            if not match: raise ValueError('malformed source template')
            shift = tuple(map(int, match.group(1).split(',')))
            if len(shift) != 11: raise ValueError('wrong source shift dimension')
            row[shift] = S.expand(row.get(shift, 0) + expression(match.group(2)))
        rows.append({k: v for k, v in row.items() if v != 0})
    if len(rows) != 18: raise ValueError('expected exactly 18 source templates')
    return rows


def external_gram():
    m1, m2, m3, m4 = M
    g = S.zeros(4)
    values = {(0,1): S.Rational(1,2), (0,2): (m3-1-m1)/2,
              (0,3): (m1-m3-m4)/2, (1,2): m1/2,
              (1,3): (m4-m1-m2)/2, (2,3): m2/2}
    for (i,j), value in values.items(): g[i,j] = g[j,i] = value
    if S.expand(sum(g)) != 0: raise ValueError('p5 masslessness failed')
    return g


def derived_templates():
    x = S.symbols('x0:11')
    z = S.symbols('z0:11')
    g = S.zeros(6)
    g[0,0], g[1,1], g[0,1], g[1,0] = x[0], x[1], x[2], x[2]
    for i in range(4):
        g[0,2+i] = g[2+i,0] = x[3+i]
        g[1,2+i] = g[2+i,1] = x[7+i]
    ext = external_gram()
    g[2:6,2:6] = ext
    vectors = [S.Matrix(v) for v in VECTORS]
    denominators = S.Matrix([S.expand((v.T*g*v)[0]) for v in vectors])
    linear = denominators.jacobian(x)
    constant = denominators.xreplace(dict.fromkeys(x, S.Integer(0)))
    solved = linear.inv() * (S.Matrix(z) - constant)
    substitution = dict(zip(x, solved))
    operators = []
    for loop in range(2):
        for q in range(6):
            delta = [S.expand(2*v[loop]*(v.T*g[:,q])[0]).xreplace(substitution) for v in vectors]
            operators.append((f'IBP_l{loop+1}_q{q}', D if q == loop else S.Integer(0), delta))
    for i,j in combinations(range(4),2):
        delta = []
        for v in vectors:
            change = S.zeros(6,1)
            for k in range(4):
                change[2+j] += v[2+k]*ext[i,k]
                change[2+i] -= v[2+k]*ext[j,k]
            delta.append(S.expand(2*(v.T*g*change)[0]).xreplace(substitution))
        operators.append((f'LI_p{i+1}_p{j+1}', S.Integer(0), delta))
    rows = []
    for label, divergence, delta in operators:
        row = {ZERO: divergence}
        for j, value in enumerate(delta):
            polynomial = S.Poly(S.expand(value), *z)
            for powers, coefficient in polynomial.terms():
                if sum(powers) > 1: raise ValueError('nonlinear denominator derivative')
                shift = [-p for p in powers]; shift[j] += 1; shift = tuple(shift)
                row[shift] = row.get(shift, 0) - A[j]*coefficient
        rows.append((label, {k:S.expand(v) for k,v in row.items() if S.expand(v) != 0}))
    return rows, str(S.factor(linear.det()))


def match_templates(source, derived):
    if len(source) != 18 or len(derived) != 18: raise ValueError('missing operator')
    unused = set(range(18)); matches = []
    for number, row in enumerate(source):
        found = None
        for index in sorted(unused):
            label, expected = derived[index]
            if set(row) != set(expected): continue
            key = min(row)
            factor = S.cancel(row[key] / expected[key])
            if factor == 0 or not factor.is_Rational: continue
            if all(S.Poly(S.expand(row[k] - factor*expected[k]), *SYMBOLS).is_zero for k in row):
                found = index, label, str(factor); break
        if found is None: raise ValueError(f'unmatched source template {number}')
        unused.remove(found[0]); matches.append(dict(source_index=number, operator=found[1], normalization=found[2]))
    return matches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source = source_templates(); derived, determinant = derived_templates()
    matches = match_templates(source, derived)
    rejected = []
    for index, row in enumerate(source):
        mutant = [dict(r) for r in source]; key = min(row); mutant[index][key] += 1
        try: match_templates(mutant, derived)
        except ValueError: rejected.append(index)
        else: raise AssertionError('coefficient mutation accepted')
    for mutant in (source[:-1], [source[0], source[0], *source[2:]]):
        try: match_templates(mutant, derived)
        except ValueError: pass
        else: raise AssertionError('missing/duplicate operator accepted')
    result = dict(valid=True, evidence_level='author-checked', exact_templates=18,
                  denominator_map_determinant=determinant, matches=matches,
                  coefficient_mutations_rejected=rejected, omission_duplicate_controls=2,
                  source_sha256=hashlib.sha256((HERE/'fixtures/IBP_LI').read_bytes()).hexdigest(),
                  scope='Symbolic operator verification, not integral reduction or performance.')
    with args.out.open('x') as out: out.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
