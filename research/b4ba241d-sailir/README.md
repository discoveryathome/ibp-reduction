# Native preflight of the SAILIR worked episode

**Author-checked.** Pinned Kira 3.0 returns all 18 requested images for the
SAILIR Appendix D target and its 17 residual integrals at the frozen rational
point. The target equals the residual combination modulo 1009. Both native
master files contain 15 entries; the source's 16 designated entries reconcile
through an exact unit-Jacobian loop change proved below. This is one native
preflight and episode check, not a learned-policy or paper-benchmark reproduction.
The solver version differs from the paper's Kira 3.1 reference.

## Frozen domain and native result

The target is `trianglebox[1,2,1,1,1,1,-3]`. The seven squared momentum forms,
in source file order, are `k1`, `k2`, `k1+k2`, `k1+p1`, `k2+p3`, `k2-p1`,
`k1+p3`; the last is auxiliary. All propagator masses are zero. The executable
kinematics say `p3=p1+p2`, with external squares `(1,31,47)` and `d=41`.
The conflicting introductory momentum-conservation comment is not used.

The isolated job uses top sector 63, `r=7,s=3`, no cut or additional dot bound,
all 18 distinct requests and the source's 16 preferred entries. It avoids the
upstream benchmark wrapper's mismatched target filename and missing `numerics`
file by generating its own job and using explicit Kira 3.0 CLI substitutions.
It does not repair or execute the upstream Kira 3.1 workflow.

The available Kira is source commit `fb745431f97c8899a512e638da8598b0cfad7521`,
binary SHA-256 `9d49f623f144ee90c3eb2f50290b180b93c5c85e9ca1272092cecb065eb47066`.
PR #10's build receipt records its arithmetic/dependency checks. One native
attempt used a 180-second timeout, 2 GiB per-process address-space cap and one
Kira worker. It returned 0 in 14.050 seconds, with maximum individual-process
RSS 57,020,416 bytes and zero reported unreduced integrals. These are one-run
execution receipts, not a timing comparison. No retry or target tuning occurred.

Native coefficients are **exact rational numbers at this specialization**.
`verify_saved.py` parses them with a restricted AST/Fraction evaluator and maps
them into F_1009 only after checking that every denominator is invertible.
This is not execution of a native finite-field backend or generic reconstruction.
All 18 images are explicit in the raw export and close on the actual native
basis. The checker verifies

`image(target) = sum(episode_coefficient * image(residual_integral)) mod 1009`.

Ten controls reject empty/duplicate/malformed exports, wrong normalization,
missing images, altered target/residual images, a denominator pole, another
prime and an undeclared master. A declared native master may have an implicit
self-image; an arbitrary missing integral may not. Three parser tests cover
the numerical, momentum and export syntax.

## Exact reconciliation of the designated master lists

The sole designated entry absent from Kira's 15-entry list is
`A=I[1,0,1,0,0,1,0]`. The retained list includes `B=I[0,1,1,1,0,0,0]`.
Make the loop-variable change `k1=-q2`, `k2=-q1`. Its loop matrix has determinant
-1 and absolute measure Jacobian 1. The active squared forms of A transform as

| old position | transformed momentum | retained squared form |
| --- | --- | --- |
| 1 | `-q2` | position 2 |
| 3 | `-(q1+q2)` | position 3 |
| 6 | `-(q1+p1)` | position 4 |

Every active power is one and all other powers are zero. Squaring removes each
overall sign, so **A=B** under invariant dimensionally regularized integration.
This relation is generic in `d` and the external kinematics; it is not inferred
from the numerical sample. `basis_relation.py` verifies the signed vector
matches, determinant and resulting index tuple from the archived geometry.
It checks that both actual native lists differ from the designated list by
exactly this entry, and emits the full 16-to-15 map. A missing loop swap,
nonunit determinant and changed active momentum all reject.

This post-run explanatory check reconciles the observed basis difference; it
did not change the native configuration or the source's frozen 16-entry list.
It proves one redundancy, not independence or minimality of the remaining 15.
Both the original list difference and the explicit map are retained in
`data/native-comparison.json` and `data/basis-relation.json`.

## Predecessor replay and provenance

PR #8 at `7e7ab86fa43481ba731e29b6bf104cde18bb4925` supplied the screened
`research/tube-online-audit-61c9b2c5/` audit. Its three scripts were replayed
against author source `e3470aab47e5abe0a0f0aff889dd0d1e1d0c7c0a`:

- All 41 source fingerprints and the static CSV/source findings reproduce.
- All eight IBP and one LI templates match symbolically, with nine changed
  coefficient controls rejected.
- The Appendix D three-action episode reproduces 10, 6 and 17 term counts,
  the final weight `(7,2)`, and the original-row combination
  `1008*row0 + row1 + 65*row2`; 17 coefficient and three omission controls reject.

All three output files are byte-identical to the predecessor's archived outputs.
These reuse the predecessor's derivation code and shared SymPy, so they establish
software replay rather than a new independent-person review. The new native
images and exact basis relation are additional checks. No SAILIR Python, shell,
notebook, checkpoint, learned model or training was executed; source was read
as data/AST only. No upstream source snapshot, model or paper is redistributed.
The inputs here are independently written configurations of the published
mathematical geometry. The executed native driver is preserved verbatim;
the public helper later gained an early existing-directory guard without changing
scientific inputs or argv.

## Replay

Use the project's pinned Python environment (3.13.5, SymPy 1.14.0 here).
From the repository root, set `P=research/b4ba241d-sailir`:

```sh
.venv/bin/python "$P/verify_saved.py"
.venv/bin/python "$P/basis_relation.py"
.venv/bin/python -m unittest discover -s "$P" -p test_parsers.py -v
.venv/bin/python tools/check_project.py
```

Those archive checks need only the standard library, except the existing project
integrity checker. Fresh native execution additionally needs PR #10's separately
built Kira/Fermat environment, a checkpoint-free checkout of the pinned author
source, and fresh output paths:

```sh
.venv/bin/python "$P/run_native.py" --source AUTHOR-SOURCE --episode "$P/data/worked-episode.json" --out /tmp/new-sailir-native --kira PINNED-KIRA
.venv/bin/python "$P/verify_saved.py" --native /tmp/new-sailir-native
.venv/bin/python "$P/basis_relation.py" --native /tmp/new-sailir-native
```

To repeat the three predecessor checks, fetch PR #8's exact commit and follow its
README with the same author checkout. `SOURCES.json` binds all scripts, outputs,
source files, native inputs, executable and build receipt. From this package
directory, check archived bytes first:

```sh
python3 -c 'import hashlib,json,pathlib; h=json.loads(pathlib.Path("HASHES.json").read_text()); assert all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==v for p,v in h.items()); print("PASS",len(h))'
```

Credit David Shih and the SAILIR contributors for the paper/data, PR #8's donated
source/episode audit, the IBP project authors, Kira/Fermat/library authors and
PR #10's pinned build. Exact scope, caps and unchecked obligations are in TASK
and VERIFY. Independent physics/maintainer review, Kira 3.1 execution, generic
episode coefficients, learned-policy/checkpoint replay, training and published
benchmark timing/memory reproduction remain open. Accepted records, formulation,
core checker and frozen benchmark are unchanged.
