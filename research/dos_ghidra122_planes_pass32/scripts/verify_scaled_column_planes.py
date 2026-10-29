from pathlib import Path
import csv,json,struct,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_MEM_WRITE,UC_HOOK_INSN
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
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xe000;writes=[];ports=[];planes=[bytearray(65536) for _ in range(4)];mask=[0]
 def out(uc,port,size,value,_):
  ports.append([port,size,value])
  if port==0x3c5:mask[0]=value&15
 def wh(uc,access,a,size,value,_):
  if 0x70000<=a<0x80000:
   writes.append([a-0x70000,value&255])
   for pl in range(4):
    if mask[0]&(1<<pl):planes[pl][a-0x70000]=value&255
 u.hook_add(UC_HOOK_MEM_WRITE,wh);u.hook_add(UC_HOOK_INSN,out,None,1,0,UC_X86_INS_OUT)
 def run(c,e,args=b''):
  u.mem_write(ds*16+sp,struct.pack('<HH',0x600,0)+args)
  for reg,val in [(UC_X86_REG_CS,c),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  u.emu_start(c*16+e,0x600,count=100000)
  assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
 init=next(r for j,r in enumerate(rows) if r['address'].startswith(f'{cs:04x}:') and r['bytes']=='c8040000' and rows[j+1]['bytes']=='56');run(cs,int(init['address'].split(':')[1],16))
 for width in [304]:
  u.mem_write(ds*16+source,struct.pack('<H',width));run(scs,se);left,top,bottom,center=[struct.unpack('<H',u.mem_read(ds*16+base+n,2))[0] for n in [4,8,10,14]];height=width//2
  u.mem_write(ds*16+page,struct.pack('<H',0x7000));u.mem_write(ds*16+shadebase,bytes(255-i for i in range(256)));payload=bytes(i%251 for i in range(65536));u.mem_write(0x60000,payload)
  for dy in [31,32,75,76,200]:
   y=center+dy;i=2*dy+1;clipped=y>=bottom;n=height if clipped else i+1;start=top if clipped else y-i;phase=(((max(i-height,0)<<6)&65535)<<16)//i>>1 if clipped else 0;inc=0x400000//i
   for x in range(8):
    for shade in [0,1]:
     for limitdelta in [-1,0,1,3]:
      for srcoff in [0x200,0xffc0]:
       enablegroup=limitdelta>=0;limit=(x+limitdelta)&65535;writes.clear();ports.clear();planes[:]=[bytearray([0xa5])*65536 for _ in range(4)];mask[0]=0;run(cs,entry,struct.pack('<7H',srcoff,0x6000,2,x,y,shade,limit));expected=[]
       for row in range(n):
        val=payload[(srcoff+2*64+((phase+row*inc)>>16))&65535];expected.append([((start&255)*80+(x>>2)+row*80)&65535,255-val if shade else val])
       assert writes==expected,(v,width,y,x,shade,len(writes),len(expected))
       group=min((4 if clipped else 2),4-(x&3)) if i>64 and enablegroup else 1
       assert u.reg_read(UC_X86_REG_AX)==group
       lowmask=((1<<group)-1)<<(x&3);expectedmask=lowmask|(lowmask<<4)
       assert ports==[[0x3c4,1,2],[0x3c5,1,expectedmask]],(v,y,x,limit,ports,expectedmask)
       expectedplanes=[bytearray([0xa5])*65536 for _ in range(4)]
       for pl in range(4):
        if lowmask&(1<<pl):
         for off,val in expected:expectedplanes[pl][off]=val
       assert planes==expectedplanes
       results.append(dict(build=v,width=width,y=y,scale_index=i,x=x,shade=shade,x_limit=limit,source_offset=srcoff,clipped=clipped,rows=n,returned_columns=group,columns_beyond_limit=max(0,x+group-1-(x+limitdelta)),ports=ports.copy(),plane_sha256=[hashlib.sha256(pl).hexdigest() for pl in planes],passed=True))
(root/'pass32/evidence/planes.json').write_text(json.dumps(dict(cases=len(results),scope='Original reciprocal initializer, entire viewport setter and scaled-column consumer. Original OUT ports feed a lower-four-bit VGA map-mask model; full four-plane bytes checked against independent expected planes. Not a complete VGA device or scanout model.',locations=locations,results=results),indent=2));print(len(results),'passed')
