# Fixed-width on-cut double-pentagon tube counts

The separately implemented enumerator reproduces **358, 589 and 820 unique seed
tuples** at ranks **4, 5 and 6**, respectively, for the frozen width-four,
zero-dot construction on cut `[1,3,6,8]`. The actual canonical sets are in
`data/rank-4.jsonl`, `data/rank-5.jsonl` and `data/rank-6.jsonl`.

This completes the count-only [handoff from PR #9](https://github.com/discoveryathome/ibp-reduction/discussions/2#discussioncomment-19132320).
The [claim](https://github.com/discoveryathome/ibp-reduction/discussions/2#discussioncomment-19140422)
records the chosen scope. Original seed `b4ba241d49ae3adec57309d131c13f06` drew
the replication track; this is its next open matching handoff after PR #10.
The person explicitly authorized multiple focused PRs within the original budget.
Base: `9427e928040cd7d71513a443da4a42811720e537`.

Evidence is **author-checked count replication**, not independent scientific
review. No IBP/LI equations were generated, no reduction was solved, and no
reduction-completeness, runtime-scaling or performance claim follows.

## Frozen definition and source audit

Primary definitions: Berman et al.,
[arXiv:2606.10698v1, Eqs. (12), (16), (17)](https://arxiv.org/html/2606.10698v1#S4.E12).
Author source: [`ec955d46f26ef497ca5ee7053f6f0286efb7971b`](https://github.com/andreslunagodoy/tube_seeding/tree/ec955d46f26ef497ca5ee7053f6f0286efb7971b).
Predecessor scope audit: PR #9 at `6ea993589a6dc4416636bec87b4f25554993dde9`.
`SOURCES.json` records exact source/data hashes and the paper download digest.

The experiment uses 11 integer indices: the first eight may denote positive
propagators; the last three remain non-positive. The top-sector mask is 255,
the cut mask is 165, and all positive powers are one. An absent propagator may
also carry a negative numerator index; numerators are not confined to the last
three positions. For a nontrivial support mask `S` with `t` positive indices,
the base numerator bound is

```text
b(S) = max(1, t - 4 + indicator(S is a subsector of 167)).
```

The rank-one floor and the exception for sector 167 **and its subsectors** are
both material. The base consists of all numerator monomials of total degree at
most `b(S)` over the `11-t` absent positions. The tube is the set union of its
translations by `a11 -> a11-k`, for `k=0,...,n-4`. Sector/cut filtering commutes
with these translations because index 11 stays non-positive and is not cut.

These rules were checked against the pinned author's `build_strip_seeds` and
`gen_all_seeds` definitions by static inspection only. No author Python, Julia,
notebook or backend code was executed. The implementation here uses numerator
monomials represented as multisets, rather than importing the author's weak-
composition generator. The byte-identical 466-entry trivial-sector fixture is
bundled with its original MIT notice. All 16 possible sectors beneath top mask
255 on this particular cut are nontrivial; this test does not exercise exclusion
of trivial sectors on other cuts.

## A complete counting check, independent of tuple enumeration

Fix a sector, let `z=11-t`, `b=b(S)` and `K=n-4`. For a fixed assignment to the
`z-1` transverse absent positions with total numerator degree `q<=b`, the last
index's nonnegative numerator degree occupies the whole interval
`0,...,b-q+K`. Translating the base fills that interval without gaps. There are
`C(b+z-1,z-1)` such transverse columns. Hence the unique set size in this sector is

```text
N_S(n) = C(b+z,z) + (n-4) C(b+z-1,z-1).
```

The finite sector breakdown is:

| Positive indices t | Base bound b | Sectors | Base tuples per sector | Columns per sector |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 1 | 1 | 8 | 7 |
| 5 | 2 | 1 | 28 | 21 |
| 5 | 1 | 3 | 7 | 6 |
| 6 | 2 | 6 | 21 | 15 |
| 7 | 3 | 4 | 35 | 20 |
| 8 | 4 | 1 | 35 | 15 |

Summing gives `358 + 231(n-4) = 231n-566` for this frozen combinatorial model and
integer `n>=4`. This is a column-count argument, not an inference from three
measurements. It reproduces the paper's stated count formula, without proving
anything about the sufficiency or cost of the resulting IBP system.

`validate` checks every tuple's dimension, integer type, support, cut, dot/ISP
bounds and contiguous-column membership. It rejects duplicates and compares
every sector's cardinality with the formula above. Unique membership plus the
complete finite-domain cardinalities establishes equality to the specified seed
set; an aggregate count or checksum alone would not.

## Replay and controls

Only Python's standard library is required. From the repository root:

```sh
python3 research/b4ba241d-tube-count/count_seeds.py --check research/b4ba241d-tube-count/data
python3 -m unittest discover -s research/b4ba241d-tube-count -p test_counts.py -v
python3 research/b4ba241d-tube-count/count_seeds.py --out scratch/tube-count-replay
```

The first command reports `valid: true` and the three counts. The output directory
for generation must be new; an existing directory is refused. The delivered and
initial replay tuple files agree byte-for-byte. Seven tests pass, covering the
published counts and all sectors, negative absent-propagator indices, 127-tuple
overlap of adjacent base copies, duplicate/missing tuples, both off-by-one shift
directions, wrong cut, dots, positive ISP, rank/type errors, and omitted floor or
exception rules. Mutants are reconstructed by the tests rather than saved as
redundant copies of the corpus. Logs are in `logs/`.

`data/counts.json` records actual enumeration times, per-sector counts, source/data
digests and process RSS. On the tested Linux/Python 3.13.5 host each tiny seed-only
enumeration took about 2–3 milliseconds; the process peak was 18,501,632 bytes,
including interpreter/setup/checks. These single receipts are not a performance
benchmark and contain no equation-generation or reduction cost.
`VERIFY.json` records checks and limitations; `HASHES.json` binds the package.

## Not checked and open next question

Not checked: IBP/LI template validity, equations/unknowns, target reducibility,
masters, primes/kinematic points, finite-field reconstruction, other cuts,
multi-ISP paths, high-rank solves, or the paper's timing/memory results. No native
FeynGym, Kira or FIRE solve was run for this family. The source/data convention
audit is author-checked; a separate reviewer is still needed. Other-platform RSS
reporting was not exercised.

Next, a contributor with independently verified double-pentagon IBP/LI fixtures
and a backend can test the rank-5 target on this same cut, retaining all unknowns
and a fixed master/field/kinematics convention. Start by replaying these exact
sets; only then attempt a separately bounded solve with failures/fallbacks
retained. Numerical samples would remain finite evidence rather than an
algebraic proof. The existing checker, family definitions, frontier, ledger and
accepted results were not modified.

## Credit

The construction, source data and count formula belong to Justin Berman,
Francois Charton, Andres Luna, Matthias Wilhelm and Mao Zeng. Their original
license accompanies the copied data. Credit PR #9's pinned scope audit and
concrete count handoff, and the original project contributors and maintainer
Doug Colkitt for the contribution framework and local benchmark/checker.
OpenAI Codex implemented this replay for thakrarsagar. A separate implementation
does not constitute a separate reviewer or scientific acceptance.
