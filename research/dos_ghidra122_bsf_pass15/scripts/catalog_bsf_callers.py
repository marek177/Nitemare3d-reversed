from pathlib import Path
import csv,json,re,struct
root=Path(__file__).resolve().parent.parent;out=[]
def linear(s):a,b=[int(x,16) for x in s.split(':')];return a*16+b
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+q['build'])/'instructions.tsv').open(),delimiter='\t'));target=linear(q['callback_entry']);direct=[]
 for i,r in enumerate(rows):
  refs=re.findall(r'[0-9a-f]{4}:[0-9a-f]{4}',r['targets'])
  if 'CALL' in r['flow'] and any(linear(s)==target for s in refs):direct.append(dict(call=r,preceding=rows[max(0,i-5):i]))
 dynamic=[d for d in direct if d['preceding'][-1]['bytes']=='ff7608'];assert len(dynamic)==1;site=dynamic[0]['call']['address'];cs=site.split(':')[0];s=linear(site);entries=[r for r in rows if r['address'].startswith(cs+':') and s-80<=linear(r['address'])<s and r['bytes'].startswith('c8')];assert len(entries)==1;generic=entries[0]['address'];users=[]
 for i,r in enumerate(rows):
  if 'CALL' in r['flow'] and any(linear(t)==linear(generic) for t in re.findall(r'[0-9a-f]{4}:[0-9a-f]{4}',r['targets'])):users.append(dict(call=r,preceding=rows[max(0,i-6):i]))
 out.append(dict(build=q['build'],dispatch=q['callback_entry'],direct_calls=direct,dynamic_caller_entry=generic,dynamic_mode_source='word at caller BP+8 = entry SP+6 (second word argument)',dynamic_caller_users=users))
p=root/'pass15/evidence/bsf_callers.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2));print([(x['build'],len(x['direct_calls']),len(x['dynamic_caller_users'])) for x in out])
