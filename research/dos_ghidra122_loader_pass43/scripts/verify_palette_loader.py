from pathlib import Path
import csv,json,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INSN
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
meta=json.loads((root/'pass42/evidence/palette.json').read_text())['locations'];targets=json.loads((root/'pass42/evidence/palette.json').read_text())['targets']
raw=bytes((i*37+11)&255 for i in range(768))
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];m=next(x for x in meta if x['build']==v);ds=q['actual_DS'];pcs,pe=[int(x,16) for x in m['entry'].split(':')];rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));pi=next(i for i,r in enumerate(rows) if r['address']==m['entry']);end=next(i for i in range(pi,len(rows)) if rows[i]['bytes']=='cb');idx=end+1;assert rows[idx]['bytes']=='c8040000';cs,entry=[int(x,16) for x in rows[idx]['address'].split(':')];body=[]
 for r in rows[idx:]:
  body.append(r)
  if r['bytes']=='cb':break
 calls=[r for r in body if r['bytes'].startswith('9a') or r['bytes'].startswith('e8')];assert len(calls)==8;roles=['open','fatal','seek','fatal','read','dac','lookup','close'];sites={cs*16+int(r['address'].split(':')[1],16):role for role,r in zip(roles,calls)};src=int(m['source_palette'],16);dirty=int(m['dirty'],16);lookup=int(m['lookup'],16)
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 for dirtyval,available in itertools.product([0,1],[0,1,767,768]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xe000;u.mem_write(ds*16+sp,struct.pack('<HH',0x600,0));u.mem_write(ds*16+src,b'\xa5'*768);u.mem_write(ds*16+lookup,b'\xa5'*16);u.mem_write(ds*16+dirty,bytes([dirtyval]));reads=[];ports=[];trace=[]
  def out(uc,port,size,value,_):ports.append([port,size,value])
  def hook(uc,a,size,_):
   if a not in sites:return
   role=sites[a];trace.append(role);st=uc.reg_read(UC_X86_REG_SP)
   if role in ['dac','lookup']:return
   assert role!='fatal'
   if role=='open':uc.reg_write(UC_X86_REG_AX,3)
   elif role=='seek':
    assert list(struct.unpack('<4H',uc.mem_read(ds*16+st,8)))==[3,0xfd00,0xffff,2];uc.reg_write(UC_X86_REG_AX,0);uc.reg_write(UC_X86_REG_DX,0)
   elif role=='read':
    handle,dest,n=struct.unpack('<3H',uc.mem_read(ds*16+st,6));assert (handle,dest,n)==(3,src+len(reads),1);i=len(reads);reads.append(dest)
    if i<available:uc.mem_write(ds*16+dest,raw[i:i+1])
    uc.reg_write(UC_X86_REG_AX,int(i<available))
   uc.reg_write(UC_X86_REG_IP,a-cs*16+5)
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INSN,out,None,1,0,UC_X86_INS_OUT)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  u.emu_start(cs*16+entry,0x600,count=500000);expected=bytes((raw[i] if i<available else 165)>>2 for i in range(768));assert bytes(u.mem_read(ds*16+src,768))==expected;assert ports==[[0x3c8,1,0]]+[[0x3c9,1,x] for x in expected];assert len(reads)==768 and trace[-1]=='close'
  el=[165]*16
  if dirtyval:
   pal=[expected[i:i+3] for i in range(0,768,3)];el=[min(range(256),key=lambda j:sum((pal[j][c]-t[c])**2 for c in range(3))) for t in targets]
  assert list(u.mem_read(ds*16+lookup,16))==el and bytes(u.mem_read(ds*16+dirty,1))==b'\0';assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,initial_dirty=dirtyval,read_success_bytes=available,read_calls=len(reads),dac_events=len(ports),palette_sha256=hashlib.sha256(expected).hexdigest(),lookup=el,passed=True))
(root/'pass43/evidence/loader.json').write_text(json.dumps(dict(cases=len(results),scope='Original palette file-loader, DAC writer and palette lookup regeneration. File open/seek/read/close mocked; original OUT events captured, no VGA device. Read mock provides prefix then returns0 without writing.',locations=locations,results=results),indent=2));print(len(results),'passed')
