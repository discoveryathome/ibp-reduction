# Formulation ibp-one-loop-v1

The question is whether a fixed, family-independent policy reduces the cost of exact
IBP reduction across CPU-scale integral families. Primary progress is fewer executed
rational-function arithmetic operations on the held-out set. Secondary measures are
intermediate expression growth, live sparse entries, process memory, and elapsed/CPU
time. Correctness and complete reduction of the frozen targets are prerequisites.

## Integrals and axioms

Use Euclidean conventions, continued analytically where on-shell external invariants
cannot be realized by real Euclidean vectors:

I(a) = integral d^d k / product_i D_i^a_i,
D_i = (k+r_i)^2 + m_i, S_ij = (r_i-r_j)^2, r_0=0.

Here m_i is a **squared mass**, not a mass. The algebra field is Q(d,s,t,m,u).
Unused variables do not enter an answer. No kinematic point is substituted.
Total derivatives vanish in dimensional regularization by analytic continuation;
scaleless integrals vanish. If all positive-power propagators have zero masses and
all their mutual S_ij vanish, that sector is scaleless even with polynomial
numerators. Empty sectors are scaleless. We do not discard a non-scaleless boundary
integral simply because it lies outside the seed bounds.

For each seed a and j, differentiate with vector k+r_j. This gives

0 = (d-sum_i a_i) I(a) - sum_i a_i I(a+e_i-e_j)
    + sum_i a_i (m_i+m_j+S_ij) I(a+e_i).

The checker derives the coefficients independently from scalar products. Equal-mass
bubble tadpoles are identified by k -> -k-r_1, a change of integration variable.
No other symmetry identification is inserted.

All identities are rational identities on generic kinematics, away from coefficient
poles. At exceptional dimensions, thresholds, or zero Gram/Cayley determinants one
must take appropriate limits or reduce separately. The certificates do not establish
analytic IBP axioms or global minimality of a master basis. They prove that every
listed target reduces exactly to the specified conventional one-loop basis. The
basis choices are explicit and can be audited independently.

## Frozen suite

Targets are all non-scaleless a_i >= 0 with 0 < sum(a_i) <= rmax, including subtopologies.
Rectangular seeds allow a_i >= -1, sum positive powers <= rmax, and total negative
power <= 1. This is a finite CPU benchmark, not a bound on general IBP complexity.
Negative powers occur in generated equations even when the requested targets have
no numerators. Every non-scaleless generated unknown is retained.

| Family | Squared masses | Nonzero S_ij (zero based) | rmax | Masters | Split |
|---|---|---|---:|---|---|
| tadpole | m | none | 4 | (1) | analytic control |
| bubble_massless | 0,0 | S01=s | 4 | (1,1) | train |
| bubble_equal_mass | m,m | S01=s | 3 | (1,0),(1,1) | train |
| triangle_one_mass | 0,0,0 | S02=s | 4 | (1,0,1) | train |
| bubble_unequal_mass | m,u | S01=s | 4 | (1,0),(0,1),(1,1) | held out |
| triangle_offshell | 0,0,0 | S01=s,S12=t,S02=u | 4 | (1,1,0),(1,0,1),(0,1,1),(1,1,1) | held out |
| box_massless | 0,0,0,0 | S02=s,S13=t | 5 | (1,0,1,0),(0,1,0,1),(1,1,1,1) | held out |

The box is the medium pilot case (580 equations with full seeding); these systems
are tiny relative to industrial IBP reductions. The unequal-mass bubble and off-shell
triangle test changed mass/kinematic structure. Only the box has a topology absent
from training. All families are one loop; there is **no demonstrated multi-loop transfer**.

## Baselines and search space

`laporta`: rectangular seeds, descending sector/positive-degree/numerator/lexicographic
integral priority, first available pivot equation. This is a starter implementation
of the published Laporta strategy, not Laporta's software or a production-solver run.
`sparse`: the same, choosing the shortest pivot row.
`golden`: additionally cap seed dots at rmax-number_of_propagators.
`improved`: also require numerator degree <= max(0,sector_size-2), an explicit
l=3 variant of the sector-dependent restriction discussed in arXiv:2502.05121.
The clamped form and its generic safe fallback are pilot choices, not exact Kira 3
configuration semantics. Our bounds concern *all* targets, including lower sectors.

The search varies those three seed modes, four integral orders (sector, total degree,
dots, reversed index tiebreak), three pivot choices (first, shortest, coefficient
term count), and a bounded cache of identical rational operations. After ten initial
or exploratory candidates, selection favors the best eight policies; mutations alter
one or two fields, with 25% fresh exploration. Forty distinct policies are evaluated
with seed 20261020. The objective is the geometric mean of training operation-count
ratios to `sparse`. No family identifier, fitted kinematic point, or held-out score
is available to the policy. This is a small evolutionary search over a hand-written
policy grammar, **not a reproduction of FunSearch or an LLM training run**.

Any pruned seed policy that fails to reduce all targets retries rectangular seeding.
The failed attempt's arithmetic and time are included; memory/expression peaks use
the larger attempt. An insufficient full system fails the run. This fallback was
implemented before held-out evaluation. Finalist training certificates pass exact
validation before `frozen.json` is written. `evaluation-lock.json` binds the evaluation
to its hash. Initial sparse baseline runs were used to debug the entire suite before
search; these are public held-out-for-tuning tests, not a sealed independent study.
Once evaluated, these examples must be treated as development data in the next study.

## Cost model and timing controls

One add, multiply, or divide in Q(d,s,t,m,u) counts as one arithmetic operation.
Subtraction is addition of a signed coefficient; copying, negation, comparisons,
feature scoring, input generation, and certificate serialization are not counted as
field operations. Polynomial gcd, coefficient integer arithmetic, and bit complexity
inside a field operation are **not** counted. Cache hits count as attempted but not
executed field operations. Report both. Consequently fewer operations need not imply
less runtime. The algebra cache holds at most 10,000 results. All implementations
also memoize recursively solved integral rows.

`max_coefficient_terms` is the largest sum of expanded numerator and denominator
monomial counts over inputs and executed arithmetic results; its ratio to the initial
maximum measures coefficient expression growth. Also report maximum polynomial total
degree and rational-coefficient bit length. `peak_live_nnz` is a representation proxy:
it counts live forward rows plus stored pivots, or solved rows plus pivots during
back substitution. It excludes transient local copies, caches, certificate DAGs,
and Python overhead; process peak RSS is the actual observed memory measure.
RSS includes interpreter and imports. It is not a minimum-memory requirement.

Each benchmark run uses a fresh subprocess with PYTHONHASHSEED=0 and a 90-second
limit. Three repeats interleave methods in seeded shuffled order within each family.
`sparse_AA` reruns the identical sparse policy as a timing noise control.
`learned_no_reuse` isolates cache effects. All arithmetic instrumentation remains on
in timed runs. Timings cover generation, reduction, and metric collection; they exclude
imports and certificate checking. Subprocess wall time is recorded separately.
Certificates are produced and checked in separate untimed runs. Report medians and
ranges, not an unsupported precision or significance claim. Processes are sequential;
other machine activity is uncontrolled. Do not benchmark while running other CPU work.
