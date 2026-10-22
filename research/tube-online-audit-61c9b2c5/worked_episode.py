"""Re-derive SAILIR Appendix D's three IBPs; replay over F_1009.

Source: David Shih, arXiv:2604.05034v1, Sections IV.1 and Appendix D.
This is an independently written calculation, not a separate-person review.
No upstream module, learned checkpoint, pickle or solver is loaded.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

PRIME = 1009
DIMENSION, M1, M2, M3 = 41, 1, 31, 47
# Momentum basis k1, k2, p1, p3, with p3 = p1+p2, as in the YAML.
K1, K2, P1, P3 = [tuple(int(i == j) for i in range(4)) for j in range(4)]
PROPAGATORS = (K1, K2, (1, 1, 0, 0), (1, 0, 1, 0),
               (0, 1, 0, 1), (0, 1, -1, 0), (1, 0, 0, 1))
START = (1, 2, 1, 1, 1, 1, -3)
SEED = (1, 1, 1, 1, 1, 1, -3)
TARGETS = (START, (1, 1, 1, 1, 1, 2, -3), (1, 1, 1, 1, 2, 1, -3))
ACTIONS = ((1, P1, SEED), (1, K2, SEED),
           (1, K1, (1, 1, 1, 1, 1, 1, -2)))


def affine(terms=None, constant=0):
    """Coefficients of D0,...,D6,1 in an exact rational affine form."""
    values = [Q(0)] * 7 + [Q(constant)]
    for i, value in (terms or {}).items():
        values[i] = Q(value)
    return tuple(values)


def dot(left, right):
    # Invert the seven propagator definitions; no published IBP template is used.
    gram = {
        (0, 0): affine({0: 1}), (1, 1): affine({1: 1}),
        (0, 1): affine({2: Q(1, 2), 0: Q(-1, 2), 1: Q(-1, 2)}),
        (0, 2): affine({3: Q(1, 2), 0: Q(-1, 2)}, Q(-M1, 2)),
        (1, 2): affine({1: Q(1, 2), 5: Q(-1, 2)}, Q(M1, 2)),
        (0, 3): affine({6: Q(1, 2), 0: Q(-1, 2)}, Q(-M3, 2)),
        (1, 3): affine({4: Q(1, 2), 1: Q(-1, 2)}, Q(-M3, 2)),
        (2, 2): affine(constant=M1), (3, 3): affine(constant=M3),
        (2, 3): affine(constant=Q(M1 + M3 - M2, 2)),
    }
    return tuple(sum(left[i] * right[j] * gram[tuple(sorted((i, j)))][k]
                     for i in range(4) for j in range(4)) for k in range(8))


def residue(value):
    value = Q(value)
    return value.numerator * pow(value.denominator, -1, PRIME) % PRIME


def derive_ibp(loop, direction, seed):
    """Integral of div_k(direction / product D_j**a_j) is zero."""
    rational = {seed: Q(DIMENSION * direction[loop])}
    for j, momentum in enumerate(PROPAGATORS):
        derivative = dot(momentum, direction)
        for k, coefficient in enumerate(derivative):
            factor = -seed[j] * 2 * momentum[loop] * coefficient
            if not factor:
                continue
            index = list(seed)
            index[j] += 1
            if k < 7:
                index[k] -= 1
            key = tuple(index)
            rational[key] = rational.get(key, Q(0)) + factor
    return {k: residue(v) for k, v in rational.items() if residue(v)}


def add_scaled(left, right, factor):
    out = dict(left)
    for key, value in right.items():
        out[key] = (out.get(key, 0) + factor * value) % PRIME
        if not out[key]:
            del out[key]
    return out


def scale(row, factor):
    return add_scaled({}, row, factor)


def top(row):
    return {k: v for k, v in row.items() if all(a > 0 for a in k[:6])}


def weight(index):
    return sum(max(a, 0) for a in index), sum(max(-a, 0) for a in index)


def encode(row):
    return [[list(k), v] for k, v in sorted(row.items())]


def run():
    raw = [derive_ibp(*action) for action in ACTIONS]
    expression, pivots, cumulative, records = {START: 1}, [], {}, []
    expected = (
        {(1, 1, 1, 1, 2, 1, -3): 991, (1, 1, 1, 1, 1, 2, -3): 1},
        {(1, 1, 1, 1, 2, 1, -3): 944, SEED: 973},
        {(1, 1, 1, 1, 2, 1, -2): 981, (1, 1, 1, 1, 1, 2, -2): 65, SEED: 973},
    )
    for i, (input_row, target) in enumerate(zip(raw, TARGETS)):
        row, provenance = dict(input_row), {i: 1}
        for old_target, old_row, old_provenance in pivots:
            factor = -row.get(old_target, 0)
            row = add_scaled(row, old_row, factor)
            provenance = add_scaled(provenance, old_provenance, factor)
        inverse = pow(row[target], -1, PRIME)
        row, provenance = scale(row, inverse), scale(provenance, inverse)
        coefficient = expression[target]
        expression = add_scaled(expression, row, -coefficient)
        cumulative = add_scaled(cumulative, provenance, coefficient)
        pivots.append((target, row, provenance))
        if top(expression) != expected[i] or len(expression) != (10, 6, 17)[i]:
            raise ValueError(f'Published Appendix D disagrees after step {i}')
        records.append(dict(step=i, input=encode(input_row), pivot=list(target),
                            normalized_row=encode(row), expression=encode(expression),
                            term_count=len(expression), top_weight=max(map(weight, top(expression)))))
    identity = add_scaled({START: 1}, expression, -1)
    replay = {}
    for i, coefficient in cumulative.items():
        replay = add_scaled(replay, raw[i], coefficient)
    if identity != replay:
        raise ValueError('Final identity does not equal its raw-IBP linear combination')
    rejected = 0
    for key in expression:
        changed = add_scaled(expression, {key: 1}, 1)
        if add_scaled({START: 1}, changed, -1) == replay:
            raise ValueError('A changed final coefficient passed the certificate')
        rejected += 1
    # The three pivots are essential; omission must change the proved identity.
    for omitted in cumulative:
        altered = add_scaled(replay, raw[omitted], -cumulative[omitted])
        if altered == identity:
            raise ValueError('An omitted IBP contribution passed')
    return dict(
        source='https://arxiv.org/html/2604.05034v1#A4',
        evidence_level='author-checked independent derivation; not independent-person acceptance',
        prime=PRIME, kinematics=dict(d=DIMENSION, m1=M1, m2=M2, m3=M3),
        initial=encode({START: 1}), steps=records, final=encode(expression),
        raw_ibp_combination=[[i, v] for i, v in sorted(cumulative.items())],
        final_top_weight=list(max(map(weight, top(expression)))),
        coefficient_mutations_rejected=rejected, omitted_inputs_rejected=len(cumulative),
        limitations=['Fixed finite-field point; not a rational-function identity certificate.',
                     'IBP and dimensional-regularization assumptions remain trusted.',
                     'A weight-lowering episode; the 17 residual integrals need further reduction.',
                     'No learned policy, checkpoint, upstream code or timing benchmark was executed.'],
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run()
    encoded = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end='')
