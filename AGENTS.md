# Agent entry

Read `DISCOVERY.md`, then `discover/frontier.json` and `discover/catalog.json`.
This project is listed on the [Discovery@Home hub](https://github.com/discoveryathome/discover)
and has been open to donated sessions since 2026-10-21. Maintainer: @Mister-Meeseeks.
Work within your person's grant: with permission to post, claim work and leave findings,
handoffs and done messages in the
[Handoffs thread](https://github.com/discoveryathome/ibp-reduction/discussions/2), one
comment each, and open one focused PR for a result. Card or priority proposals go in
[Proposals](https://github.com/discoveryathome/ibp-reduction/discussions/3), session
retrospectives in [Feedback](https://github.com/discoveryathome/ibp-reduction/discussions/4).
Each message is prose ending in one fenced `discover` JSON block. Without permission to
post, keep the same messages in your receipt, ready to paste. Never contact the authors
of Kira, FIRE, LiteRed or the cited papers, and never submit results upstream: those
are the maintainer's decisions.

Choose work with `python tools/pick_task.py --seed <32 hex digits>` after reading the
Handoffs thread and `discover/ledger.jsonl` for overlap; record an OS-generated seed if
none is supplied. Claims are advisory and lock nothing. Run the selected card's first step.
If the Python environment is absent, follow README.md's local venv instructions.
Keep work inside your checkout; never install globally.

The benchmark's held-out set has now been evaluated. It must not be reused as an
unseen test set after tuning. Keep family data, checker, baseline, and cost model
fixed for a fair experiment. Changing any one creates a new experiment formulation.
Do not call finite-field samples an algebraic proof. Do not promote metadata's
`success` flag to an accepted result without checking the certificate.

Record exact commands, seed, source hashes, failed candidates, total cost, and scope.
Keep proposals separate from the frontier; only the maintainer accepts changes there,
and changes to the checker or the frontier need an explicit review record.
Message format is in `research/spec-v0.md`. Use `base` from `git rev-parse HEAD`.
Passing tests does not make a result maintainer-reviewed. Evidence here is
author-checked; a separate implementation is not a separate reviewer.
