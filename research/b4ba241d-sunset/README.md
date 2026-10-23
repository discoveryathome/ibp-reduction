# Native and operation-count replay of the sunset candidate

**Author-checked.** A fresh Linux execution of pinned Kira 3.0 reduces all nine
non-master targets of `sunset_equal_mass_v1`, including the three numerator
insertions. Both native master files give the two prescribed masters. Every
coefficient agrees exactly in generic `d` and nonzero squared mass `m` with the
original 107-operation candidate and all three fresh policy certificates.
The operation traces independently reproduce the 425/139/107 counted operations.
This is software replication and accounting inspection; the original handoff's
separate physics-review request remains open.

The predecessor is commit `ad48fb195d51103c20e5dfedc17ee673e46fe0e4`, package
`research/48b86116551382cfb4d5f1fea362211a`, from the donated 2026-10-22 session by
@thakrarsagar with OpenAI Codex. The [open handoff](https://github.com/discoveryathome/ibp-reduction/discussions/2#discussioncomment-19130456)
asks for exact replay and accounting review. `PREDECLARED_TASK.md` and `TASK.json`
freeze this contribution's software scope; no new policy search was performed.

## Exact native result

The family is `D1=k1²+m`, `D2=k2²+m`, `D3=(k1-k2)²+m`. The unchanged native
input uses mass-squared expressions `-m`, since Kira subtracts those expressions.
There are no external momenta. The prescribed masters are `(1,1,1)` and
`(1,1,0)`, with the project's S3 permutation convention.

Targets are `(2,1,1)`, `(3,1,1)`, `(2,2,1)`, `(2,1,0)`, `(2,2,0)`,
`(3,1,0)`, `(1,1,-1)`, `(2,1,-1)` and `(2,2,-1)`. The last three are numerator
insertions. The five input files are byte-identical to the accepted repository's
readiness fixture; no target, dot, seed or master adaptation was used.

`verify_saved.py` replays the original candidate and three fresh certificates
through the unchanged exact checker, compares each to the raw native export,
and checks both `masters` and `masters.final`. It rejects empty/incomplete/
duplicate targets, a changed coefficient, different basis, executable expression,
wrong target normalization and altered/incomplete certificates. There are nine
distinct native target identities, not 36 different targets merely because four
certificates are compared.

The native binary is the screened source-built Kira 3.0 commit
`fb745431f97c8899a512e638da8598b0cfad7521`, SHA-256
`9d49f623f144ee90c3eb2f50290b180b93c5c85e9ca1272092cecb065eb47066`.
PR #10's `BUILD.json`/`BUILD.md` give its source, dependencies and arithmetic
controls; `SOURCES.json` binds that receipt and this run's unchanged input files.
The run used one worker, a 180-second timeout and a 2 GiB address-space cap per
process. It returned 0 in 4.714 seconds; maximum individual-process RSS was
21,843,968 bytes. These are execution receipts, not a Python/Kira speed comparison.
No binary, intermediate database or third-party source tree is redistributed.

## Operation-count replay

| frozen method | attempted add/mul/div | executed add/mul/div | cache hits | pruned proof nodes |
| --- | ---: | ---: | ---: | ---: |
| cached sparse | 657 | 425 | 232 | 43 |
| inherited online (`target`, `dots`) | 185 | 139 | 46 | 29 |
| candidate online (`simple`, `reverse`) | 162 | 107 | 55 | 28 |

`audit_cost.py` uses the existing producers and a temporary read-only wrapper
around `Arithmetic.op`, restored in `finally`. The wrapper records the operands,
result, operation kind and whether the producer executed an operation or served
a cached result. A separate replay checks every rational result, reconstructs
the ordered-key cache (capacity 10,000), and counts attempts, misses and hits
without reading the producer's cache. All counter totals agree. Altered results,
cache flags and operation counts reject for each of the three policies.

The candidate's pruned proof DAG and outputs match the pinned predecessor digest
exactly. Pruning follows the existing `ibp.trial.worker` procedure and does not
change the operation counts. The first direct replay omitted that step and
therefore failed its candidate-DAG digest assertion. Its raw certificates,
traces, original driver and failure log are retained in `results/initial-cost/`
and `logs/sunset-cost-driver.log`. That setup attempt had 30-second producer
alarms and a 120-second outer timeout but omitted the address-space cap; the
corrected replay applies 2 GiB before imports and preserves the same policies
and engine. No candidate was retuned or discarded.

`ACCOUNTING.md` records a concrete documentation discrepancy: the predecessor's
table mixes pruned sparse/candidate node counts with the unpruned inherited
online count 76. Uniform pruning gives 43/29/28. Its 425/139/107 operation claim
is unaffected. These operation counts charge the model's explicit `add`, `mul`
and `div` cache misses; they do not measure all CPU work or symbolic-polynomial
primitive operations. See that note for exclusions and unreviewed assumptions.

## Replay

Use the repository's pinned environment (Python 3.13.5, SymPy 1.14.0 here).
From the repository root, set `P=research/b4ba241d-sunset`:

```sh
.venv/bin/python "$P/verify_saved.py"
.venv/bin/python "$P/audit_cost.py" --source . --candidate "$P/fixtures/best.json" --out /tmp/new-sunset-cost
.venv/bin/python -m unittest discover -s tests -p test_kira.py -v
.venv/bin/python -m unittest discover -s tests -p test_two_loop.py -v
.venv/bin/python tools/check_project.py
```

The archive checker requires no native solver. It also rejects drift in the
bound project source, candidate and native inputs. For fresh native execution,
use PR #10's local-build environment (`LD_LIBRARY_PATH` and `FERMATPATH`), copy
no previous native outputs, and run:

```sh
.venv/bin/python "$P/run_native.py" --input research/readiness-20261021/kira/sunset --out /tmp/new-sunset-native --kira PATH-TO-PINNED-KIRA
.venv/bin/python "$P/verify_saved.py" --native /tmp/new-sunset-native
```

Fresh output directories are mandatory. From the package directory, verify all
archived bytes before replay:

```sh
python3 -c 'import hashlib,json,pathlib; h=json.loads(pathlib.Path("HASHES.json").read_text()); assert all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==v for p,v in h.items()); print("PASS",len(h))'
```

`VERIFY.json`, raw outputs, exact comparison, policy traces and logs preserve the
commands, failures and checks. No core checker, formulation, accepted result or
frozen benchmark changed. Credit the preceding sunset donor and project
formulation/checker authors, plus the Kira, Fermat and arithmetic-library authors
and PR #10's native build. This does not establish master minimality, new-family
transfer, published runtime superiority or independent scientific acceptance.
