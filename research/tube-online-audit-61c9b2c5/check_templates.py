"""Derive the published 8 IBP and 1 LI templates as exact polynomials.

Reads the upstream IBP/LI text as mathematical data, using a restricted AST
reader. Does not import or execute any upstream Python, shell or notebook code.
Requires the project's pinned SymPy 1.14.0 (and mpmath 1.3.0).
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

import sympy as sp

HERE = Path(__file__).resolve().parent
A = sp.symbols('a0:7')
D, M2, M3 = sp.symbols('d m2 m3')
SYMBOLS = {str(x): x for x in (*A, D, M2, M3)}
ZERO = (0,) * 7
K1, K2, P1, P3 = [tuple(int(i == j) for i in range(4)) for j in range(4)]
P2 = (0, 0, -1, 1)  # p3 = p1+p2, as in the actual upstream YAML.
MOMENTA = (K1, K2, (1, 1, 0, 0), (1, 0, 1, 0),
           (0, 1, 0, 1), (0, 1, -1, 0), (1, 0, 0, 1))
PROP = sp.symbols('D0:7')
C = (1 + M3 - M2) / 2
GRAM = sp.Matrix([
    [PROP[0], (PROP[2]-PROP[0]-PROP[1])/2, (PROP[3]-PROP[0]-1)/2, (PROP[6]-PROP[0]-M3)/2],
    [(PROP[2]-PROP[0]-PROP[1])/2, PROP[1], (PROP[1]+1-PROP[5])/2, (PROP[4]-PROP[1]-M3)/2],
    [(PROP[3]-PROP[0]-1)/2, (PROP[1]+1-PROP[5])/2, 1, C],
    [(PROP[6]-PROP[0]-M3)/2, (PROP[4]-PROP[1]-M3)/2, C, M3],
])


def polynomial(node):
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return sp.Integer(node.value)
    if isinstance(node, ast.Name) and node.id in SYMBOLS:
        return SYMBOLS[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = polynomial(node.operand)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
        left, right = polynomial(node.left), polynomial(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        return left - right if isinstance(node.op, ast.Sub) else left * right
    if (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow)
            and isinstance(node.right, ast.Constant) and type(node.right.value) is int
            and 0 <= node.right.value <= 2):
        return polynomial(node.left) ** node.right.value
    raise ValueError('Unsupported expression in mathematical template')


def read_templates(path):
    result = []
    for block in path.read_text().strip().split('\n\n'):
        if not block.strip():
            continue
        row = {}
        for line in block.splitlines():
            match = re.fullmatch(r'trianglebox\[([0-9, -]+)\]\*\((.+)\)', line.strip())
            if match is None:
                raise ValueError(f'Unexpected template data: {path.name}')
            shift = tuple(map(int, match[1].split(',')))
            if len(shift) != 7:
                raise ValueError('Wrong shift arity')
            value = polynomial(ast.parse(match[2].replace('^', '**'), mode='eval').body)
            row[shift] = row.get(shift, 0) + value
        result.append(row)
    return result


def dot(left, right):
    return (sp.Matrix([left]) * GRAM * sp.Matrix(right))[0]


def differentiated_row(derivatives, divergence=0):
    row = {ZERO: divergence}
    for j, derivative in enumerate(derivatives):
        poly = sp.Poly(sp.expand(-A[j] * derivative), *PROP)
        for powers, coefficient in poly.terms():
            if sum(powers) > 1:
                raise ValueError('Propagator derivative is not affine')
            shift = [-x for x in powers]
            shift[j] += 1
            key = tuple(shift)
            row[key] = row.get(key, 0) + coefficient
    return row


def derive():
    actions = ((0, K1), (1, K2), (0, P1), (1, P1),
               (1, K1), (0, K2), (0, P2), (1, P2))
    rows = [differentiated_row([2*q[loop]*dot(q, v) for q in MOMENTA], D*v[loop])
            for loop, v in actions]
    # External Lorentz generator contracted with p1 and p3. Upstream's
    # homogeneous LI relation is -2 times this normalization.
    v1, v3 = (0, 0, -C, 1), (0, 0, -M3, C)
    lorentz = differentiated_row([2*q[2]*dot(q, v1) + 2*q[3]*dot(q, v3) for q in MOMENTA])
    return rows + [{key: -2*value for key, value in lorentz.items()}]


def same(left, right):
    return all(sp.Poly(sp.expand(left.get(k, 0)-right.get(k, 0)), *SYMBOLS.values()).is_zero
               for k in left.keys() | right.keys())


def run(source):
    manifest = json.loads((HERE/'sailir-sources.json').read_text())
    paths = ['scripts/data_gen/IBP', 'scripts/data_gen/LI']
    for name in paths:
        if hashlib.sha256((source/name).read_bytes()).hexdigest() != manifest['files'][name]:
            raise ValueError(f'Source fingerprint mismatch: {name}')
    published = read_templates(source/paths[0]) + read_templates(source/paths[1])
    derived = derive()
    if len(published) != 9:
        raise ValueError('Expected eight IBP and one LI templates')
    controls = 0
    counts = []
    for i, (left, right) in enumerate(zip(derived, published)):
        if not same(left, right):
            differences = {str(k): str(sp.expand(left.get(k, 0)-right.get(k, 0)))
                           for k in left.keys() | right.keys()
                           if sp.expand(left.get(k, 0)-right.get(k, 0)) != 0}
            raise ValueError(f'Template {i} disagrees: {differences}')
        altered = dict(right)
        altered[ZERO] = altered.get(ZERO, 0) + 1
        if same(left, altered):
            raise ValueError('Changed coefficient was not rejected')
        controls += 1
        counts.append(sum(sp.expand(v) != 0 for v in right.values()))
    return dict(source_commit=manifest['commit'], sympy=sp.__version__,
                identities_checked=9, template_term_counts=counts,
                coefficient_mutations_rejected=controls,
                domain='Polynomial identity in a0,...,a6,d,m2,m3 over Q, with m1=1',
                kinematics='p3=p1+p2; m2=p2^2, m3=p3^2',
                method='Independent scalar-product differentiation; restricted parsing of upstream formula data',
                limitations=['Checks identity templates, not all solver paths, master minimality or benchmark correctness.',
                             'Dimensional-regularization IBP and Lorentz-invariance assumptions remain trusted.',
                             'Same authoring AI session; SymPy is a shared arithmetic dependency, not a formal proof kernel.'],
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sailir-source', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = json.dumps(run(args.sailir_source), indent=2) + '\n'
    if args.output:
        args.output.write_text(result)
    else:
        print(result, end='')
