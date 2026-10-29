from pathlib import Path
import csv,json,struct,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_INSN
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
meta=json.loads((root/'pass26/evidence/viewport_boundary.json').read_text())['locations'];cons=json.loads((root/'pass31/evidence/consumer.json').read_text())['locations']
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];m=next(x for x in meta if x['build']==v);co=next(x for x in cons if x['build']==v);ds=q['actual_DS'];scs,se=[int(x,16) for x in m['setter_entry'].split(':')];ccs,ce=[int(x,16) for x in co['entry'].split(':')];target=ccs*16+ce;rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));matches=[]
 for j,r in enumerate(rows):
  b=bytes.fromhex(r['bytes'])
  if len(b)==5 and b[0]==154 and int.from_bytes(b[3:],'little')*16+int.from_bytes(b[1:3],'little')==target:matches.append(j)
 assert len(matches)==1;j=matches[0];a=next(k for k in range(j-100,j) if rows[k]['bytes']=='c746f20100');cs,entry=[int(x,16) for x in rows[a]['address'].split(':')];end=j+1
 while rows[end]['bytes']!='8bfb':end+=1
 stop=cs*16+int(rows[end]['address'].split(':')[1],16);body=rows[a:end+1];helpers={cs*16+int(r['address'].split(':')[1],16):r for r in body if (r['bytes'].startswith('9a') or r['bytes'].startswith('e8')) and r!=rows[j]};after=cs*16+int(rows[j+1]['address'].split(':')[1],16)
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(build=v,caller_fragment=f'{cs:04x}:{entry:04x}',consumer=co['entry'],instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xe000
 def run(c,e):
  u.mem_write(ds*16+sp,struct.pack('<HH',0x600,0))
  for reg,val in [(UC_X86_REG_CS,c),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  u.emu_start(c*16+e,0x600,count=100000);assert u.reg_read(UC_X86_REG_CS)==0
 init=next(r for k,r in enumerate(rows) if r['address'].startswith(f'{ccs:04x}:') and r['bytes']=='c8040000' and rows[k+1]['bytes']=='56');run(ccs,int(init['address'].split(':')[1],16));u.mem_write(ds*16+int(m['source_width'],16),struct.pack('<H',304));run(scs,se);u.mem_write(ds*16+int(co['primary_page_global'],16),struct.pack('<H',0x7000));u.mem_write(0x60000,bytes(i%251 for i in range(65536)));base=int(m['output_base'],16);center=struct.unpack('<H',u.mem_read(ds*16+base+14,2))[0];calls=[];returns=[];done=[];active={};mask=[0];planes=[bytearray(65536) for _ in range(4)]
 def out(uc,port,size,value,_):
  if port==0x3c5:mask[0]=value&15
 def wh(uc,access,addr,size,value,_):
  if 0x70000<=addr<0x80000:
   for plane in range(4):
    if mask[0]&(1<<plane):planes[plane][addr-0x70000]=value&255
 u.hook_add(UC_HOOK_MEM_WRITE,wh);u.hook_add(UC_HOOK_INSN,out,None,1,0,UC_X86_INS_OUT)
 def hook(uc,addr,size,_):
  if addr==stop:done.append(True);uc.emu_stop()
  if addr==target:
   st=uc.reg_read(UC_X86_REG_SP);args=list(struct.unpack('<7H',uc.mem_read(ds*16+st+4,14)));calls.append(args)
  if addr==after:returns.append(uc.reg_read(UC_X86_REG_AX))
  if addr in helpers:
   r=helpers[addr];xx=uc.reg_read(UC_X86_REG_DI);uc.reg_write(UC_X86_REG_AX,active['columns'][xx-active['left']])
   if r['bytes'].startswith('e8'):uc.reg_write(UC_X86_REG_SP,uc.reg_read(UC_X86_REG_SP)+2);uc.reg_write(UC_X86_REG_IP,addr-cs*16+3)
   else:uc.reg_write(UC_X86_REG_IP,addr-cs*16+5)
 u.hook_add(UC_HOOK_CODE,hook)
 for left in range(4):
  for length in range(1,10):
   right=left+length-1
   for dy in [31,32,76]:
    for pattern in ['constant','alternating','ramp','pairs','single_change']:
     columns=[2 if pattern=='constant' else 2+(xx%2) if pattern=='alternating' else 2+xx if pattern=='ramp' else 2+(xx//2)%2 if pattern=='pairs' else 2+(xx>=length//2) for xx in range(length)];active.update(left=left,columns=columns);planes[:]=[bytearray([0xa5])*65536 for _ in range(4)];mask[0]=0
     frame=0xd000;record=0x6400;u.mem_write(ds*16+frame-0x26,b'\0'*0x26)
     def word(off,val):u.mem_write(ds*16+frame+off,struct.pack('<H',val&65535))
     word(-0x22,0x6100);word(-0x14,0x6200);u.mem_write(ds*16+0x6200,b'\x40');u.mem_write(ds*16+frame-0x18,struct.pack('<HH',0x200,0x6000));word(-0x1c,0);u.mem_write(ds*16+record,b'\0'*20);u.mem_write(ds*16+record+2,struct.pack('<H',left));u.mem_write(ds*16+record+6,struct.pack('<H',right));u.mem_write(ds*16+record+14,struct.pack('<I',(dy*16)<<16));calls.clear();returns.clear();done.clear()
     for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp),(UC_X86_REG_BP,frame),(UC_X86_REG_DI,record)]:u.reg_write(reg,val)
     u.emu_start(cs*16+entry,0,count=100000);assert done and len(calls)==len(returns) and u.reg_read(UC_X86_REG_SP)==sp and u.reg_read(UC_X86_REG_DS)==ds
     expected=[];remaining=1;previous=0;i=2*dy+1;clipped=center+dy>=155
     for xx,col in enumerate(columns,left):
      remaining-=1
      if remaining==0 or col!=previous:
       n=min(4 if clipped else 2,4-(xx&3)) if i>64 and xx<=right-3 else 1;expected.append((xx,n,col));remaining=n;previous=col
     actual=[(a[3],n,a[2]) for a,n in zip(calls,returns)];assert actual==expected,(v,left,right,dy,pattern,actual,expected)
     assert all(a==[0x200,0x6000,col,x,center+dy,0,(right-3)&65535] for a,(x,n,col) in zip(calls,expected));assert all(x+n-1<=right for x,n,col in actual)
     expectedplanes=[bytearray([0xa5])*65536 for _ in range(4)];height=152;top=4;nrows=height if clipped else i+1;start=top if clipped else center+dy-i;phase=((((max(i-height,0)<<6)&65535)<<16)//i)>>1 if clipped else 0;inc=0x400000//i
     for xx,col in enumerate(columns,left):
      for row in range(nrows):
       off=((start&255)*80+(xx>>2)+row*80)&65535;src=(0x200+col*64+((phase+row*inc)>>16))&65535;expectedplanes[xx&3][off]=src%251
     assert planes==expectedplanes,(v,left,right,dy,pattern)
     results.append(dict(build=v,left=left,right=right,dy=dy,pattern=pattern,texture_columns=columns,groups=actual,plane_sha256=[hashlib.sha256(pl).hexdigest() for pl in planes],passed=True))
(root/'pass34/evidence/invalidation.json').write_text(json.dumps(dict(cases=len(results),scope='Original bounded caller loop, original scaled-column consumer and table generation. Two projection/texture helpers inject controlled per-x columns. Four-plane map-mask model compared to independent scalar per-column reference; complete VGA device and outer renderer not executed.',locations=locations,results=results),indent=2));print(len(results),'passed')
