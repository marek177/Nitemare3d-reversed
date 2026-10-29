from pathlib import Path
import csv,json,struct,hashlib,random
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
def s16(n):return (n+32768)%65536-32768
targets=[(42 if i&4 else 0,42 if i&2 else 0,42 if i&1 else 0) if i<8 else (63 if i&4 else 21,63 if i&2 else 21,63 if i&1 else 21) for i in range(16)];targets[6]=(42,21,0)
rng=random.Random(42);palettes={}
palettes['exact_with_ties']=[(10,10,10)]*256
for i,t in enumerate(targets):palettes['exact_with_ties'][200+i]=t
palettes['exact_with_ties'][3]=targets[2]
palettes['grayscale']=[(i%64,)*3 for i in range(256)];palettes['random6']=[tuple(rng.randrange(64) for _ in range(3)) for i in range(256)];palettes['zero']=[(0,0,0)]*256;palettes['bytes8']=[tuple(rng.randrange(256) for _ in range(3)) for i in range(256)]
meta=json.loads((root/'pass41/evidence/map_effect.json').read_text())['locations']
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];m=next(x for x in meta if x['build']==v);ds=q['actual_DS'];cb=bytes.fromhex(next(r['bytes'] for r in m['instructions'] if r['bytes'].startswith('9a')));cs=int.from_bytes(cb[3:],'little');entry=int.from_bytes(cb[1:3],'little');rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));idx=next(i for i,r in enumerate(rows) if r['address']==f'{cs:04x}:{entry:04x}');body=[]
 for r in rows[idx:]:
  body.append(r)
  if r['bytes']=='cb':break
 src=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('be')))[1:],'little');dirty=int(m['palette_dirty'],16);lookup=int(m['palette_lookup'],16)
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',source_palette=hex(src),lookup=hex(lookup),dirty=hex(dirty),instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 for name,pal in palettes.items():
  expected=[]
  for t in targets:
   scores=[s16(sum((c-d)**2 for c,d in zip(rgb,t))) for rgb in pal];best=32767;winner=None
   for j,score in enumerate(scores):
    if score<best:best=score;winner=j
   assert winner is not None;expected.append(winner)
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xe000;u.mem_write(ds*16+src,bytes(c for rgb in pal for c in rgb));u.mem_write(ds*16+lookup,b'\xa5'*16);u.mem_write(ds*16+dirty,b'\xff')
  def run(index):
   u.mem_write(ds*16+sp,struct.pack('<3H',0x600,0,index))
   for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
   u.emu_start(cs*16+entry,0x600,count=500000);assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds;return u.reg_read(UC_X86_REG_AX)&255
  assert run(0)==expected[0];actual=list(u.mem_read(ds*16+lookup,16));assert actual==expected,(v,name,actual,expected);assert bytes(u.mem_read(ds*16+dirty,1))==b'\0'
  assert [run(i) for i in range(16)]==expected and run(256)==expected[0]
  u.mem_write(ds*16+src,b'\0'*768);assert [run(i) for i in range(16)]==expected # dirty0 intentionally caches despite palette mutation
  u.mem_write(ds*16+dirty,b'\x01');assert run(0)==0 and bytes(u.mem_read(ds*16+lookup,16))==b'\0'*16
  results.append(dict(build=v,palette=name,palette_sha256=hashlib.sha256(bytes(c for rgb in pal for c in rgb)).hexdigest(),lookup=actual,cache_preserved_after_source_mutation=True,regenerated_zero_lookup=True,passed=True))
(root/'pass42/evidence/palette.json').write_text(json.dumps(dict(cases=len(results),original_calls_per_case=35,targets=targets,scope='Complete original palette accessor and squared-distance helper; two regenerations and cached reads per scenario, no mocks. Six-bit palettes plus explicit eight-bit overflow probe.',locations=locations,results=results),indent=2));print(len(results),'passed;',len(results)*35,'original accessor calls')
