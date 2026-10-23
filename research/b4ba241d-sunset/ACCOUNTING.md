# What the sunset operation count and proof-node table establish

The pinned predecessor README reports proof nodes 43/76/28 for cached sparse,
inherited online and the candidate. Its `search-result.json` actually reports
validated, pruned node counts **43/29/28**. The archived readiness online witness
has 76 unpruned nodes. The fresh replay confirms the distinction:

| policy | before pruning | after the existing `validator.prune` |
| --- | ---: | ---: |
| cached sparse | 207 | 43 |
| inherited online | 76 | 29 |
| candidate online | 68 | 28 |

The initial unpruned replay and final pruned replay are both archived. The
candidate's final DAG/output digest equals the pinned `best.json` digest;
all nine outputs replay exactly before and after pruning. The predecessor's
README table therefore mixes two counting conventions. This is a documentation
correction, not a counterexample to the candidate identities or the operation
totals. No historical package or accepted record is rewritten here. Predecessor
README and search-result hashes are pinned in `SOURCES.json`.

For each policy, the saved trace separately verifies every reported rational
`add`, `mul` or `div` result, including cached results. Ordered operand keys are
reconstructed from their canonical encoded field values; the replay does not
inspect the producer cache. None of these traces reaches its capacity of
10,000 entries. The independent totals are:

| policy | executed add | executed mul | executed div | total | attempts | hits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cached sparse | 157 | 214 | 54 | 425 | 657 | 232 |
| inherited online | 45 | 68 | 26 | 139 | 185 | 46 |
| candidate online | 35 | 49 | 23 | 107 | 162 | 55 |

Thus the reduction from 139 to 107 is 32 fewer counted cache misses under the
existing model. This audit does not turn that number into runtime improvement.
The model omits equation generation, sorting/priority work, hashing and cache
lookup, row bookkeeping, coefficient negations outside `Arithmetic.op`, work
inside rational-polynomial arithmetic, coefficient observation, proof generation,
pruning and certificate verification. Cache hits are free only in this operation
metric, not on a CPU. The tracing wrapper adds runtime overhead, so this replay's
producer times must not be compared to uninstrumented native timings. The
predecessor's separate trivial/nontrivial-operation classification and repeated
wall-time benchmark were not reproduced here.

The exact checker and native comparison support the stated identities under
the fixed dimensional-regularization IBP, scaleless-factor and permutation
conventions. They do not independently prove those physical axioms, global
master minimality, general two-loop transfer, or adequacy of the cost model for
production solvers. The original handoff's separate scientific review remains
open. All evidence in this package is author-checked.
