from pathlib import Path
import csv,json,collections
root=Path(__file__).resolve().parent.parent;results=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];d=root/'pass7/audit'/('DOS'+v);p=d/'explicit_model_results.tsv'
 if not p.exists():continue
 now={ (r['entry'],r['model']):r for r in csv.DictReader(p.open(),delimiter='\t')};before={(r['entry'],r['model']):r for r in csv.DictReader((root/'pass6/audit'/('DOS'+v)/'explicit_model_results.tsv').open(),delimiter='\t')};assert now.keys()==before.keys();good=lambda r:r['completed']=='true' and r['C_available']=='true';assert all(good(now[k])==good(before[k]) for k in before)
 a=list(csv.DictReader((d/'instructions.tsv').open(),delimiter='\t'));b=list(csv.DictReader((root/'pass6/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));assert [(r['address'],r['bytes']) for r in a]==[(r['address'],r['bytes']) for r in b]
 typed=list(csv.DictReader((root/'pass7/evidence'/('DOS'+v)/'types/typed_functions.tsv').open(),delimiter='\t'));assert len(typed)==3 and typed[0]['storage']=='DX:2,AX:2' and typed[1]['storage']=='AL:1';assert 'length=54' in (root/'pass7/evidence'/('DOS'+v)/'types/header_type.txt').read_text()
 results.append(dict(build=v,functions=len(now)//2,stock_completed=sum(good(r) for r in now.values() if r['model']=='stock'),explicit_completed=sum(good(r) for r in now.values() if r['model']!='stock'),typed_functions=typed,unchanged_instructions=len(a)))
(root/'pass7/evidence/validation.json').write_text(json.dumps(results,indent=2));print([(r['build'],r['stock_completed'],r['explicit_completed']) for r in results])
