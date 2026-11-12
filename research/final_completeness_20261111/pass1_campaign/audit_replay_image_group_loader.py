"""python audit_replay_image_group_loader.py IMAGE INVENTORY DECODER EMULATOR OUT
Whole original0277:0584; record decoder/DOS IO/allocation substituted explicitly.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
todo=[0x584];dec={};edges=[]
while todo:
 ip=todo.pop()
 if ip in dec:continue
 assert 0x584<=ip<0x686;i=Decoder(16,b[0x2770+ip:0x2770+0x686],ip=ip).decode();assert not i.is_invalid;dec[ip]=i
 if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
 if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
rows=[]
for ip,i in sorted(dec.items()):
 raw=b[0x2770+ip:0x2770+i.next_ip];assert old[0x2770+ip]['bytes']==raw.hex();rows.append(dict(cs=0x277,ip=ip,image_offset=0x2770+ip,bytes=raw.hex(),instruction=fmt.format(i)))
save('image_group_header_records_load',rows);save('image_group_header_records_load_cfg',edges);rel=list(csv.DictReader((image.parent/'relocations.csv').open()));runtimes={};cases=[];visited=set()
for load in (0x824,0x1000):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 runtimes[load]=bytes(raw)
def run(load,codeword,classword,wall,count,readlen,error_kind=''):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,runtimes[load]);ds=load+0x2771;buffer=0x7000;allocated=0x9000;payload=0 if error_kind=='missing_payload' else 0x12345678;handle=7;dg=bytearray([0x55]*0xe030);dg[buffer+2]=2;dg[buffer+3]=1;header=bytearray((j*17+3)&255 for j in range(90));header[2]=count;header[3]=1;expected=bytearray(dg);code=codeword&255;actual_count=count if readlen>=3 else 2;header_offset=0x800+90*(code+(0 if wall else 256));calls=[];decoder_flags=[];diagnostic=[];done=[]
 if error_kind not in ('missing_payload','class_limit'):
  expected[buffer:buffer+min(readlen,90)]=header[:min(readlen,90)]
  if error_kind!='allocation_failure':
   for n in range(actual_count):expected[allocated+10*n:allocated+10*(n+1)]=bytes((code+n*13+j)&255 for j in range(10))
 u.mem_write(ds*16,bytes(dg));args=[handle,payload&65535,payload>>16,codeword,classword,buffer,wall];frame=struct.pack('<'+'H'*(2+len(args)),0x100,0x5000,*args);u.mem_write(ds*16+0xf000,frame)
 for q,value in [(UC_X86_REG_CS,load+0x277),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(q,value)
 targets={(load+0x11ee)*16+0x1bd6:'seek',(load+0x11ee)*16+0x1e14:'read',(load+0x11ee)*16+0x3ccf:'allocate',(load+0x277)*16+0x45c:'decode',(load+0xfba)*16+0xc:'error'}
 def hook(emu,address,size,data):
  if address==0x50100:done.append(True);emu.emu_stop();return
  p=address-load*16
  if 0x2cf4<=p<0x2df6:visited.add(p-0x2770)
  if address not in targets:return
  name=targets[address];sp=emu.reg_read(UC_X86_REG_SP)
  def get(n):return struct.unpack('<'+'H'*n,bytes(emu.mem_read(ds*16+sp+4,2*n)))
  if name=='error':
   expected_args={'missing_payload':(0x3f5,0x3e9 if wall else 0x3ee,code),'class_limit':(0x411,70),'allocation_failure':(0x43c,0x428)}[error_kind];assert get(len(expected_args))==expected_args;diagnostic.append(name);emu.emu_stop();return
  calls.append(name)
  if name=='seek':
   wanted=(handle,header_offset,0,0) if calls.count('seek')==1 else (handle,payload&65535,payload>>16,0);assert get(4)==wanted;emu.reg_write(UC_X86_REG_AX,wanted[1]);emu.reg_write(UC_X86_REG_DX,wanted[2])
  elif name=='read':assert get(3)==(handle,buffer,90);emu.mem_write(ds*16+buffer,bytes(header[:min(readlen,90)]));emu.reg_write(UC_X86_REG_AX,readlen)
  elif name=='allocate':assert get(1)==(actual_count*10,);emu.reg_write(UC_X86_REG_AX,0 if error_kind=='allocation_failure' else allocated)
  else:
   n=calls.count('decode')-1;v=get(5);assert v[:4]==(handle,allocated+10*n,code,n) and v[4]&255==wall&255;assert v[4]>>8==(0x56 if n==0 else 0);decoder_flags.append(v[4]);emu.mem_write(ds*16+allocated+10*n,bytes((code+n*13+j)&255 for j in range(10)));emu.reg_write(UC_X86_REG_AX,0xd2e3)
  ret,cs=struct.unpack('<HH',bytes(emu.mem_read(ds*16+sp,4)));emu.reg_write(UC_X86_REG_SP,sp+4);emu.reg_write(UC_X86_REG_CS,cs);emu.reg_write(UC_X86_REG_IP,ret)
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((load+0x277)*16+0x584,0xfffff,count=30000)
 assert bool(diagnostic)==bool(error_kind) and bool(done)==(not error_kind) and bytes(u.mem_read(ds*16,len(dg)))==expected,(load,codeword,classword,wall,count,readlen,error_kind,calls)
 if not error_kind:
  assert calls==['seek','read','allocate','seek']+['decode']*actual_count and u.reg_read(UC_X86_REG_AX)==allocated and u.reg_read(UC_X86_REG_SP)==0xf004
  assert u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x2345 and u.reg_read(UC_X86_REG_DI)==0x3456 and bytes(u.mem_read(ds*16+0xf000,len(frame)))==frame
 assert u.reg_read(UC_X86_REG_DS)==u.reg_read(UC_X86_REG_SS)==ds
 cases.append(dict(load=load,code_WORD=codeword,class_WORD=classword,wall_BYTE=wall,count_in_read_header=count,read_return_AX=readlen,header_seek_offset=header_offset,consumed_count=actual_count,decoder_calls=len(decoder_flags),first_flag_WORD=decoder_flags[0] if decoder_flags else None,error_stop=error_kind,status='PASS'))
for args in itertools.product((0x824,0x1000),(0,129,255,0xab81),(0,69,65535),(0,1,255),(0,1,12,255),(0,2,3,89,90)):run(*args)
for load,wall in itertools.product((0x824,0x1000),(0,1,255)):
 run(load,0xab81,0,wall,12,90,'missing_payload');run(load,129,70,wall,12,90,'class_limit');run(load,129,32767,wall,12,90,'class_limit');run(load,129,0,wall,12,90,'allocation_failure')
save('cases',cases);save('instruction_execution_coverage',[dict(ip=ip,executed=ip in visited) for ip in sorted(dec)])
s=dict(functions=[dict(name='image_group_header_records_load',start=0x2cf4,end_exclusive=0x2df6,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows))],cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,executed_instruction_starts=len(visited),unexecuted_starts=sorted(set(dec)-visited),scope='whole0584; seek/read/nearallocation/045Crecorddecoder substituted; diagnostics stop atentry, no nonreturn/error closure; short read return unchecked and stale headerBYTE2 consumed; signedclassbound permitsnegativeWORD; decoder flagWORD retains first highBYTE fromseekAX; DS=SS',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,image.parent/'relocations.csv',Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
