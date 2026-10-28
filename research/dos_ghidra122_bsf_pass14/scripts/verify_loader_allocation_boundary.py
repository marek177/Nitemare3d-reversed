from pathlib import Path
import struct,json,csv,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
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
 for length,fail in itertools.product([0,1,0xffe7,0xffe8,0xfffe,0xffff],[False,True]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(0x50000,b'\xa5'*65536);u.mem_write(ds*16+handler,bytes(24));u.mem_write(ds*16+minimum-2,bytes(4));u.mem_write(ds*16+sp,struct.pack('<HHHIH',0x600,0,0x9100,54,length));state=dict(requested=None,dos_paragraphs=[],read_length=None,nul_writes=[],phase=None,stopped=None)
  for reg,val in [(UC_X86_REG_CS,lc),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  kinds={lc*16+int(r['address'].split(':')[1],16):k for r,k in zip(fc,['open','open_error','alloc','alloc_error','seek','read','close','decoder'])}
  def intr(uc,n,_):
   assert n==0x21 and uc.reg_read(UC_X86_REG_AH)==0x48;state['dos_paragraphs'].append(uc.reg_read(UC_X86_REG_BX));uc.reg_write(UC_X86_REG_AX,8 if fail else 0x5000);uc.reg_write(UC_X86_REG_EFLAGS,(uc.reg_read(UC_X86_REG_EFLAGS)&~1)|fail)
  def writes(uc,access,address,size,value,_):
   if state['phase']=='read' and size==1 and value==0:state['nul_writes'].append(address)
  def hook(uc,a,n,_):
   if a not in kinds:return
   kind=kinds[a];stack=ds*16+uc.reg_read(UC_X86_REG_SP)
   if kind=='open':uc.reg_write(UC_X86_REG_AX,3)
   elif kind=='alloc':state['requested']=struct.unpack('<H',uc.mem_read(stack,2))[0];return
   elif kind.endswith('_error'):state['stopped']=kind;uc.emu_stop();return
   elif kind=='seek':pass
   elif kind=='read':
    handle,off,seg,count=struct.unpack('<4H',uc.mem_read(stack,8));assert (handle,off,seg,count)==(3,0x16,0x5000,length);state['read_length']=count;state['phase']='read';uc.reg_write(UC_X86_REG_AX,0)
   elif kind=='close':pass
   elif kind=='decoder':
    off,seg,count=struct.unpack('<3H',uc.mem_read(stack,6));assert (off,seg,count)==(0x16,0x5000,length);state['stopped']='before_decoder';uc.emu_stop();return
   uc.reg_write(UC_X86_REG_IP,a-lc*16+5)
  u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,writes);u.emu_start(lc*16+le,0x600,count=100000)
  requested=(length+1)&65535;rejected=fail or requested>0xffe8;assert state['requested']==requested
  assert state['stopped']==('alloc_error' if rejected else 'before_decoder'),(v,length,fail,state)
  if rejected:assert state['nul_writes']==[] and state['read_length'] is None
  else:
   target=0x50000+((0x16+length)&65535);assert state['nul_writes']==[target] and u.mem_read(target,1)[0]==0,(v,length,state)
  results.append(dict(build=v,length=length,dos_allocation_failure=fail,**state,passed=True))
out=root/'pass14/evidence';out.mkdir(parents=True,exist_ok=True);(out/'loader_allocation_boundary.json').write_text(json.dumps(dict(cases=len(results),scope='Original loader and allocator through terminator write, stopped before decoder or fatal allocation callee. DOS allocation and open/seek/read/close mocked; read returns0.',locations=locations,results=results),indent=2));print(len(results),'passed')
