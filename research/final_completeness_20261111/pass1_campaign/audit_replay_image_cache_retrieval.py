"""IMAGE INVENTORY DECODER EMULATOR OUT: original0402+0350+07FE, external IO fixtures."""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
functions=[];starts={};visited={}
for name,lo,hi in [('xms_read_to_conventional',0x350,0x3ce),('image_cache_slot_fill',0x402,0x4d7)]:
 todo=[lo];dec={};edges=[]
 while todo:
  ip=todo.pop()
  if ip in dec:continue
  assert lo<=ip<hi;i=Decoder(16,b[0x7680+ip:0x7680+hi],ip=ip).decode();assert not i.is_invalid;dec[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
   todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):
   todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 rr=[]
 for ip,i in sorted(dec.items()):
  pos=0x7680+ip;raw=b[pos:0x7680+i.next_ip];assert old[pos]['bytes']==raw.hex()
  rr.append(dict(cs=0x768,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rr);save(name+'_cfg',edges);functions.append(dict(name=name,start=0x7680+lo,end_exclusive=0x7680+hi,instructions=len(rr),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rr)))
 starts[name]=set(r['image_offset'] for r in rr);visited[name]=set()
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));runtimes={};cases=[]
for load in (0x824,0x1000):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 runtimes[load]=bytes(raw)

