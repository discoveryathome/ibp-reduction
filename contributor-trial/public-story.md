# A public story that stays within the evidence

**Can an AI find a shorter calculation without changing the answer?**

Quantum-field-theory predictions involve large families of related integrals.
Integration-by-parts identities let physicists express them using a smaller set
of master integrals. Finding and applying those identities can itself be expensive.
A contributor proposes a better way to choose or process equations. The benchmark
measures the work; a separate exact algebraic checker checks the answer.

The demo should show one fixed family, its target count and master-basis count,
and the work/time of each strategy. Keep every target and the basis unchanged.
Show a real certificate passing, and show a deliberately corrupted identity failing.
Then switch to an unseen family and show whether the saving transfers—including
regressions. This is more persuasive than a training-only best-score curve.

Use measured arithmetic-operation counts with the label “this prototype,” alongside
runtime and expression size. Do not equate an operation-count percentage with an
LHC calculation speedup. Do not imply that fewer master integrals were discovered:
our basis is fixed. The arithmetic search is useful solver research; it has not
measured a physical quantity or discovered a new particle.

The first featured challenge should offer a ladder: verified beginner controls,
medium systems with several credible baselines, then production-solver/multi-loop
cases. A contribution can be an improvement, an exact counterexample to a heuristic,
or a checker fix. The public score should advance only after a new-family test and
independent review, and should retain negative results.
