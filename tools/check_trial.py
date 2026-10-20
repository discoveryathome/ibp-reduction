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
checks=json.loads((p/'validation.json').read_text())
assert len(checks)==len(lock['cases'])*len(lock['methods'])
start=time.perf_counter();n=0
for f in lock['cases']:
 for method in lock['methods']:
  result=check(json.loads((p/'certificates'/f'{f}-{method}.json').read_text()))
  if not result['valid']:raise ValueError(result)
  print(f,method,result['identities'],'exact identities',flush=True);n+=1
print(f'PASS: {n} trial certificates; frozen bindings; {time.perf_counter()-start:.2f} seconds')
