"""Turn the timed contributor trial into a candid feature-pilot assessment."""
import hashlib,json,math,statistics
from pathlib import Path
p=Path('contributor-trial');rows=json.loads((p/'summary.json').read_text());checks=json.loads((p/'validation.json').read_text());explore=json.loads((p/'exploration.json').read_text());frozen=json.loads((p/'frozen.json').read_text());protocol=json.loads((p/'protocol.json').read_text())
def get(f,m):return next(x for x in rows if x['instance']==f and x['method']==m)
cases=list(dict.fromkeys(x['instance'] for x in rows));new=frozen['new'];baselines=['cached_sparse','cached_tight','initial_learned']
valid=all(c.get('validation',{}).get('valid') for c in checks)
lines=['# Timed contributor trial: featured-pilot assessment','',
'**Recommendation: keep this as a technical pilot; complete mature-solver, multi-loop, and independent-contributor tests before making it a lead feature.** Before making it a headline feature, add a pinned mature-solver baseline, one genuinely multi-loop case, and an independent newcomer/reviewer run. The local experiment provides a credible contribution workflow and a useful demo, but does not yet establish production relevance.','',
'## What was tested','',
'This was a same-author contributor-style trial, not independent onboarding. Its protocol was written before the new experiments. The first part was spent building the candidate, strengthening the rival baseline, and reviewing correctness while the initial benchmark finished. CPU-heavy trial runs followed that benchmark rather than overlapping its timing.','',
f"Start: `{protocol['started_at']}`. See `receipt.json` for the actual finish time and elapsed minutes. Development evaluated {len(explore['trials'])} policies on three previously exposed families, taking {explore['seconds']:.1f} seconds including subprocess startup and counters. The initial 40-policy search is a separate experiment, not part of this candidate-selection budget.",
'',
'The agent-designed change processes input equations online against known pivots and stops once every target has a dependency chain to the fixed basis. It still generates the full initial seed set. It only back-substitutes the required closure. A small schedule search selected a target-intersection-first ordering, shortest-row tiebreak, and dot-first integral priority. This is a classical elimination variant implemented for the pilot, not a claim of inventing a new algebraic algorithm.','',
'Two attempts to explain away the gain were included: give the old solver the same arithmetic cache; and tighten its seed bound by one layer, while keeping all targets unchanged. The tighter bound was insufficient on the evaluated triangle and box cases, triggering a full-system retry. Those failed attempts are included in the cost; fewer initial seeds did not mean less total work.','',
'## Complete evaluation','',
'The massless box is an exposed development regression. The other three mass/kinematic settings were specified before evaluation and were not scored during trial policy selection. These remain one-loop problems with nonnegative target indices; they test neither multi-loop transfer, high-rank numerator targets, nor reconstruction costs.','',
'| Case | Method | Field ops | Nontrivial ops | Median seconds [min, max] | Peak MiB | Max coefficient terms | Fallback |',
'|---|---|---:|---:|---:|---:|---:|---|']
for r in rows:
 if not r['success']:lines.append(f"| {r['instance']} | {r['method']} | failed | | | | | |");continue
 lo,hi=r['reduction_seconds_range']
 lines.append(f"| {r['instance']} | {r['method']} | {r['arithmetic_operations']:,} | {r['nontrivial_arithmetic_operations']:,} | {r['reduction_seconds']:.3f} [{lo:.3f}, {hi:.3f}] | {r['peak_rss_bytes']/2**20:.1f} | {r['max_coefficient_terms']} | {r['fallback']} |")
