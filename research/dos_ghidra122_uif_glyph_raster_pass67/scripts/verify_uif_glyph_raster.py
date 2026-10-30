from pathlib import Path
import json,struct,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_INSN
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass67/evidence';spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));results=[];locations=[]
for line in (o/'seeds.tsv').read_text().splitlines():
 v,_,entry=line.split('\t');cs,ip=[int(x,16) for x in entry.split(':')];ds=next(s['actual_DS'] for s in spec if s['build']==v);q=[x.split('\t') for x in (o/f'DOS{v}.exe.ghidra.tsv').read_text().splitlines() if x.startswith('instruction\t')];pg=[int.from_bytes(bytes.fromhex(x[3])[1:3],'little') for x in q if x[3].startswith('a1')];assert len(pg)==2
 b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+4*k);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 locations.append(dict(build=v,entry=entry,page_zero_global=hex(pg[0]),page_nonzero_global=hex(pg[1]),exe_sha256=hashlib.sha256(b).hexdigest()))
 cases=[(x,17,9,3,page) for x in range(4) for page in [0,1]]+[(3,19,w,1,page) for w in [0,1,7,8,16,248,249,255] for page in [0,2]]+[(1,255,8,0,0),(319,199,9,3,1),(65535,0x101,8,1,0)]
 for x,y,width,height,page in cases:
  stride=((width+7)&255)>>3;iters=stride or 256;rows=height or 256;data=bytes((i*73+0x81)&255 for i in range(iters*rows));u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+pg[0],struct.pack('<H',0xa000));u.mem_write(ds*16+pg[1],struct.pack('<H',0xb000));u.mem_write(0x90000+0x1000,bytes([height,width])+data);u.mem_write(ds*16+0xe000,struct.pack('<8H',0,0x600,x,y,0xffa7,page,0x1000,0x9000));state=dict(mask=0,index=None,ports=[],writes=0,done=False);planes=[bytearray([0x44])*65536 for _ in range(4)];expected=[bytearray(a) for a in planes];target=0xa0000 if page==0 else 0xb0000
  def out(u,port,size,value,_):
   assert size==1 and port in [0x3c4,0x3c5];state['ports'].append((port,value))
   if port==0x3c4:state['index']=value
   else:assert state['index']==2;state['mask']=value&15
  def write(u,access,a,size,value,_):
   if not target<=a<target+65536:return
   assert size==1 and value==0xa7;state['writes']+=1
   for plane in range(4):
    if state['mask']&(1<<plane):planes[plane][a-target]=value
  def code(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop()
  u.hook_add(UC_HOOK_INSN,out,None,1,0,UC_X86_INS_OUT);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_CODE,code)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  u.emu_start(cs*16+ip,0,count=5000000);assert state['done'] and u.reg_read(UC_X86_REG_DS)==ds
  for row in range(rows):
   for j in range(iters):
    val=data[row*iters+j]
    for bit in range(8):
     if val&(1<<bit):
      pixel=(x&3)+j*8+bit;addr=(((y&255)*80+(x>>2))+row*80+pixel//4)&65535;expected[pixel&3][addr]=0xa7
  assert planes==expected,(v,x,y,width,height,page)
  assert state['writes']==iters*rows*3;assert len(state['ports'])==2+state['writes'];assert state['ports'][0]==(0x3c4,2)
  results.append(dict(build=v,x=x,y=y,width=width,height=height,page=page,decoded_rows=rows,bytes_per_row=iters,stores=state['writes'],ports=len(state['ports']),planar_sha256=hashlib.sha256(b''.join(planes)).hexdigest(),passed=True))
 print(v,len(cases),'passed',flush=True)
(o/'glyph_raster_tests.json').write_text(json.dumps(dict(locations=locations,cases=results,passed=len(results),model='VGA sequencer index 2 low-four-bit write mask; synthetic independent four-plane memory; no hardware emulator'),indent=2)+'\n')
