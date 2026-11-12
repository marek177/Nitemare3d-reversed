"""IMAGE INVENTORY DECODER EMULATOR OUT: original count-calculation prefix only."""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);witness=[]
for lo,hi in ((0x40,0xbe),(0xce,0x167)):
 for i in Decoder(16,b[0x7680+lo:0x7680+hi],ip=lo):
  p=0x7680+i.ip;raw=b[p:p+i.len];assert old[p]['bytes']==raw.hex();witness.append(dict(cs=0x768,ip=i.ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
def save(name,rows):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save('allocation_producer_witness',witness);cases=[];rel=list(csv.DictReader((image.parent/'relocations.csv').open()))
for load in (0x824,0x1000):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 for kib in range(1024):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,bytes(raw));ds=load+0x2771;dg=bytearray([0x66]*0xe030);struct.pack_into('<H',dg,0x3cb4,kib);u.mem_write(ds*16,bytes(dg))
  for reg,val in [(UC_X86_REG_CS,load+0x768),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xf000),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
  n=(abs(kib-70)*1024//3074)*(-1 if kib<70 else 1);count=min(n,128);diagnostic=count<1;stop=[]
  def hook(emu,address,size,data):
   if address==(load+0x768)*16+0x11e:assert not diagnostic;stop.append('loop_entry');emu.emu_stop()
   elif address==(load+0xfba)*16+0xc:
    assert diagnostic;sp=emu.reg_read(UC_X86_REG_SP);assert struct.unpack('<H',bytes(emu.mem_read(ds*16+sp+4,2)))[0]==0xbee;stop.append('diagnostic');emu.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((load+0x768)*16+0xce,0xfffff,count=200);expected=bytearray(dg);struct.pack_into('<H',expected,0x3504,count&65535);assert stop and bytes(u.mem_read(ds*16,len(dg)))==expected
  if not diagnostic:assert u.reg_read(UC_X86_REG_SP)==0xf000
  cases.append(dict(load=load,probe_KiB=kib,unclamped_count=n,final_signed_count=count,allocation_request_bytes=3074,diagnostic=diagnostic,status='PASS'))
save('cases',cases);s=dict(functions=[],cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='Original0768:00CE..011E count prefix only;2048inputs,signed truncate((KiB-70)*1024/3074),uppercap128,diagnostic count<1. Allocation/whole0024 lifecycle not executed; witness confirms3074B allocations and firstWORD0 initialization.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,image.parent/'relocations.csv',Path(__file__))]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
