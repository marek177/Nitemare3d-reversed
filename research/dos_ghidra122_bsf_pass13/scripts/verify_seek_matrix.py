from pathlib import Path
import json,csv,struct,itertools,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=16*seg+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));lc,le=[int(x,16) for x in q['loader_entry'].split(':')];fc=[r for r in rows if r['address'].startswith(f'{lc:04x}:') and le<=int(r['address'].split(':')[1],16)<le+0x98 and r['bytes'].startswith('9a')];entry,cs=struct.unpack_from('<HH',bytes.fromhex(fc[4]['bytes']),1)
 body=[r for r in rows if r['address'].startswith(f'{cs:04x}:') and entry<=int(r['address'].split(':')[1],16)<entry+0x82];cmp=next(bytes.fromhex(r['bytes']) for r in body if r['bytes'].startswith('3b1e'));maxaddr=struct.unpack_from('<H',cmp,2)[0];guardrow=next(bytes.fromhex(r['bytes']) for r in body if r['bytes'].startswith('833e'));guardaddr=struct.unpack_from('<H',guardrow,2)[0];ds=q['actual_DS'];sp=0xe000
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',negative_guard_address=hex(guardaddr),maxhandle_address=hex(maxaddr),exe_sha256=hashlib.sha256(b).hexdigest()))
 for origin,offset,guard,handle,error in itertools.product([0,1,2],[0,1,0xffff,0x10000,0x7fffffff,0x80000000,0xffffffff],[0,1],[5,25],[0,5]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+sp,struct.pack('<HHHIH',0x600,0,handle,offset,origin));u.mem_write(ds*16+maxaddr,struct.pack('<H',20));u.mem_write(ds*16+guardaddr,struct.pack('<H',guard));u.mem_write(ds*16+maxaddr+2+handle,b'\xa7');state=dict(position=100,trace=[])
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def intr(uc,n,_):
   ax=uc.reg_read(UC_X86_REG_AX);assert n==0x21 and ax>>8==0x42 and uc.reg_read(UC_X86_REG_BX)==handle
   mode=ax&255;raw=(uc.reg_read(UC_X86_REG_CX)<<16)|uc.reg_read(UC_X86_REG_DX);signed=raw if raw<0x80000000 else raw-0x100000000;target=[0,state['position'],1000][mode]+signed;failure=error or (5 if target<0 else 0)
   state['trace'].append(dict(origin=mode,offset=raw,target=target,error=failure))
   if failure:uc.reg_write(UC_X86_REG_AX,failure)
   else:state['position']=target;uc.reg_write(UC_X86_REG_AX,target&65535);uc.reg_write(UC_X86_REG_DX,(target>>16)&65535)
   uc.reg_write(UC_X86_REG_EFLAGS,(uc.reg_read(UC_X86_REG_EFLAGS)&~1)|bool(failure))
  u.hook_add(UC_HOOK_INTR,intr);u.emu_start(cs*16+entry,0x600,count=20000)
  signed=offset if offset<0x80000000 else offset-0x100000000;target=[0,100,1000][origin]+signed;failed=handle>=20 or bool(error) or target<0
  actual=(u.reg_read(UC_X86_REG_DX)<<16)|u.reg_read(UC_X86_REG_AX);assert actual==(0xffffffff if failed else target),(v,origin,offset,guard,error,state,hex(actual))
  flags=u.mem_read(ds*16+maxaddr+2+handle,1)[0];assert flags==(0xa7 if failed else 0xa5)
  assert state['position']==(100 if failed else target),(v,origin,offset,guard,error,state)
  assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4
  results.append(dict(build=v,origin=origin,offset=offset,negative_guard=guard,handle=handle,injected_error=error,returned_DXAX=actual,handle_flags=flags,**state,passed=True))
out=root/'pass13/evidence';out.mkdir(parents=True,exist_ok=True);(out/'seek_matrix.json').write_text(json.dumps(dict(cases=len(results),scope='Original complete CRT seek; DOS INT21 seek simulated with position100,length1000; nonnegative 32-bit positions accepted. No actual DOS.',locations=locations,results=results),indent=2));print(len(results),'passed')
