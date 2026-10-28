from pathlib import Path
import csv,json,struct,shutil
root=Path(__file__).resolve().parent.parent;summary=[]
for v in ['10','11','12','15','17','18']:
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=b[h[4]*16:];rows=list(csv.DictReader((root/'pass3/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'))
 farsegments={int.from_bytes(bytes.fromhex(r['bytes'])[3:5],'little') for r in rows if r['bytes'].startswith('9a') and len(r['bytes'])==10};specs=[];proof=[];flows=[]
 def phys(a):seg,off=map(lambda x:int(x,16),a.split(':'));return seg*16+off
 for i,r in enumerate(rows):
  bb=bytes.fromhex(r['bytes'])
  if i>=5 and bb.startswith(b'\x2e\xff\xa7'):
   w=rows[i-5:i+1];bs=[bytes.fromhex(x['bytes']) for x in w]
   if bs[0]==b'\x8b\xc7' and bs[1][:1]==b'\x3d' and bs[2].startswith((b'\x77',b'\x0f\x87')) and bs[3]==b'\x03\xc7' and bs[4]==b'\x93' and all(phys(a['address'])+len(bytes.fromhex(a['bytes']))==phys(c['address']) for a,c in zip(w,w[1:])):
    seg=int(r['address'].split(':')[0],16);count=int.from_bytes(bs[1][1:],'little')+1;table=int.from_bytes(bb[3:],'little');targets=list(struct.unpack_from('<'+'H'*count,p,seg*16+table-0x10000));assert seg in farsegments
    specs.append(dict(source=r['address'],table=f'{seg:04x}:{table:04x}',count=count,guard=w[1]['address']));proof.append(dict(source=r['address'],window=w,targets=[f'{seg:04x}:{t:04x}' for t in targets]))
  disp=None
  if len(bb)==3 and bb[0] in [0xe8,0xe9]:disp=int.from_bytes(bb[1:],'little',signed=True)
  elif len(bb)==4 and bb[0]==0x0f and 0x80<=bb[1]<=0x8f:disp=int.from_bytes(bb[2:],'little',signed=True)
  if disp is None:continue
  seg,off=map(lambda x:int(x,16),r['address'].split(':'));want=seg*16+((off+len(bb)+disp)&65535)
  import re
  targets=re.findall(r'([0-9a-f]+):([0-9a-f]+)',r['targets'])
  if seg not in farsegments or len(targets)!=1:continue
  actual=int(targets[0][0],16)*16+int(targets[0][1],16)
  if actual==want:continue
  flows.append(dict(source=r['address'],target=f'{seg:04x}:{(off+len(bb)+disp)&65535:04x}',bytes=r['bytes'],type='CALL' if bb[0]==0xe8 else 'JUMP' if bb[0]==0xe9 else 'CONDITIONAL_JUMP',old=r['targets']))
 pos=p.find(bytes.fromhex('895ee88c46ea26833f00'));assert pos>=0 and p.find(bytes.fromhex('895ee88c46ea26833f00'),pos+1)<0
 end=p.find(bytes.fromhex('5e5fc9cb'),pos)
 if end<0 or end-pos>500:
  end=p.find(bytes.fromhex('5f5ec9cb'),pos)
 assert pos<end<pos+500,(v,pos,end)
 d=root/'pass4/evidence'/('DOS'+v);d.mkdir(exist_ok=True)
 with (d/'switch_specs.tsv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=['source','table','count','guard'],delimiter='\t');w.writeheader();w.writerows(specs)
 with (d/'flow_specs.tsv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=['source','target','bytes','type','old'],delimiter='\t');w.writeheader();w.writerows(flows)
 (d/'switch_proofs.json').write_text(json.dumps(proof,indent=2));(d/'boundary.json').write_text(json.dumps(dict(start=f'1000:{pos:04x}',end=f'1000:{end+3:04x}',function='1000:0ae0' if v in ['10','11','12'] else '1000:0aea'),indent=2))
 for ext in ['.gpr','.rep']:
  src=root/'pass3/projects'/('DOS'+v+ext);dst=root/'pass4/projects'/src.name
  if src.is_dir():shutil.copytree(src,dst,dirs_exist_ok=True)
  else:shutil.copy2(src,dst)
 summary.append(dict(build=v,switches=len(specs),flows=len(flows),boundary_start=hex(pos),boundary_end=hex(end+3)))
(root/'pass4/evidence/preparation.json').write_text(json.dumps(summary,indent=2));print(summary)
