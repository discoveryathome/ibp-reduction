"""Export a static public-demo SVG from checked contributor-trial evidence."""
import html,json
from pathlib import Path
p=Path('contributor-trial');rows=json.loads((p/'summary.json').read_text());checks=json.loads((p/'validation.json').read_text());assert all(x.get('validation',{}).get('valid') for x in checks)
cases=['bubble_one_mass','triangle_two_mass','box_one_mass'];names=['One-mass bubble','Two-mass triangle','One-mass box']
methods=['cached_sparse','cached_tight','initial_learned'];data=[]
for f,label in zip(cases,names):
 online=next(x for x in rows if x['instance']==f and x['method']=='online')
 prior=min((x for x in rows if x['instance']==f and x['method'] in methods),key=lambda x:x['arithmetic_operations'])
 data.append((label,online,prior))
width,height=960,460;left=245;plotwidth=590;top=80;scale=plotwidth/200
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
'<title id="title">Same integrals, exact answers, different amounts of work</title>',
'<desc id="desc">Three new one-loop families, comparing online elimination with the lowest-operation prior strategy on each case. A lower bar is better. The triangle is a regression, retained in the results.</desc>',
'<rect width="960" height="460" fill="#fff"/>',
'<g font-family="Helvetica" fill="#152536">',
'<text x="24" y="34" font-size="23" font-weight="600">Can an agent find a shorter calculation?</text>',
'<text x="24" y="59" font-size="14">Exact algebra checked • new one-loop families • this prototype, not production Kira/FIRE</text>']
for tick in [0,50,100,150,200]:
 x=left+tick*scale;parts.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="370" stroke="#d7dde3"/>');parts.append(f'<text x="{x}" y="393" text-anchor="middle" font-size="13">{tick}%</text>')
for i,(label,new,old) in enumerate(data):
 y=105+i*96;ratio=100*new['arithmetic_operations']/old['arithmetic_operations'];delta=ratio-100
 parts += [f'<text x="24" y="{y+7}" font-size="17">{html.escape(label)}</text>',f'<text x="24" y="{y+29}" font-size="13">{new["targets"]} integrals → {new["masters"]} masters</text>',
 f'<rect x="{left}" y="{y-10}" width="{100*scale}" height="17" fill="#b8c1c9"/>',
 f'<text x="{left+100*scale+7}" y="{y+3}" font-size="12">{old["arithmetic_operations"]:,} prior</text>',
 f'<rect x="{left}" y="{y+16}" width="{ratio*scale}" height="20" fill="{"#9d4a29" if delta>0 else "#176868"}"/>',
 f'<text x="{left+ratio*scale+7}" y="{y+31}" font-size="12">{new["arithmetic_operations"]:,} ({delta:+.1f}%)</text>']
parts+=['<text x="540" y="418" text-anchor="middle" font-size="14">Field operations relative to the best prior strategy on each case</text>',
'<text x="24" y="446" font-size="12">Gray: best prior strategy on that case (oracle comparison). Color: frozen online method. All regressions shown.</text>','</g></svg>']
(p/'demo.svg').write_text('\n'.join(parts)+'\n');print('Wrote contributor-trial/demo.svg')
