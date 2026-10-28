from pathlib import Path
import struct,json,csv,re,shutil,hashlib
root=Path(__file__).resolve().parent.parent;cfgs=json.loads((root/'pass5/evidence/scopes.json').read_text());old=json.loads((root/'pass5/evidence/validation.json').read_text())['builds'];specs=[]
for q in cfgs:
 v=q['build'];rows=list(csv.DictReader((root/'pass4/audit'/('DOS'+v)/'functions.tsv').open(),delimiter='\t'));manifest=(root/'pass4/audit'/('DOS'+v)/'manifest.txt').read_text();seg=re.search(r'block=CODE_13 ([0-9a-f]+):',manifest)[1];entry=next(r['entry'] for r in rows if r['entry'].startswith(seg+':') and int(r['entry'].split(':')[1],16)>0x2800 and int(r['computed_flows'])>0)
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=b[h[4]*16:];s,o=map(lambda x:int(x,16),entry.split(':'));pos=s*16+o-0x10000;table=struct.unpack_from('<H',p,pos+0x13)[0];assert p[pos+0x10:pos+0x13]==b'\x2e\xff\xa7';target=struct.unpack_from('<H',p,s*16+table-0x10000+2)[0];t=s*16+target-0x10000;assert p[t:t+2]==b'\x80\x3e' and p[t+5:t+8]==bytes.fromhex('7407b8') and p[t+10:t+12]==bytes.fromhex('8cda')
 flag=struct.unpack_from('<H',p,t+2)[0];assert struct.unpack_from('<H',p,t+8)[0]==flag
 spec={**q,'callback_entry':entry,'mode1_target':f'{s:04x}:{target:04x}','mode1_flag':flag,'candidates':next(r for r in old if r['build']==v)['remaining_in_explicit_view'],'exe_sha256':hashlib.sha256(b).hexdigest()};specs.append(spec);d=root/'pass6/evidence'/('DOS'+v);d.mkdir(exist_ok=True);(d/'abi_spec.tsv').write_text(q['renderer_entry']+'\t'+entry+'\t'+','.join(spec['candidates'])+'\n')
 for ext in ['.gpr','.rep']:
  src=root/'pass5/projects'/('DOS'+v+ext);dst=root/'pass6/projects'/src.name
  if src.is_dir():shutil.copytree(src,dst,dirs_exist_ok=True)
  else:shutil.copy2(src,dst)
(root/'pass6/evidence/specs.json').write_text(json.dumps(specs,indent=2));print([(q['build'],q['callback_entry'],hex(q['mode1_flag'])) for q in specs])
