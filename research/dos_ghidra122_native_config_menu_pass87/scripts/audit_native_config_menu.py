from pathlib import Path
import json,struct,hashlib
r=Path(__file__).resolve().parent.parent;out=[]
for l in json.load(open(r/'pass87/evidence/source_locations.json')):
 v=l['build'];b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 ds=next(x['actual_DS'] for x in json.load(open(r/'baseline58/pass7/evidence/specs.json')) if x['build']==v);sg=struct.unpack_from('<H',p,(ds-4096)*16+l['record_segment_global'])[0];records=[]
 for i in range(6):
  off=0x1212+i*18;raw=bytes(p[(sg-4096)*16+off:(sg-4096)*16+off+18]);rid=raw[0]
  if rid==0:break
  cb,cbsg=struct.unpack_from('<HH',raw,6);label,labelsg=struct.unpack_from('<HH',raw,14);text=bytes(p[(labelsg-4096)*16+label:(labelsg-4096)*16+label+100]).split(b'\0')[0].decode('cp437');records.append(dict(id=rid,value=struct.unpack_from('<h',raw,2)[0],raw=raw.hex(),callback=f'{cbsg:04x}:{cb:04x}',label_pointer=f'{labelsg:04x}:{label:04x}',label=text))
 assert [x['id'] for x in records]==[10,11,13,12,21];assert all(x['callback']==l['entry'] for x in records)
 print(v,[(x['id'],x['label']) for x in records]);out.append(dict(build=v,exe_sha256=hashlib.sha256(b).hexdigest(),segment_global=l['record_segment_global'],record_segment=sg,record_offset=0x1212,records=records))
(r/'pass87/evidence/native_records.json').write_text(json.dumps(out,indent=2)+'\n')
