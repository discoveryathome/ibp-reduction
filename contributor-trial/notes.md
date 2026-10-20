# Timed contributor-style trial

Start: 2026-10-20 21:11:10 UTC. Same author as the harness; not an independent donor.
The original benchmark continues separately. No overlapping CPU-heavy experiments
will be used as clean runtime comparisons.

## Initial diagnosis

The frozen search winner relies heavily on a generic arithmetic cache. Its pruned
seeds fail on the box, requiring a charged fallback. A public demo showing only the
large win over an uncached starter would exaggerate algorithmic progress.

Hypothesis H1: Online elimination can avoid updating many equations never needed
for the requested reductions. Process each input against known pivots, test whether
the target dependency closure is solvable, then back-substitute just that closure.
This is an established algorithmic idea, not a novel mathematical discovery. Agent
reasoning matters in choosing completeness conditions and finding a useful schedule.

Plan: compare against cached sparse elimination, not only the uncached starter.
Explore schedules on already-exposed development families; freeze the implementation
and schedule before three newly specified mass/kinematic cases. Record failures.
Use exact proof DAGs, the same arithmetic counters, and isolated interleaved timing.

## Pre-evaluation protocol

H1 search is deliberately bounded: four input schedules and two integral priorities,
24 development reductions plus three cached-baseline reductions. Each candidate
uses caching; the comparator receives the same cache. Only the original three
training families select the policy. Existing massless box is an exposed regression.
New cases: one-mass bubble (rmax=5), two-mass triangle (rmax=4), one-mass box (rmax=5).
They were specified before candidate evaluation and have independent checker entries.
No new topology beyond one loop is claimed. Each run has a timeout. Three interleaved
repeats and exact certificates follow selection.

## Accounting review

Found a reporting omission: the original fallback correctly added failed-attempt
arithmetic and time, but its top-level cache-hit count included only the successful
attempt. Corrected the aggregation and tagged it accounting_version=2. Normalize
older saved fallback summaries from their already-recorded failed_attempt metadata;
this changes no arithmetic-operation score or executed reduction. Preserve the
original frozen search log and its hash. This is a concrete contributor-quality
cost-accounting finding independent of H1's performance outcome.

## Stronger rival identified before development runs

H2: Some H1 savings may merely come from the starter generating one redundant
outer layer of seeds. IBPs often raise one propagator power, so seeds with positive
sum <= rmax-1 may already reduce targets through rmax (our targets/bases are unchanged).
Add a cached `tight` baseline, with a charged full-seed fallback if insufficient.
Select H1 against this stronger baseline, then evaluate both. This is a deliberate
attempt to falsify a flattering interpretation of the improvement. The simpler
bound adjustment may be the more useful contributor result if H1 does not beat it.

Cost sensitivity: trial workers separately count executed nontrivial field operations,
excluding additions of zero/opposites, products by 0 or +/-1, and divisions of zero,
by +/-1, or of equal/opposite operands. This diagnostic is not the selection objective;
it tests whether score gains are dominated by identity bookkeeping. The wrapper is
identical for all trial methods and its overhead is present in trial timings.

## First held-out pass (provisional until certificate checks)

The online method reduced field operations on the one-mass bubble and one-mass box,
but was worse than the initial learned policy on the two-mass triangle. A smaller
seed set was not uniformly better: cached tight seeding lost on the exposed box,
and needed a charged fallback on the one-mass box. This rules out claiming a
universal seeding/order improvement. Final report must preserve the triangle loss.
