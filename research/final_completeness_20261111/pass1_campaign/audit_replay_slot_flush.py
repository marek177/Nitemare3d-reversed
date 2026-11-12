"""python audit_replay_slot_flush.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rs):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
rows=[];p=0x273c
for i in Decoder(16,b[0x273c:0x2771],ip=0x72c):
 assert not i.is_invalid and lookup[p]['bytes']==b[p:p+i.len].hex()
 rows.append(dict(cs=0x201,ip=i.ip,image_offset=p,bytes=b[p:p+i.len].hex(),instruction=fmt.format(i)));p+=i.len
assert p==0x2771 and rows[-1]['bytes']=='cb'
save('slot_pending_flush',rows)
contexts=[]
for r in old:
 if r['cs']==0xaea and 0x5d6<=r['ip']<0x60f:
  raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw
  i=Decoder(16,raw,ip=r['ip']).decode();assert i.len==len(raw) and not i.is_invalid
  contexts.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
save('slot_producer_context',contexts);rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];events_out=[]
for load,layout,resource_mode,fill_effect in itertools.product((0,0x1000),range(8),range(4),(0,1)):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for r in rel:struct.pack_into('<H',runtime,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));ds=load+0x2771;cs=load+0x201;fill=(load+0x768)*16+0x4d8;draw=(load+0x156)*16+0x5de
 # Only external callees replaced for this replay; the 53B sweep itself is original.
 u.mem_write(fill,b'\xcb');u.mem_write(draw,b'\xcb');start=0x50f2;initial=bytearray(1800);expected_events=[]
 flags=[];resource_values=[]
 for n in range(100):
  flag=([1,0,2,255,(n%2),[0,1,2,255][n%4],0 if n in (0,99) else 1,0 if n==99 else 1][layout]);flags.append(flag)
  rec=bytes(((n*13+j*7+3)&255) for j in range(18));initial[n*18:n*18+18]=rec;initial[n*18]=flag
  resource=0x8000+n*16;struct.pack_into('<H',initial,n*18+6,resource)
  value=[0,1,0x80000000,0xffffffff][resource_mode];resource_values.append(value);u.mem_write(ds*16+resource+6,struct.pack('<I',value))
  if flag==0:
   if value==0:expected_events.append(('fill',resource))
   expected_events.append(('draw',start+n*18))
 u.mem_write(ds*16+start-1,b'\xa5'+bytes(initial)+b'\x5a');expected=bytearray(initial)
 for n,f in enumerate(flags):
  if f==0:expected[n*18]=1
 observed=[]
 def hook(uc,address,size,user):
  if address not in (fill,draw):return
  ss=uc.reg_read(UC_X86_REG_SS);sp=uc.reg_read(UC_X86_REG_SP);arg=struct.unpack('<H',bytes(uc.mem_read(ss*16+sp+4,2)))[0];kind='fill' if address==fill else 'draw';observed.append((kind,arg))
  assert uc.reg_read(UC_X86_REG_DS)==ds
  if kind=='fill' and fill_effect:uc.mem_write(ds*16+arg+6,struct.pack('<I',0x12345678))
  if kind=='draw':assert bytes(uc.mem_read(ds*16+arg,1))==b'\0'
 u.hook_add(UC_HOOK_CODE,hook)
 for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
 u.mem_write(0x5ff00,struct.pack('<HH',0x6000,cs));u.emu_start(cs*16+0x72c,cs*16+0x6000,count=4000)
 assert observed==expected_events and bytes(u.mem_read(ds*16+start,1800))==bytes(expected)
 assert bytes(u.mem_read(ds*16+start-1,1))==b'\xa5' and bytes(u.mem_read(ds*16+start+1800,1))==b'\x5a'
 for n,value in enumerate(resource_values):
  wanted=0x12345678 if fill_effect and flags[n]==0 and value==0 else value
  assert struct.unpack('<I',bytes(u.mem_read(ds*16+0x8000+n*16+6,4)))[0]==wanted
 for reg,v in [(UC_X86_REG_DS,ds),(UC_X86_REG_SP,0xff04),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)]:assert u.reg_read(reg)==v
 case=len(cases);cases.append(dict(case=case,load=load,layout=layout,resource_mode=resource_mode,fill_effect=fill_effect,fill_calls=sum(k=='fill' for k,a in observed),draw_calls=sum(k=='draw' for k,a in observed),passed=True))
 events_out.extend(dict(case=case,order=n,callee=k,argument=a) for n,(k,a) in enumerate(observed))
save('cases',cases);save('callee_events',events_out)
save('bss_slot_layout',[
 dict(offset=0,width=1,type='BYTE_pending_zero_else_skip',evidence='0201:0734,0755; 0AEA:05D6,05DD',status='PARTIAL'),
 dict(offset=1,width=1,type='UNKNOWN',evidence='no access in audited producer/sweep',status='UNKNOWN'),
 dict(offset=2,width=4,type='FAR16_object_pointer_candidate',evidence='0AEA:05E0,05E4,05E7; renderer meaning not closed',status='PARTIAL'),
 dict(offset=6,width=2,type='NEAR16_resource_record_pointer',evidence='0AEA:05EE; 0201:0739,073C; 0156:05E7,05EF',status='PARTIAL'),
 *[dict(offset=o,width=2,type='WORD_renderer_parameter',evidence='0AEA producer 05F4..060C; exact semantic units open',status='PARTIAL') for o in (8,10,12,14,16)]])
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=[dict(name='slot_pending_flush',start=0x273c,end_exclusive=0x2771,instruction_bytes=53,instructions=len(rows))],cases=len(cases),cases_sha256=sha((out/'cases.csv').read_bytes()),failures=0,runtime_tests=0,new_deep_verified_bytes=0,typed_file_bytes=0,scope='native 100-slot sweep; resource-load and renderer callees mocked with RETF, optional resource pointer update; DS fixed in seeded replay, no renderer output or natural runtime proof')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
