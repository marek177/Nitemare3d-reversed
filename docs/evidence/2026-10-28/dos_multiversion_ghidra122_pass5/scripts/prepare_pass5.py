from pathlib import Path
import csv,json,re,shutil
root=Path(__file__).resolve().parent.parent;proofs=[]
for v in ['10','11','12','15','17','18']:
 rows=list(csv.DictReader((root/'pass4/audit'/('DOS'+v)/'functions.tsv').open(),delimiter='\t'));manifest=(root/'pass4/audit'/('DOS'+v)/'manifest.txt').read_text();block=re.search(r'block=CODE_21 ([0-9a-f]+):([0-9a-f]+) ([0-9a-f]+):([0-9a-f]+)',manifest);seg=int(block[1],16);nb=seg*16;ne=int(block[3],16)*16+int(block[4],16);far1=0x10ae0 if v in ['10','11','12'] else 0x10aea;fe1=0x10dec if v in ['10','11','12'] else 0x10df6
 def phys(a):s,o=map(lambda x:int(x,16),a.split(':'));return s*16+o
 remain=next(x for x in json.loads((root/'pass4/evidence/validation.json').read_text()) if x['build']==v)['remaining'];entry=next(x for x in remain if not x.startswith('1000:') and x.split(':')[0].startswith('1c' if v=='10' else '1d'));fs=phys(entry);fe=min(phys(x['entry']) for x in rows if phys(x['entry'])>fs)-1
 target=next(x['entry'] for x in rows if x['entry'].startswith(f'{seg:04x}:') and int(x['entry'].split(':')[1],16) in [0x178,0x170,0x16e,0x16a])
 spec=dict(build=v,far1_start=far1,far1_end=fe1,far2_start=fs,far2_end=fe,near_start=nb,near_end=ne,renderer_CS=seg,renderer_entry=target,far2_entry=entry);proofs.append(spec);d=root/'pass5/evidence'/('DOS'+v);d.mkdir(exist_ok=True);(d/'scope.tsv').write_text('\t'.join(str(spec[k]) for k in ['far1_start','far1_end','far2_start','far2_end','near_start','near_end','renderer_CS'])+'\n')
 for ext in ['.gpr','.rep']:
  src=root/'pass4/projects'/('DOS'+v+ext);dst=root/'pass5/projects'/src.name
  if src.is_dir():shutil.copytree(src,dst,dirs_exist_ok=True)
  else:shutil.copy2(src,dst)
(root/'pass5/evidence/scopes.json').write_text(json.dumps(proofs,indent=2));print([(q['build'],q['renderer_entry'],q['far2_entry']) for q in proofs])
