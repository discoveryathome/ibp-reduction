"""Offline protocol-schema, artifact hash, frozen-input, and result consistency checks."""
import hashlib,json
from pathlib import Path
import jsonschema
root=Path(__file__).resolve().parents[1]
for target,schema in [('discover.json','manifest'),('discover/catalog.json','catalog'),('discover/frontier.json','frontier')]:
    value=json.loads((root/target).read_text());definition=json.loads((root/'research'/f'{schema}.schema.json').read_text())
    jsonschema.Draft202012Validator(definition,format_checker=jsonschema.FormatChecker()).validate(value)
catalog=json.loads((root/'discover/catalog.json').read_text())
assert sum(t['weight'] for t in catalog['tracks'])==100
frontier=json.loads((root/'discover/frontier.json').read_text())
for a in frontier.get('artifacts',[]):
    assert hashlib.sha256((root/a['path']).read_bytes()).hexdigest()==a['sha256'],a['path']
frozen=json.loads((root/'results/frozen.json').read_text());lock=json.loads((root/'results/evaluation-lock.json').read_text())
assert hashlib.sha256((root/'results/frozen.json').read_bytes()).hexdigest()==lock['frozen_sha256']
assert hashlib.sha256((root/'results/search.json').read_bytes()).hexdigest()==frozen['search_sha256']
assert set(frozen['training']).isdisjoint(frozen['held_out'])
assert lock['methods']['learned']==frozen['policy']
print('PASS: protocol schemas, track weights, artifact hashes, and frozen evaluation binding')
