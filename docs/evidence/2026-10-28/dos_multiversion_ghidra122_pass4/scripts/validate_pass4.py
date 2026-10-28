from pathlib import Path
import csv,json
root=Path(__file__).resolve().parent.parent;results=[]
for v in ['10','11','12','15','17','18']:
 d=root/'pass4/audit'/('DOS'+v);b={r['entry']:r for r in csv.DictReader((root/'pass3/audit'/('DOS'+v)/'functions.tsv').open(),delimiter='\t')};a={r['entry']:r for r in csv.DictReader((d/'functions.tsv').open(),delimiter='\t')};assert b.keys()==a.keys()
 regression=[k for k in b if b[k]['completed']=='true' and a[k]['completed']!='true'];assert not regression
 calls=list(csv.DictReader((d/'calls.tsv').open(),delimiter='\t'));proof=json.loads((root/'pass4/evidence'/('DOS'+v)/'switch_proofs.json').read_text())
 for q in proof:assert {r['target'] for r in calls if r['source']==q['source'] and r['type']=='COMPUTED_JUMP'}==set(q['targets'])
 flows=list(csv.DictReader((root/'pass4/evidence'/('DOS'+v)/'flow_specs.tsv').open(),delimiter='\t'))
 for q in flows:assert {r['target'] for r in calls if r['source']==q['source'] and r['type']=='CONDITIONAL_JUMP'}=={q['target']}
 expected=int((d/'flow_export_verified.txt').read_text().split('=')[1]);ins=list(csv.DictReader((d/'instructions.tsv').open(),delimiter='\t'));assert len(ins)==expected
 boundary=json.loads((root/'pass4/evidence'/('DOS'+v)/'boundary.json').read_text());lookup={r['address']:r for r in ins};assert lookup[boundary['start']]['bytes']=='895ee8' and lookup[boundary['end']]['bytes']=='cb'
 r=a[boundary['function']];assert int(r['instructions'])>=250
 motion=json.loads((root/'pass4/evidence'/('motion_'+v+'.json')).read_text());assert motion['passed']==464 and motion['stop_before_retf']==boundary['end'] and motion['hooks']==False
 results.append(dict(build=v,functions=len(a),before_completed=sum(x['completed']=='true' for x in b.values()),after_completed=sum(x['completed']=='true' for x in a.values()),recovered=[k for k in b if b[k]['completed']!='true' and a[k]['completed']=='true'],regressions=regression,remaining=[k for k in a if a[k]['completed']!='true'],movement_before_instructions=int(b[boundary['function']]['instructions']),movement_after_instructions=int(r['instructions']),switches=len(proof),conditional_flow_repairs=len(flows),motion_cases=motion['passed']))
(root/'pass4/evidence/validation.json').write_text(json.dumps(results,indent=2));print([(r['build'],r['after_completed'],len(r['remaining'])) for r in results]);print('recovered',sum(len(r['recovered']) for r in results),'remaining',sum(len(r['remaining']) for r in results))
