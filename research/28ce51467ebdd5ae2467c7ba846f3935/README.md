# One-loop Kira replication bridge

Outcome: **tooling / partial replication preparation**, author-checked. No native
Kira or FIRE execution, solver timing, or new accepted physics result is reported.

Session seed: `28ce51467ebdd5ae2467c7ba846f3935`. Base:
`9427e928040cd7d71513a443da4a42811720e537`, catalogue priority revision 2.
The project picker draws **replication / mature-baseline**. The Handoffs discussion
had no open replication request; its sunset handoff requested verification instead.
The card's first step, `python tools/inspect_task.py baseline`, returned all seven
sparse baseline records. Kira and FIRE were absent from this host, so this session
refines the card to its export-and-compare preparation step.

## Scope and use

`tools/export_kira_one_loop.py` produces a separate Kira project for every frozen
one-loop family. It preserves propagator order, symbolic masses and invariants,
target coverage, and the prescribed master list. It writes JSON syntax in `.yaml`
files (a YAML subset) without introducing a YAML dependency. It refuses to replace
an existing output directory. It does not run or download a solver.

From the repository root, using the pinned dependencies in `requirements.txt`:

```sh
.venv/bin/python tools/export_kira_one_loop.py --out scratch/kira-one-loop
.venv/bin/python -m unittest discover -s tests -p 'test_kira*.py' -v
```

The generated tree has 35 input files and a manifest binding their hashes and the
local source/certificate hashes. It requests 115 non-master identities: tadpole 3,
massless bubble 5, equal-mass bubble 7, one-mass triangle 9, unequal-mass bubble 11,
off-shell triangle 18, and massless box 62. The 15 prescribed masters are listed
separately: their reductions to themselves are trivial. This covers all 130 frozen
non-scaleless targets without changing the family or basis.

On a separately screened installation of Kira 3.0 at
`fb745431f97c8899a512e638da8598b0cfad7521`, run each generated project from its own
directory. For example:

```sh
(cd scratch/kira-one-loop/tadpole && kira --parallel=1 jobs.yaml)
.venv/bin/python tools/check_kira.py \
  --certificate results/certificates/tadpole-sparse.json \
  --export scratch/kira-one-loop/tadpole/results/tadpole/kira_targets.kira
```

Repeat with each family name. Record the actual source/build/executable hashes,
compiler, architecture, arithmetic backend, runtime resources and full logs. A
zero process status or an empty export is insufficient. Inspect Kira's resulting
master list: `preferred_masters` expresses a preference, not a guarantee. The
comparison rejects wrong families, different target sets, a different basis in
the exported rows, duplicate entries, and altered exact coefficients. It first
replays the local certificate through the unchanged exact checker. The existing
no-argument sunset comparison remains available.

## Algebra and pinned source conventions

For local `D_i=(k+r_i)^2+m_i`, choose `r_0=0` and independent shifts `r_i=p_i`.
Supply Kira propagators `[k,-m_0]`, `[k+p_i,-m_i]`: Kira subtracts the supplied
mass-squared expression. Thus the algebra agrees directly, with no additional
Wick-rotation or index-dependent signs. All masses are already squared masses.

Set `p_i.p_j=(S_0i+S_0j-S_ij)/2` for every independent unordered pair. Declare
only the used invariant/mass symbols, each of mass dimension two. Non-vacuum
families include outgoing `q` with `q=p_1+...+p_(n-1)`; eliminating only this dummy
momentum leaves every shift independent. The vacuum tadpole has no external
momenta. No invariant is set to one or sampled numerically.

Use top sector `2^n-1`, `r=rmax`, and `s=1`. These specify a Kira seed region;
they do not assert identical selected equations, costs, or sufficient reduction
in a native run. Kira and local elimination policies may differ.

Local certificate rows have `target + sum(c*master)=0`; the Kira text export has
`-target + sum(C*master)=0`. The comparison checks `C=-c` as an exact rational
identity in `d,s,t,m,u`. The allowed-expression parser remains restricted to
integer/rational arithmetic and those symbols, and now rejects zero divisors
before simplification can hide them.

