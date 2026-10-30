from pathlib import Path
import json,struct
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass64/evidence';spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));loc=json.load(open(r/'pass63/evidence/lookup_tests.json'))['locations'];results=[]
for l in loc:
 v=l['build'];lines=[x.split('\t') for x in (o/f'DOS{v}.exe.xrefs.tsv').read_text().splitlines()];entry=[q[3] for q in lines if q[0]=='lookup'][1];cs,ip=[int(x,16) for x in entry.split(':')];rows=[q for q in lines if q[:2]==['instruction',entry]];calls=[q for q in rows if q[3].startswith('9a')];assert len(calls)==6;sites={cs*16+int(q[2].split(':')[1],16):k for q,k in zip(calls,['open','fatal_open','seek','read','fatal_read','close'])};ds=next(s['actual_DS'] for s in spec if s['build']==v);seg=int(l['table_segment'],16);flag=int(l['flag'],16);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+4*k);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 for n,mode in [(n,'ok') for n in [0,1,127,32768,65535]]+[(17,'short'),(17,'open_negative'),(17,'seek_fail')]:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+flag,b'\0');u.mem_write(seg*16+42,struct.pack('<HI',n,0x12345678));u.mem_write(ds*16+0xe000,struct.pack('<HHHHH',0,0x600,7,0x20,0x9000));state=dict(events=[],fatal=None,returned=False)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  def hook(u,a,size,_):
   if a==0x6000:state['returned']=True;u.emu_stop();return
   k=sites.get(a)
   if k is None:return
   state['events'].append(k);sp=u.reg_read(UC_X86_REG_SP);args=struct.unpack('<4H',u.mem_read(ds*16+sp,8))
   if k=='open':
    assert bytes(u.mem_read(ds*16+args[0],8)).split(b'\0')[0].lower()==b'uif.dat';assert args[1]==0x8000;u.reg_write(UC_X86_REG_AX,0x8000 if mode=='open_negative' else 0x4444)
   elif k=='seek':assert args==(0x4444,0x5678,0x1234,0);u.reg_write(UC_X86_REG_AX,65535 if mode=='seek_fail' else 0)
   elif k=='read':assert args==(0x4444,0x20,0x9000,n);u.reg_write(UC_X86_REG_AX,n-1 if mode=='short' else n)
   elif k.startswith('fatal'):state['fatal']=k;u.emu_stop();return
   elif k=='close':assert args[0]==0x4444
   u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+5)
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+ip,0,count=10000);expected='fatal_open' if mode=='open_negative' else 'fatal_read' if mode=='short' else None;assert state['fatal']==expected and state['returned']==(expected is None),(v,n,mode,state)
  results.append(dict(build=v,entry=entry,length=n,mode=mode,**state,passed=True))
 print(v,'8 passed')
(o/'raw_loader_tests.json').write_text(json.dumps(dict(passed=len(results),cases=results),indent=2)+'\n')
