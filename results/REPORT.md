# Initial pilot experiment

Local, author-checked evidence only. This is the initial 40-policy experiment, preserved separately from the later timed contributor trial. It is not a comparison against production Kira/FIRE, a FunSearch reproduction, or a new state-of-the-art claim.

## Results

Costs below include failed seed-selection attempts and full-system fallback. Runtime is the median of three fresh, interleaved subprocess reductions, with instrumentation enabled. RSS includes the interpreter and imports.

| Family | Split | Targets / basis | Sparse ops | Learned ops | Ops reduction | Sparse / learned seconds | Sparse / learned peak MiB | Fallback |
|---|---|---:|---:|---:|---:|---:|---:|---|
| tadpole | control | 4 / 1 | 14 | 14 | 0.0% | 0.004 / 0.033 | 60.4 / 60.1 | False |
| bubble_massless | train | 6 / 1 | 85 | 61 | 28.2% | 0.179 / 0.080 | 60.4 / 60.5 | False |
| bubble_equal_mass | train | 9 / 2 | 259 | 102 | 60.6% | 0.226 / 0.184 | 60.4 / 60.3 | False |
| triangle_one_mass | train | 10 / 1 | 523 | 84 | 83.9% | 0.432 / 0.169 | 60.4 / 60.5 | False |
| bubble_unequal_mass | test | 14 / 3 | 518 | 303 | 41.5% | 1.541 / 1.476 | 60.3 / 61.2 | False |
| triangle_offshell | test | 22 / 4 | 2,145 | 327 | 84.8% | 1.581 / 0.346 | 60.8 / 60.6 | False |
| box_massless | test | 65 / 3 | 11,116 | 4,618 | 58.5% | 13.503 / 9.719 | 62.8 / 67.9 | True |

Held-out geometric-mean operation ratio to sparse: **0.3334** (66.7% fewer field operations). This aggregate is not a universal scaling result.

## What actually improved

The frozen policy is `{'order': 'dots', 'reuse': True, 'row': 'complexity', 'seed': 'improved'}`. Search evaluated 40 distinct policies on three training families in 48.5 seconds (including metric collection and logged trials, excluding subsequent certificate validation). The benchmark/validation driver took 1076.1 seconds including interpreter startup and check passes.

The learned restriction does not solve the massless box alone. Its fallback is essential. On that case, removing caching gives 14878 operations versus 11116 for sparse elimination. Therefore the seeding/order combination alone does not generalize as an improvement. A matched cached baseline is needed before attributing the gain to discovery; the contributor trial makes that comparison.

## Expression growth

| Family | Sparse / learned max coefficient terms | Sparse / learned max degree | Sparse / learned peak live entries |
|---|---:|---:|---:|
| tadpole | 5 / 5 | 3 / 3 | 14 / 14 |
| bubble_massless | 5 / 4 | 3 / 2 | 30 / 30 |
| bubble_equal_mass | 7 / 6 | 3 / 3 | 103 / 58 |
| triangle_one_mass | 5 / 4 | 3 / 3 | 140 / 59 |
| bubble_unequal_mass | 59 / 59 | 7 / 7 | 154 / 98 |
| triangle_offshell | 13 / 10 | 4 / 3 | 516 / 170 |
| box_massless | 18 / 14 | 6 / 6 | 2168 / 2166 |

## Timing control

| Family | Sparse A median seconds | Identical A/A median seconds | A/A / A |
|---|---:|---:|---:|
| tadpole | 0.0038 | 0.0500 | 13.063 |
| bubble_massless | 0.1794 | 0.1056 | 0.588 |
| bubble_equal_mass | 0.2257 | 0.2446 | 1.084 |
| triangle_one_mass | 0.4316 | 0.5835 | 1.352 |
| bubble_unequal_mass | 1.5408 | 1.3135 | 0.853 |
| triangle_offshell | 1.5807 | 2.3221 | 1.469 |
| box_massless | 13.5027 | 10.5774 | 0.783 |

Raw min/max ranges, CPU seconds, and process peak RSS are retained in `runs.json` and `summary.json`. Startup is separately timed. The machine was not CPU-isolated; A/A variability limits timing conclusions. No CPU-heavy contributor experiment was intentionally overlapped with this benchmark.

## Exact evidence and reproducibility

The separate validation stage reports 14/14 valid sparse/learned certificates. Training finalist certificates are retained too. Every accepted target is checked as a symbolic identity. Test controls independently reproduce the known Gamma-function bubble and tadpole recurrences and reject corrupt candidates.

```sh
python -m ibp.experiment reproduce
python -m unittest discover -s tests -v
```

`frozen.json` binds the training log; `evaluation-lock.json` binds evaluation methods and the frozen policy. The full run table includes baseline variants and cache ablation. The operation metric counts rational field operations, not underlying polynomial bit operations. See `../docs/formulation.md` for exact exclusions and conventions.

## Donated-session assessment

The search/check loop is cheap enough to support useful 30–60 minute work on ordinary CPUs. A session can test a bounded hypothesis, improve a verifier, or produce an honest negative result. This does not establish that donated agents will repeatedly find novel production-relevant algorithms. These are small one-loop cases and a newly written reference solver. The later contributor trial tests whether the next step survives a stronger baseline and new families.

Full reproduction, especially production-solver integration and genuine multi-loop transfer, remains necessary before a general algorithmic improvement claim. Source audit: `../docs/literature.md`.

## Machine

`macOS-26.6.2-arm64-arm-64bit-Mach-O`; arm64; Python 3.14.6; SymPy 1.14.0; 8 logical CPUs. Runs are single-process reductions; no GPU.
