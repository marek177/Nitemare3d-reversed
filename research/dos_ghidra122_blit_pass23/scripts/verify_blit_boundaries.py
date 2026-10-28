from pathlib import Path
import json,csv,struct,itertools,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INSN,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];loc=next(x for x in json.loads((root/'pass18/evidence/text_layout.json').read_text())['locations'] if x['build']==v);entry,cs=struct.unpack_from('<HH',bytes.fromhex(loc['calls'][8]['bytes']),1);b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));body=[r for r in rows if r['address'].startswith(f'{cs:04x}:') and entry<=int(r['address'].split(':')[1],16)<entry+0x20];addresses=[struct.unpack_from('<H',bytes.fromhex(r['bytes']),1)[0] for r in body if r['bytes'].startswith('a1')];assert len(addresses)==2;primary,alternate=addresses;locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',page_globals=[hex(primary),hex(alternate)],exe_sha256=hashlib.sha256(b).hexdigest()))
 cases=[(x,y,page,stride,transparent,sourceoff,widtharg) for x,y in [(0,0),(1,7),(3,199),(319,199),(320,200),(65535,255),(4,256)] for page,stride,transparent,sourceoff,widtharg in itertools.product([0,1,65535],[3,5],[65535,31,255],[0x200,0xfffc],[0,99])]
 for x,y,page,stride,transparent,sourceoff,widtharg in cases:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));ds=q['actual_DS'];sp=0xe000;w=3;hh=2
  for i in range(32):u.mem_write(0x60000+((sourceoff+i)&65535),bytes([[10,31,255,40,50,60,70][i%7]]))
  u.mem_write(ds*16+primary,struct.pack('<H',0x7000));u.mem_write(ds*16+alternate,struct.pack('<H',0x8000));u.mem_write(ds*16+sp,struct.pack('<12H',0x600,0,sourceoff,0x6000,x,y,widtharg,stride,w,hh,page,transparent));state=dict(mask=0,writes=[])
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def port(uc,port,size,value,_):
   assert size==1 and port in [0x3c4,0x3c5]
   if port==0x3c4:assert value==2
   else:state['mask']=value&15
  def write(uc,access,a,size,value,_):
   if 0x70000<=a<0x90000:assert size==1;state['writes'].append((state['mask'],a,value))
  u.hook_add(UC_HOOK_INSN,port,None,1,0,UC_X86_INS_OUT);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(cs*16+entry,0x600,count=5000)
  destination=0x80000 if page else 0x70000;base=((y&255)*80+(x>>2))&65535;expected=[]
  for col in range(w):
   # Original mask starts at x low2; offset advances when the mask rotates past plane3.
   columnbyte=(base+((x&3)+col)//4)&65535
   for row in range(hh):
    value=u.mem_read(0x60000+((sourceoff+col*stride+row)&65535),1)[0]
    if transparent==65535 or value!=transparent:expected.append((1<<((x+col)&3),destination+((columnbyte+row*80)&65535),value))
  assert state['writes']==expected,(v,x,y,page,stride,transparent,sourceoff,widtharg,state['writes'],expected);assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,x=x,y=y,page=page,stride=stride,transparent=transparent,source_offset=sourceoff,source_width_argument=widtharg,writes=state['writes'],passed=True))
out=root/'pass23/evidence';out.mkdir(parents=True,exist_ok=True);(out/'blit_boundaries.json').write_text(json.dumps(dict(cases=len(results),scope='Original blitter; synthetic source, controlled page globals, observed OUT and memory-write trace. Nonzero draw3x2 only; no full VGA/DAC.',locations=locations,results=results),indent=2));print(len(results),'passed')
