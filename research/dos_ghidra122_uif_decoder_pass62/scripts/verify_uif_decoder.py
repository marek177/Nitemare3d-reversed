from pathlib import Path
import json,struct,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent; out=root/'pass62/evidence'; base=root/'baseline58'; results=[]; locations=[]
specs=json.loads((base/'pass7/evidence/specs.json').read_text())
roles='lookup open seek read_header fatal_manufacturer fatal_dimensions read_code read_value blit_rle blit_literal close'.split()
def encode(data):
 r=bytearray(); i=0
 while i<len(data):
  n=1
  while n<63 and i+n<len(data) and data[i+n]==data[i]:n+=1
  v=data[i];r.extend([192|n,v] if n>1 or v>=192 else [v]);i+=n
 return bytes(r)
for seed in (out/'seeds.tsv').read_text().splitlines():
 v,role,entry=seed.split('\t')
 if role!='resource_reload':continue
 cs,ip=map(lambda x:int(x,16),entry.split(':'));ds=next(s['actual_DS'] for s in specs if s['build']==v)
 rows=[l.split('\t') for l in (out/f'DOS{v}.exe.ghidra.tsv').read_text().splitlines() if l.startswith('instruction\tresource_reload\t')]
 calls=[r for r in rows if r[3].startswith(('e8','9a'))]; assert len(calls)==11
 sites={int(r[2].split(':')[1],16)+cs*16:k for r,k in zip(calls,roles)}
 b=(base/f'analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+4*k);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 locations.append(dict(build=v,entry=entry,exe_sha256=hashlib.sha256(b).hexdigest(),calls={k:r[2] for r,k in zip(calls,roles)}))
 for case in ['missing','constant','literal','mixed','zero_run','manufacturer','width_wrong','height_wrong','both_wrong','other_fields']:
  pixels=bytes([90])*64000 if case not in ['literal','mixed'] else bytes((i%192 if case=='literal' else (i//7)%256) for i in range(64000));stream=encode(pixels)
  if case=='zero_run':stream=b'\xc0\x91'+stream
  header=bytearray(128);header[:4]=bytes([10,5,1,8]);struct.pack_into('<HHHH',header,4,0,0,318 if case in ['width_wrong','both_wrong'] else 319,198 if case in ['height_wrong','both_wrong'] else 199);header[65]=1;struct.pack_into('<H',header,66,320)
  if case=='manufacturer':header[0]=11
  if case=='other_fields':header[2]=0;header[3]=4;header[65]=3;struct.pack_into('<H',header,66,123)
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+0x5000,struct.pack('<HI',0 if case=='missing' else 1,0x1234));u.mem_write(ds*16+0xe000,struct.pack('<HHH',0,0x600,4));state=dict(cursor=0,rows=0,events=[],fatal=None,returned=False)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  def hook(u,a,size,_):
   if a==0x6000:state['returned']=True;u.emu_stop();return
   k=sites.get(a)
   if k is None:return
   sp=u.reg_read(UC_X86_REG_SP);args=struct.unpack('<10H',u.mem_read(ds*16+sp,20));state['events'].append(k) if k not in ['read_code','read_value','blit_literal','blit_rle'] else None
   if k=='lookup':u.reg_write(UC_X86_REG_AX,0x5000);u.reg_write(UC_X86_REG_DX,ds);u.reg_write(UC_X86_REG_SP,sp+2)
   elif k=='open':
    def cstr(off):return bytes(u.mem_read(ds*16+off,32)).split(b'\0')[0].decode('ascii')
    assert cstr(args[0]).lower()=='uif.dat';assert cstr(args[1])=='rb';u.reg_write(UC_X86_REG_AX,0x4444)
   elif k=='seek':assert args[:4]==(0x4444,0x1234,0,0)
   elif k.startswith('read_'):
    dest,n,count,handle=args[:4];assert handle==0x4444 and count==1
    if k=='read_header':assert n==128;data=bytes(header)
    else:
     assert n==1 and state['cursor']<len(stream);data=stream[state['cursor']:state['cursor']+1];state['cursor']+=1
    u.mem_write(ds*16+dest,data);u.reg_write(UC_X86_REG_AX,1)
   elif k.startswith('fatal_'):state['fatal']=k;u.emu_stop();return
   elif k.startswith('blit_'):
    src,seg,x,y,w,stride,dw,dh,page,trans=args;assert (seg,x,y,w,stride,dw,dh,page,trans)==(ds,0,state['rows'],320,1,320,1,0,65535),args
    assert bytes(u.mem_read(seg*16+src,320))==pixels[y*320:(y+1)*320];state['rows']+=1
   elif k=='close':assert args[0]==0x4444
   u.reg_write(UC_X86_REG_IP,(u.reg_read(UC_X86_REG_IP)+(3 if k=='lookup' else 5))&65535)
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+ip,0,count=6000000)
  fatal='fatal_manufacturer' if case=='manufacturer' else 'fatal_dimensions' if case=='both_wrong' else None
  assert state['fatal']==fatal and state['returned']==(fatal is None),(v,case,state)
  assert state['rows']==(0 if fatal or case=='missing' else 200),(v,case,state)
  if fatal is None:assert u.reg_read(UC_X86_REG_AX)&255==(0 if case=='missing' else 1)
  results.append(dict(build=v,case=case,rows=state['rows'],input_bytes_consumed=state['cursor'],fatal=fatal,events=state['events'],passed=True))
 print(v,'10 passed',flush=True)
(out/'uif_decoder_tests.json').write_text(json.dumps(dict(locations=locations,cases=results,passed=len(results),boundary_mocks=roles),indent=2)+'\n')
