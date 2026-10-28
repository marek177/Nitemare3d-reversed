from pathlib import Path
import csv,json,struct,itertools,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
def s16(x):return ((x+32768)&65535)-32768
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];blit=next(x for x in json.loads((root/'pass23/evidence/blit_boundaries.json').read_text())['locations'] if x['build']==v)['entry'];rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));candidates=[]
 for i,r in enumerate(rows):
  a=[x['bytes'] for x in rows[i:i+7]]
  if len(a)<7:continue
  if a[:5]==['c8020000','57','56','8b760a','8b7e08']:candidates.append(('dual',i))
  if a[:5]==['55','8bec','57','56','8b760a'] and a[5].startswith('a1') and a[6]=='2b4608':candidates.append(('split',i))
 selected={}
 for kind,i in candidates:
  cs,entry=[int(x,16) for x in rows[i]['address'].split(':')];body=[]
  for r in rows[i:]:
   if not r['address'].startswith(f'{cs:04x}:'):break
   body.append(r)
   if r['bytes']=='cb':break
  calls=[r for r in body if blit in r['targets'] and 'CALL' in r['flow']]
  if len(calls)==2:assert kind not in selected;selected[kind]=(cs,entry,body,calls)
 assert set(selected)=={'dual','split'},(v,selected)
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 ds=q['actual_DS'];sp=0xe000
 for kind,(cs,entry,body,calls) in selected.items():
  boundaryaddr=struct.unpack_from('<H',bytes.fromhex(next(r for r in body if r['bytes'].startswith('a1'))['bytes']),1)[0] if kind=='split' else None;sites={cs*16+int(r['address'].split(':')[1],16):r for r in calls};locations.append(dict(build=v,kind=kind,entry=f'{cs:04x}:{entry:04x}',boundary_global=hex(boundaryaddr) if boundaryaddr else None,instructions=body,exe_sha256=hashlib.sha256(b).hexdigest()))
  tests=itertools.product([-32768,-1,0,198,199,200,32767],[0,1,2,255],[0,1,255],[0,198,199,255] if kind=='split' else [None],[31,65535] if kind=='split' else [65535])
  for y,height,width,boundary,transparent in tests:
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+0x9000,bytes([width,height])+bytes(4)+struct.pack('<I',0x6000fffc));u.mem_write(ds*16+sp,struct.pack('<6H',0x600,0,319,y&65535,0x9000,transparent));trace=[]
   if boundaryaddr:u.mem_write(ds*16+boundaryaddr,struct.pack('<H',boundary))
   for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
   def hook(uc,a,n,_):
    if a not in sites:return
    trace.append(list(struct.unpack('<10H',uc.mem_read(ds*16+uc.reg_read(UC_X86_REG_SP),20))));uc.reg_write(UC_X86_REG_IP,a-cs*16+5)
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+entry,0x600,count=1000)
   def args(src,yy,hh,page,t):return [src&65535,0x6000,319,yy&65535,width,height,width,hh&65535,page,t]
   if kind=='dual':expected=[args(0xfffc,y,height,0,65535),args(0xfffc,y,height,1,65535)] if s16(y+height)<200 else []
   else:
    n=min(s16(boundary-y+1),height);expected=([args(0xfffc,y,n,0,transparent)] if n>0 else [])+([args(0xfffc+n,y+n,height-n,0,65535)] if height>n else [])
   assert trace==expected,(v,kind,y,height,width,boundary,trace,expected);assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
   results.append(dict(build=v,kind=kind,y=y,width=width,height=height,boundary=boundary,transparent=transparent,blit_arguments=trace,passed=True))
out=root/'pass25/evidence';(out/'blit_callers.json').write_text(json.dumps(dict(cases=len(results),scope='Original two caller wrappers, blitter call interception only. Tests assert exact20-byte argument blocks and far return; no pixel writes/full VGA or caller reachability.',locations=locations,results=results),indent=2));print(len(results),'passed')
