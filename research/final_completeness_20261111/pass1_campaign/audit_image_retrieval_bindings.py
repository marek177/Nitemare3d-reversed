"""IMAGE COMPARISONS DECODER OUT: explain retained normalization differences."""
import csv,hashlib,json,sys
from pathlib import Path
image,comparisons,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()))
from iced_x86 import Decoder,FlowControl,Formatter,FormatterSyntax,Register
fmt=Formatter(FormatterSyntax.INTEL);b=image.read_bytes();out.mkdir(exist_ok=True)
# Keep the exact normalization function shared with the version audit.
source=(comparisons.parent.parent/'audit_image_retrieval_versions.py').read_text(encoding='utf-8')
exec(source[source.index('def norm('):source.index("for label in (")],globals())
root=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');rows=[];files=[]
for r in csv.DictReader(comparisons.open(encoding='utf-8')):
 if r['status']!='COMPARED':continue
 p=root/('N3D-'+r['version'])/'unpacked_image.bin';v=p.read_bytes();files.append(dict(path=str(p),sha256=hashlib.sha256(v).hexdigest()))
 start,end,ip=map(lambda k:int(r[k]),('start','end_exclusive','ip'));ref=0x79d0 if r['function']=='xms_read_to_conventional' else 0x7a82;refend=0x7a4e if ref==0x79d0 else 0x7b57
 rc,re,_,_=norm(b[ref:refend],ref-0x7680);vc,ve,_,_=norm(v[start:end],ip);assert len(rc)==len(vc) and re==ve
 diffs=[i for i,(x,y) in enumerate(zip(rc,vc)) if x!=y]
 if ref==0x79d0:
  assert set(diffs)<={0x65,0x66,0x75,0x76}, (r['version'],diffs); requestbase=int.from_bytes(v[start+0x65:start+0x67],'little'); diagnostic= int.from_bytes(v[start+0x75:start+0x77],'little')
  for delta,field in ((0x3a,0),(0x3e,2),(0x46,4),(0x4e,6),(0x53,10),(0x5e,12)):
   ins=Decoder(16,v[start+delta:end],ip=ip+delta).decode();assert ins.memory_displacement==requestbase+field
  rows.append(dict(version=r['version'],function=r['function'],request_descriptor_offset=requestbase,unmasked_difference_offsets=','.join('%02X'%i for i in diffs),diagnostic_near_offset=diagnostic,slot_table_start='',slot_table_end='',slot_count='',scope='Differences confined to request-offset and diagnostic PUSH immediates; six descriptor field writes checked against request base, message/callee semantics not inferred'))
 else:
  assert set(diffs)<={0x17,0x18,0x37,0x38,0x93}, (r['version'],diffs)
  a=int.from_bytes(v[start+0x17:start+0x19],'little');z=int.from_bytes(v[start+0x37:start+0x39],'little');assert z-a==40
  rows.append(dict(version=r['version'],function=r['function'],request_descriptor_offset='',unmasked_difference_offsets=','.join('%02X'%i for i in diffs),diagnostic_near_offset='',slot_table_start=a,slot_table_end=z,slot_count=(z-a)//4,scope='Differences confined to pointer-vector immediates and excluded inventory-gap BYTE; ten slots retained, not whole behavioral parity'))
with (out/'binding_differences.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
proof=dict(comparisons=len(rows),all_remaining_differences_accounted=True,scope='Exact normalization retained; request-offset/diagnostics/vector-address immediates and inventory-gap differences explained, not silently masked into equivalence',files=files+[dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (image,comparisons,comparisons.parent.parent/'audit_image_retrieval_versions.py',Path(__file__))])
(out/'binding_summary.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in proof.items() if k!='files'}))
