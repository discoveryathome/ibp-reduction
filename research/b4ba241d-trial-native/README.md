# Native Kira replication of the three contributor-trial families

Pinned Kira 3.0 reduced all **98 non-master targets** to the **eight prescribed
masters**, with exact rational-polynomial agreement against the three saved
online certificates. Both native `masters` and `masters.final` agree; every log
reports zero unreduced requested integrals. No generated input required correction.

| Existing trial family | Non-master identities | Native masters |
| --- | ---: | ---: |
| bubble_one_mass | 13 | 2 |
| triangle_two_mass | 14 | 2 |
| box_one_mass | 71 | 4 |
| Total | 98 | 8 |

This is **author-checked correctness replication**, pending separate review.
It is not a performance result, basis-minimality result or fresh-family test.
The trial examples were already public. Together with PR #10, native coverage
now includes all ten public one-loop families, in separate scoped receipts.

## Scope, predecessors and the only adapter change

Seed `b4ba241d49ae3adec57309d131c13f06` drew `replication / mature-baseline`.
After the two open matching handoffs were completed in PRs #10 and #11, this
continues that card on the still-unreplicated contributor-trial targets.
[Claim](https://github.com/discoveryathome/ibp-reduction/discussions/2#discussioncomment-19141174).
Base: `9427e928040cd7d71513a443da4a42811720e537`. The person authorized multiple
focused PRs within the original 480-minute session; the 12:02 UTC new-work cutoff
and final-quarter verification reservation remain in force.

The pinned [PR #7](https://github.com/discoveryathome/ibp-reduction/pull/7)
exporter/importer at `d051133ed7c01652e21b53e34fcd5610051705a8` already has generic
geometry logic. Its producer and independently declared checker specifications
already contain these three families. The exporter alone restricts its accepted
name catalogue to the original seven. `trial_kira.py` temporarily extends that
module's allowed-name tuple when requesting one of these three cases, then
restores the original object in `finally`. The producer's original seven-family
list, exporter source, checker, family definitions and all saved results remain
unchanged. Catalog restoration was explicitly checked after each call.

Generated propagators, negative supplied squared masses, full Gram/distance
matrix, generic invariants, dummy external-momentum elimination, seed bounds and
preferred masters are checked against `ibp.validator.SPECS`. The requested targets
must equal the complete saved certificate output set. Input text is also compared
byte-for-byte with the pinned exporter. No invariant is numerically substituted.

The native executable is the pristine Kira 3.0 release build from
[PR #10](https://github.com/discoveryathome/ibp-reduction/pull/10), source
`fb745431f97c8899a512e638da8598b0cfad7521`, without FireFly/FLINT, with one Fermat
7.9b worker on Linux x86_64/GCC 14.2.0. `SOURCES.json` pins the predecessor and
15 source/certificate files, the adapter, and that exact build receipt. Every
native executable/Fermat digest matches the prior receipt, and all ten runtime
library digests were rechecked. This package does not duplicate third-party
build artifacts or the predecessor's unmerged production changes.

## Replay the saved evidence

Use a clean, screened checkout of the pinned predecessor beside this repository,
and the project's pinned Python requirements. From this repository root:

```sh
.venv/bin/python research/b4ba241d-trial-native/trial_kira.py \
  --predecessor ../predecessor --check research/b4ba241d-trial-native/data
python3 -m unittest discover -s research/b4ba241d-trial-native -p test_metadata.py -v
```

The archive command reports three families, 98 exact identities, eight masters
and **12 rejecting controls**: for each family, empty export, missing target,
altered coefficient and altered scalar product must fail. Two metadata tests
also exercise valid sector annotations and reject empty, wrong-family,
wrong-dimension, wrong-sector and duplicate native master entries. The logs in
`logs/` record the successful archived replay and metadata tests.

`data/` retains all 15 exact input files, complete raw stdout/stderr, coefficient
exports, both actual master files and `runs.json`. The original three online
certificates are independently replayed by the unchanged core checker before
comparison. The output checker rejects changed inputs, target sets, master sets,
malformed metadata, incomplete runs and exact coefficient disagreements. Raw
`.log`/`.kira` bytes retain native whitespace under a package-local Git attribute.
`HASHES.json` binds the distributed files.

For a fresh native repeat, follow PR #10's pinned source build recipe, set the
local library path and `FERMATPATH`, then use a new output directory:

```sh
.venv/bin/python research/b4ba241d-trial-native/trial_kira.py \
  --predecessor ../predecessor --out scratch/trial-kira-replay \
  --kira /path/to/locally-built/kira
.venv/bin/python research/b4ba241d-trial-native/trial_kira.py \
  --predecessor ../predecessor --check scratch/trial-kira-replay
```

Each native call has a 180-second timeout and 2 GiB address-space cap per process.
All failures stop the run and are retained. A new output tree is required; no
existing run is overwritten. Delivered source/input controls and all three
native calls passed on their first native attempt; no fallback or pivot was used.

## Resources and limits

`data/runs.json` records actual commands, input/output/certificate/log digests,
return codes, native elapsed/CPU times and maximum individual-process RSS.
The three native calls took 14.350 seconds total, including Kira/Fermat startup
and excluding Python exact checks, input preparation, the prior build and session
work. `wait4` RSS is an individual-process maximum, not aggregate simultaneous
memory. These are single correctness receipts, not benchmark measurements.

Not checked: independent scientific/maintainer review; analytic IBP axioms or
basis minimality; exceptional kinematic limits; other solvers, configurations,
hosts or multi-loop transfer; a performance/A-A comparison or the contributor
trial's operation-cost claims; aggregate RSS or cap exhaustion. Only the online
certificate for each trial family was replayed; the other saved producer-policy
certificates and full historical benchmark were not rerun. The full upstream
Kira/dependency test suites were not run.

The accepted frontier, ledger, core checker, family/formulation files and cost
model were not modified. A separate contributor can next audit the process-local
adapter and input conventions, then repeat these three unchanged configurations
on another source-built host. Success requires all 98 identities and both native
sets of eight masters, rejecting controls and complete fresh receipts.

## Credit

Credit the original contributor-trial families, online certificates, experiments
and independently derived checker; the original pilot and sunset Kira work;
PR #7's exporter/importer; PR #10's source build and arithmetic diagnostic;
the project's contributors and maintainer Doug Colkitt; Kira's developers,
Robert H. Lewis/Fermat and dependency authors. OpenAI Codex performed this
contribution for thakrarsagar. Reusing a separate solver does not constitute an
independent scientific reviewer or acceptance.
