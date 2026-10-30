from pathlib import Path
import json,struct,csv
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass66/evidence';spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));loc=json.load(open(r/'pass65/evidence/bitmap_bank_tests.json'))['locations'];results=[];locations=[]
for l in loc:
 v=l['build'];lines=[s.split('\t') for s in (o/f'DOS{v}.exe.xrefs.tsv').read_text().splitlines()];functions=list(dict.fromkeys(q[3] for q in lines if q[0]=='current' and q[2]=='READ'));width,string,draw=functions[:3];cs=int(width.split(':')[0],16);rows=[q for q in lines if q[:2]==['instruction',draw]];near=next(q for q in rows if q[3].startswith('e8'));nb=bytes.fromhex(near[3]);center=f'{cs:04x}:{(int(near[2].split(":")[1],16)+3+int.from_bytes(nb[1:3],"little",signed=True))&65535:04x}';blit=next(q for q in rows if q[3].startswith('9a'));site=cs*16+int(blit[2].split(':')[1],16);ds=next(s['actual_DS'] for s in spec if s['build']==v);table=int(l['pointer_table'],16);current=int(l['current'],16)
 old=list(csv.DictReader(open(r/f'baseline58/pass7/audit/DOS{v}/instructions.tsv'),delimiter='\t'));i=next(i for i,q in enumerate(old) if q['address']==center);body=[]
 for q in old[i:]:
  body.append(q)
  if q['bytes']=='cb':break
 locations.append(dict(build=v,width=width,string=string,center=center,draw=draw,blit_call=blit[2],center_instructions=body))
 b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+4*k);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 def new():
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+current,b'\1')
  for c in range(256):
   signed=c if c<128 else c-256;ptr=0x1000+c*4;u.mem_write(ds*16+table+512+signed*4,struct.pack('<HH',ptr,0x9000));u.mem_write(0x90000+ptr,bytes([3,(c*37+11)&255]))
  return u
 def run(u,entry,args,hook=None):
  state={'done':False}
  def cb(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop()
   elif hook:hook(u,a)
  u.hook_add(UC_HOOK_CODE,cb);u.mem_write(ds*16+0xe000,struct.pack('<'+'H'*(len(args)+2),0,0x600,*args));c,i=[int(x,16) for x in entry.split(':')]
  for reg,val in [(UC_X86_REG_CS,c),(UC_X86_REG_IP,i),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  u.emu_start(c*16+i,0,count=1000000);assert state['done'];assert u.reg_read(UC_X86_REG_DS)==ds
 def advance(c):return ((c*37+11)&255)+1
 for c in [0,1,65,127,128,255]:
  u=new();run(u,width,[c]);assert u.reg_read(UC_X86_REG_AX)==advance(c);results.append(dict(build=v,case='char_width',char=c,passed=True))
 for text in [b'',b'ABC',bytes([127,128,255]),b'A'*300,b'A'*600]:
  w=sum(map(advance,text))&65535;signed=w if w<32768 else w-65536;cx=((320-signed)//2)&65535
  for entry,kind,expected in [(string,'string_width',w),(center,'center',cx)]:
   u=new();u.mem_write(0x80000+0x200,text+b'\0');run(u,entry,[0x200,0x8000]);assert u.reg_read(UC_X86_REG_AX)==expected,(v,kind,len(text),u.reg_read(UC_X86_REG_AX),expected);results.append(dict(build=v,case=kind,length=len(text),expected=expected,passed=True))
  for x in [17,65535]:
   u=new();u.mem_write(0x80000+0x200,text+b'\0');trace=[];pos=[cx if x==65535 else x]
   def hook(u,a):
    if a!=site:return
    args=struct.unpack('<6H',u.mem_read(ds*16+u.reg_read(UC_X86_REG_SP),12));c=text[len(trace)];assert args==(pos[0],23,0xab|(0xff00 if c>=128 else 0),2,0x1000+c*4,0x9000),(v,args,c);trace.append(args);pos[0]=(pos[0]+advance(c))&65535;u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+5)
   run(u,draw,[x,23,0x200,0x8000,0xab,2],hook);assert len(trace)==len(text);results.append(dict(build=v,case='draw_layout',length=len(text),x=x,blits=len(trace),passed=True))
 print(v,'26 passed')
(o/'text_metrics_tests.json').write_text(json.dumps(dict(locations=locations,cases=results,passed=len(results)),indent=2)+'\n')
