from pathlib import Path
import json,struct,csv,shutil
root=Path(__file__).resolve().parent.parent;proofs=[]
for v in ['10','11','12','15','17','18']:
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);j=seg*16+off;struct.pack_into('<H',p,j,(struct.unpack_from('<H',p,j)[0]+0x1000)&65535)
 startup=h[11]*16;di=p.find(b'\xbf',startup+h[10],startup+h[10]+32);assert p[di+3:di+7]==bytes.fromhex('8b360200');ds=struct.unpack_from('<H',p,di+1)[0]
 manifest=(root/'pass2/evidence/validation.json');remaining=next(x for x in json.loads(manifest.read_text()) if x['build']==v)['remaining_failures'];entry=next(x for x in remaining if x.endswith((':1648',':164c',':1744')));seg,off=map(lambda x:int(x,16),entry.split(':'));pos=seg*16+off-0x10000
 code=p[pos+0x2e:pos+0x57];assert code[:1]==b'\xbb';table=struct.unpack_from('<H',code,1)[0];assert code[3:]==bytes.fromhex('2c203c587705d7240feb02b000b103d2e00246fbd7fec1d2e88846fb988bd8d1e32effa7')+p[pos+0x55:pos+0x57]
 data=p[ds*16-0x10000+table:ds*16-0x10000+table+89];classes={x&15 for x in data}|{0};states={0}
 while True:
  nxt=states|{data[(c<<3)+s]>>4 for c in classes for s in states}
  if nxt==states:break
  states=nxt
 assert states==set(range(8));jump=off+0x52;jtable=struct.unpack_from('<H',p,pos+0x55)[0];targets=struct.unpack_from('<8H',p,seg*16-0x10000+jtable)
 d=root/'pass3/evidence'/('DOS'+v);d.mkdir(exist_ok=True)
 (d/'switch_specs.tsv').write_text(f'source\ttable\tcount\tguard\n{seg:04x}:{jump:04x}\t{seg:04x}:{jtable:04x}\t8\tXLAT_FIXED_POINT\n')
 q=dict(build=v,entry=entry,source=f'{seg:04x}:{jump:04x}',table=f'{seg:04x}:{jtable:04x}',ds=f'{ds:04x}',class_table=f'{table:04x}',class_bytes=data.hex(),classes=sorted(classes),reachable_states=sorted(states),targets=[f'{seg:04x}:{x:04x}' for x in targets],dispatch_start=f'{seg:04x}:{off+0x2e:04x}',startup_ds_operand=f'{h[11]+0x1000:04x}:{di-startup+1:04x}')
 proofs.append(q)
 for ext in ['.gpr','.rep']:
  src=root/'pass2/projects'/('DOS'+v+ext);dst=root/'pass3/projects'/src.name
  if src.is_dir():shutil.copytree(src,dst,dirs_exist_ok=True)
  else:shutil.copy2(src,dst)
(root/'pass3/evidence/xlat_proofs.json').write_text(json.dumps(proofs,indent=2));print([(q['build'],q['ds'],q['class_table']) for q in proofs])
