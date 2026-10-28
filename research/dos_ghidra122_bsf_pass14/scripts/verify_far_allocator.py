from pathlib import Path
import struct,json,csv,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));lc,le=[int(x,16) for x in q['loader_entry'].split(':')];fc=[r for r in rows if r['address'].startswith(f'{lc:04x}:') and le<=int(r['address'].split(':')[1],16)<le+0x98 and r['bytes'].startswith('9a')];entry,cs=struct.unpack_from('<HH',bytes.fromhex(fc[2]['bytes']),1)
 def section(ip,n):return [r for r in rows if r['address'].startswith(f'{cs:04x}:') and ip<=int(r['address'].split(':')[1],16)<ip+n]
 body=section(entry,0x99);head=struct.unpack_from('<H',bytes.fromhex(next(r for r in body if r['bytes'].startswith('a1'))['bytes']),1)[0];handler=struct.unpack_from('<H',bytes.fromhex(next(r for r in body if r['bytes'].startswith('0b0e'))['bytes']),2)[0];nr=next(r for r in body if r['bytes'].startswith('e8'));nip=int(nr['address'].split(':')[1],16);growth=(nip+3+struct.unpack('<h',bytes.fromhex(nr['bytes'])[1:])[0])&65535;minimum=struct.unpack_from('<H',bytes.fromhex(next(r for r in section(growth,0x44) if r['bytes'].startswith('3b06'))['bytes']),2)[0];ds=q['actual_DS'];sp=0xe000
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',growth=f'{cs:04x}:{growth:04x}',heap_head_segment_address=hex(head),failure_handler_address=hex(handler),minimum_segment_address=hex(minimum),exe_sha256=hashlib.sha256(b).hexdigest()))
 for size,fail in itertools.product([0,1,2,52,53,54,512,32767,0xffe8,0xffe9,0xffff],[False,True]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+handler,bytes(24));u.mem_write(ds*16+minimum-2,bytes(4));u.mem_write(ds*16+sp,struct.pack('<3H',0x600,0,size));trace=[]
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def intr(uc,n,_):
   assert n==0x21 and uc.reg_read(UC_X86_REG_AH)==0x48;trace.append(uc.reg_read(UC_X86_REG_BX));uc.reg_write(UC_X86_REG_AX,8 if fail else 0x5000);uc.reg_write(UC_X86_REG_EFLAGS,(uc.reg_read(UC_X86_REG_EFLAGS)&~1)|fail)
  u.hook_add(UC_HOOK_INTR,intr);u.emu_start(cs*16+entry,0x600,count=100000)
  result=(u.reg_read(UC_X86_REG_DX)<<16)|u.reg_read(UC_X86_REG_AX);expected=0 if fail or size>0xffe8 else 0x50000016;assert result==expected,(v,size,fail,trace,hex(result))
  assert len(trace)==(0 if size>0xffe8 else 1);assert u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_CS)==0
  word=struct.unpack('<H',u.mem_read(0x50014,2))[0] if result else None
  if result:assert word==((size+1)&0xfffe),(v,size,word)
  results.append(dict(build=v,requested=size,dos_allocation_failure=fail,dos_paragraph_requests=trace,returned_DXAX=hex(result),allocated_header_word=word,passed=True))
out=root/'pass14/evidence';out.mkdir(parents=True,exist_ok=True);(out/'far_allocator.json').write_text(json.dumps(dict(cases=len(results),scope='Original far allocator, heap initialization and first-block split; empty heap and null failure handler; only DOS INT21 allocation mocked.',locations=locations,results=results),indent=2));print(len(results),'passed')
