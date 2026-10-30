from pathlib import Path
import json,struct,csv
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass78/evidence';o.mkdir(parents=True,exist_ok=True);spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));loc=json.load(open(r/'pass75/evidence/parser_locations.json'));results=[];locations=[]
fixtures=[('%d','123',1,123),('%d','-123',1,(-123)&65535),('%d',' +42tail',1,42),('%d','0x10',1,0),('%d','bad',0,None),('%d','',65535,None),('%d','   ',65535,None),('%d','+',65535,None),('%d','32768',1,32768),('%d','65535',1,65535),('%d','65536',1,0),('%d','-32769',1,32767),('%x','ff',1,255),('%x','0x1234',1,0x1234),('%x','ffff',1,65535),('%x','10000',1,0),('%x','-1',1,65535),('%x','bad',1,0xbad),('%x','z',0,None),('%x','',65535,None)]
for l in loc:
 v=l['build'];allrows=list(csv.DictReader(open(r/f'baseline58/pass7/audit/DOS{v}/instructions.tsv'),delimiter='\t'));rows=next(x['instructions'] for x in json.load(open(r/'pass75/evidence/parser_instructions.json')) if x['build']==v);align=int(l['align_instruction'].split(':')[1],16);call=max((q for q in rows if q['bytes'].startswith('9a') and int(q['address'].split(':')[1],16)<align),key=lambda q:int(q['address'].split(':')[1],16));cb=bytes.fromhex(call['bytes']);cs=int.from_bytes(cb[3:5],'little');ip=int.from_bytes(cb[1:3],'little');entry=f'{cs:04x}:{ip:04x}'
 def body(e):
  i=next(i for i,q in enumerate(allrows) if q['address']==e);out=[]
  for q in allrows[i:]:
   out.append(q)
   if q['bytes']=='cb':break
  return out
 wrapper=body(entry);corecall=[q for q in wrapper if q['bytes'].startswith('9a')][-1];z=bytes.fromhex(corecall['bytes']);core=f'{int.from_bytes(z[3:5],"little"):04x}:{int.from_bytes(z[1:3],"little"):04x}';corebody=body(core);guardcall=next(q for q in corebody[:12] if q['bytes'].startswith('9a'));z=bytes.fromhex(guardcall['bytes']);guard=f'{int.from_bytes(z[3:5],"little"):04x}:{int.from_bytes(z[1:3],"little"):04x}';gi=next(i for i,q in enumerate(allrows) if q['address']==guard);limit=int.from_bytes(bytes.fromhex(next(q['bytes'] for q in allrows[gi:gi+20] if q['bytes'].startswith('3b1e')))[2:4],'little');ds=next(s['actual_DS'] for s in spec if s['build']==v);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);pos=seg*16+off;struct.pack_into('<H',p,pos,(struct.unpack_from('<H',p,pos)[0]+4096)&65535)
 locations.append(dict(build=v,entry=entry,core=core,guard=guard,stack_limit_global=hex(limit),fixture_stack_limit='0x8000',wrapper_instructions=wrapper,guard_instructions=allrows[gi:gi+20]))
 for fmt,string,ret,val in fixtures:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+limit,struct.pack('<H',0x8000));u.mem_write(ds*16+0x5000,string.encode()+b'\0');u.mem_write(ds*16+0x5100,fmt.encode()+b'\0');u.mem_write(ds*16+0x5200,b'\xaa\x55\xcc\xcc');u.mem_write(ds*16+0xe000,struct.pack('<5H',0,0x600,0x5000,0x5100,0x5200));state=dict(done=False,interrupts=[])
  def hook(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop()
  def intr(u,n,_):state['interrupts'].append(n);u.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,intr)
  for reg,value in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,value)
  u.emu_start(cs*16+ip,0,count=1000000);actualret=u.reg_read(UC_X86_REG_AX);actualval=struct.unpack('<H',u.mem_read(ds*16+0x5200,2))[0];assert state['done'] and not state['interrupts'];assert actualret==ret and actualval==(val if val is not None else 0x55aa),(v,fmt,string,actualret,hex(actualval),ret,val);assert bytes(u.mem_read(ds*16+0x5202,2))==b'\xcc\xcc'
  results.append(dict(build=v,format=fmt,input=string,return_AX=actualret,destination_word=actualval,passed=True))
 print(v,len(fixtures),'passed')
(o/'native_scan_tests.json').write_text(json.dumps(dict(locations=locations,cases=results,passed=len(results),mocks='none; original CRT code; explicit valid stack limit precondition; no DOS interrupts permitted'),indent=2)+'\n')
