from pathlib import Path
import json,struct,hashlib
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass90/evidence';results=[]
for meta in json.load(open(o/'input_locations.json'))['native']:
 v=meta['build'];rows=[x.split('\t') for x in (o/f'DOS{v}.menu.tsv').read_text().splitlines()];rows=[x for x in rows if x[0]=='instruction'];entry=rows[0][2];cs,ip=[int(x,16) for x in entry.split(':')];calls={cs*16+int(x[2].split(':')[1],16):x for x in rows if 'CALL' in x[4]};keysite=[a for a,x in calls.items() if x[3].startswith('9a')][-1];ds=next(x['actual_DS'] for x in json.load(open(r/'baseline58/pass7/evidence/specs.json')) if x['build']==v);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 cm=next(x for x in json.load(open(o/'input_locations.json'))['config'] if x['build']==v);cl=next(x for x in json.load(open(o/'input_locations.json'))['commits'] if x['build']==v);commitcalls={int(x['address'].split(':')[0],16)*16+int(x['address'].split(':')[1],16):['instruction','commit',x['address'],x['bytes'],x['text']] for x in cl['instructions'] if x['bytes'].startswith(('9a','e8'))};commitcs,commitip=[int(x,16) for x in cm['commit_entry'].split(':')];commitaddr=commitcs*16+commitip
 sg=meta['record_segment'];base=sg*16+0x1212;mapping={10:(4,8),11:(5,11),13:(6,9),12:(7,10)}
 init=next(x for x in json.load(open(o/'initializers.json')) if x['build']==v);ics,iip=[int(x,16) for x in init['entry'].split(':')];initcalls={ics*16+int(x[2].split(':')[1],16):x for x in init['instructions'] if 'CALL' in x[4]};assert len(initcalls)==2;initrender=list(initcalls)[0];initmenu=list(initcalls)[1]
 outer=next(x for x in json.load(open(o/'outer.json')) if x['build']==v);ocs,oip=[int(x,16) for x in outer['entry'].split(':')];outercalls={ocs*16+int(x[2].split(':')[1],16):x for x in outer['instructions'] if 'CALL' in x[4]};outs=list(outercalls);assert len(outs)==5
 for magnitude,enabled,selected,key in [(m,e,i,k) for m in [0,50,255] for e in [0,1] for i,k in [(0,0x1b),(0,0x4d),(0,0x20),(4,0x0d)]]:
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p))
   for i in range(selected):u.mem_write(base+i*18+4,b'\0')
   u.mem_write(base+selected*18+4,b'\1')
   initial=bytes([0x30,1,0x77,0x66]+[magnitude]*4+[enabled]*4+[0x55,0x44,0x33,0x22]);u.mem_write(ds*16+cm['config'],initial);u.mem_write(ds*16+0xe000,struct.pack('<HH',0,0x600));state={'done':False,'keys':[],'callbacks':[],'commit_entries':0,'side_effects':[],'initialized':None,'outer_selections':[],'save_calls':0,'dos':[],'payloads':[]}
   for reg,val in [(UC_X86_REG_CS,ocs),(UC_X86_REG_IP,oip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
   def hook(u,a,size,_):
    if a==0x6000:state['done']=True;u.emu_stop();return
    if a in outercalls:
     idx=outs.index(a);x=outercalls[a]
     if idx in [3,4]:
      if idx==4:state['save_calls']+=1
      return
     ret=0
     if idx==1:ret=35 if not state['outer_selections'] else 6;state['outer_selections'].append(ret)
     u.reg_write(UC_X86_REG_AX,ret)
     if x[3].startswith('e8'):u.reg_write(UC_X86_REG_SP,u.reg_read(UC_X86_REG_SP)+2)
     u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+len(bytes.fromhex(x[3])));return
    if a==initmenu:
     state['initialized']=[struct.unpack('<h',u.mem_read(base+i*18+2,2))[0] for i in range(4)];return
    if a==initrender:
     x=initcalls[a];u.reg_write(UC_X86_REG_AX,0);u.reg_write(UC_X86_REG_SP,u.reg_read(UC_X86_REG_SP)+2);u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+3);return
    if a==commitaddr:state['commit_entries']+=1
    x=commitcalls.get(a)
    if x is not None:
     state['side_effects'].append(x[2]);u.reg_write(UC_X86_REG_AX,0);u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+len(bytes.fromhex(x[3])));return
    x=calls.get(a)
    if x is None:return
    ret=0
    if a==keysite:ret=key if not state['keys'] else 0x1b;state['keys'].append(ret)
    if x[3].startswith('26ff'):
     state['callbacks'].append(struct.unpack('<h',u.mem_read(base+selected*18+2,2))[0]);return
    u.reg_write(UC_X86_REG_AX,ret)
    if x[3].startswith('e8'):u.reg_write(UC_X86_REG_SP,u.reg_read(UC_X86_REG_SP)+2)
    u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+len(bytes.fromhex(x[3])))
   def intr(u,n,_):
    assert n==33;ax=u.reg_read(UC_X86_REG_AX);cx=u.reg_read(UC_X86_REG_CX);dx=u.reg_read(UC_X86_REG_DX);state['dos'].append(dict(ax=ax,cx=cx,dx=dx,bx=u.reg_read(UC_X86_REG_BX)));u.reg_write(UC_X86_REG_EFLAGS,u.reg_read(UC_X86_REG_EFLAGS)&~1)
    if ax==0x3d01:
     path=bytes(u.mem_read(ds*16+dx,100)).split(b'\0')[0];assert path==b'config.sav';u.reg_write(UC_X86_REG_AX,5)
    elif ax==0x4400:u.reg_write(UC_X86_REG_DX,0)
    elif ax==0x4300:u.reg_write(UC_X86_REG_CX,0)
    elif ax>>8==0x40:
     assert u.reg_read(UC_X86_REG_BX)==5
     if cx:assert cx==16;state['payloads'].append(bytes(u.mem_read(ds*16+dx,cx)).hex())
     u.reg_write(UC_X86_REG_AX,cx)
    elif ax>>8==0x3e:u.reg_write(UC_X86_REG_AX,0)
    else:raise AssertionError(hex(ax))
   u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,intr);u.emu_start(ocs*16+oip,0,count=100000)
   n=magnitude if enabled else -magnitude;assert state['initialized']==[n]*4
   expected=n
   if selected==0:
    if key==0x4d:expected=min(100,abs(n)+5)
    elif key in [0x20,0x0d]:expected=-n
   values=[n]*4
   if selected==0:values[0]=expected
   callback=key!=0x1b;expectedconfig=bytearray(initial)
   if callback:
    for record,val in zip(meta['records'][:4],values):
     mag,en=mapping[record['id']];expectedconfig[mag]=abs(val)&255;expectedconfig[en]=int(val>0)
   assert state['done'] and state['commit_entries']==int(callback);assert bytes(u.mem_read(ds*16+cm['config'],16))==expectedconfig;assert u.reg_read(UC_X86_REG_SP)==0xe004
   accepted=selected==4 and key in [0x20,0x0d];assert state['outer_selections']==([35] if accepted else [35,6]);assert state['save_calls']==1 and state['payloads']==[expectedconfig.hex()];assert [x['ax']>>8 for x in state['dos']]==[0x3d,0x44,0x40,0x43,0x40,0x3e]
   results.append(dict(build=v,magnitude=magnitude,enabled=enabled,selected=selected,key=key,accepted=accepted,config=expectedconfig.hex(),**state,passed=True))
 print(v,'24 passed')
(o/'outer_save_tests.json').write_text(json.dumps(dict(passed=len(results),cases=results,boundary='Original outer dispatcher, initializer, menu, indirect commit, save and CRT; UI/input/hardware callees mocked, DOS replies modeled.'),indent=2)+'\n')
