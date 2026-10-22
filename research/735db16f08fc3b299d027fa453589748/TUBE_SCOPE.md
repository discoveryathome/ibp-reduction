# Tube-seeding scaling: frozen-benchmark eligibility

- Donation: `735db16f08fc3b299d027fa453589748`; card: `literature/tube-and-online-audit`.
- Local source pin: `9427e928040cd7d71513a443da4a42811720e537` (also checkout HEAD when inspected).
- Paper pin: Berman et al., [arXiv:2606.10698v1](https://arxiv.org/abs/2606.10698v1), [versioned full text](https://arxiv.org/html/2606.10698v1).
- Author-code pin: [`ec955d46f26ef497ca5ee7053f6f0286efb7971b`](https://github.com/andreslunagodoy/tube_seeding/commit/ec955d46f26ef497ca5ee7053f6f0286efb7971b), committed 2026-06-10; inspected 2026-10-22 UTC. This is a public-code snapshot, not an asserted paper-release tag.
- Source-reading subtask scope: primary-source reading and static local-source inspection only; no code execution, installs or posts by this researcher. The parent separately ran the local diagnostic and tests recorded in `VERIFY.json`. Broad setup/reproduction inventory belongs to the separate claim at [discussion 2, comment 19132014](https://github.com/discoveryathome/ibp-reduction/discussions/2#discussioncomment-19132014).
- Labels: **S** source fact; **L** local observation at the local pin; **I** inference/proposal; **U** unmeasured resource expectation.

## Definitions and source-backed claim

**S** Paper §2, Eq. (3), agrees with author-code [`r_level`, `s_level`, `d_level`, `t_level`, lines 945–962][levels]:

| Quantity | Definition for index tuple `a` |
|---|---|
| Present propagators `t` | `sum(a_i > 0)` |
| Positive degree `r` | `sum(a_i for a_i > 0)` |
| Dots `d` | `r-t = sum(a_i-1 for a_i > 0)` |
| Numerator rank `s` | `-sum(a_i for a_i < 0)` |

**I** Rank counts exponent multiplicities, not negative slots: `(1^8,-8,-6,-6)` has `s=20`, three negative slots, and `d=0`; `(5,4)` has `s=0,d=7`. Physical momentum-polynomial degree/Lorentz tensor rank additionally requires the numerator basis and its expansion; it is not universally equal to either negative-slot count or `s`. Paper §2, Eq. (1), explicitly allows polynomial `D_i`; do not infer a universal degree conversion.

**S** “Tube radius” is not a universal Euclidean-radius parameter: §4.2.2, Eq. (16), translates a fixed decreasing-rank seed set with `s_max=4`; §4.3.2, Eq. (20), adds skeleton/junction widths.

**S** On cut `[1,3,6,8]`, for single target `I_(1^8,0,0,-n)`, §4.2.3, Eqs. (17)–(18), gives:

`N_tube(n)=231n-566 (n>=4)`; `N_decreasing(n)=C(n+7,7)+C(n+4,6)=O(n^7)`.

**S** Timing/RSS linearity is empirical over `n=5..40` (§4.2.3, Table 3/Fig. 16); analytic reconstruction is excluded (§5; Appendix A).

**S** Published targets: equal-mass one-loop bubble (§3.1, Eq. (5); no top-sector ISP), and massless nonplanar two-loop five-point double pentagon (§4.1, Fig. 12/Eq. (10): eight propagators, three ISPs). Rank-20 examples include `(0,0,20)` and `(8,6,6)`; all 66 triples summing to 10 are covered in §4.3.3. Full reduction needs spanning cuts (Eq. (11)); multi-ISP tubes need supplementary seeds (§4.3.2–3).

## Code corroboration and held-fixed variables

**S** [`scan_n_feyngym_metrics.py`, lines 63–66, 100–116][scan] fixes `MODULUS=2**31-1`, numerical substitutions, top sector `(1^8,0,0,0)`, and cut `[1,3,6,8]`. `build_strip_seeds` fixes `(s_max,r_max,d_max)=(4,8,0)`, applies the sector-167 exception, shifts only the last ISP by `0..max(0,n-4)`, deduplicates, and excludes trivial sectors. This corroborates paper §4.1 Eq. (12) and §4.2.2 Eq. (16).

**I** The linear seed-growth comparison holds family/index dimension, propagator support rules, dot budget, base width, cut, and exception rules fixed while changing target rank. For timing comparisons also fix templates/identity set, master conventions, field/kinematic point, elimination strategy, implementation, and hardware. Increasing width, adding rank-dependent fallback seeds, or changing the number of requested targets changes the comparison. Linear seed count alone does not establish linear elimination cost or symbolic coefficient growth.

**S** The [family configuration][family-code] lists eight denominator positions and auxiliary `(l2+p1)^2`, `(l2+p2)^2`, `(l2+p4)^2`, matching paper §4.1/Fig. 12. The [rank-20 notebook][rank20-code] submits both single- and three-ISP examples (Appendix A); the [rank-10 generator, lines 114–119][rank10-code] enumerates 66 triples. Its `build_path_seeds(..., width=2)` parameter is unused in the inspected body: transverse ranges are hard-coded (lines 135–197). Changing that argument alone is therefore not a radius experiment.

**I** A single-target `O(n)` construction must not be promoted to `O(n)` total cost for every target of rank `n`: the three-ISP target shell itself has `C(n+2,2)` members. Cut-only success also cannot establish the uncut result.

## Frozen local suite: ineligible for numerator-rank scaling

**L** At the local pin, [`ibp/families.py`, lines 34–51][local-families] lists seven one-loop families and calls `indices(..., numerators=0)` for their targets. Therefore every requested target has `s=0`. The positive-degree bounds are only 3–5. [`docs/formulation.md`, lines 41–65][local-formulation] explicitly states the nonnegative-index target restriction and absence of a high-rank numerator benchmark.

**L** `seeds()` permits total negative exponent magnitude at most one (`families.py`, lines 53–61); those auxiliary seeds/unknowns do not make the requested targets high-rank. The family convention is Euclidean with squared-mass parameters and symbolic `QQ(d,s,t,m,u)` coefficients (lines 1–8). Here `d,s,t` also name field variables, so their meanings must not be confused with paper Eq. (3).

**L** [`ibp/reducer.py`, lines 35–38][local-reducer] measures `max_degree` on coefficient numerator/denominator polynomials. That metric is not the integral numerator rank. The local equal-mass bubble also adds a tadpole symmetry relation (lines 55–56), whereas paper §3.1 retains both tadpoles for its presentation.

**I** These targets can test correctness, sparse-seed selection, and a separately labelled dotted-bubble analogue; they cannot test increasing-`s` scaling or transfer to the published double-pentagon ISP structure. Raising local `rmax` alone increases denominator degree, not numerator rank. Adding negative-index targets/families or changing the checker creates a new formulation; preserve the frozen benchmark and accepted records.

## Minimum bounded falsification experiment for the parent

1. **I — eligibility guard:** statically audit all seven target definitions and record separate maxima for `s`, `d`, and `r`; report `max(s)=0`. Add controls `(5,4)` and `(1^8,-8,-6,-6)` to catch swapped definitions. This is an audit, not a scaling measurement.
2. **I — smallest numerator-sensitive check:** in a separate fixture, enumerate Eq. (16) seeds at `n=4,5,6`, retaining the pinned family, trivial sectors, sector exception, `d_max=0`, and quadruple cut. Compare *on-cut unique seeds* with Eq. (17): `358,589,820`; increment `231`. An off-by-one shift, dropped exception, positive ISP, or count mismatch falsifies that implementation of this construction. Do not compare pre-cut counts or equation counts to seed counts.
3. **I — reduction gate, only if the parent has the required verified fixtures/backend:** at `n=5`, compare the target's coefficients against a separately checked decreasing-rank reduction on the same cut and master convention. Retain all unknowns; reject any residual non-master or silently used fallback. Repeat at two generic points/primes to detect numerical accidents; samples remain evidence, not an algebraic proof. A failure is actionable; a pass establishes only this bounded instance.
4. **I — optional cheaper bubble-only control:** implement paper §3.2/Table 1's `(5,4)` path (17 seed locations) with its Eqs. (6)–(8); compare exact coefficients after explicitly reconciling signs and tadpole symmetry. Label it a dotted-bubble implementation check, never a high-rank numerator reproduction.
5. **U — resource bounds:** no time/RAM measurement was made here. Seed-only checks are expected to be small because the required on-cut output is at most 820 tuples; this is not a measured runtime estimate. For any optional solve, propose a hard 120-second/2-GiB/one-worker cap per trial, recording setup separately. This is a stop budget, not a prediction that the run fits. A timeout or missing backend means unmeasured/incomplete, not mathematical failure.

**I — handoff obligations:** freeze an experiment manifest before running; include source pins, tuple conventions, seed/target counts, cuts, widths, trivial-sector data, master list, primes/points, operator/pivot choices, caps, and explicit fallback status. Save failures and coefficients/certificates; check the existing frozen suite separately. Parent owns execution, tests, and PR. No inference from this note authorizes accepted-record promotion or claims the rank-20/rank-10 production results were reproduced.

[levels]: https://github.com/andreslunagodoy/tube_seeding/blob/ec955d46f26ef497ca5ee7053f6f0286efb7971b/FeynGym/pyfeyngym/src/pyfeyngym/__init__.py#L945-L962
[scan]: https://github.com/andreslunagodoy/tube_seeding/blob/ec955d46f26ef497ca5ee7053f6f0286efb7971b/doublePentagon/benchmarks/scan_n_feyngym_metrics.py#L63-L116
[family-code]: https://github.com/andreslunagodoy/tube_seeding/blob/ec955d46f26ef497ca5ee7053f6f0286efb7971b/doublePentagon/kira_equation_template_generation/config/integralfamilies.yaml#L1-L17
[rank20-code]: https://github.com/andreslunagodoy/tube_seeding/blob/ec955d46f26ef497ca5ee7053f6f0286efb7971b/doublePentagon/rank20/high_rank.ipynb#L374-L598
[rank10-code]: https://github.com/andreslunagodoy/tube_seeding/blob/ec955d46f26ef497ca5ee7053f6f0286efb7971b/doublePentagon/rank10/path_coverage_rank10.py#L114-L197
[local-families]: https://github.com/discoveryathome/ibp-reduction/blob/9427e928040cd7d71513a443da4a42811720e537/ibp/families.py#L34-L61
[local-formulation]: https://github.com/discoveryathome/ibp-reduction/blob/9427e928040cd7d71513a443da4a42811720e537/docs/formulation.md#L41-L65
[local-reducer]: https://github.com/discoveryathome/ibp-reduction/blob/9427e928040cd7d71513a443da4a42811720e537/ibp/reducer.py#L35-L56
