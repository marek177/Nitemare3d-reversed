from pathlib import Path
import csv,json
root=Path(__file__).resolve().parent.parent;results=[]
for v in ['10','11','12','15','17','18']:
 log=root/'pass2'/('DOS'+v+'.log')
 if not log.exists() or 'Save succeeded for processed file' not in log.read_text():continue
 before={r['entry']:r for r in csv.DictReader((root/'audit'/('DOS'+v)/'functions.tsv').open(),delimiter='\t')};after={r['entry']:r for r in csv.DictReader((root/'pass2/audit'/('DOS'+v)/'functions.tsv').open(),delimiter='\t')}
 regressions=[a for a in before if before[a]['completed']=='true' and (a not in after or after[a]['completed']!='true')]
 recovered=[a for a in before if before[a]['completed']!='true' and a in after and after[a]['completed']=='true']
 proofs=json.loads((root/'pass2/evidence'/('DOS'+v)/'switch_proofs.json').read_text())
 calls=list(csv.DictReader((root/'pass2/audit'/('DOS'+v)/'calls.tsv').open(),delimiter='\t'))
 for p in proofs:
  actual={r['target'] for r in calls if r['source']==p['source'] and r['type']=='COMPUTED_JUMP'}
  assert actual==set(p['targets']),(v,p['source'],actual,set(p['targets']))
 near=json.loads((root/'pass2/evidence'/('DOS'+v)/'near_specs.json').read_text())
 for p in near:
  actual={r['target'] for r in calls if r['source']==p['source'] and 'CALL' in r['type']}
  assert actual=={p['target']},(v,p,actual)
 r=dict(build=v,before_functions=len(before),after_functions=len(after),before_completed=sum(x['completed']=='true' for x in before.values()),after_completed=sum(x['completed']=='true' for x in after.values()),recovered=recovered,regressions=regressions,remaining_failures=[a for a,x in after.items() if x['completed']!='true'],switches=len(proofs),near_calls=len(near))
 results.append(r)
(root/'pass2/evidence/validation.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
