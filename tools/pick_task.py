"""Weighted picker. Seeded hash draws; advisory: a draw doesn't reserve work, so check the Handoffs thread first."""
import argparse,hashlib,json,re,secrets
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--seed');args=p.parse_args()
seed=args.seed or secrets.token_hex(16)
if not re.fullmatch('[0-9a-fA-F]{32}',seed):raise SystemExit('Seed must have 32 hex digits')
root=Path(__file__).resolve().parents[1];catalog=json.loads((root/'discover/catalog.json').read_text())
def draw(label):return int.from_bytes(hashlib.sha256(json.dumps([seed.lower(),label],separators=(',',':')).encode()).digest(),'big')
n=draw('track')%100
for track in catalog['tracks']:
    if n<track['weight']:break
    n-=track['weight']
card=track['tasks'][draw('card')%len(track['tasks'])]
ledger=[json.loads(s) for s in (root/'discover/ledger.jsonl').read_text().splitlines() if s.strip()]
print(json.dumps(dict(seed=seed,track=track['id'],card=card,local_ledger=ledger,intake='open since 2026-10-21; maintainer @Mister-Meeseeks',overlap='Check the Handoffs thread (https://github.com/discoveryathome/ibp-reduction/discussions/2) and discover/ledger.jsonl.'),indent=2))
