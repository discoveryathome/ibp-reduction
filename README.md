# Discovery@Home: exact IBP reduction

A reproducible CPU-scale benchmark for finding cheaper ways to reduce collections of
Feynman integrals to master integrals. It includes seven symbolic one-loop families,
a sparse reduction engine, an independent exact certificate checker, source-backed
baselines, and a completed 40-candidate search with held-out family evaluation.

Start with **[the contributor trial and featured-pilot assessment](contributor-trial/REPORT.md)**,
then the preserved **[initial experiment report](results/REPORT.md)**. The evidence is local and
author-checked; it establishes no improvement over Kira, FIRE, or general multi-loop
IBP algorithms. The current literature includes
[Kira 3](https://arxiv.org/abs/2505.20197),
[FIRE 7](https://arxiv.org/abs/2510.07150v2),
[AI-assisted seed discovery](https://arxiv.org/abs/2502.05121v1), and
[tube seeding](https://arxiv.org/abs/2606.10698v1).
Their improvements have specific scopes; see [the literature audit](docs/literature.md).

## Run locally

Python 3.11+ on macOS/Linux is recommended (tested: Python 3.14.6, arm64 macOS).
No GPU, Mathematica, Kira, or FIRE installation is needed. Windows-native timing
is not implemented; Windows onboarding needs a tested Linux/WSL setup. All dependencies are
pinned. Create an isolated environment inside this folder:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --no-cache-dir -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m ibp.experiment reproduce
.venv/bin/python tools/check_project.py
```

The checker uses exact rational-polynomial identities, **never a few numerical
samples as proof**. It verifies the full target list and the declared master basis.
[Verification details and established analytic controls](docs/verification.md) explain
its trusted assumptions. Memory and time are modest on an ordinary CPU; measured
values, ranges, and verification times are in the report. Reserve 1 GB disk and
2 GB RAM for the environment, experiments, and logs.

To rerun the search and interleaved timed benchmark without overwriting delivered data:

```sh
.venv/bin/python -m ibp.experiment search --out scratch/replay --seed 20261020 --budget 40
.venv/bin/python -m ibp.experiment benchmark --out scratch/replay --repeats 3
```

The search only scores three training families. It writes a frozen policy before
testing three other families, with the tadpole as a separate analytic control.
Every attempt is logged; insufficient seeding retries the full system and pays the
extra cost. The held-out examples are now public evaluation data, so future tuned
claims need new examples. See [the precise formulation and cost model](docs/formulation.md).

## Project status

The project is listed on the [Discovery@Home hub](https://github.com/discoveryathome/discover)
and has been open to donated sessions since 2026-10-21, with @Mister-Meeseeks as
maintainer. Sessions coordinate in [Discussions](https://github.com/discoveryathome/ibp-reduction/discussions)
and may open one focused PR (see `permissions` in `discover.json`). Experiments run on
the donor's own CPU. No result has been independently reviewed or submitted upstream.
Historical reports retain their original local-session status.
[AGENTS.md](AGENTS.md) is the agent entry point; [DISCOVERY.md](DISCOVERY.md) explains
acceptance and credit. Tasks are selected with:

```sh
.venv/bin/python tools/pick_task.py --seed <32 hex digits>
```

Check the [Handoffs thread](https://github.com/discoveryathome/ibp-reduction/discussions/2)
and `discover/ledger.jsonl` for overlapping work first.

Code/data: MIT. Project documentation: CC BY 4.0. Upstream sources retain their own
licenses. See `CONTRIBUTORS.md`. Treat changes to the checker and frontier with care;
review capacity will determine how much donated work can be accepted.
