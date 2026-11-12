"""IMAGE COMPARISONS DECODER OUT: resolve indexed calendar table bindings."""
import csv,hashlib,json,sys
from pathlib import Path
image,comparisons,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()))
from iced_x86 import Decoder,FlowControl,Formatter,FormatterSyntax,Register
fmt=Formatter(FormatterSyntax.INTEL);source=(comparisons.parent.parent/'audit_crt_calendar_versions.py').read_text(encoding='utf-8');exec(source[source.index('def norm('):source.index('for label in (')],globals())
b=image.read_bytes();common=b[0x29b98:0x29bb2];leap=b[0x29b7e:0x29b98];defs={r['name']:r for r in json.loads((comparisons.parent.parent/'crt_calendar_replay/summary.json').read_text())['functions']}
root=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');rows=[];files=[]
for r in csv.DictReader(comparisons.open(encoding='utf-8')):
 assert r['status']=='COMPARED';p=root/('N3D-'+r['version'])/'unpacked_image.bin';v=p.read_bytes();files.append(dict(path=str(p),sha256=hashlib.sha256(v).hexdigest()));f=defs[r['function']];start,end,ip=(int(r[k]) for k in ('start','end_exclusive','ip'));rc,re,_,_=norm(b[f['start']:f['end_exclusive']],f['start']-0x11ee0);vc,ve,_,_=norm(v[start:end],ip);assert re==ve and len(rc)==len(vc)
 differences=[i for i,(x,y) in enumerate(zip(rc,vc)) if x!=y];base='';ds='';table_start=''
 if f['name']=='crt_DST_style_predicate':
  assert set(differences)<={0x47,0x48,0x57,0x58};base=int.from_bytes(v[start+0x47:start+0x49],'little');assert int.from_bytes(v[start+0x57:start+0x59],'little')==base+2
 elif f['name']=='crt_calendar_to_epoch32':
  assert set(differences)<={0x12,0x13};base=int.from_bytes(v[start+0x12:start+0x14],'little')+2
 else:assert not differences
 if base!='':
  signature=bytes.fromhex('b430cd213c02730533c00650cbbf');hits=[i for i in range(len(v)) if v.startswith(signature,i)];assert len(hits)==1;ds=int.from_bytes(v[hits[0]+len(signature):hits[0]+len(signature)+2],'little');table_start=ds*16+base
  assert v[table_start:table_start+26]==common and v[table_start-26:table_start]==leap
 rows.append(dict(version=r['version'],function=f['name'],remaining_normalized_difference_offsets=','.join('%02X'%i for i in differences),startup_DS=ds,common_table_DS=base,common_table_image=table_start,common_and_leap_tables_equal_DOS20=(base!=''),scope='Remaining differences restricted to indexed table addresses; full26B common/leap neighbor identity checked against startupDS. Does not prove leap table consumption or timezone behavior.'))
out.mkdir(exist_ok=True)
with (out/'table_bindings.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(comparisons=len(rows),table_bound_functions=sum(r['common_table_DS']!='' for r in rows),remaining_differences_accounted=True,scope='Exact normalized comparison results retained; indexed address binding explains residual bytes; no behavioral parity or PASS1 promotion.',files=files+[dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (image,comparisons,comparisons.parent.parent/'audit_crt_calendar_versions.py',comparisons.parent.parent/'crt_calendar_replay/summary.json',Path(__file__))])
(out/'binding_summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'}))
