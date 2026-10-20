"""Small first steps for donor cards; read-only, no external calls."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('topic',choices=['suite','search','sources','baseline','review']);args=p.parse_args()
root=Path(__file__).resolve().parents[1]
if args.topic=='suite':
    import sys
    sys.path.insert(0,str(root))
    from ibp.families import NAMES,family,equations,targets
    for name in NAMES:
        f=family(name);print(name,f['split'],'targets',len(targets(f)),'IBP equations (excluding symmetry)',sum(bool(r) for _,_,r in equations(f)),'basis',f['masters'])
elif args.topic=='search':
    f=json.loads((root/'results/frozen.json').read_text());print(json.dumps(f,indent=2))
elif args.topic=='sources':
    print((root/'docs/literature.md').read_text())
elif args.topic=='baseline':
    for row in json.loads((root/'results/summary.json').read_text()):
        if row['method']=='sparse':print(json.dumps(row))
else:
    print((root/'docs/verification.md').read_text())
