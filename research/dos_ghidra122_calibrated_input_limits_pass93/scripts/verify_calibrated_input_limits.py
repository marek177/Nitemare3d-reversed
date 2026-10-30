from pathlib import Path
import json,struct,itertools,hashlib
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass93/evidence';out=[];loc=[]
for meta in json.load(open(o/'source_limits.json')):
 v=meta['build'];ds=next(x['actual_DS'] for x in json.load(open(r/'baseline58/pass7/evidence/specs.json')) if x['build']==v);rows=[x.split('\t') for x in (o/f'DOS{v}.refs.tsv').read_text().splitlines()];f=next(x[4] for x in rows if x[0]=='si_global' and x[3]=='WRITE');ins=[x for x in rows if x[:2]==['instruction',f]];k=next(i for i,x in enumerate(ins) if x[3]=='b8e803' and ins[i+2][3].startswith('f73e'));start=ins[k][2];cs,ip=[int(x,16) for x in start.split(':')];rate=int.from_bytes(bytes.fromhex(ins[k+2][3])[2:4],'little');stop=next(x[2] for x in ins[k:] if x[3]=='5e');si=meta['si_global'];di=meta['di_global'];extra=next(int.from_bytes(bytes.fromhex(x[3])[2:4],'little') for x in ins[k:] if x[3].startswith('8936'));loc.append(dict(build=v,producer=f,entry=start,stop=stop,rate_global=rate,si_global=si,di_global=di,twice_si_global=extra))
 b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 loc[-1]['exe_sha256']=hashlib.sha256(b).hexdigest()
 for m,cap in itertools.product([0,1,10,64,65,1000,65535,65536,0xffffffff],[0,1,18,70,1000,-1,-32768]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+0xd000-4,struct.pack('<I',m));u.mem_write(ds*16+rate,struct.pack('<h',cap));state={'done':False,'trap':None}
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_BP,0xd000),(UC_X86_REG_SP,0xc000)]:u.reg_write(reg,val)
  def hook(u,a,size,_):
   if a==cs*16+int(stop.split(':')[1],16):state['done']=True;u.emu_stop()
  def intr(u,n,_):state['trap']=n;u.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,intr);u.emu_start(cs*16+ip,0,count=200)
  if cap==0:assert state['trap']==0 and not state['done'];expected=None
  else:
   q=(1000//abs(cap))*(1 if cap>0 else -1);a=max(m,q&0xffffffff);t=((a+2)&0xffffffff)>>2;x=1 if t==0 else t&65535;y=max(1,((a*360+1400)&0xffffffff)//2800)&65535;expected=[x,y,(x*2)&65535];actual=[struct.unpack('<H',u.mem_read(ds*16+g,2))[0] for g in [si,di,extra]];assert state['done'] and state['trap'] is None and actual==expected,(v,m,cap,actual,expected)
  out.append(dict(build=v,measurement=m,rate=cap,result=expected,**state,passed=True))
 print(v,'63 passed')
(o/'calibration_tests.json').write_text(json.dumps(dict(locations=loc,passed=len(out),cases=out,boundary='Original post-measurement calibration tail only, no calls/mocks; synthetic BP-4 u32 measurement and signed rate global.'),indent=2)+'\n')
