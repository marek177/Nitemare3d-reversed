from pathlib import Path
import json,struct
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass77/evidence';spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));loc=json.load(open(r/'pass75/evidence/parser_locations.json'));dispatch=json.load(open(r/'pass76/evidence/switch_recovery_tests.json'))['cases'];results=[];locations=[]
for l in loc:
 v=l['build'];cs,ip=[int(x,16) for x in l['entry'].split(':')];rows=next(x['instructions'] for x in json.load(open(r/'pass75/evidence/parser_instructions.json')) if x['build']==v);calls=[x for x in rows if x['bytes'].startswith(('e8','9a'))];sites={cs*16+int(x['address'].split(':')[1],16):x for x in calls};ds=next(s['actual_DS'] for s in spec if s['build']==v);mapping={x['option']:x['target'] for x in dispatch if x['build']==v};effects={}
 for c in ['o','p','r','s','t','x']:
  j=next(i for i,x in enumerate(rows) if x['address']==mapping[c]);ef=[]
  for x in rows[j:]:
   z=bytes.fromhex(x['bytes'])
   if z.startswith((b'\xeb',b'\xe9')):break
   if z.startswith(b'\xc6\x06'):ef.append((int.from_bytes(z[2:4],'little'),1,z[4]))
   elif z.startswith(b'\xc7\x06'):ef.append((int.from_bytes(z[2:4],'little'),2,int.from_bytes(z[4:6],'little')))
  assert ef;effects[c]=ef
 watch={a:size for eff in effects.values() for a,size,value in eff};locations.append(dict(build=v,entry=l['entry'],flags={c:[dict(address=hex(a),size=size,value=val) for a,size,val in ef] for c,ef in effects.items()},environment_equivalent_flag='t',local_flag_option='b',known_table_options=mapping))
 b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 for option in ['b','o','p','r','s','t','x']:
  for env in [0,1]:
   for repeats in [1,2]:
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));expected={a:0x66 if size==1 else 0x6666 for a,size in watch.items()}
    for a,size in watch.items():u.mem_write(ds*16+a,bytes([0x66])*size)
    for a,size,val in (effects['t'] if env else [])+effects.get(option,[]):expected[a]=val
    argv=[0x5100]+[0x5120]*repeats;u.mem_write(ds*16+0x5000,struct.pack('<'+'H'*len(argv),*argv));u.mem_write(ds*16+0x5100,b'n3d\0');u.mem_write(ds*16+0x5120,('-'+option).encode()+b'\0');u.mem_write(ds*16+0xe000,struct.pack('<4H',0,0x600,len(argv),0x5000));state=dict(done=False,tail=None,env_calls=0)
    def hook(u,a,size,_):
     if a==0x6000:state['done']=True;u.emu_stop();return
     q=sites.get(a)
     if q is None:return
     sp=u.reg_read(UC_X86_REG_SP);near=q['bytes'].startswith('e8');args=struct.unpack('<3H',u.mem_read(ds*16+sp,6));ret=0
     if q['address']==calls[2]['address']:
      assert bytes(u.mem_read(ds*16+args[0],7))==b'windir\0';state['env_calls']+=1;ret=0x6000 if env else 0
     if q['address']==calls[-2]['address']:state['tail']=list(args)
     u.reg_write(UC_X86_REG_AX,ret)
     if near:u.reg_write(UC_X86_REG_SP,sp+2)
     u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+(3 if near else 5))
    u.hook_add(UC_HOOK_CODE,hook)
    for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
    u.emu_start(cs*16+ip,0,count=100000);assert state['done'] and state['env_calls']==1;assert state['tail'][:2]==[1,1] and state['tail'][2]&255==(1 if option=='b' else 0)
    for a,size in watch.items():assert int.from_bytes(u.mem_read(ds*16+a,size),'little')==expected[a],(v,option,env,a)
    results.append(dict(build=v,option=option,environment_present=env,repeats=repeats,expected_globals={hex(a):val for a,val in expected.items()},tail_low_byte=state['tail'][2]&255,passed=True))
 print(v,'28 passed')
(o/'flag_tests.json').write_text(json.dumps(dict(locations=locations,cases=results,passed=len(results),mocks='all parser callees; getenv return controlled; original dispatch, globals and stack-local state execute unchanged'),indent=2)+'\n')
