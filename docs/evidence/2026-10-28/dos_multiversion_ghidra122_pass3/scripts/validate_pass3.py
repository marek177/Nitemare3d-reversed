from pathlib import Path
import json,csv
root=Path(__file__).resolve().parent.parent;results=[]
for q in json.loads((root/'pass3/evidence/xlat_proofs.json').read_text()):
 v=q['build'];d=root/'pass3/audit'/('DOS'+v);b={r['entry']:r for r in csv.DictReader((root/'pass2/audit'/('DOS'+v)/'functions.tsv').open(),delimiter='\t')};a={r['entry']:r for r in csv.DictReader((d/'functions.tsv').open(),delimiter='\t')}
 assert b.keys()==a.keys()
 regression=[k for k in b if b[k]['completed']=='true' and a[k]['completed']!='true'];assert not regression
 calls=list(csv.DictReader((d/'calls.tsv').open(),delimiter='\t'));assert {r['target'] for r in calls if r['source']==q['source'] and r['type']=='COMPUTED_JUMP'}==set(q['targets'])
 expected=int((d/'flow_export_verified.txt').read_text().split('=')[1]);assert len(list(csv.DictReader((d/'instructions.tsv').open(),delimiter='\t')))==expected
 for n in ['functions.tsv','calls.tsv','instructions.tsv']:assert (d/n).read_bytes().endswith(b'\n')
 normalized=list(csv.DictReader((root/'pass3/evidence'/('DOS'+v)/'residual/normalized_results.tsv').open(),delimiter='\t'));refs=list(csv.DictReader((root/'pass3/evidence'/('DOS'+v)/'residual/incoming_references.tsv').open(),delimiter='\t'))
 remain=[k for k in a if a[k]['completed']!='true'];orphans=[k for k in remain if not any(r['entry']==k for r in refs)]
 results.append(dict(build=v,functions=len(a),before_completed=sum(r['completed']=='true' for r in b.values()),after_completed=sum(r['completed']=='true' for r in a.values()),recovered=[k for k in b if b[k]['completed']!='true' and a[k]['completed']=='true'],regressions=regression,remaining=remain,no_incoming_reference_candidates=orphans,normalized_IR_only=[r['entry'] for r in normalized if r['completed']=='true' and r['C_available']=='false' and r['entry'] in remain]))
(root/'pass3/evidence/validation.json').write_text(json.dumps(results,indent=2));print([(r['build'],r['after_completed'],len(r['remaining'])) for r in results]);print('recovered',sum(len(r['recovered']) for r in results),'remaining',sum(len(r['remaining']) for r in results),'IR only',sum(len(r['normalized_IR_only']) for r in results))
