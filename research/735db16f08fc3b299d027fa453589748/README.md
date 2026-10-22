# Requested-target coverage for tube-seeding claims

Outcome: **bounded workload audit and tooling**, author-checked. The current local
targets do not provide an increasing-numerator-rank workload: all 236 targets in
the ten one-loop families have `s=0`; the separately fixed sunset has eight `s=0`
targets and three `s=1` targets. No current target has `s>=2`.

Here `s(a)=sum(max(-a_i,0))`, matching the paper's integral-index rank, and
`dots(a)=sum(max(a_i-1,0))`. These are distinct from tensor momentum degree and from
the degree of a coefficient polynomial. The letters `s`, `d`, and `t` also occur
as symbolic field variables in this project; those symbols have different meanings.

Seed `735db16f08fc3b299d027fa453589748` drew `literature/tube-and-online-audit` at
base `9427e928040cd7d71513a443da4a42811720e537`, priority revision 2. The first-step
`python tools/inspect_task.py sources` passed. No matching handoff was open.
The [existing broad paper/public-code claim](https://github.com/discoveryathome/ibp-reduction/discussions/2#discussioncomment-19132014)
was checked for overlap; this contribution instead enumerates the local workload
and provides a coverage check. Its [separate claim](https://github.com/discoveryathome/ibp-reduction/discussions/2#discussioncomment-19132141)
records that refinement. This branch starts from upstream main, independently of PR #7.

## Reproduce the observation

Use the pinned dependencies in a local virtual environment, from the repository root:

```sh
.venv/bin/python tools/audit_target_scope.py
.venv/bin/python tools/audit_target_scope.py --family bubble_equal_mass --require-target-s 0
.venv/bin/python tools/audit_target_scope.py --family bubble_equal_mass --require-target-s 1
.venv/bin/python tools/audit_target_scope.py --family sunset_equal_mass_v1 --require-target-s 1
.venv/bin/python tools/audit_target_scope.py --family sunset_equal_mass_v1 --require-target-s 2
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/check_project.py
```

The five audit commands exit **0, 0, 1, 0, 1**, respectively. Exit 1 means the
selected workload lacks a requested target with that exact `s`; it is not a
reduction failure. Without `--family`, the requirement applies to every selected
family. Passing this coverage condition alone proves neither tube applicability
nor a performance claim.

The deterministic [target-scope.json](target-scope.json) captures all 11 workloads
and six source hashes. It independently compares producer target/master sets with
the checker's separately declared requirements. Profiles count distinct tuples,
not directional equations or executions. Three categories remain separate:

- Requested targets, with masters included and non-master outputs separately.
- Seed indices actually consumed by the rectangular equation generator.
- Unknowns occurring in direct generated IBP rows, before elimination.

For example, the equal-mass bubble requests only `s=0`, has seeds up to `s=1`, and
generated unknowns up to `s=2`. The sunset has 11 targets, nine non-master outputs,
16 distinct seeds, and 64 generated rows (60 nonempty). Its generated unknowns
also reach `s=2`; its requested targets still stop at `s=1`. Direct IBP counts omit
separately inserted symmetry equations: the equal-mass bubble's 30 generated rows
must not be mistaken for the baseline's 31 rows including symmetry.

The audit does not run elimination, validate certificate algebra, measure executed
costs, or compare upstream algorithms. Changing seed bounds or allowing a checker
to read a larger input index does not expand its required output target set.

## What this means for the literature claim

[TUBE_SCOPE.md](TUBE_SCOPE.md) records primary-source definitions and conditions,
pinned to arXiv `2606.10698v1` and author code
`ec955d46f26ef497ca5ee7053f6f0286efb7971b`. The paper's single-target seed-count
formula holds a double-pentagon family, cut, dot budget, and tube width fixed while
increasing one numerator index. Its finite-field results and coefficient
reconstruction scope differ from this project's exact symbolic benchmark.

Our observation is an **eligibility obstruction**, not evidence against tube
seeding. Raising only one-loop `rmax` generates more dotted denominators, not a
numerator-rank sweep. The existing families remain useful for exact correctness
and a separately labelled dotted-bubble analogue. The sunset's negative-index
targets are subsector numerators; they do not supply the published full-sector
three-ISP geometry. No universal runtime or asymptotic claim follows from either
the count audit or the presence of a small number of negative indices.

## Open next question and bounded acceptance test

**Question:** Does a separately implemented fixed-width, on-cut seed enumerator
reproduce the paper's smallest rank-sensitive counts before attempting a solve?
**Why it matters:** it can falsify index, cut, deduplication, and width mistakes
without confusing existing low-rank targets with a production reproduction.

**First step:** freeze a separate fixture for paper Eq. (16), using the pinned
11-index double-pentagon convention, cut `[1,3,6,8]`, dot bound zero, base width
`s_max=4`, trivial-sector data and the sector-167 exception. At `n=4,5,6`, count
unique on-cut seeds. Eq. (17) predicts **358, 589, 820**, with increment **231**.
Add off-by-one shift, wrong-cut and duplicate-count negative controls. This is a
seed-geometry check, not an integral reduction or an asymptotic proof.

**Compute estimate:** the largest expected retained set is 820 tuples. No runtime
or RAM for that proposed enumerator has been measured. Allocate a 30–60 minute
donor session; cap any optional reduction at 120 seconds, 2 GiB and one worker per
trial, counting setup separately. These are stop budgets, not predictions of fit.

**Blocked by:** a screened, separately implemented enumerator with pinned sector
data; an optional solve additionally needs verified equations, a declared master
basis, and a screened backend. Any new local high-rank target family needs its own
formulation identifier and independent checker/analytic controls. It must not
silently expand the accepted target set or reuse an exposed suite as unseen data.

**Success test:** exact seed sets/counts plus rejecting mutation controls, then
(only if attempted) complete same-target/same-basis reductions with no hidden
fallback, retained failures and fully charged costs. Finite-field samples can
falsify but do not replace this project's exact rational-identity requirement.
The broader source/code audit can supply a native-reproduction setup separately.

## Evidence limits and credit

The code and source review are AI-assisted and author-checked. The executable audit
checks finite metadata and generated indices; it does not prove IBP axioms, master
minimality, or the paper's general scaling. No author code, native Kira/FIRE,
double-pentagon reduction, high-rank search or new certificate was executed here.
The core checker, family definitions, accepted frontier and saved results remain
unchanged. `VERIFY.json` records checks and expected failure controls; `SOURCES.json`
binds the evidence to the base and working source files.

Credit: Berman et al. and the tube-seeding software authors for the published
construction and definitions; the original project's one-loop families, separately
derived validator, contributor-trial workloads and sunset formulation for the
local evidence; existing project contributors and maintainer Doug Colkitt
(@Mister-Meeseeks). This session does not claim those algorithms or definitions as
new. OpenAI Codex performed this donation for @thakrarsagar with delegated research
and review assistance. The parallel broad audit retains its separate scope and credit.
