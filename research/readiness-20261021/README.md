# Feynman integral reduction: second-cohort preparation

Local preparation authorized by the project coordinator on 2026-10-21. Evidence is
**author-checked**; outside scientific review and public intake approval are pending.
No external contact, hub submission, or new reviewer consent is implied.

## Prepared work

A separately versioned two-loop equal-mass vacuum sunset includes nine reduced targets, including numerator insertions. Sparse and online reducers emit exact row-operation certificates. The checker derives the four directional IBPs separately; analytic scaling and factorized numerator controls plus negative mutations are checked. Production-solver preparation is recorded separately in the Kira package.

The machine-readable portfolio is [`two-loop-results.json`](two-loop-results.json).
Historical experiments retain their original exposure and evidence labels. These
preparation cases are now exposed development material, not a sealed test set.

## First contributor step

Activate the repository's documented Python environment, then run from its root:

```sh
python -m ibp.validator research/readiness-20261021/two-loop-online.json
```

Generic symbolic d and nonzero squared mass m. Euclidean D1=k1^2+m, D2=k2^2+m, D3=(k1-k2)^2+m; dimensional regularization, scaleless zeros, S3 changes of integration variables. Master minimality is not proved. This small symmetric family does not establish transfer to general scattering integrals.

Before searching, read the portfolio and select one bounded task. Preserve the
starting witness, source hashes, seed and budget. Reserve time to verify the final
artifact. Record unsuccessful runs. A useful handoff can be a replication, a
reproducible defect, a bounded negative finding, or an improvement under the same
formulation; identify which one it is. Passing a local check does not imply novelty
or independent acceptance.

## Outside review

[REVIEW.md](REVIEW.md) contains concrete questions; [review.json](review.json) is an
unfilled review receipt. Review must identify a commit and exact artifact hashes.
The person reproducing a result should disclose any involvement in its creation.

## Independent contributor trial protocol

Choose a task using the refreshed catalogue and give a new contributor only the
published instructions. Record setup time, time to first valid artifact, total
compute, failed attempts and reviewer minutes. Start from the inherited frontier.
Freeze algorithm submissions before evaluating on a separately prepared unseen
case pool. Author-run smoke checks here do not count as independent trials.

Remaining gates:

- Independent physics/checker review.
- Representative multi-loop problem selection.
- Independent contributor trial; production-solver comparison status in Kira report.

## Completed external-solver cross-check

Kira 3.0 reduces the same nine targets to the same two masters. Both local
certificates match every exported coefficient exactly. The [Kira package](kira/README.md)
contains inputs, raw output, source/build bindings, a fail-closed comparison command
and the Apple Silicon modular-arithmetic issue found during setup. The tested
upstream integer path resolves the local failure; release runs with empty output
are explicitly retained as failures. This is same-author software cross-validation,
not a human review or a production performance comparison.

The 16 historical trial certificates also replay successfully. Their original
source files are preserved byte-for-byte under `contributor-trial/source-snapshot`,
so extending the live family dispatcher does not rewrite historical timing evidence.
