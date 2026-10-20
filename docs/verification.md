# Exact checking and worked reductions

Run `python -m ibp.validator results/certificates/bubble_massless-sparse.json`.
The checker accepts JSON polynomial data, never executable expressions. Rational
functions are numerator/denominator lists of `[exponent_vector, numerator, denominator]`
terms in the fixed order d,s,t,m,u. Denominators must be nonzero polynomials.

Each certificate is a directed acyclic graph of input IBPs, a supported change-of-variable
symmetry, row scaling, and row addition. Its output rows assert target + sum c_i master_i=0.
The checker:

1. Uses its own trusted family definitions and enumerates the complete target set.
2. Derives each IBP input via directional derivatives in k^2 and k.r_i, then substitutes
   propagator variables. It independently determines scaleless terms.
3. Replays the DAG with SymPy expressions and exact rational simplification, separate
   from the reducer's fraction-field implementation and Gaussian-elimination choices.
4. Clears denominators and checks the zero polynomial over Q[d,s,t,m,u]. It verifies
   output normalization, only designated masters on the right, every required target,
   and equality of advertised reductions to the proven rows.

No numerical sampling, finite-field rank guess, or comparison of a few evaluations
counts as correctness. Input assumptions are dimensional-regularization IBP, scaleless
zeros, and translation/reflection invariance, stated in `formulation.md`. Shared SymPy
arithmetic and hand-written family specifications remain in the trusted computing
base. This is an independent implementation, not independently authored research or
a formally verified kernel. Master minimality requires a separate mathematical audit.

`python -m unittest discover -s tests -v` includes altered coefficients, missing
targets, invalid references, changed input seeds, fake symmetry, undeclared masters,
and zero-denominator rejection. It cross-checks independently derived inputs and
reproduces the known analytic Gamma-function recurrences below.

## Established reduction reproduced

The massless off-shell bubble has the established expression

I(a,b) = pi^(d/2) s^(d/2-a-b)
 Gamma(a+b-d/2) Gamma(d/2-a) Gamma(d/2-b)
 / [Gamma(a) Gamma(b) Gamma(d-a-b)].

See Bitoun, Bogner, Klausen and Panzer, *Feynman integral relations from parametric
annihilators*, [arXiv:1712.09215](https://arxiv.org/abs/1712.09215), the one-loop
propagator example; conventions are converted to Euclidean s here. Overall measure
normalization cancels in ratios. Gamma(z+1)=z Gamma(z) gives

I(2,1) = -(d-3)/s I(1,1),
I(2,2) = (d-6)(d-3)/s^2 I(1,1).

The test compares **every** bubble target in the suite against the exact rational
Gamma-function ratio, independently of the certificate proof. All six targets through
sum(a)<=4 reach the single master. Costs for the full collection, rather than just
one recurrence, are in `results/summary.json` and `results/REPORT.md`. These are locally
measured implementation costs; no published Kira/FIRE timing has been reproduced.

The massive tadpole is an additional analytic control:

I(a)/I(1) = (1-d/2)_(a-1) / [(a-1)! m^(a-1)],
I(2) = (2-d)/(2m) I(1).

The formula follows by radial integration or Feynman parameters. Both controls
compare rational identities for symbolic d and scale, not Gamma values at sample points.

## Reproduction boundaries

`python -m ibp.experiment reproduce` checks all saved certificates and reruns sparse
and learned reductions to compare exact operation and expression metrics. It does
not claim to reproduce the original machine's seconds or peak RSS. To measure those,
run a fresh search and benchmark in a new output directory. The CLI never treats
metadata's `success` flag as an algebraic proof. Changes to the trusted checker,
family definitions, or frontier require maintainer review and new tamper tests.
