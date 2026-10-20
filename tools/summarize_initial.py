"""Generate a reviewable report from the frozen initial experiment's measured data."""
import json,math,statistics
from pathlib import Path
r=Path('results');rows=json.loads((r/'summary.json').read_text());machine=json.loads((r/'machine.json').read_text());search=json.loads((r/'search.json').read_text());frozen=json.loads((r/'frozen.json').read_text());checks=json.loads((r/'validation.json').read_text())
def get(f,m):return next(x for x in rows if x['instance']==f and x['method']==m)
families=list(dict.fromkeys(x['instance'] for x in rows))
lines=['# Initial pilot experiment','',
'Local, author-checked evidence only. This is the initial 40-policy experiment, preserved separately from the later timed contributor trial. It is not a comparison against production Kira/FIRE, a FunSearch reproduction, or a new state-of-the-art claim.','',
'## Results','',
'Costs below include failed seed-selection attempts and full-system fallback. Runtime is the median of three fresh, interleaved subprocess reductions, with instrumentation enabled. RSS includes the interpreter and imports.','',
'| Family | Split | Targets / basis | Sparse ops | Learned ops | Ops reduction | Sparse / learned seconds | Sparse / learned peak MiB | Fallback |',
'|---|---|---:|---:|---:|---:|---:|---:|---|']
for f in families:
 a,b=get(f,'sparse'),get(f,'learned')
 if not(a['success'] and b['success']):lines.append(f'| {f} | | | | | failed | | | |');continue
 lines.append(f"| {f} | {a['split']} | {a['targets']} / {a['masters']} | {a['arithmetic_operations']:,} | {b['arithmetic_operations']:,} | {100*(1-b['arithmetic_operations']/a['arithmetic_operations']):.1f}% | {a['reduction_seconds']:.3f} / {b['reduction_seconds']:.3f} | {a['peak_rss_bytes']/2**20:.1f} / {b['peak_rss_bytes']/2**20:.1f} | {b['fallback']} |")
test=frozen['held_out'];ratio=math.exp(statistics.mean(math.log(get(f,'learned')['arithmetic_operations']/get(f,'sparse')['arithmetic_operations']) for f in test))
lines+=['',f'Held-out geometric-mean operation ratio to sparse: **{ratio:.4f}** ({100*(1-ratio):.1f}% fewer field operations). This aggregate is not a universal scaling result.','',
'## What actually improved','',
f"The frozen policy is `{frozen['policy']}`. Search evaluated {len(search['trials'])} distinct policies on three training families in {search['seconds']:.1f} seconds (including metric collection and logged trials, excluding subsequent certificate validation). The benchmark/validation driver took {machine['seconds']:.1f} seconds including interpreter startup and check passes.",
'',
'The learned restriction does not solve the massless box alone. Its fallback is essential. On that case, removing caching gives '+str(get('box_massless','learned_no_reuse')['arithmetic_operations'])+' operations versus '+str(get('box_massless','sparse')['arithmetic_operations'])+' for sparse elimination. Therefore the seeding/order combination alone does not generalize as an improvement. A matched cached baseline is needed before attributing the gain to discovery; the contributor trial makes that comparison.','',
'## Expression growth','',
'| Family | Sparse / learned max coefficient terms | Sparse / learned max degree | Sparse / learned peak live entries |',
'|---|---:|---:|---:|']
for f in families:
 a,b=get(f,'sparse'),get(f,'learned')
 lines.append(f"| {f} | {a['max_coefficient_terms']} / {b['max_coefficient_terms']} | {a['max_polynomial_degree']} / {b['max_polynomial_degree']} | {a['peak_live_nnz']} / {b['peak_live_nnz']} |")
lines+=['','## Timing control','',
'| Family | Sparse A median seconds | Identical A/A median seconds | A/A / A |','|---|---:|---:|---:|']
for f in families:
 a,b=get(f,'sparse'),get(f,'sparse_AA');lines.append(f"| {f} | {a['reduction_seconds']:.4f} | {b['reduction_seconds']:.4f} | {b['reduction_seconds']/a['reduction_seconds']:.3f} |")
lines+=['','Raw min/max ranges, CPU seconds, and process peak RSS are retained in `runs.json` and `summary.json`. Startup is separately timed. The machine was not CPU-isolated; A/A variability limits timing conclusions. No CPU-heavy contributor experiment was intentionally overlapped with this benchmark.','',
'## Exact evidence and reproducibility','',
f"The separate validation stage reports {sum(bool(c.get('validation',{}).get('valid')) for c in checks)}/{len(checks)} valid sparse/learned certificates. Training finalist certificates are retained too. Every accepted target is checked as a symbolic identity. Test controls independently reproduce the known Gamma-function bubble and tadpole recurrences and reject corrupt candidates.",
'',
'```sh\npython -m ibp.experiment reproduce\npython -m unittest discover -s tests -v\n```','',
'`frozen.json` binds the training log; `evaluation-lock.json` binds evaluation methods and the frozen policy. The full run table includes baseline variants and cache ablation. The operation metric counts rational field operations, not underlying polynomial bit operations. See `../docs/formulation.md` for exact exclusions and conventions.','',
'## Donated-session assessment','',
'The search/check loop is cheap enough to support useful 30–60 minute work on ordinary CPUs. A session can test a bounded hypothesis, improve a verifier, or produce an honest negative result. This does not establish that donated agents will repeatedly find novel production-relevant algorithms. These are small one-loop cases and a newly written reference solver. The later contributor trial tests whether the next step survives a stronger baseline and new families.','',
'Full reproduction, especially production-solver integration and genuine multi-loop transfer, remains necessary before a general algorithmic improvement claim. Source audit: `../docs/literature.md`.','',
'## Machine','',f"`{machine['platform']}`; {machine['machine']}; Python {machine['python'].split()[0]}; SymPy {machine['sympy']}; {machine['cpu_count']} logical CPUs. Runs are single-process reductions; no GPU."]
(r/'REPORT.md').write_text('\n'.join(lines)+'\n')
print('Wrote results/REPORT.md')
