"""Correct cached-hit reporting in older artifacts; no scores/timings are changed."""
import json
from pathlib import Path
fixed=[]
def update(x):
    if isinstance(x,dict):
        if x.get('fallback') and x.get('accounting_version',1)<2 and 'failed_attempt' in x:
            f=x['failed_attempt'];x['cache_hits']+=f['cache_hits']
            x['cache_entries']=max(x['cache_entries'],f['cache_entries'])
            x['initial_max_coefficient_terms']=max(x['initial_max_coefficient_terms'],f['initial_max_coefficient_terms'])
            x['expression_growth_ratio']=x['max_coefficient_terms']/max(1,x['initial_max_coefficient_terms'])
            x['accounting_version']=2
        for k,v in x.items():
            if k!='failed_attempt':update(v)
    elif isinstance(x,list):
        for v in x:update(v)
for path in [Path('results/runs.json'),Path('results/validation.json'),*Path('results/certificates').glob('*-sparse.json'),*Path('results/certificates').glob('*-learned.json')]:
    if not path.exists():continue
    before=path.read_text();data=json.loads(before);update(data);after=json.dumps(data,indent=2,sort_keys=True)+'\n'
    if before!=after:path.write_text(after);fixed.append(str(path))
print('Normalized reporting only:',fixed)
