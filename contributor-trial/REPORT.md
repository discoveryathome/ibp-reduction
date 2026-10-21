# Timed contributor trial: featured-pilot assessment

> **Historical (2026-10-20).** Written before the launch: the project has been open to
> donated sessions since 2026-10-21, with a maintainer and GitHub Discussions, so
> "No public repository or hub listing was created" no longer holds. The featured-launch
> gates below are still open. Current status is in `DISCOVERY.md`.

**Recommendation: keep this as a technical pilot; complete mature-solver, multi-loop, and independent-contributor tests before making it a lead feature.** Before making it a headline feature, add a pinned mature-solver baseline, one genuinely multi-loop case, and an independent newcomer/reviewer run. The local experiment provides a credible contribution workflow and a useful demo, but does not yet establish production relevance.

## What was tested

This was a same-author contributor-style trial, not independent onboarding. Its protocol was written before the new experiments. The first part was spent building the candidate, strengthening the rival baseline, and reviewing correctness while the initial benchmark finished. CPU-heavy trial runs followed that benchmark rather than overlapping its timing.

Start: `2026-10-20T21:11:10.890496+00:00`. See `receipt.json` for the actual finish time and elapsed minutes. Development evaluated 8 policies on three previously exposed families, taking 136.3 seconds including subprocess startup and counters. The initial 40-policy search is a separate experiment, not part of this candidate-selection budget.

The agent-designed change processes input equations online against known pivots and stops once every target has a dependency chain to the fixed basis. It still generates the full initial seed set. It only back-substitutes the required closure. A small schedule search selected a target-intersection-first ordering, shortest-row tiebreak, and dot-first integral priority. This is a classical elimination variant implemented for the pilot, not a claim of inventing a new algebraic algorithm.

Two attempts to explain away the gain were included: give the old solver the same arithmetic cache; and tighten its seed bound by one layer, while keeping all targets unchanged. The tighter bound was insufficient on the evaluated triangle and box cases, triggering a full-system retry. Those failed attempts are included in the cost; fewer initial seeds did not mean less total work.

## Complete evaluation

The massless box is an exposed development regression. The other three mass/kinematic settings were specified before evaluation and were not scored during trial policy selection. These remain one-loop problems with nonnegative target indices; they test neither multi-loop transfer, high-rank numerator targets, nor reconstruction costs.

| Case | Method | Field ops | Nontrivial ops | Median seconds [min, max] | Peak MiB | Max coefficient terms | Fallback |
|---|---|---:|---:|---:|---:|---:|---|
| box_massless | cached_sparse | 3,228 | 1,702 | 9.490 [9.350, 23.191] | 66.3 | 18 | False |
| box_massless | cached_tight | 4,149 | 2,187 | 9.799 [9.679, 12.354] | 66.5 | 18 | True |
| box_massless | initial_learned | 4,618 | 2,527 | 11.290 [10.810, 18.825] | 68.0 | 14 | True |
| box_massless | online | 2,201 | 1,353 | 5.869 [5.805, 6.169] | 66.3 | 11 | False |
| bubble_one_mass | cached_sparse | 481 | 283 | 1.896 [1.215, 4.107] | 61.5 | 30 | False |
| bubble_one_mass | cached_tight | 273 | 158 | 0.609 [0.383, 1.166] | 61.3 | 23 | False |
| bubble_one_mass | initial_learned | 340 | 208 | 0.763 [0.666, 4.330] | 61.2 | 23 | False |
| bubble_one_mass | online | 113 | 73 | 0.526 [0.271, 1.104] | 60.8 | 23 | False |
| triangle_two_mass | cached_sparse | 862 | 484 | 0.951 [0.892, 2.311] | 61.9 | 12 | False |
| triangle_two_mass | cached_tight | 1,108 | 623 | 2.182 [0.978, 3.157] | 62.2 | 12 | True |
| triangle_two_mass | initial_learned | 203 | 117 | 0.877 [0.359, 1.251] | 61.0 | 12 | False |
| triangle_two_mass | online | 361 | 220 | 0.708 [0.460, 1.060] | 61.0 | 12 | False |
| box_one_mass | cached_sparse | 14,878 | 8,810 | 34.992 [20.535, 39.988] | 80.1 | 46 | False |
| box_one_mass | cached_tight | 18,789 | 11,212 | 55.512 [40.407, 74.286] | 80.5 | 46 | True |
| box_one_mass | initial_learned | 15,403 | 9,435 | 31.764 [20.228, 41.986] | 80.2 | 41 | True |
| box_one_mass | online | 7,731 | 5,304 | 12.432 [10.269, 18.761] | 76.3 | 27 | False |

