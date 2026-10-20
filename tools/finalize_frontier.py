"""Record scoped initial evidence and hashes; does not assert maintainer acceptance."""
import hashlib,json
from pathlib import Path
rows=json.loads(Path('results/summary.json').read_text())
checks=json.loads(Path('results/validation.json').read_text())
assert all(c.get('validation',{}).get('valid') for c in checks),'Do not finalize failed checks'
files=['ibp/families.py','ibp/reducer.py','ibp/validator.py','ibp/experiment.py','results/frozen.json','results/search.json','results/evaluation-lock.json','results/runs.json','results/summary.json','results/validation.json','requirements.txt']
frontier={
 'schema':'discover-frontier/v0','statement':'Seven one-loop families are reduced to fixed conventional master bases with exact algebraic certificates. A frozen 40-candidate search lowers field-operation counts on three held-out families relative to this pilot sparse implementation; no production-solver or multi-loop superiority is claimed.',
 'status':'Local pilot; author-checked, awaiting independent and maintainer review',
 'evidence_level':['author-checked'],'claim_kind':['exact','measured'],
 'scope':'ibp-one-loop-v1; exact Q(d,s,t,m,u) identities under dimensional-regularization IBP/scaleless axioms; instrumented Python costs on Apple M2, macOS arm64; public family-level held-out tests, not sealed evaluation.',
 'review':'DISCOVERY.md','updated_on':'2026-10-20',
 'formulation':{'id':'ibp-one-loop-v1','doc':'docs/formulation.md','since':'2026-10-20'},
 'sources':['https://arxiv.org/abs/2502.05121v1','https://arxiv.org/abs/2505.20197v1','https://arxiv.org/abs/2510.07150v2','https://arxiv.org/abs/2606.10698v1','https://arxiv.org/abs/1712.09215','results/REPORT.md'],
 'assumptions':[{'id':'ibp-axioms','statement':'Dimensional regularization, scaleless zeros, and change-of-variable invariance; generic kinematics away from poles.','status':'open','link':'docs/formulation.md'},{'id':'basis-minimality','statement':'Certificates prove reduction to the specified basis, not global master minimality; external audit remains open.','status':'open','link':'docs/verification.md'},{'id':'mature-comparison','statement':'No Kira 3/FIRE 7 execution or multi-loop transfer established.','status':'open','link':'docs/literature.md'}],
 'suite':{'path':'results/runs.json','format':'json','objective':'Executed rational-function field operations, including failed seed attempts','direction':'lower-is-better','current':'learned','baselines':[{'method':'sparse','strength':'starter','source':'ibp/reducer.py'},{'method':'laporta','strength':'starter','source':'https://arxiv.org/abs/hep-ph/0102033'},{'method':'improved','strength':'starter','source':'https://arxiv.org/abs/2502.05121v1'}],'instances':{'draw':'fixed','count':7,'dev':'docs/formulation.md','note':'Three training, three held-out, one analytic control. All are now exposed; future tuning requires fresh test cases.'},'budget':{'unit':'candidate policies','amount':40,'note':'Training-only evolutionary selection; each timed evaluation has 90s timeout.'},'evaluate':['python','-m','ibp.experiment','reproduce'],'evaluate_minutes':5},
 'reproduce':'python -m ibp.experiment reproduce','reproduce_full':'python -m ibp.experiment search --out scratch/replay && python -m ibp.experiment benchmark --out scratch/replay','reproduce_minutes':5,'prerequisites':['Python 3.11+ (tested 3.14.6)','pip install -r requirements.txt','macOS/Linux for resource-based memory metrics'],
 'artifacts':[{'path':p,'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest(),'role':'frozen input, implementation, or evidence'} for p in files]
}
Path('discover/frontier.json').write_text(json.dumps(frontier,indent=2)+'\n')
print('Wrote author-checked initial frontier')
