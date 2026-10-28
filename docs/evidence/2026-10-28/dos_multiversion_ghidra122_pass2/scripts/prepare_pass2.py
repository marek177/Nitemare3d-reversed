from pathlib import Path
import csv,json,struct,hashlib,re,shutil
root=Path(__file__).resolve().parent.parent
summary=[]
for v in ['10','11','12','15','17','18']:
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for i in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+i*4);j=seg*16+off;struct.pack_into('<H',p,j,(struct.unpack_from('<H',p,j)[0]+0x1000)&65535)
 rows=list(csv.DictReader((root/'audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'))
 def phys(a):s,o=map(lambda t:int(t,16),a.split(':'));return s*16+o
 farsegments={int.from_bytes(bytes.fromhex(r['bytes'])[3:5],'little') for r in rows if r['bytes'].startswith('9a') and len(r['bytes'])==10}
 specs=[];proof=[];near=[]
 for i,r in enumerate(rows):
  if not r['bytes'].startswith('2effa7') or len(r['bytes'])!=10 or i<4:continue
  win=rows[i-4:i+1];bb=[bytes.fromhex(x['bytes']) for x in win]
  if not(len(bb[0])==3 and bb[0][0]==0x3d and bb[1].startswith((b'\x77',b'\x0f\x87')) and bb[2] in [b'\x03\xc0',b'\x03\xc2'] and bb[3]==b'\x93'):continue
  if not all(phys(a['address'])+len(bytes.fromhex(a['bytes']))==phys(c['address']) for a,c in zip(win,win[1:])):continue
  seg=int(r['address'].split(':')[0],16)
  if seg not in farsegments:continue
  assert all(bytes(p[phys(x['address'])-0x10000:phys(x['address'])-0x10000+len(bytes.fromhex(x['bytes']))])==bytes.fromhex(x['bytes']) for x in win)
  n=int.from_bytes(bb[0][1:],'little')+1;tableoff=int.from_bytes(bb[4][3:],'little');tp=seg*16+tableoff-0x10000
  assert 0<n<=256 and 0<=tp<=len(p)-2*n
  targets=list(struct.unpack_from('<'+'H'*n,p,tp))
  assert all(0<=seg*16+t-0x10000<len(p) for t in targets)
  if bb[2]==b'\x03\xc2':
   # ADD AX,DX only doubles AX when DX is already a copy of AX.
   if i<5 or rows[i-5]['bytes'] not in ['8bd0','89c2']:continue
  specs.append(dict(source=r['address'],table=f'{seg:04x}:{tableoff:04x}',count=n,guard=win[0]['address']))
  proof.append(dict(source=r['address'],window=win,targets=[f'{seg:04x}:{t:04x}' for t in targets],CS_evidence='segment appears as decoded far-call operand',exe_sha256=hashlib.sha256(b).hexdigest()))
 for r in json.loads((root/'audit'/('DOS'+v)/'near_flow_discrepancies.json').read_text()):
  bb=bytes.fromhex(r['bytes']);seg,off=map(lambda x:int(x,16),r['source'].split(':'))
  if len(bb)!=3 or bb[0]!=0xe8 or seg not in farsegments:continue
  target=(off+3+int.from_bytes(bb[1:],'little',signed=True))&65535
  near.append(dict(source=r['source'],target=f'{seg:04x}:{target:04x}',bytes=r['bytes'],previous=r['reported']))
 out=root/'pass2/evidence'/('DOS'+v);out.mkdir(exist_ok=True)
 with (out/'switch_specs.tsv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=['source','table','count','guard'],delimiter='\t');w.writeheader();w.writerows(specs)
 (out/'switch_proofs.json').write_text(json.dumps(proof,indent=2));(out/'near_specs.json').write_text(json.dumps(near,indent=2))
 for ext in ['.gpr','.rep']:
  src=root/'projects_clean'/('DOS'+v+ext);dst=root/'pass2/projects'/src.name
  if src.is_dir():shutil.copytree(src,dst,dirs_exist_ok=True)
  else:shutil.copy2(src,dst)
 summary.append(dict(build=v,switches=len(specs),table_entries=sum(s['count'] for s in specs),near_calls=len(near)))
(root/'pass2/evidence/preparation.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