Nontrivial operations exclude zero/unit/sign/cancellation identities as defined in `notes.md`. This is a sensitivity check, not the selection score. Trial timings include the same extra profiling wrapper for every method; they should not be directly compared with initial-stage timings. Peak RSS includes Python/SymPy imports. Arithmetic counts are deterministic; noisy wall times are measurements.

## Transfer and the strongest rival

| New family | Online ops | Best existing strategy on that case | Its ops | Online change |
|---|---:|---|---:|---:|
| bubble_one_mass | 113 | cached_tight | 273 | -58.6% |
| triangle_two_mass | 361 | initial_learned | 203 | +77.8% |
| box_one_mass | 7,731 | cached_sparse | 14,878 | -48.0% |

Online wins on 2/3 new cases by operation count. Its geometric-mean ratio to the **per-case best** existing strategy is 0.7259. This comparator is an oracle summary, not a deployable single baseline. All cases, including regressions, remain in the table.

## Can early contributors hill-climb?

**Yes, within this prototype.** Changing the processing schedule moved the training score from essentially no improvement to a substantial decrease. The structural candidate is an understandable code contribution with exact certificates. The cost-accounting review also found and fixed a missing aggregation of failed-attempt cache hits; primary operation scores were unaffected.

**The available scientific headroom is still unknown.** Caching and sensible seeding are established ideas, and the starting solver is new and deliberately small. A large percentage against it does not imply a large percentage against Kira 3 or FIRE 7. Tightening a bound was not uniformly beneficial; the richer algorithm was not uniformly best. That is a real research landscape, but its current hills may be mostly implementation maturity.

## Suitability against the requested criteria

| Criterion | Assessment |
|---|---|
| Tangible early progress | Demonstrated local improvements and a concrete accounting fix, with exact checks; a newcomer has not yet been tested. |
| Hill climbing | Several meaningful choices change cost, including negative outcomes; retain a ladder of harder, fresh cases to avoid exhausting easy wins. |
| Public appeal | Strong scientific connection: make the mathematics behind particle-physics predictions cheaper while keeping the answer exact. The reduction itself is abstract; use a fixed-task before/after demo and a visible rejecting checker. |
| Home hardware | Apple M2, 24 GiB installed RAM, CPU only; measured process memory is in the table. This does not need a high-end GPU. Full orchestration includes significant Python startup overhead. |
| Agent intelligence | Designing the dependency-completeness check, challenging an easy baseline, and interpreting a regression required reasoning. This single run does not causally prove superiority over random search or expert human tuning. |
| Meaningful results | Useful reproducible solver engineering and generalization evidence. New domain-level algorithms, multi-loop gains, and wins against mature solvers remain unestablished. |
| Featured launch readiness | Conditional. Good technical pilot or secondary feature now; mature baseline, multi-loop bridge, independent review, and a ready challenge ladder are the gates for leading with it. |

## Exact verification

Separate checker results: 16/16 passed. All methods in the trial receive exact row-DAG checks on every evaluation family. Corrupt-candidate tests and analytic Gamma-function controls are included in the full test suite. The checker is separately implemented but shares SymPy and the stated dimensional-regularization assumptions; it is not a formal proof kernel or an independently authored audit.

```sh
python -m ibp.trial explore --out scratch/contributor-replay
python -m ibp.trial evaluate --out scratch/contributor-replay
python tools/check_trial.py
```

Rerunning the search after seeing these examples does not create new held-out evidence. `frozen.json` hashes the candidate implementation and exploration log; `evaluation-lock.json` binds the tested policy. `next-stage.md` lists launch gates and `public-story.md` gives a claim-safe demo script. No public repository or hub listing was created.
