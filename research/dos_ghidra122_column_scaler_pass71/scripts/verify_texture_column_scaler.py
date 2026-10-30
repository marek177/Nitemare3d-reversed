from pathlib import Path
import json,struct
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_INSN
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass71/evidence';spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));results=[];locations=[]
for v in ['10','11','12','15','17','18']:
 q=[s.split('\t') for s in (o/f'DOS{v}.exe.xrefs.tsv').read_text().splitlines()];entry=next(s[3] for s in q if s[0]=='at');cs,ip=[int(x,16) for x in entry.split(':')];rows=[s for s in q if s[:2]==['instruction',entry]]
 def imm(prefix,start=2,last=False):
  items=[s for s in rows if s[3].startswith(prefix)];return int.from_bytes(bytes.fromhex(items[-1 if last else 0][3])[start:start+2],'little')
 center=imm('2b06');limit=imm('8b0e');aa=[immval for immval in [int.from_bytes(bytes.fromhex(s[3])[1:3],'little') for s in rows if s[3].startswith('a1')]];assert len(aa)==3;top,visible,page=aa;table=imm('8b97');clipbyte=imm('8a87');clipfrac=imm('8b87',last=True);shade=imm('c746f6',3);ds=next(s['actual_DS'] for s in spec if s['build']==v);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+4*k);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 locations.append(dict(build=v,entry=entry,center=hex(center),limit=hex(limit),top=hex(top),visible=hex(visible),page=hex(page),reciprocal_base=hex(table),clip_byte_table=hex(clipbyte),clip_fraction_table=hex(clipfrac),shade_table=hex(shade)))
 cases=[(d,x,sh,False,0) for d in [1,3,31,65,511] for x in range(4) for sh in [0,1]]+[(101,x,sh,True,0) for x in range(4) for sh in [0,1]]+[(31,1,sh,False,1) for sh in [0,1]]
 for d,x,sh,cropped,stackhigh in cases:
  y=100+(d-1)//2;R=0x400000//d;n=7 if cropped else d+1;desty=2 if cropped else y-d;adjust=cropped or stackhigh!=0;src=0x1000+2*64+(5 if adjust else 0);phase=12345 if adjust else 0;source=bytes(i%251 for i in range(65536));mapping=bytes((i*7+9)&255 for i in range(256));u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(0x90000,source)
  for a,val in [(center,100),(limit,y if cropped else 1000),(top,2),(visible,7),(page,0xa000)]:u.mem_write(ds*16+a,struct.pack('<H',val))
  u.mem_write(ds*16+table+d*4,struct.pack('<I',R));u.mem_write(ds*16+clipbyte+d,b'\5');u.mem_write(ds*16+clipfrac+d*2,struct.pack('<H',12345));u.mem_write(ds*16+shade,mapping);u.mem_write(ds*16+0xe000,struct.pack('<9H',0,0x600,0x1000,0x9000,2,x,y,sh,319));u.mem_write(ds*16+0xdff7,bytes([stackhigh]));state=dict(done=False,ports=[],writes=[])
  def out(u,port,size,value,_):state['ports'].append((port,size,value))
  def write(u,access,a,size,value,_):
   if 0xa0000<=a<0xb0000:state['writes'].append((a-0xa0000,size,value))
  def code(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop()
  u.hook_add(UC_HOOK_INSN,out,None,1,0,UC_X86_INS_OUT);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_CODE,code)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  u.emu_start(cs*16+ip,0,count=100000);assert state['done'] and u.reg_read(UC_X86_REG_DS)==ds
  mask=((0x11<<x)|(0x11>>(8-x)))&255;span=1
  if d>64:
   extra=3 if cropped else 1;rot=mask
   for j in range(extra):
    carry=bool(rot&128);rot=((rot<<1)|(rot>>7))&255
    if carry:break
    mask|=rot;span+=1
  expected=[]
  for i in range(n):
   idx=(src+((phase+i*R)>>16))&65535;val=source[idx];val=mapping[val] if sh else val;expected.append((((desty&255)*80+(x>>2)+i*80)&65535,1,val))
  assert state['writes']==expected,(v,d,x,sh,cropped,stackhigh,state['writes'][:3],expected[:3]);assert state['ports']==[(0x3c4,1,2),(0x3c5,1,mask)];assert u.reg_read(UC_X86_REG_AX)==span
  results.append(dict(build=v,d=d,x=x,shade=sh,cropped=cropped,stack_high_byte=stackhigh,rows=n,reciprocal=R,span=span,mask=mask,passed=True))
 print(v,len(cases),'passed')
(o/'column_scaler_tests.json').write_text(json.dumps(dict(locations=locations,cases=results,passed=len(results),mocks='OUT observed only; original scaler executes with synthetic textures/tables and explicit stack fixture'),indent=2)+'\n')
