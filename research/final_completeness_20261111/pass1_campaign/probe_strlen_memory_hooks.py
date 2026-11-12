"""IMAGE RELOCS NATIVE_DS64 DECODER EMULATOR OUT: isolate callback sensitivity."""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,relocs,snapshot,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();load=0x824;ds=load+0x2771;cs=load+0x11ee;b=bytearray(image.read_bytes());assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',b,int(r['image_offset']),(int(r['original_word'])+load)&65535)
rows=[]
for mode in ('none','read','write','read_write','read_string_only','read_return_frame_only'):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,bytes(b));u.mem_write(ds*16,snapshot.read_bytes());u.mem_write(ds*16+0xe768,struct.pack('<3H',0x100,0x5000,0x24a2))
 for reg,value in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,0x2398),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,ds),(UC_X86_REG_SP,0xe768),(UC_X86_REG_BP,0xe770),(UC_X86_REG_SI,0x1234),(UC_X86_REG_DI,0x2345),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,value)
 seen=[];mem=[];done=[]
 def code(emu,address,size,data):
  seen.append(address)
  if address==0x50100:done.append(True);emu.emu_stop()
 def memory(emu,access,address,size,value,data):mem.append((access,address,size))
 u.hook_add(UC_HOOK_CODE,code)
 if mode=='read_string_only':u.hook_add(UC_HOOK_MEM_READ,memory,begin=ds*16+0x24a2,end=ds*16+0x24a4)
 elif mode=='read_return_frame_only':u.hook_add(UC_HOOK_MEM_READ,memory,begin=ds*16+0xe768,end=ds*16+0xe76b)
 elif mode!='none':u.hook_add({'read':UC_HOOK_MEM_READ,'write':UC_HOOK_MEM_WRITE,'read_write':UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE}[mode],memory)
 error=None
 try:u.emu_start(cs*16+0x2398,0xfffff,count=80)
 except Exception as e:error=repr(e)
 rows.append(dict(mode=mode,returned=bool(done),AX=u.reg_read(UC_X86_REG_AX),SP=u.reg_read(UC_X86_REG_SP),CS=u.reg_read(UC_X86_REG_CS),IP=u.reg_read(UC_X86_REG_IP),instructions=len(seen),memory_callbacks=len(mem),error=error,expected_return_AX2=bool(done) and u.reg_read(UC_X86_REG_AX)==2,trace=[hex(p-load*16) for p in seen[:30]]))
out.mkdir(exist_ok=True);s=dict(probe=rows,scope='Synthetic isolated original strlen with native DS snapshot; not extra central analytical or native scenarios. Investigates instrumentation sensitivity only.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,relocs,snapshot,Path(__file__))]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps(rows,indent=2))