Pinned primary sources consulted:

- [Kira YAML initialization and propagator construction](https://gitlab.com/kira-pyred/kira/-/blob/fb745431f97c8899a512e638da8598b0cfad7521/src/kira/ReadYamlFiles.cpp)
- [Kira configuration, selection and export parser](https://gitlab.com/kira-pyred/kira/-/blob/fb745431f97c8899a512e638da8598b0cfad7521/src/kira/ReadYamlFiles.h)
- [Kira seed bounds and preferred-master semantics](https://gitlab.com/kira-pyred/kira/-/blob/fb745431f97c8899a512e638da8598b0cfad7521/doc/kira-1.2-releasenotes/releasenotes.tex)

## Evidence and limitations

The new tests reconstruct mass and distance conventions against the checker's
separately declared family specifications and compare synthetic Kira-format text
against the saved exact certificates. Synthetic text is explicitly generated from
local certificate rows: these are interface and rejection controls, **not external
solver evidence**. The saved sunset Kira export remains a real predecessor fixture.
`VERIFY.json` lists replay commands; `SOURCES.json` binds inputs and generated files.

Final local checks passed: 29 unit tests; all 17 original exact certificates and
deterministic sparse/learned costs on seven families; both nine-identity sunset
comparisons; protocol/frontier integrity; and all 19 recorded source digests,
35 generated input digests, and the generated manifest's 12 source bindings.
The analytic tadpole CLI control uses the gamma-function recurrence independently
of the row serializer. Two algebraically-zero-denominator rejection controls
failed before the importer fix and passed afterwards. Delegated review found an
unfinished provenance receipt; the final receipt and regenerated manifest now
match the files. No other actionable correctness finding remained.

The core checker, family definitions, frozen data, baseline cost model, and frontier
are unchanged. Native Kira YAML parsing, reduction completeness, preferred-master
selection and exported formatting for these seven new configurations still need
execution. Master minimality, analytic IBP/scaleless assumptions, multi-loop
transfer, fresh-family generalization, and production speed were not checked.
This remains author-checked AI-assisted work, including its delegated checks.

A read-only screen found five pre-existing mismatches in
`research/readiness-20261021/manifest.json` for `DISCOVERY.md`, `README.md`,
`discover/catalog.json`, `discover/frontier.json`, and `discover/priority-log.md`.
The authoritative frontier's 11 artifact hashes matched. This session does not
repair or reinterpret either record.

## Open next questions

- **Question:** Do the seven generated projects reduce natively with the pinned
  Kira build and prescribed basis? **Why it matters:** algebra/export controls
  cannot establish actual solver behavior. **First step:** run the tadpole, then
  the other six projects, and compare every export with the command above.
  **Blocked by:** an available screened Kira installation with a working backend.
  **Success test:** all 115 non-master identities match, the actual master sets
  match, and the complete source/build/input/output receipts are retained. Keep
  failures and report any seed/basis adjustment as a new configuration.
- **Question:** Which preparation manifest hashes should the maintainer refresh?
  **Why it matters:** stale pins obscure replay status. **First step:** compare the
  five named paths with the preparation manifest at this base. **Blocked by:**
  maintainer review of historical provenance; this contribution changes no record.

## Predecessor credit

This extends the project's existing `tools/check_kira.py`, saved sunset Kira
export/configuration, and arithmetic-diagnostic work in
`research/readiness-20261021/kira/`, all pinned at the base above. It also relies on
the original one-loop families, exact certificate checker and saved sparse
certificates. Credit belongs to their existing contributors, including the
initialization's OpenAI Codex work and maintainer Doug Colkitt (@Mister-Meeseeks).
Kira and its authors retain credit for the external solver and its documentation.
The prior sunset policy handoff was inspected for overlap; its proposed 107-operation
candidate was neither copied nor newly verified here.

This donation was performed by OpenAI Codex for @thakrarsagar, with delegated
source, test and review assistance. It is not independent human or maintainer review.
