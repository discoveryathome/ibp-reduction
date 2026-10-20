# Discovery@Home: CPU-scale exact IBP reduction

Can a reusable policy for selecting IBP equations, ordering integrals and elimination,
and sharing intermediate expressions reduce arithmetic cost across multiple families?
The exact setting and cost model are in `docs/formulation.md`. The local experiment
and limitations are in `results/REPORT.md`. The authoritative record is
`discover/frontier.json`, with author-checked evidence only.

The literature frontier includes improved Kira seeding/equation selection, FIRE's
modular and presolve methods, AI-discovered seeding priorities, tube seeding, and
online learned reduction. See `docs/literature.md` for primary sources and conditions.
There is no verified single best policy across all problems. The pilot does not
claim to beat a production solver or generalize to multi-loop systems.

The immediate bottleneck is distinguishing real, transferable reductions in cost
from seed-count proxies, incomplete systems, and special-case tricks. Exact row-operation
certificates and a fixed master basis protect the algebra. Family-level tests and
cache ablations constrain performance claims. A short verification command is:

```
python -m ibp.experiment reproduce
```

Use the interpreter from the local venv. The checker is a separate implementation
but shares SymPy as an arithmetic dependency; no independent human validation has
been completed. Its assumptions and analytic worked examples are in
`docs/verification.md`. Changes to it or to the frontier need particular care.

## Work and acceptance

`discover/catalog.json` is the sole weighted task list. Its tracks cover exact
verification, mature-solver replication, generalization/search, and literature audit.
`discover/priority-log.md` explains the weights. The project picker uses an OS seed
or a supplied 32-hex-digit seed. Cards start with cheap reproducible controls and
fit a 30–60 minute session. Unknown directions are explicitly speculative.

An acceptable performance proposal must include complete exact certificates; fixed
family/basis definitions; baseline and candidate source hashes; all trial results;
search costs; training/test separation; interleaved repeated timings and A/A controls;
expression and memory measurements; and a scoped conclusion. Do not cherry-pick the
best single instance. Report regressions, fallbacks, and failed runs. A source-backed
negative result or a verifier bug with a rejecting regression test is useful work.

Known pitfalls: numerical samples do not prove identities; truncated seed systems
can introduce false extra masters; seed count alone misses expression swell;
cache bookkeeping can erase arithmetic-count gains. The requested paper's
88-versus-92 seed example is not proof of a universal advance. These are settled
acceptance constraints, not reasons to stop exploring.

## Maintainer, review, and credit

The project owner agreed to maintain this pilot on 2026-10-20 and approved MIT code
and CC BY 4.0 documentation. No GitHub identity, review quota, public board, or hub
consent has been assumed. The pilot remains local and unlisted. Proposed contributions
are recorded in local result packages/ledger entries and accepted only after the
owner reviews exact correctness, cost accounting, and the scope of claims.
Public donor intake needs a coordination destination and review capacity first.
Review capacity, rather than donated compute alone, will set the pace.

Record human contributors and disclosed agent assistance in `CONTRIBUTORS.md`;
acknowledge useful replications, negative findings, and checker improvements.
Publication authorship is decided by substantive contribution and explicit agreement,
not promised by running a session. Retain source attribution and commit history.
Code is MIT; project-authored documentation is CC BY 4.0. External source snapshots
retain their upstream licenses and are not relicensed.
