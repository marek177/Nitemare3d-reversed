from pathlib import Path
import json,struct,hashlib
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass87/evidence';results=[]
for meta in json.load(open(o/'native_records.json')):
 v=meta['build'];rows=[x.split('\t') for x in (o/f'DOS{v}.exe.ghidra.tsv').read_text().splitlines()];rows=[x for x in rows if x[0]=='instruction'];entry=rows[0][2];cs,ip=[int(x,16) for x in entry.split(':')];calls={cs*16+int(x[2].split(':')[1],16):x for x in rows if 'CALL' in x[4]};keysite=[a for a,x in calls.items() if x[3].startswith('9a')][-1];ds=next(x['actual_DS'] for x in json.load(open(r/'baseline58/pass7/evidence/specs.json')) if x['build']==v);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 sg=meta['record_segment'];base=sg*16+0x1212
 for n in [-32768,-100,-1,0,1,100,32767]:
  for key in [0x4b,0x4d,0x20,0x0d,0x7f,0x1b]:
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(base+2,struct.pack('<h',n));u.mem_write(ds*16+0xe000,struct.pack('<4H',0,0x600,0x1212,sg));state={'done':False,'keys':[],'callbacks':[]}
   for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
   def hook(u,a,size,_):
    if a==0x6000:state['done']=True;u.emu_stop();return
    x=calls.get(a)
    if x is None:return
    ret=0
    if a==keysite:ret=key if not state['keys'] else 0x1b;state['keys'].append(ret)
    if x[3].startswith('26ff'):state['callbacks'].append(struct.unpack('<h',u.mem_read(base+2,2))[0])
    u.reg_write(UC_X86_REG_AX,ret)
    if x[3].startswith('e8'):u.reg_write(UC_X86_REG_SP,u.reg_read(UC_X86_REG_SP)+2)
    u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+len(bytes.fromhex(x[3])))
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+ip,0,count=10000)
   signed=lambda x:(x+32768)%65536-32768
   expected=n
   if key in [0x4b,0x4d]:expected=min(100,max(0,signed(signed(abs(n))+(-5 if key==0x4b else 5))))
   elif key in [0x20,0x0d]:expected=signed(-n)
   assert state['done'] and struct.unpack('<h',u.mem_read(base+2,2))[0]==expected,(v,n,key,state,expected);assert state['callbacks']==([] if key==0x1b else [expected]);assert u.reg_read(UC_X86_REG_AX)&255==6
   results.append(dict(build=v,initial=n,key=key,result=expected,**state,passed=True))
 print(v,'42 passed')
(o/'menu_key_tests.json').write_text(json.dumps(dict(passed=len(results),cases=results,boundary='Original menu loop and native relocated record; font/render/key/navigation and indirect callback mocked; Escape ends after first tested key.'),indent=2)+'\n')
