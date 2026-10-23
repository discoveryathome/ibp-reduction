# Double-pentagon templates and a bounded rank-5 replay

**Author-checked.** All 12 IBP and 6 Lorentz-invariance templates in the pinned
tube source agree symbolically with a separate momentum-space derivation.
At two fixed finite-field samples, the 589-seed tube and 876-seed decreasing-rank
systems reduce one rank-5 target to identical coefficients in the frozen source
27-master convention. All four expanded original-equation witnesses replay.
The attempted native Kira cross-check is **incomplete**: both initial valid
configurations hit the 120-second wall limit; a later explicitly declared
600-second resource-only continuation aborted with `std::bad_alloc` after
308.036 seconds under the same 2 GiB cap. This package establishes no generic algebraic
reduction, complete master basis, native coefficient comparison or speedup.

## Frozen experiment

The target is `doublePentagon[1,1,1,1,1,1,1,1,0,0,-5]`, with cut positions
`[1,3,6,8]` (one-based), top sector 255 and zero dots in the seeds. Generated
equations may contain dots. The source's 113 distinct global master tuples are
filtered by the cut to 27 tuples **before** solving. These are a prescribed
convention, not a proof of minimality. `TASK.json` records the predeclared scope;
`SOURCES.json` pins the paper, original data, preceding PRs and native build.

| sample | prime | d | m1=s23 | m2=s34 | m3=s45 | m4=s51 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 2147483647 | 23 | 3 | 5 | 17 | 23 |
| 1 | 2147483629 | 61 | 13 | 71 | 89 | 101 |

Here `s12=1`; all five external legs are massless and
`p5=-p1-p2-p3-p4`. These paired samples were fixed from the author's validation
defaults. They are two samples, not the author's complete point/prime grid or
an algebraic reconstruction.

The tube fixture is byte-identical to PR #11's rank-5 set. The reference here is
the paper's actual decreasing-rank policy, Eq. (12) at width 5, with its sector-167
exception and rank-one floor; its count is Eq. (18)'s 876. The pinned author's
`validation/validate_tube_reduction.py` instead seeds a full rank-5 ball in each
on-cut sector (4,712 seeds). That distinct validation-script policy was inspected,
not run, and is not the reference solved here. Neither upstream Python nor Julia
code was imported or executed.

## Exact template check

`identities.py` constructs the scalar-product matrix in the basis
`(l1,l2,p1,p2,p3,p4)`. The map from 11 primitive loop scalar products to the 11
source denominators is affine and invertible, with determinant 512. The 12 IBP
operators are the two loop derivatives contracted with each of the six vectors.
The six LI operators are the external-momentum wedges. Each denominator derivative
is converted into index shifts, including the IBP divergence term.

A bijection matches every source polynomial/shift row to one derived operator
over `Q(d,m1,m2,m3,m4,a0,...,a10)`: the IBP normalizations are 1 and the LI
normalizations are -2. This uses symbolic polynomial equality, not sample values.
`identities.json` records the matching and all 18 rejected coefficient mutations;
the tests also reject a changed shift, omitted/duplicated operators and unsupported
coefficient syntax. Source file order defines propagator positions: the original
YAML comments label entries 6 and 8 inconsistently; the archived order is used.

## Field witnesses

`finite_field.py` generates the verified operator rows, projects out integrals
missing a cut propagator or in a source-declared trivial sector, and performs
sparse Gaussian elimination with the frozen masters ordered last. It rejects
relations among those masters and any non-master survivor in the target image.
It expands the target reduction back to original equation-row weights.

The replay path separately parses and directly evaluates the original coefficient
ASTs in the field. It adds the selected original rows and checks
`target - sum(master_coefficient * master) = sum(row_weight * original_row)`.
It does not reuse Gaussian elimination or compiled affine seed coefficients.
It shares the source identities, seed definition, cut/trivial-sector axioms and
Python runtime; this is a separate calculation path, not a separate reviewer.

Both samples give the following structural counts:

| policy | seeds | equations | variables | pivots | global free columns | witness rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tube | 589 | 10,602 | 9,342 | 8,301 | 1,041 | 5,938 |
| decreasing rank | 876 | 15,768 | 12,352 | 11,264 | 1,088 | 7,479 |

The target uses 27 master coefficients in each case, with **zero non-master
target survivors**. The matrices still have 1,014/1,061 other free columns beyond
the 27 declared masters. Target closure does not imply closure of the whole
matrix. Column/pivot counts are solver diagnostics; the independent replay
certifies the target identity, not those rank statistics.

## Native attempts, failures and cost