lines+=['','Nontrivial operations exclude zero/unit/sign/cancellation identities as defined in `notes.md`. This is a sensitivity check, not the selection score. Trial timings include the same extra profiling wrapper for every method; they should not be directly compared with initial-stage timings. Peak RSS includes Python/SymPy imports. Arithmetic counts are deterministic; noisy wall times are measurements.','',
'## Transfer and the strongest rival','',
'| New family | Online ops | Best existing strategy on that case | Its ops | Online change |','|---|---:|---|---:|---:|']
ratios=[];wins=0
for f in new:
 candidate=get(f,'online');best=min((get(f,m) for m in baselines if get(f,m)['success']),key=lambda r:r['arithmetic_operations'])
 if not candidate['success']:lines.append(f'| {f} | failed | {best["method"]} | {best["arithmetic_operations"]} | failure |');continue
 ratio=candidate['arithmetic_operations']/best['arithmetic_operations'];ratios.append(ratio);wins+=ratio<1
 lines.append(f"| {f} | {candidate['arithmetic_operations']:,} | {best['method']} | {best['arithmetic_operations']:,} | {100*(ratio-1):+.1f}% |")
if len(ratios)==len(new):
 gm=math.exp(statistics.mean(math.log(x) for x in ratios));lines+=['',f'Online wins on {wins}/{len(new)} new cases by operation count. Its geometric-mean ratio to the **per-case best** existing strategy is {gm:.4f}. This comparator is an oracle summary, not a deployable single baseline. All cases, including regressions, remain in the table.']
lines+=['','## Can early contributors hill-climb?','',
'**Yes, within this prototype.** Changing the processing schedule moved the training score from essentially no improvement to a substantial decrease. The structural candidate is an understandable code contribution with exact certificates. The cost-accounting review also found and fixed a missing aggregation of failed-attempt cache hits; primary operation scores were unaffected.','',
'**The available scientific headroom is still unknown.** Caching and sensible seeding are established ideas, and the starting solver is new and deliberately small. A large percentage against it does not imply a large percentage against Kira 3 or FIRE 7. Tightening a bound was not uniformly beneficial; the richer algorithm was not uniformly best. That is a real research landscape, but its current hills may be mostly implementation maturity.','',
'## Suitability against the requested criteria','',
'| Criterion | Assessment |','|---|---|',
'| Tangible early progress | Demonstrated local improvements and a concrete accounting fix, with exact checks; a newcomer has not yet been tested. |',
'| Hill climbing | Several meaningful choices change cost, including negative outcomes; retain a ladder of harder, fresh cases to avoid exhausting easy wins. |',
'| Public appeal | Strong scientific connection: make the mathematics behind particle-physics predictions cheaper while keeping the answer exact. The reduction itself is abstract; use a fixed-task before/after demo and a visible rejecting checker. |',
'| Home hardware | Apple M2, 24 GiB installed RAM, CPU only; measured process memory is in the table. This does not need a high-end GPU. Full orchestration includes significant Python startup overhead. |',
'| Agent intelligence | Designing the dependency-completeness check, challenging an easy baseline, and interpreting a regression required reasoning. This single run does not causally prove superiority over random search or expert human tuning. |',
'| Meaningful results | Useful reproducible solver engineering and generalization evidence. New domain-level algorithms, multi-loop gains, and wins against mature solvers remain unestablished. |',
'| Featured launch readiness | Conditional. Good technical pilot or secondary feature now; mature baseline, multi-loop bridge, independent review, and a ready challenge ladder are the gates for leading with it. |',
'',
'## Exact verification','',
f"Separate checker results: {sum(bool(c.get('validation',{}).get('valid')) for c in checks)}/{len(checks)} passed. All methods in the trial receive exact row-DAG checks on every evaluation family. Corrupt-candidate tests and analytic Gamma-function controls are included in the full test suite. The checker is separately implemented but shares SymPy and the stated dimensional-regularization assumptions; it is not a formal proof kernel or an independently authored audit.",
'',
'```sh\npython -m ibp.trial explore --out scratch/contributor-replay\npython -m ibp.trial evaluate --out scratch/contributor-replay\npython tools/check_trial.py\n```','',
'Rerunning the search after seeing these examples does not create new held-out evidence. `frozen.json` hashes the candidate implementation and exploration log; `evaluation-lock.json` binds the tested policy. `next-stage.md` lists launch gates and `public-story.md` gives a claim-safe demo script. No public repository or hub listing was created.']
(p/'REPORT.md').write_text('\n'.join(lines)+'\n')
print('Wrote contributor-trial/REPORT.md; all checks valid:',valid)
