"""python audit_replay_classification_producers.py IMAGE INVENTORY DECODER EMULATOR OUT
Whole original two producers; exhaustive local initial BYTE seeds, full BYTE input domain.
"""
import csv,hashlib,json,random,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
defs=[('tile_flags_generate',0x1b6,0x24f,0xd30e,0xd00c),('occupancy_flags_generate',0x250,0x2f2,0xd40e,0xd10c)];functions=[];visited={};decoded_all={}
for name,start,end,source,dest in defs:
 todo=[start];decoded={};edges=[];rows=[]
 while todo:
  ip=todo.pop()
  if ip in decoded:continue
  assert start<=ip<end;i=Decoder(16,b[0xf70+ip:0xf70+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 for ip,i in sorted(decoded.items()):
  pos=0xf70+ip;raw=b[pos:0xf70+i.next_ip];assert old[pos]['bytes']==raw.hex();rows.append(dict(cs=0xf7,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rows);save(name+'_cfg',edges);visited[name]=set();decoded_all[name]=set(decoded);functions.append(dict(name=name,start=0xf70+start,end_exclusive=0xf70+end,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows)))
def flags(which,n,seed):
 if which==0:return (seed&128)|(4 if 1<=n<=0x30 else 0)|(16 if 0x2e<=n<=0x2f else 0)|(8 if 0x31<=n<=0x40 else 0)|(1 if 1<=n<=0x40 else 0)|(2 if 1<=n<=0x40 else 0)|(64 if 0x47<=n<=0x48 else 0)
 return (seed&128)|(1 if 6<=n<=0x3d else 0)|(2 if 8<=n<=0x2d else 0)|(4 if 0x2f<=n<=0x3d else 0)|(8 if 8<=n<=0x25 else 0)|(32 if n==0x2a else 0)|(64 if n==4 else 0)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
def run(which,load,seed,values,group):
 name,start,end,source,dest=defs[which];u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for x in rel:struct.pack_into('<H',runtime,int(x['image_offset']),(int(x['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));ds=load+0x2771;dg=bytearray((j*37+19)&255 for j in range(0xe030));dg[source:source+256]=values;expected=bytearray(dg);expected[dest:dest+256]=bytes(flags(which,n,seed) for n in values);u.mem_write(ds*16,bytes(dg));u.mem_write(ds*16+0xeffd,bytes([seed]));frame=struct.pack('<HH',0x100,0x5000);u.mem_write(ds*16+0xf000,frame)
 for reg,v in [(UC_X86_REG_CS,load+0xf7),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_AX,0xabcd),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
 done=[];writes=[]
 def code(emu,address,size,data):
  if address==0x50100:done.append(True);emu.emu_stop();return
  ip=address-(load+0xf7)*16;assert ip in decoded_all[name];visited[name].add(ip)
 def write(emu,access,address,size,value,data):
  if ds*16+dest<=address<ds*16+dest+256:assert size==1;writes.append((address-ds*16,value))
  else:assert ds*16+0xeffa<=address<ds*16+0xf000,'unexpected write outside destination or local frame'
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((load+0xf7)*16+start,0,count=30000)
 assert done and bytes(u.mem_read(ds*16,len(dg)))==expected and writes==[(dest+i,expected[dest+i]) for i in range(256)]
 assert bytes(u.mem_read(ds*16+0xf000,4))==frame and u.reg_read(UC_X86_REG_SP)==0xf004
 assert u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x2345 and u.reg_read(UC_X86_REG_DS)==u.reg_read(UC_X86_REG_SS)==ds
 cases.append(dict(function=name,group=group,load=load,initial_local_BYTE=seed,retained_high_bit=seed&128,input_sha256=sha(bytes(values)),output_sha256=sha(bytes(expected[dest:dest+256])),destination_stores=256,status='PASS'))
for which in range(2):
 for load in (0x1000,0x824):
  for seed in range(256):run(which,load,seed,bytes(range(256)),'all_values_all_local_seeds')
  rng=random.Random(0xC0111+which)
  for k in range(16):run(which,load,(k*73)&255,bytes(rng.randrange(256) for _ in range(256)),'deterministic_random_tables')
save('cases',cases);save('instruction_execution_coverage',[dict(function=n,ip=ip,executed=ip in visited[n]) for n in visited for ip in sorted(decoded_all[n])]);save('value_flag_truth_table',[dict(function=defs[w][0],input_BYTE=n,output_low7=flags(w,n,0),output_if_initial_bit80=flags(w,n,128)) for w in range(2) for n in range(256)])
result=dict(functions=functions,cases=len(cases),table_entries_compared=len(cases)*256,failures=0,runtime_tests=0,new_deep_verified_bytes=0,instruction_starts_executed=sum(len(x) for x in visited.values()),unexecuted_starts={n:sorted(decoded_all[n]-visited[n]) for n in visited},scope='whole original no-argument producers, no stubs; all256inputBYTEs and all256initial localBYTEseeds under2relocations; full DGROUP exact,256ordered BYTE stores; bit80 copied from uninitialized localBPminus1, not forced0; randomtables supplemental',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
