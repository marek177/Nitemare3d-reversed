from pathlib import Path
import json,csv,struct,itertools,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];loc=next(x for x in json.loads((root/'pass10/evidence/checksum_open_locations.json').read_text()) if x['build']==v);b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=16*seg+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));vc,ve=[int(x,16) for x in loc['entry'].split(':')];cb=int(q['callback_entry'].split(':')[1],16);calls=[r for r in rows if r['address'].startswith(f'{vc:04x}:') and ve<=int(r['address'].split(':')[1],16)<cb and r['bytes'].startswith('9a')];raw=bytes.fromhex(calls[-1]['bytes']);entry,cs=struct.unpack_from('<HH',raw,1)
 def section(ip,n):return [r for r in rows if r['address'].startswith(f'{cs:04x}:') and ip<=int(r['address'].split(':')[1],16)<ip+n]
 near=[r for r in section(entry,0x60) if r['bytes'].startswith('e8')];r=near[1];ip=int(r['address'].split(':')[1],16);cleanup=(ip+3+struct.unpack('<h',bytes.fromhex(r['bytes'])[1:])[0])&65535;fc=next(r for r in section(cleanup,0x2c) if r['bytes'].startswith('9a'));freesite=cs*16+int(fc['address'].split(':')[1],16)
 ds=q['actual_DS'];stream=int(loc['stream_table'],16);extra=int(loc['extra_table'],16);maxaddr=int(loc['maxhandle_address'],16);sp=0xe000
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',cleanup=f'{cs:04x}:{cleanup:04x}',free_callsite=fc['address'],exe_sha256=hashlib.sha256(b).hexdigest()))
 for flags,error,handle in itertools.product([0,1,5,9,0x19,0x29,0x41,0x49],[0,5],[5,25]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+sp,struct.pack('<3H',0x600,0,stream));u.mem_write(ds*16+stream,struct.pack('<HHHBB',0x9403,3,0x9400,flags,handle));u.mem_write(ds*16+extra,bytes(8));u.mem_write(ds*16+maxaddr,struct.pack('<H',20));u.mem_write(ds*16+maxaddr+2+handle,b'\xa5')
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  freed=[];trace=[]
  def hook(uc,a,n,_):
   if a==freesite:
    ptr=struct.unpack('<H',uc.mem_read(ds*16+uc.reg_read(UC_X86_REG_SP),2))[0];assert ptr==0x9400;freed.append(ptr);uc.reg_write(UC_X86_REG_IP,a-cs*16+5)
  def intr(uc,n,_):
   ax=uc.reg_read(UC_X86_REG_AX);assert n==0x21 and ax>>8==0x3e and uc.reg_read(UC_X86_REG_BX)==handle;trace.append(hex(ax));uc.reg_write(UC_X86_REG_AX,error);uc.reg_write(UC_X86_REG_EFLAGS,(uc.reg_read(UC_X86_REG_EFLAGS)&~1)|bool(error))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,intr);u.emu_start(cs*16+entry,0x600,count=20000)
  active=bool(flags&0x83) and not flags&0x40;failed=not active or bool(error) or handle>=20;ax=u.reg_read(UC_X86_REG_AX);assert ax==(65535 if failed else 0)
  ptr,count,base,finalflag,hnd=struct.unpack('<HHHBB',u.mem_read(ds*16+stream,8));assert finalflag==0 and hnd==handle
  assert len(trace)==(1 if active and handle<20 else 0);assert freed==([0x9400] if active and flags&8 else [])
  expected=(0,0,0) if active and flags&8 else ((0x9400,0,0x9400) if active else (0x9403,3,0x9400));assert (ptr,count,base)==expected
  hf=u.mem_read(ds*16+maxaddr+2+handle,1)[0];assert hf==(0 if active and not error and handle<20 else 0xa5)
  assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4
  results.append(dict(build=v,initial_flags=hex(flags),dos_close_error=error,handle=handle,returned_AX=ax,final_flags=finalflag,final_pointer=ptr,final_count=count,final_base=base,handle_flags=hf,freed=freed,dos_trace=trace,passed=True))
out=root/'pass12/evidence';out.mkdir(parents=True,exist_ok=True);(out/'fclose_matrix.json').write_text(json.dumps(dict(cases=len(results),scope='Original fclose/flush/cleanup/low-level close and return/error code; only free and DOS INT21 close mocked. Read streams, temporary-file field0.',locations=locations,results=results),indent=2));print(len(results),'passed')
