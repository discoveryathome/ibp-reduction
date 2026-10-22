"""Recheck frozen trial bindings and every final trial certificate exactly."""
import hashlib,json,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from ibp.validator import check
p=root/'contributor-trial';frozen=json.loads((p/'frozen.json').read_text());lock=json.loads((p/'evaluation-lock.json').read_text())
assert hashlib.sha256((p/'frozen.json').read_bytes()).hexdigest()==lock['frozen_sha256']
assert hashlib.sha256((root/'ibp/contributor.py').read_bytes()).hexdigest()==frozen['code_sha256']
assert hashlib.sha256((p/'exploration.json').read_bytes()).hexdigest()==frozen['exploration_sha256']
assert set(frozen['dev']).isdisjoint(frozen['new'])
source_lock=json.loads((p/'source-lock.json').read_text())
for name,expected in source_lock['files'].items():
 # Historical timings belong to the frozen source, not the evolving checkout.
 assert hashlib.sha256((p/'source-snapshot'/name).read_bytes()).hexdigest()==expected,name
raw=json.loads((p/'runs.json').read_text());summary=json.loads((p/'summary.json').read_text())
for row in raw:
 assert row['success'],row
 assert row['arithmetic_operations']==row['trivial_arithmetic_operations']+row['nontrivial_arithmetic_operations']
 assert row['attempted_operations']==row['arithmetic_operations']+row['cache_hits']
for row in summary:
 matching=[x for x in raw if x['instance']==row['instance'] and x['method']==row['method']]
 assert len(matching)==lock['repeats']
 assert all(x['arithmetic_operations']==row['arithmetic_operations'] for x in matching)
 cert=json.loads((p/'certificates'/f"{row['instance']}-{row['method']}.json").read_text())
 assert cert['metrics']['arithmetic_operations']==row['arithmetic_operations']
checks=json.loads((p/'validation.json').read_text())
assert len(checks)==len(lock['cases'])*len(lock['methods'])
start=time.perf_counter();n=0
for f in lock['cases']:
 for method in lock['methods']:
  result=check(json.loads((p/'certificates'/f'{f}-{method}.json').read_text()))
  if not result['valid']:raise ValueError(result)
  print(f,method,result['identities'],'exact identities',flush=True);n+=1
print(f'PASS: {n} trial certificates; frozen bindings; {time.perf_counter()-start:.2f} seconds')
