from pathlib import Path
import csv,json,collections,re,struct,hashlib
root=Path(__file__).resolve().parent.parent
summary=[]
for v in ['10','11','12','15','17','18']:
 d=root/'audit'/('DOS'+v)
 if not (d/'functions.tsv').exists() or 'Import succeeded' not in (root/('clean_DOS'+v+'.log')).read_text():continue
 rows=list(csv.DictReader((d/'functions.tsv').open(),delimiter='\t'))
 problems=[x for x in rows if x['completed']!='true' or int(x['computed_flows'])>0]
 with (d/'review_queue.tsv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys(),delimiter='\t');w.writeheader();w.writerows(problems)
 ins=list(csv.DictReader((d/'instructions.tsv').open(),delimiter='\t'))
 wrong=[]
 for x in ins:
  b=bytes.fromhex(x['bytes']);a=x['address']
  if ':' not in a or a.startswith('HEADER'):continue
  seg,off=[int(q,16) for q in a.split(':')]
  disp=None
  if len(b)==3 and b[0] in [0xe8,0xe9]:disp=int.from_bytes(b[1:],'little',signed=True)
  if len(b)==4 and b[:1]==b'\x0f' and 0x80<=b[1]<=0x8f:disp=int.from_bytes(b[2:],'little',signed=True)
  if disp is None:continue
  expected=seg*16+((off+len(b)+disp)&65535)
  targets=re.findall(r'([0-9a-fA-F]+):([0-9a-fA-F]+)',x['targets'])
  if len(targets)!=1:continue
  actual=int(targets[0][0],16)*16+int(targets[0][1],16)
  if actual!=expected:wrong.append(dict(source=a,bytes=x['bytes'],reported=x['targets'],expected_linear=hex(expected),delta=actual-expected))
 (d/'near_flow_discrepancies.json').write_text(json.dumps(wrong,indent=2))
 summary.append(dict(label=v,functions=len(rows),decompiled=sum(x['completed']=='true' for x in rows),failed=sum(x['completed']!='true' for x in rows),computed_functions=sum(int(x['computed_flows'])>0 for x in rows),instructions=len(ins),unowned_instructions=sum(1 for _ in (d/'unowned_instructions.tsv').open())-1,near_flow_discrepancies=len(wrong)))
(root/'evidence/audit_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
