"""DECODER EMULATOR OUT: original pending flush demonstrates DOS10 direct-draw difference."""
import csv,hashlib,json,struct,sys
from pathlib import Path
decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);cases=[];bindings=[];asm=[];files=[];sha=lambda b:hashlib.sha256(b).hexdigest()
for label in ('10','11','12','15','17','18','19','20'):
 image=root/('N3D-'+label)/'unpacked_image.bin';inventory=image.with_name('instructions.json');b=image.read_bytes();inv=json.loads(inventory.read_text(encoding='utf-8'));lookup={r['image_offset']:r for r in inv};hits=[]
 for pos,r in lookup.items():
  if b[pos:pos+3]==bytes.fromhex('5756be') and b[pos+5:pos+11]==bytes.fromhex('bf6400803c00'):hits.append(pos)
 assert len(hits)==1;(start,)=hits;entry=lookup[start];cs,ip=entry['cs'],entry['ip'];owner='%04X:%04X'%(cs,ip);end=max(r['image_offset']+len(bytes.fromhex(r['bytes'])) for r in inv if owner in r['owners']);slotbase=int.from_bytes(b[start+3:start+5],'little');callees=[]
 for i in Decoder(16,b[start:end],ip=ip):
  pos=cs*16+i.ip;raw=b[pos:pos+i.len];assert lookup[pos]['bytes']==raw.hex();asm.append(dict(version=label,cs=cs,ip=i.ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
  if i.flow_control==FlowControl.CALL:callees.append((i.far_branch_selector,i.far_branch16))
 assert len(callees)==(1 if label=='10' else 2);bindings.append(dict(version=label,cs=cs,ip=ip,start=start,end_exclusive=end,slotbase=slotbase,FAR_calls=len(callees),fetch_call_present=label!='10',renderer_CS=callees[-1][0],renderer_IP=callees[-1][1]))
 for pending in (0,255):
  for resident in (0,0x12345678):
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,b);ds=0x7000;record=0x8000;dg=bytearray([0x66]*0xe030);slots=bytearray([0x66]*1800)
   for n in range(100):slots[18*n]=1;struct.pack_into('<H',slots,18*n+6,record)
   slots[0]=pending;dg[slotbase:slotbase+1800]=slots;struct.pack_into('<I',dg,record+6,resident);u.mem_write(ds*16,bytes(dg));u.mem_write(ds*16+0xf000,struct.pack('<HH',0x100,0x5000));events=[];done=[]
   for reg,value in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,value)
   targets={s*16+p:('renderer' if n==len(callees)-1 else 'fetch') for n,(s,p) in enumerate(callees)}
   def hook(emu,address,size,data):
    if address==0x50100:done.append(True);emu.emu_stop();return
    if address not in targets:return
    name=targets[address];sp=emu.reg_read(UC_X86_REG_SP);retip,retcs,arg=struct.unpack('<3H',bytes(emu.mem_read(ds*16+sp,6)))
    assert arg==(record if name=='fetch' else slotbase)
    if name=='fetch':emu.mem_write(ds*16+record+6,struct.pack('<I',0xabcdef01))
    events.append(dict(kind=name,argument=arg,record_buffer=struct.unpack('<I',bytes(emu.mem_read(ds*16+record+6,4)))[0]));emu.reg_write(UC_X86_REG_SP,sp+4);emu.reg_write(UC_X86_REG_CS,retcs);emu.reg_write(UC_X86_REG_IP,retip)
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start(start,0xfffff,count=3000);assert done
   wanted=[] if pending else (['fetch','renderer'] if label!='10' and resident==0 else ['renderer']);assert [e['kind'] for e in events]==wanted
   expected=bytearray(dg)
   if not pending:expected[slotbase]=1
   if 'fetch' in wanted:struct.pack_into('<I',expected,record+6,0xabcdef01)
   assert bytes(u.mem_read(ds*16,len(dg)))==expected
   for reg,value in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xf004),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)]:assert u.reg_read(reg)==value
   cases.append(dict(version=label,pending_flag=pending,resident_pointer_hex='%08X'%resident,events=json.dumps(events),status='PASS'))
 files.extend(dict(path=str(p),sha256=sha(p.read_bytes())) for p in (image,inventory))
# DOS10 raw object loader03A? actual whole raw039C..042E returns allocated pixels without tag/free.
p=root/'N3D-10/instructions.json';inv=json.loads(p.read_text(encoding='utf-8'));v=(p.parent/'unpacked_image.bin').read_bytes();rawrows=[]
for r in inv:
 if r['cs']==0x273 and 0x39c<=r['ip']<0x42e:
  i=Decoder(16,bytes.fromhex(r['bytes']),ip=r['ip']).decode();assert v[r['image_offset']:r['image_offset']+i.len].hex()==r['bytes'];rawrows.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=r['bytes'],instruction=fmt.format(i)))
for name,rows in [('flush_cases',cases),('flush_bindings',bindings),('flush_instructions',asm),('DOS10_raw_object_loader',rawrows)]:
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='32separate original DOS pending-flush caller cases,load0/DS=SS7000,fetch/draw fixtures. DOS10 draws directly without resident-null fetch gate;11+ fetch when null. DOS10 rawloader039C retains allocated pointer;not proof of global cache absence,decoder parity or natural null source. No additions to centralDOS2case total.',files=files+[dict(path=str(Path(__file__).resolve()),sha256=sha(Path(__file__).read_bytes()))]);(out/'flush_cross_version_summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
