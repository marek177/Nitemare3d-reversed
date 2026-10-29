from pathlib import Path
import csv,json,struct,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
meta=json.loads((root/'pass26/evidence/viewport_boundary.json').read_text())['locations']
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];m=next(x for x in meta if x['build']==v);ds=q['actual_DS'];source=int(m['source_width'],16);scs,se=[int(x,16) for x in m['setter_entry'].split(':')];rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));idx=next(i for i,r in enumerate(rows) if r['bytes']=='c80a0000' and rows[i+3]['bytes']=='c646f800');body=[]
 for r in rows[idx:]:
  body.append(r)
  if r['bytes']=='cb':break
 cs,entry=[int(x,16) for x in body[0]['address'].split(':')];base=int(m['output_base'],16);b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 page=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('a1')))[1:],'little') if False else int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('a1') and r['disassembly'].endswith(']') and int.from_bytes(bytes.fromhex(r['bytes'])[1:],'little')<0x200))[1:],'little')
 shadebase=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('c746f6')))[3:],'little')
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',primary_page_global=hex(page),shade_table=hex(shadebase),instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xe000;writes=[]
 def wh(uc,access,a,size,value,_):
  if 0x70000<=a<0x80000:writes.append([a-0x70000,value&255])
 u.hook_add(UC_HOOK_MEM_WRITE,wh)
 def run(c,e,args=b''):
  u.mem_write(ds*16+sp,struct.pack('<HH',0x600,0)+args)
  for reg,val in [(UC_X86_REG_CS,c),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  u.emu_start(c*16+e,0x600,count=100000)
  assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
 init=next(r for j,r in enumerate(rows) if r['address'].startswith(f'{cs:04x}:') and r['bytes']=='c8040000' and rows[j+1]['bytes']=='56');run(cs,int(init['address'].split(':')[1],16))
 for width in [160,304,320]:
  u.mem_write(ds*16+source,struct.pack('<H',width));run(scs,se);left,top,bottom,center=[struct.unpack('<H',u.mem_read(ds*16+base+n,2))[0] for n in [4,8,10,14]];height=width//2
  u.mem_write(ds*16+page,struct.pack('<H',0x7000));u.mem_write(ds*16+shadebase,bytes(255-i for i in range(256)));payload=bytes(i%251 for i in range(65536));u.mem_write(0x60000,payload)
  for dy in [0,1,31,39,75,100,200]:
   y=center+dy;i=2*dy+1;clipped=y>=bottom;n=height if clipped else i+1;start=top if clipped else y-i;phase=(((max(i-height,0)<<6)&65535)<<16)//i>>1 if clipped else 0;inc=0x400000//i
   for x in [0,3,4]:
    for shade in [0,1]:
     for enablegroup in [False,True]:
      limit=x+3 if enablegroup else (x-1)&65535;writes.clear();run(cs,entry,struct.pack('<7H',0x200,0x6000,2,x,y,shade,limit));expected=[]
      for row in range(n):
       val=payload[(0x200+2*64+((phase+row*inc)>>16))&65535];expected.append([((start&255)*80+(x>>2)+row*80)&65535,255-val if shade else val])
      assert writes==expected,(v,width,y,x,shade,len(writes),len(expected),writes[:2],expected[:2])
      # Signed x-limit compare; ffff represents -1, disabling grouping at x0.
      group=min((4 if clipped else 2),4-(x&3)) if i>64 and enablegroup else 1
      assert u.reg_read(UC_X86_REG_AX)==group,(v,width,y,x,enablegroup,u.reg_read(UC_X86_REG_AX),group)
      results.append(dict(build=v,width=width,y=y,scale_index=i,x=x,shade=shade,group_enabled=enablegroup,clipped=clipped,rows=n,returned_columns=group,writes_sha256=hashlib.sha256(json.dumps(writes).encode()).hexdigest(),passed=True))
(root/'pass31/evidence/consumer.json').write_text(json.dumps(dict(cases=len(results),scope='Original reciprocal initializer, entire viewport setter and original scaled-column consumer. No callee mocks. Ordinary mapped video memory records per-address writes, not VGA plane emulation.',locations=locations,results=results),indent=2));print(len(results),'passed')