The native source/binary and local dependencies are the pinned Kira 3.0 build
from PR #10. Each attempt used one Kira worker, a 120-second timeout and a 2 GiB
address-space limit per process (also inherited by helpers); RSS is maximum
individual-process RSS, not aggregate memory. The target and all 27 source
masters were requested together, with preferred masters specified. No native
basis or coefficient output was validated.

1. The first invocation used `--prime_user`, as printed in Kira's help, but the
   pinned source actually registers `--prime`. It exited by signal 6 in 0.021 s.
2. The corrected `r=8,s=5` configuration, without a dot restriction, timed out
   after 120.176 s; maximum individual-process RSS was 1,137,016,832 bytes.
3. One bounded configuration pivot added the supported `d: 0` seed bound, keeping
   the same target, point, cut and master requests. It also timed out after
   120.040 s; maximum individual-process RSS was 210,141,184 bytes.

All three inputs, logs, receipts and driver versions are retained under
`results/native/`. The failed broad configuration is not a best-tuned Kira
benchmark; no relative timing claim follows from the two timeouts. Intermediate
databases, core dumps, binaries and third-party build trees are not bundled.

After publishing the original partial result at commit
`59cd25e05db9e306438678eb55b1e7836802afcd`, one additional resource plan was
explicitly claimed before execution (see `CONTINUATION.json`). It raised only
the zero-dot job's wall limit to 600 seconds, keeping all five scientific input
files, first specialization, binary, one worker and 2 GiB per-process cap fixed.
This is a post-timeout continuation, not part of the original preregistered
experiment. `results/native/extended-zero-dots/` contains the pre-run manifest,
task, exact inputs, driver, log and receipt. The process aborted by signal 6
after 308.036 seconds while normalizing coefficients, with `std::bad_alloc` in
the log; maximum individual-process RSS was 295,923,712 bytes. This observation
does not diagnose the allocation failure or establish an intrinsic memory
requirement. No complete native images or basis conversion were checked, and
no further retry was made. The original scientific artifacts are unchanged.

The four final field trials took 50.723, 87.540, 50.232 and 87.140 s wall time,
including generation, elimination, witness expansion and replay. Peak process
RSS ranged from 180,424,704 to 235,671,552 bytes. These are one-run local receipts,
not performance comparisons. A successful preliminary tube/sample-0 trial is
retained separately; its coefficients and witness equal the final trial exactly.
Its elapsed component timings are saved, but a standalone process-RSS receipt
was not captured. Before the final four trials, only the verifier's metadata
guards and signed-exponent handling were hardened; the seed policies, target,
samples, elimination and witness algorithm were unchanged. Both source versions
are retained. `VERIFY.json` gives the complete checks and limitations.

## Replay

Use the repository's pinned Python environment (Python 3.13.5, SymPy 1.14.0 in
this run). From the repository root, with `P=research/b4ba241d-rank5`:

```sh
.venv/bin/python "$P/test_validation.py" -v
.venv/bin/python "$P/identities.py" --out /tmp/new-identities.json
.venv/bin/python "$P/finite_field.py" --verify "$P/results/fields/tube-0.json"
.venv/bin/python "$P/run_fields.py" --out /tmp/new-rank5-fields
.venv/bin/python tools/check_project.py
```

Fresh output paths are required. The full field replay takes about five minutes
on this host; the four certificates can be checked without repeating elimination.
First verify all archived bytes from the package directory:

```sh
python3 -c 'import hashlib,json,pathlib; h=json.loads(pathlib.Path("HASHES.json").read_text()); assert all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==v for p,v in h.items()); print("PASS",len(h))'
```

Native replay additionally needs the separately built Kira/Fermat dependencies
and environment from PR #10's `BUILD.md`. Copy a saved trial's input files to a
fresh directory and run `run_kira.py --directory NEW --kira PATH`; the driver
uses the corrected CLI. It does not reproduce the deliberately retained option
error, nor assert scientific success merely from process exit status.

## Credit and remaining scope

Credit Justin Berman, Francois Charton, Andres Luna, Matthias Wilhelm and Mao
Zeng for the paper, seed construction and source data; the original MIT notice
is in `fixtures/TUBE-SEEDING-LICENSE`. PR #9 supplied the scope audit; PR #11
supplied the separately counted tube set; PR #10 supplied the screened native
build. Credit the Kira, Fermat, arithmetic-library and IBP project authors.
This package is a continuation by the same donor, not independent review of
those PRs. No accepted record, formulation, core checker or frozen benchmark was
changed. Generic algebraic reconstruction, an actually completed native
comparison, other targets/cuts, multi-ISP/high-rank paths and published timing
reproduction remain open for later work and maintainer review.
