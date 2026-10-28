from pathlib import Path
import struct,json,csv,re,shutil,zipfile,hashlib,functools,operator
root=Path(__file__).resolve().parent.parent;cfgs=json.loads((root/'pass6/evidence/specs.json').read_text());dsproof=json.loads((root/'pass3/evidence/xlat_proofs.json').read_text());paths={'10':'n3-4-10','11':'N3-5','12':'n3dfull','15':'N3-6','17':'n3-7','18':'nd-3-19'};z=zipfile.ZipFile(root/'inputs/all-nite3d.zip');specs=[];resources=[]
for q in cfgs:
 v=q['build'];b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=b[h[4]*16:];ds=int(next(x for x in dsproof if x['build']==v)['ds'],16);keytext=b'Copyright 1992, David P Gray, Gray Design Associates';assert p.count(keytext)==1;kp=p.find(keytext);keyoff=kp-(ds*16-0x10000)
 manifest=(root/'pass4/audit'/('DOS'+v)/'manifest.txt').read_text() if (root/'pass4/audit'/('DOS'+v)/'manifest.txt').exists() else ''
 candidates=list((root/'pass6/audit'/('DOS'+v)).glob('*_stock.c'));decoder=next(c.name.removesuffix('_stock.c').replace('_',':') for c in candidates if '% 0x34' in c.read_text() and 'local_3 ^' in c.read_text())
 s,o=map(lambda x:int(x,16),q['callback_entry'].split(':'));pos=s*16+o-0x10000;table=struct.unpack_from('<H',p,pos+0x13)[0];targets=list(struct.unpack_from('<6H',p,s*16+table-0x10000));ins=list(csv.DictReader((root/'pass6/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));calls=[r for r in ins if r['address'].startswith(f'{s:04x}:') and o<=int(r['address'].split(':')[1],16)<o+0x110 and r['bytes'].startswith('9a') and len(r['bytes'])==10];last=bytes.fromhex(calls[-1]['bytes']);loader=f'{int.from_bytes(last[3:5],"little"):04x}:{int.from_bytes(last[1:3],"little"):04x}'
 # Exported instruction bytes already contain load relocation, unlike source payload.
 data_name=next(n for n in z.namelist() if n.lower()==('nite3d/dos/'+paths[v]+'/nite3d.bsf').lower());data=z.read(data_name);(root/'pass7/data'/('DOS'+v+'.bsf')).write_bytes(data);header=bytes(c^keytext[i%52] for i,c in enumerate(data[:54]));assert functools.reduce(operator.xor,data[:54],0)==0
 blocks=[]
 for mode,off,lpos in [(3,40,50),(4,36,48),(5,44,52)]:
  at=struct.unpack_from('<I',header,off)[0];n=struct.unpack_from('<H',header,lpos)[0];raw=data[at:at+n];assert len(raw)==n;decoded=bytes(c^keytext[i%52] for i,c in enumerate(raw));(root/'pass7/data'/f'DOS{v}_mode{mode}.bin').write_bytes(decoded);blocks.append(dict(mode=mode,file_offset=at,length=n,sha256_encoded=hashlib.sha256(raw).hexdigest(),sha256_decoded=hashlib.sha256(decoded).hexdigest(),first_text=decoded[:110].decode('cp437')))
 sorted_blocks=sorted(blocks,key=lambda x:x['file_offset']);assert sorted_blocks[0]['file_offset']==54 and all(a['file_offset']+a['length']==b['file_offset'] for a,b in zip(sorted_blocks,sorted_blocks[1:])) and sorted_blocks[-1]['file_offset']+sorted_blocks[-1]['length']==len(data)
 resource=dict(build=v,source=data_name,bsf_sha256=hashlib.sha256(data).hexdigest(),file_bytes=len(data),header_hex=header.hex(),header_encoded_xor=0,blocks=blocks);resources.append(resource)
 spec={**q,'actual_DS':ds,'key_offset':keyoff,'decoder_entry':decoder,'loader_entry':loader,'mode_targets':[f'{s:04x}:{x:04x}' for x in targets],'header_base':q['mode1_flag']-3};specs.append(spec);d=root/'pass7/evidence'/('DOS'+v);d.mkdir(exist_ok=True)
 for ext in ['.gpr','.rep']:
  src=root/'pass6/projects'/('DOS'+v+ext);dst=root/'pass7/projects'/src.name
  if src.is_dir():shutil.copytree(src,dst,dirs_exist_ok=True)
  else:shutil.copy2(src,dst)
(root/'pass7/evidence/specs.json').write_text(json.dumps(specs,indent=2));(root/'pass7/evidence/bsf_resources.json').write_text(json.dumps(resources,indent=2));print([(q['build'],q['decoder_entry'],q['loader_entry']) for q in specs]);print([(r['build'],r['file_bytes'],[(b['mode'],b['file_offset'],b['length']) for b in r['blocks']]) for r in resources])
