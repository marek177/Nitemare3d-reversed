from pathlib import Path
import struct,json,csv,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
free_locations=json.loads((root/'pass15/evidence/mode4_owner.json').read_text())['locations']
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));lc,le=[int(x,16) for x in q['loader_entry'].split(':')];fc=[r for r in rows if r['address'].startswith(f'{lc:04x}:') and le<=int(r['address'].split(':')[1],16)<le+0x98 and r['bytes'].startswith('9a')];entry,cs=struct.unpack_from('<HH',bytes.fromhex(fc[2]['bytes']),1)
 def section(ip,n):return [r for r in rows if r['address'].startswith(f'{cs:04x}:') and ip<=int(r['address'].split(':')[1],16)<ip+n]
 body=section(entry,0x99);head=struct.unpack_from('<H',bytes.fromhex(next(r for r in body if r['bytes'].startswith('a1'))['bytes']),1)[0];handler=struct.unpack_from('<H',bytes.fromhex(next(r for r in body if r['bytes'].startswith('0b0e'))['bytes']),2)[0];nr=next(r for r in body if r['bytes'].startswith('e8'));nip=int(nr['address'].split(':')[1],16);growth=(nip+3+struct.unpack('<h',bytes.fromhex(nr['bytes'])[1:])[0])&65535;minimum=struct.unpack_from('<H',bytes.fromhex(next(r for r in section(growth,0x44) if r['bytes'].startswith('3b06'))['bytes']),2)[0];ds=q['actual_DS'];sp=0xe000
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',growth=f'{cs:04x}:{growth:04x}',heap_head_segment_address=hex(head),failure_handler_address=hex(handler),minimum_segment_address=hex(minimum),exe_sha256=hashlib.sha256(b).hexdigest()))
 free_cs,free_ip=[int(x,16) for x in next(x for x in free_locations if x['build']==v)['free'].split(':')]
 for a in [16,32,64,128,512]:
  for scenario in ['reuse_smaller','reuse_equal','too_large','coalesce','split','growth_failure_recover']:
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+handler,bytes(24));u.mem_write(ds*16+minimum-2,bytes(4));trace=[];calls=[];state=dict(fail_growth=False)
   def intr(uc,n,_):
    assert n==0x21 and uc.reg_read(UC_X86_REG_AH)==0x48;seg=0x5000+0x100*len(trace);trace.append(dict(paragraphs=uc.reg_read(UC_X86_REG_BX),segment=None if state['fail_growth'] else seg,failure=state['fail_growth']));uc.reg_write(UC_X86_REG_AX,8 if state['fail_growth'] else seg);uc.reg_write(UC_X86_REG_EFLAGS,(uc.reg_read(UC_X86_REG_EFLAGS)&~1)|state['fail_growth'])
   u.hook_add(UC_HOOK_INTR,intr)
   def call(ip,seg,args):
    u.mem_write(ds*16+sp,struct.pack('<HH',0x600,0)+args)
    for reg,val in [(UC_X86_REG_CS,seg),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
    u.emu_start(seg*16+ip,0x600,count=100000);assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
    return (u.reg_read(UC_X86_REG_DX)<<16)|u.reg_read(UC_X86_REG_AX)
   def alloc(size,allow_null=False):
    ptr=call(entry,cs,struct.pack('<H',size));assert ptr or allow_null;calls.append(dict(operation='alloc',size=size,pointer=hex(ptr),dos_blocks=len(trace)));return ptr
   def free(ptr):
    call(free_ip,free_cs,struct.pack('<I',ptr));calls.append(dict(operation='free',pointer=hex(ptr),dos_blocks=len(trace)))
   def phys(ptr):return (ptr>>16)*16+(ptr&65535)
   A=alloc(a);B=alloc(2);assert A==0x50000016 and B==A+a+2,(v,a,A,B)
   u.mem_write(phys(B),b'\x5a\xa5');free(A);before=len(trace)
   if scenario=='reuse_smaller':C=alloc(a//2);assert C==A and len(trace)==before
   elif scenario=='reuse_equal':C=alloc(a);assert C==A and len(trace)==before
   elif scenario=='too_large':C=alloc(a+2);assert C>>16==0x5100 and len(trace)==before+1
   elif scenario=='coalesce':
    free(B);C=alloc(a+2);assert C==A and len(trace)==before
   elif scenario=='growth_failure_recover':
    state['fail_growth']=True;C=alloc(a+2,True);assert C==0 and len(trace)==before+1;assert bytes(u.mem_read(phys(B),2))==b'\x5a\xa5';free(B);D=alloc(a+2);assert D==A and len(trace)==before+1
   else:
    C=alloc(a//2-2);D=alloc(a//2);assert C==A and D==A+a//2 and len(trace)==before
   if scenario not in ['coalesce','growth_failure_recover']:assert bytes(u.mem_read(phys(B),2))==b'\x5a\xa5'
   results.append(dict(build=v,initial_size=a,scenario=scenario,operations=calls,dos_allocations=trace,passed=True))
out=root/'pass16/evidence';out.mkdir(parents=True,exist_ok=True);(out/'allocator_reuse.json').write_text(json.dumps(dict(cases=len(results),scope='Original allocation/free routines and existing-heap search/split/coalesce. Only DOS INT21 allocation mocked; null failure handler, initially empty heap.',locations=locations,results=results),indent=2));print(len(results),'sequences passed')
