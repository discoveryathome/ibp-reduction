# SAILIR: exact identity checks and bounded reproduction tasks

This is the completed SAILIR portion of the seeded `tube-and-online-audit` card,
seed `61c9b2c527abb202d37c722af4d46def`, project base
`9427e928040cd7d71513a443da4a42811720e537`. The user shortened the overall donation
during this round. The tube-seeding source investigation is a separate handoff;
this package makes no completed tube reproduction claim.

**Results:** all eight published IBP templates and the Lorentz-invariance template
match an independent exact polynomial derivation. The three actions in SAILIR
Appendix D reproduce its coefficients and 10, 6, 17 term counts over F_1009.
The package also identifies concrete reproduction prerequisites and differences
between the published benchmark metrics. These are author-checked results from
one AI-assisted session, not independent-person or maintainer acceptance.

## Sources and scope

Credit David Shih for [SAILIR, arXiv:2604.05034v1](https://arxiv.org/html/2604.05034v1),
and the authors and contributors credited by its
[public implementation](https://github.com/davidshih17/RL_IBPreduction_claude/tree/e3470aab47e5abe0a0f0aff889dd0d1e1d0c7c0a).
The inspected code commit is `e3470aab47e5abe0a0f0aff889dd0d1e1d0c7c0a`.
[sailir-sources.json](sailir-sources.json) records 41 file SHA-256 hashes and the
complete source-tree path inventory. Source was read statically; upstream Python,
shell, checkpoints, notebooks and solvers were not executed. The model checkpoint
was not downloaded. The primary paper is CC BY 4.0; no paper or upstream source
snapshot is redistributed in this package.

The local project's `ibp/contributor.py` performs classical demand-driven sparse
elimination over a rational-function field. It is not a reproduction of SAILIR's
learned finite-field beam search. A local arithmetic-count win does not establish
a performance comparison against SAILIR. This audit changes no formulation,
checker, frozen result, frontier or accepted record.

## Exact mathematical checks

[check_templates.py](check_templates.py) builds scalar products from the seven
propagators, then differentiates their powers. It compares polynomial coefficients
in `a0,...,a6,d,m2,m3` over Q, with `m1=1`, against the published IBP/LI text data.
The text parser permits only integer constants, known symbols and polynomial
arithmetic; it does not execute source expressions. The LI relation uses the
external Lorentz generator contracted with `p1,p3`; the published normalization
is -2 times that generator. All nine identities agree, and nine changed-coefficient
controls reject. See [template-check.json](template-check.json).

[worked_episode.py](worked_episode.py) independently derives the three Appendix D
IBPs from scalar products using standard-library rational arithmetic and then
works modulo 1009 at `d=41,m1=1,m2=31,m3=47`. Starting from
`I[1,2,1,1,1,1,-3]`, the result has 17 terms and lowers the maximum top-sector weight
from `(7,3)` to `(7,2)`. Its final identity is the raw-IBP combination
`1008*row0 + row1 + 65*row2`. All 17 changed final coefficients and all three
omitted-input controls reject. The full residual expression is saved in
[worked-episode.json](worked-episode.json).

The kinematic convention is `p3=p1+p2`, as specified by the actual upstream YAML;
its introductory comment instead says `p1+p2+p3=0`. Thus
`p1.p3=(m1+m3-m2)/2`. The first draft of this audit followed the conflicting comment
and failed the worked-example comparison; using the executable configuration
resolves it. An earlier local generator-expression construction error also failed
before producing any result. Neither failed draft is counted as evidence.

These checks assume dimensional-regularization IBP and Lorentz invariance. They
verify templates and one specified episode, not master-basis minimality, the
learned policy, every solver path or all published benchmark reductions. The
episode is finite-field evidence; the template comparison is symbolic. The
17 residual integrals still need reduction. SymPy is a trusted arithmetic
dependency of the template check, not a formally verified kernel.

## Reproduction findings

1. **A worker success is an episode.** The
   [worker's final test](https://github.com/davidshih17/RL_IBPreduction_claude/blob/e3470aab47e5abe0a0f0aff889dd0d1e1d0c7c0a/scripts/eval/onestep_worker.py#L220)
   accepts a lower weight. It does not require a final expression containing only
   the 16 designated masters. The quick start therefore does not reproduce a
   full benchmark reduction.
2. **Specify the replay prime.** The
   [replay CLI](https://github.com/davidshih17/RL_IBPreduction_claude/blob/e3470aab47e5abe0a0f0aff889dd0d1e1d0c7c0a/scripts/eval/replay_reduction_path.py#L208)
   defaults to 10007, while generation defaults to 1009. First replay with
   `--prime 1009` to check saved coefficients. Another prime is an additional
   check, not a rational-function proof. For a complete reduction, verify all
   worker traces, composition, target coverage and the prescribed master set.
3. **The Kira wrapper and YAML disagree.**
   [run_benchmark_s7.sh](https://github.com/davidshih17/RL_IBPreduction_claude/blob/e3470aab47e5abe0a0f0aff889dd0d1e1d0c7c0a/scripts/kira/run_benchmark_s7.sh#L24)
   copies each target to `integrals`, but
   [jobs_benchmark.yaml](https://github.com/davidshih17/RL_IBPreduction_claude/blob/e3470aab47e5abe0a0f0aff889dd0d1e1d0c7c0a/scripts/kira/jobs_benchmark.yaml#L7)
   selects `integrals-13.7.7`. Providing other prerequisites would still leave
   this target-selection mismatch. Generate a separate job and clean working
   directory for each intended target before making any timing claim.
4. **The numerical-point input is missing.** Both Kira jobs reference `numerics`,
   absent from the pinned tree. [Kira 3, section 3.4](https://arxiv.org/html/2505.20197v1#S3.SS4)
   documents that this file supplies the prime and parameter values. A proposed
   input for this normalized family is `prime 1009`, then `d m2 m3`, then
   `41 31 47`, on three lines. This proposal has not been run in Kira. The official
   Kira 3.1 tag resolves to `5760f42f8decd7eb5474c780db75b5e5e7b450a0`.
5. **Time and memory denominators matter.**
   [Table 5](https://arxiv.org/html/2604.05034v1#A6) uses ideal parallel time, and
   the published implementation divides worker memory by allocated CPUs. The
   [CSV audit](source-check.json) preserves elapsed time, ideal time, raw worker
   peak and per-CPU peak separately. For `(r,s)=(10,7)` and `(12,7)`, the reported
   per-CPU memory is below Kira's, while raw worker peak is above it. Neither is
   aggregate simultaneous cluster memory. The 16 paper cases account for
   194,895 reported jobs; their worker DAGs and total CPU-seconds are not supplied
   by these CSVs.
6. **Training is a separate budget.** The published log contains 30 CUDA epochs
   totaling 28,243.1 reported seconds, excluding data generation and setup. It
   records 946,168 training samples and 118,271 validation samples. Do not treat
   this as CPU timing or include checkpoint reuse as fresh training. Dependencies
   in the upstream README are not version locked.

All 19 CSV targets agree between the two result files; the 16 paper targets also
match their Kira input files. CSV column `d` denotes dots, not spacetime dimension
41. These are static consistency checks, not validation of the reported timings.

## Bounded follow-up tasks

| Task | Budget and prerequisites | Acceptance test |
|---|---|---|
| Independent replay of this package | 20–30 minutes; Python, pinned SymPy; ordinary CPU | Re-derive the nine templates and three-step identity; inspect the momentum convention; reproduce every negative control. |
| One learned Appendix D episode | 30–45 minutes after screened dependencies/checkpoint are available; provision at least 4 GiB and impose a 10-minute execution cap | Use target `(1,2,1,1,1,1,-3)`, prime 1009, beam width 20, `--beam-sort mixed`, `--paper-masters-only`, and a bounded step count. Retain timeout/failure. Replay all actual steps at the same prime and check a strict sector-weight decrease. No complete-reduction or speed claim. |
| Kira comparison preflight | 30–60 minutes with an existing pinned Kira 3.1 installation | Repair the selected-target wiring, supply and hash the numerical point, isolate each working directory, inspect actual masters and export completeness. Compare the same target, field point and basis; stop if any differs. |

The learned episode estimate is a proposed session allocation, not a measured
runtime guarantee. The published quick-start target is harder and different.
Training from scratch and reproducing the full Condor benchmark are outside
these small tasks. Independent review of tube-seeding configurations remains
the other part of the selected literature card.

## Replay

Obtain a sparse checkout of the pinned source with `sailir`, `scripts` and `results`
included; the checkpoint is unnecessary. From this project's root, with
`SAILIR_SOURCE` set to that checkout and the pinned dependencies installed locally:

```sh
python3 research/tube-online-audit-61c9b2c5/worked_episode.py --output /tmp/worked-episode.json
python3 research/tube-online-audit-61c9b2c5/audit_sources.py --sailir-source "$SAILIR_SOURCE" --output /tmp/source-check.json
python research/tube-online-audit-61c9b2c5/check_templates.py --sailir-source "$SAILIR_SOURCE" --output /tmp/template-check.json
```

The last command requires `sympy==1.14.0` and `mpmath==1.3.0`; the first two need
only the standard library. All three commands passed in this session. No full
project solver regression is claimed for this research-only addition.