def run(load,tag,pattern,owner,manager_ok,error):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,runtimes[load]);ds=load+0x2771;record=0x7100;oldrecord=0x7000
 dg=bytearray([0x66]*0xe030);tick=100
 times={'distinct':[90,80,70,60,50,40,30,20,10,0], 'ties':[10]*10,'fallback':[100+i for i in range(10)],'unsigned':[0xffffffff,0x80000000,99,98,97,96,95,94,93,92]}[pattern]
 candidates=[(t,i) for i,t in enumerate(times) if t<tick];selected=min(candidates)[1] if candidates else 0
 struct.pack_into('<I',dg,0x4540,tick);struct.pack_into('<II',dg,0xe006,0xffffffff,0xffffffff)
 struct.pack_into('<I',dg,record+2,tag);struct.pack_into('<I',dg,oldrecord+6,0xdeadbeef)
 reqseg=load+0x1be7;struct.pack_into('<H',dg,0x2560,reqseg);struct.pack_into('<H',dg,0x3506,7);struct.pack_into('<HH',dg,0x350e,0x100,0x9000)
 slots=[]
 for n,t in enumerate(times):
  base=0x60000+0x2200*n;slot=bytearray([0x5a]*0x2100);struct.pack_into('<IH',slot,0,t,oldrecord if owner and n==selected else 0)
  slots.append((base,slot));struct.pack_into('<I',dg,0x34cc+4*n,(base>>4)<<16);u.mem_write(base,bytes(slot))
 u.mem_write(ds*16,bytes(dg));u.mem_write(reqseg*16+0x200,b'\xa5'*16);u.mem_write(0x90100,b'\xcb')
 frame=struct.pack('<3H',0x100,0x5000,record);u.mem_write(ds*16+0xf000,frame)
 for reg,val in [(UC_X86_REG_CS,load+0x768),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 dest=slots[selected][0]+6;far=((slots[selected][0]>>4)<<16)|6;pixels=bytes((j*13+(tag&255))&255 for j in range(8192));fromfile=0<tag<0x80000000;fatal=(not fromfile and not manager_ok and error>=128)
 expected=bytearray(dg)
 if owner:struct.pack_into('<I',expected,oldrecord+6,0);struct.pack_into('<I',expected,0xe006,0)
 if not candidates:struct.pack_into('<I',expected,0xe00a,0)
 if not fatal:
  struct.pack_into('<I',expected,record+6,far);struct.pack_into('<IH',slots[selected][1],0,tick,record)
  if fromfile or manager_ok:slots[selected][1][6:8198]=pixels
 done=[];diagnostic=[];calls=[]
 def hook(emu,address,size,data):
  pos=address-load*16
  for name,ss in starts.items():
   if pos in ss:visited[name].add(pos)
  if address==0x50100:done.append(True);emu.emu_stop();return
  if address==0x90100:
   assert not fromfile and emu.reg_read(UC_X86_REG_AH)==11
   assert emu.reg_read(UC_X86_REG_DS)==reqseg and emu.reg_read(UC_X86_REG_SI)==0x200
   assert bytes(emu.mem_read(reqseg*16+0x200,16))==struct.pack('<IHIHI',8192,7,(-tag)&0xffffffff,0,far)
   calls.append('manager')
   if manager_ok:emu.mem_write(dest,pixels)
   emu.reg_write(UC_X86_REG_AX,manager_ok);emu.reg_write(UC_X86_REG_BL,error);return
  if address not in ((load+0x277)*16+2,(load+0xfba)*16+0xc):return
  sp=emu.reg_read(UC_X86_REG_SP);args=bytes(emu.mem_read(ds*16+sp+4,10))
  if address==(load+0xfba)*16+0xc:
   assert fatal and struct.unpack('<3H',args[:6])==(0xc83,0,error<<8);diagnostic.append(True);emu.emu_stop();return
  assert fromfile and struct.unpack('<IIH',args)==(far,tag,8192);calls.append('file');emu.mem_write(dest,pixels)
  ip,cs=struct.unpack('<HH',bytes(emu.mem_read(ds*16+sp,4)));emu.reg_write(UC_X86_REG_SP,sp+4);emu.reg_write(UC_X86_REG_CS,cs);emu.reg_write(UC_X86_REG_IP,ip)
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((load+0x768)*16+0x402,0xfffff,count=2000)
 assert bool(done)==(not fatal) and bool(diagnostic)==fatal
 assert calls==(['file'] if fromfile else ['manager'])
 assert bytes(u.mem_read(ds*16,len(dg)))==expected,(load,hex(tag),pattern,owner,manager_ok,error)
 for base,slot in slots:assert bytes(u.mem_read(base,len(slot)))==slot,(hex(tag),pattern,base)
 if not fatal:
  assert u.reg_read(UC_X86_REG_AX)==6 and u.reg_read(UC_X86_REG_DX)==slots[selected][0]>>4
  for reg,val in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xf004),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)]:assert u.reg_read(reg)==val
  assert bytes(u.mem_read(ds*16+0xf000,6))==frame
 cases.append(dict(load=load,tag='%08X'%tag,timestamps=pattern,old_owner=owner,manager_AX=manager_ok,manager_BL=error,selected_slot=selected,path='file' if fromfile else 'XMS',diagnostic=fatal,status='PASS'))

for params in itertools.product((0x824,0x1000),(0,0xfffffc00,0xffffe000,0x80000000,1,0x12345,0x7fffffff),('distinct','ties','fallback','unsigned'),(0,1),((1,0),(0,0x7f),(0,0x80))):
 load,tag,pattern,owner,manager=params
 if 0<tag<0x80000000 and manager!=(1,0):continue # Manager is not called on file path; avoid duplicate machine scenarios.
 run(load,tag,pattern,owner,*manager)
save('cases',cases);save('instruction_execution_coverage',[dict(function=n,image_offset=p,executed=p in visited[n]) for n in starts for p in sorted(starts[n])])
s=dict(functions=functions,cases=len(cases),failures=0,executed_instruction_starts=sum(map(len,visited.values())),unexecuted_starts={n:sorted(starts[n]-visited[n]) for n in starts},runtime_tests=0,new_deep_verified_bytes=0,scope='Original0402/0350/07FE. External file and XMS manager fixtures. Full DGROUP and ten slot regions compared; dimensions and allocation capacities are synthetic. Diagnostic stops, no handler-return assumption. No native/render parity.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,image.parent/'relocations.csv',Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
