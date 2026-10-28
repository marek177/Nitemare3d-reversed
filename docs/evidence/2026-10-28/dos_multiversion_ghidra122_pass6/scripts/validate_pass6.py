from pathlib import Path
import csv,json
root=Path(__file__).resolve().parent.parent;out=[]
for q in json.loads((root/'pass6/evidence/specs.json').read_text()):
 v=q['build'];d=root/'pass6/audit'/('DOS'+v);p=d/'explicit_model_results.tsv'
 if not p.exists():continue
 rows=list(csv.DictReader(p.open(),delimiter='\t'));previous=list(csv.DictReader((root/'pass5/audit'/('DOS'+v)/'explicit_model_results.tsv').open(),delimiter='\t'));key=lambda r:(r['entry'],r['model']);now={key(r):r for r in rows};before={key(r):r for r in previous};assert now.keys()==before.keys()
 good=lambda r:r['completed']=='true' and r['C_available']=='true'
 assert all(good(now[k])==good(before[k]) for k in before)
 b=list(csv.DictReader((root/'pass5/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));a=list(csv.DictReader((d/'instructions.tsv').open(),delimiter='\t'));assert [(r['address'],r['bytes']) for r in a]==[(r['address'],r['bytes']) for r in b]
 fixes=list(csv.DictReader((root/'pass6/evidence'/('DOS'+v)/'abi_fix/abi_fixes.tsv').open(),delimiter='\t'));assert len(fixes)==2;assert fixes[0]['after_storage']=='AL:1';assert fixes[1]['after_storage']=='DX:2,AX:2'
 refs=list(csv.DictReader((root/'pass6/evidence'/('DOS'+v)/'abi_fix/candidate_incoming.tsv').open(),delimiter='\t'));assert not refs
 out.append(dict(build=v,stock_completed=sum(good(r) for r in rows if r['model']=='stock'),explicit_completed=sum(good(r) for r in rows if r['model']!='stock'),functions=len(rows)//2,prototype_fixes=fixes,unchanged_instructions=len(a),remaining_candidates=q['candidates'],incoming_references_to_candidates=0))
(root/'pass6/evidence/validation.json').write_text(json.dumps(out,indent=2));print([(q['build'],q['stock_completed'],q['explicit_completed']) for q in out])
