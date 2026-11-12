"""IMAGE COMPARISONS DECODER OUT: explain retained indexed displacement differences."""
import csv,hashlib,json,sys
from pathlib import Path
image,comparisons,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()))
from iced_x86 import Decoder,FlowControl,Formatter,FormatterSyntax,Register
fmt=Formatter(FormatterSyntax.INTEL);source=(comparisons.parent.parent/'audit_crt_ftime_versions.py').read_text(encoding='utf-8');exec(source[source.index('def norm('):source.index('for label in (')],globals())
b=image.read_bytes();common=b[0x29b98:0x29bb2];defs={r['name']:r for r in json.loads((comparisons.parent.parent/'crt_ftime_replay/summary.json').read_text())['functions']};root=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');rows=[];files=[]
for r in csv.DictReader(comparisons.open(encoding='utf-8')):
 assert r['status']=='COMPARED';p=root/('N3D-'+r['version'])/'unpacked_image.bin';v=p.read_bytes();files.append(dict(path=str(p),sha256=hashlib.sha256(v).hexdigest()));f=defs[r['function']];start,end,ip=(int(r[k]) for k in ('start','end_exclusive','ip'));rc,re,_,_=norm(b[f['start']:f['end_exclusive']],f['start']-0x11ee0);vc,ve,_,_=norm(v[start:end],ip);assert re==ve and len(rc)==len(vc);diffs=[i for i,(x,y) in enumerate(zip(rc,vc)) if x!=y];base='';ds='';table=''
 if f['name']=='crt_ftime_timeb10':
  assert set(diffs)<={0x85,0x86},diffs;base=int.from_bytes(v[start+0x85:start+0x87],'little');signature=bytes.fromhex('b430cd213c02730533c00650cbbf');hits=[i for i in range(len(v)) if v.startswith(signature,i)];assert len(hits)==1;ds=int.from_bytes(v[hits[0]+len(signature):hits[0]+len(signature)+2],'little');table=ds*16+base;assert v[table:table+26]==common
 else:assert not diffs
 rows.append(dict(version=r['version'],function=f['name'],remaining_normalized_difference_offsets=','.join('%02X'%i for i in diffs),startup_DS=ds,common_table_DS=base,common_table_image=table,scope='Indexed common-calendar address binding explains residual bytes; exact25B date/time wrappers; no DOS response/clock/TZ/Win16 equivalence'))
out.mkdir(exist_ok=True)
with (out/'table_bindings.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(comparisons=len(rows),remaining_differences_accounted=True,files=files+[dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (image,comparisons,comparisons.parent.parent/'audit_crt_ftime_versions.py',comparisons.parent.parent/'crt_ftime_replay/summary.json',Path(__file__))]);(out/'binding_summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'}))
