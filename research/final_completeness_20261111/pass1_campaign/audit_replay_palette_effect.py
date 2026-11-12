"""python audit_replay_palette_effect.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

from unicorn import UC_HOOK_INSN
functions=[]
for name,cs,start,end in [('vga_set_colour_lowbytes',0x156,0x150,0x16d),('palette_periodic_flash',0x83d,0x1cfc,0x1dc9)]:
 todo=[start];decoded={};edges=[];rows=[]
 while todo:
  ip=todo.pop()
  if ip in decoded:continue
  assert start<=ip<end;i=Decoder(16,b[cs*16+ip:cs*16+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 for ip,i in sorted(decoded.items()):
  pos=cs*16+ip;raw=b[pos:cs*16+i.next_ip];assert lookup[pos]['bytes']==raw.hex();rows.append(dict(cs=cs,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rows);save(name+'_cfg',edges);functions.append(dict(name=name,start=cs*16+start,end_exclusive=cs*16+end,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows)))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
def setup(load):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for x in rel:struct.pack_into('<H',runtime,int(x['image_offset']),(int(x['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));ds=load+0x2771;u.mem_write((load+0xfba)*16+0x1a0,b'\xcb');u.mem_write((load+0x83d)*16+0xea0,b'\xcb');u.mem_write(ds*16+0xd2f7,b'\xe3');u.mem_write(ds*16+0x4a64,b'\xa5'*768);return u,ds

def registers(u,load,ds,cs,words):
 for reg,value in [(UC_X86_REG_CS,load+cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_AX,0xabcd),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,value)
 u.mem_write(ds*16+0xf000,struct.pack('<'+'H'*(2+len(words)),0x100,0x5000,*words))

def effect(load,episode,level,flag,count,phase,rng,u=None,ds=None,kind='matrix',real_rng_seed=None):
 if u is None:u,ds=setup(load)
 if real_rng_seed is not None:
  u.mem_write((load+0xfba)*16+0x1a0,b[0xfd40:0xfd41]);u.mem_write(ds*16+0x24b8,struct.pack('<I',real_rng_seed));next_rng_state=(real_rng_seed*214013+2531011)&0xffffffff;rng=(next_rng_state>>16)&32767
 u.mem_write(ds*16+0x626a,struct.pack('<HH',episode,level));u.mem_write(ds*16+0x3634,struct.pack('<HB',count,phase));registers(u,load,ds,0x83d,[flag]);ports=[];called=[]
 def port(uc,port,size,value,user):assert size==1;ports.append((port,value))
 def callee(uc,address,size,user):
  if address==(load+0xfba)*16+0x1a0:
   called.append('rng')
   if real_rng_seed is None:uc.reg_write(UC_X86_REG_AX,rng)
  elif address==(load+0x83d)*16+0xea0:called.append('followup')
 h1=u.hook_add(UC_HOOK_INSN,port,None,1,0,UC_X86_INS_OUT);h2=u.hook_add(UC_HOOK_CODE,callee);u.emu_start((load+0x83d)*16+0x1cfc,0x50100,count=2000);u.hook_del(h1);u.hook_del(h2)
 signedlevel=(level+1)&65535;signedlevel=signedlevel if signedlevel<32768 else signedlevel-65536;skip=episode==2 or (episode==3 and signedlevel<10);expected_count=count;expected_phase=phase;expected_calls=[];rgb=None
 if not skip:
  if flag&255:expected_count=80;expected_phase=0;rgb=0
  else:
   expected_count=(count-1)&65535
   if count==0:
    if phase:
     expected_phase=0;n=rng if rng<32768 else rng-65536;q=(abs(n)//240)*(1 if n>=0 else -1);expected_count=(n-q*240+160)&65535;rgb=0;expected_calls=['rng','followup']
    else:expected_phase=1;expected_count=3;rgb=255
 expected_ports=[]
 if rgb is not None:
  for index in (235,227):expected_ports.extend([(0x3c8,index),(0x3c9,rgb),(0x3c9,rgb),(0x3c9,rgb)])
 assert ports==expected_ports and called==expected_calls and bytes(u.mem_read(ds*16+0x3634,3))==struct.pack('<HB',expected_count,expected_phase)
 assert bytes(u.mem_read(ds*16+0x4a64,768))==b'\xa5'*768
 assert u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SP)==0xf004 and u.reg_read(UC_X86_REG_DS)==u.reg_read(UC_X86_REG_SS)==ds
 if real_rng_seed is not None:assert bytes(u.mem_read(ds*16+0x24b8,4))==struct.pack('<I',next_rng_state)
 cases.append(dict(kind=kind,load=load,episode=episode,level=level,flag=flag,count_before=count,phase_before=phase,rng=rng,rng_seed=real_rng_seed,rng_next_state=next_rng_state if real_rng_seed is not None else None,count_after=expected_count,phase_after=expected_phase,out_instructions=len(ports),dependency_entries=len(expected_calls),passed=True));return expected_count,expected_phase
for load,episode,level,flag,count,phase,rng in itertools.product((0,0x1000),(0,1,2,3,65535),(0,8,9,10,32766,32767,65535),(0,1,256),(0,80),(0,1),(0,65535)):effect(load,episode,level,flag,count,phase,rng)
gate_cases=len(cases)
for load,count,phase,rng in itertools.product((0,0x1000),(0,1,3,80,65535),(0,1,255),(0,239,240,32767,65535,32768)):effect(load,1,0,0,count,phase,rng,kind='state_edges')
edge_cases=len(cases)-gate_cases
for load,rng in itertools.product((0,0x1000),(0,239)):
 u,ds=setup(load);count,phase=effect(load,1,0,1,65535,255,rng,u,ds,'cycle_reset')
 for n in range(81):count,phase=effect(load,1,0,0,count,phase,rng,u,ds,'cycle_dark_to_flash')
 assert (count,phase)==(3,1)
 for n in range(4):count,phase=effect(load,1,0,0,count,phase,rng,u,ds,'cycle_flash_to_dark')
 assert (count,phase)==(160+rng,0)
cycle_cases=len(cases)-gate_cases-edge_cases
real_rng_cases=0
for load,seed in itertools.product((0,0x1000),(0,1,0xffffffff,0x80000000,0x12345678,0x7fff0000)):
 effect(load,1,0,0,0,1,0,kind='original_rng_chain',real_rng_seed=seed);real_rng_cases+=1
port_cases=[]
for load,index,rgb in itertools.product((0,0x1000),(0,227,235,255,256,65535),((0,0,0),(63,63,63),(255,255,255),(256,257,65535),(0x1234,0xabcd,0xff00),(1,2,3))):
 u,ds=setup(load);registers(u,load,ds,0x156,[index,*rgb]);ports=[]
 def hook(uc,port,size,value,user):assert size==1;ports.append((port,value))
 u.hook_add(UC_HOOK_INSN,hook,None,1,0,UC_X86_INS_OUT);u.emu_start((load+0x156)*16+0x150,0x50100,count=100)
 assert ports==[(0x3c8,index&255)]+[(0x3c9,v&255) for v in rgb] and u.reg_read(UC_X86_REG_AX)==(rgb[2]&255) and u.reg_read(UC_X86_REG_DX)==0x3c9
 assert u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SP)==0xf004
 port_cases.append(dict(load=load,index=index,red=rgb[0],green=rgb[1],blue=rgb[2],passed=True))
save('effect_cases',cases);save('port_cases',port_cases)
s=dict(functions=functions,cases=len(cases)+len(port_cases),gate_cases=gate_cases,state_edge_cases=edge_cases,chained_cycle_invocations=cycle_cases,port_cases=len(port_cases),original_rng_chain_cases=real_rng_cases,failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='original palette state machine plus actual original VGA helper OUT instructions; RNG stubbed in matrix/edge/cycle probes, actual original wrapper/CRT/multiply chain in12seed cases; follow-upEA0 stubbed; ports observed only, no DAC hardware simulation; normal DS=SS; explicit signed-RNG boundary probes do not establish natural RNG output domain; cycles count individual86-invocation sequences',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
