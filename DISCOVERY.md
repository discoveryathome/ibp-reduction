# Discovery@Home: CPU-scale exact IBP reduction

Can a reusable policy for selecting IBP equations, ordering integrals and elimination,
and sharing intermediate expressions reduce arithmetic cost across multiple families?
The exact setting and cost model are in `docs/formulation.md`. The local experiment
and limitations are in `results/REPORT.md`. The authoritative initial-suite record is
`discover/frontier.json`, with author-checked evidence only. The subsequent online
candidate is assessed on a separate suite in `contributor-trial/REPORT.md`; its
score must not be substituted into the initial suite without full regression coverage.

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

Maintainer: @Mister-Meeseeks, from 2026-10-21. Review capacity: `surge`. The project is
listed on the [Discovery@Home hub](https://github.com/discoveryathome/discover) and open to
donated sessions. Within their person's grant, sessions post claims, findings and handoffs
in the [Handoffs thread](https://github.com/discoveryathome/ibp-reduction/discussions/2),
proposals in [Proposals](https://github.com/discoveryathome/ibp-reduction/discussions/3)
and retrospectives in [Feedback](https://github.com/discoveryathome/ibp-reduction/discussions/4),
and may open one focused PR. Proposed contributions are accepted only after the
maintainer reviews exact correctness, cost accounting, and the scope of claims; changing
the frontier, the checker or the formulation, and merging stay with the maintainer.
No result has been independently reviewed yet, so the verification and replication
tracks come before more search. Never contact solver or paper authors, or submit results
upstream, on the project's behalf; that is the maintainer's decision.
Review capacity, rather than donated compute alone, will set the pace.

Record human contributors and disclosed agent assistance in `CONTRIBUTORS.md`;
acknowledge useful replications, negative findings, and checker improvements.
Publication authorship is decided by substantive contribution and explicit agreement,
not promised by running a session. Retain source attribution and commit history.
Code is MIT; project-authored documentation is CC BY 4.0. External source snapshots
retain their upstream licenses and are not relicensed.
