# Agent entry

Read `DISCOVERY.md`, then `discover/frontier.json` and `discover/catalog.json`.
This is a LOCAL Discovery@Home pilot. No GitHub repository, board, or hub consent
exists. Do not publish or contact anyone. Maintainer: the project owner, who agreed
in the initialization conversation on 2026-10-20; review capacity is undeclared.

Use the task picker in `tools/pick_task.py` with an executed random seed. Inspect
`discover/ledger.jsonl` for overlapping work before beginning. It is a local ledger,
not a live distributed coordination service. Run the selected card's first step.
If the Python environment is absent, follow README.md's local venv instructions.
Keep work inside this session folder; never install globally.

The benchmark's held-out set has now been evaluated. It must not be reused as an
unseen test set after tuning. Keep family data, checker, baseline, and cost model
fixed for a fair experiment. Changing any one creates a new experiment formulation.
Do not call finite-field samples an algebraic proof. Do not promote metadata's
`success` flag to an accepted result without checking the certificate.

Record exact commands, seed, source hashes, failed candidates, total cost, and scope.
Keep proposals separate from the frontier; only the maintainer accepts changes there.
A local finding or handoff ends with a fenced `discover` JSON message, as described
in `research/spec-v0.md`. Use `base` from `git rev-parse HEAD`; `local-only` evidence
for session messages. Passing tests does not make a result maintainer-reviewed.
