"""python audit_replay_sound_xms_cache.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

todo=[0x580];decoded={};edges=[];rows=[]
while todo:
 ip=todo.pop()
 if ip in decoded:continue
 assert 0x580<=ip<0x684;i=Decoder(16,b[0x7680+ip:0x7d04],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
 if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
 if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
for ip,i in sorted(decoded.items()):
 pos=0x7680+ip;raw=b[pos:0x7680+i.next_ip];assert lookup[pos]['bytes']==raw.hex();rows.append(dict(cs=0x768,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
save('sound_xms_cache_record',rows);save('sound_xms_cache_record_cfg',edges)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));snd=Path(r'L:\nite3d\nite3\dos\SND.DAT');source=snd.read_bytes();assert sha(source)=='f3434984d315531602d32285cb8ff55990bba786f5fb37f53710e88379388614';original=source[192:666];native_path=out.parent/'../work/dosboxx_newgame_map_runtime_v3/sound_directory_runtime.bin';native=native_path.read_bytes();assert len(native)==474
cases=[]
def session(load,table):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for r in rel:struct.pack_into('<H',runtime,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));ds=load+0x2771;u.mem_write(ds*16+0x3f64,bytes(table));u.mem_write(ds*16+0x34f4,struct.pack('<HH',0x1000,0x7000));u.mem_write((load+0x277)*16+0x8a,b'\xcb');u.mem_write((load+0x768)*16+0x294,b'\xcb');return u,ds

def execute(u,ds,load,index,append_result,real_payload=False):
 before=bytes(u.mem_read(ds*16+0x3f64,474));expected=bytearray(before);length,offset=struct.unpack_from('<HI',before,index*6);duplicate=any(struct.unpack_from('<HI',before,k*6)==(length,offset) for k in range(index));attempt=bool(length and not duplicate and length<=8192);failed=attempt and append_result>=0x80000000;oversized=bool(length and not duplicate and length>8192);state=[]
 if attempt and not failed:
  for k in range(index+1,79):
   if struct.unpack_from('<I',before,k*6+2)[0]==offset:struct.pack_into('<I',expected,k*6+2,(-append_result)&0xffffffff)
  struct.pack_into('<I',expected,index*6+2,(-append_result)&0xffffffff)
 counters=struct.unpack('<HH',bytes(u.mem_read(ds*16+0xe026,4)))
 def hook(uc,address,size,user):
  name='read' if address==(load+0x277)*16+0x8a else 'append' if address==(load+0x768)*16+0x294 else None
  if name is None:return
  state.append(name);sp=uc.reg_read(UC_X86_REG_SP);args=bytes(uc.mem_read(ds*16+sp+4,10 if name=='read' else 6))
  if name=='read':
   off,seg,seek,count=struct.unpack('<HHIH',args);assert (off,seg,seek,count)==(0x1006,0x7000,offset,length)
   if real_payload:assert offset+length<=len(source);uc.mem_write(seg*16+off,source[offset:offset+length])
  else:
   off,seg,count=struct.unpack('<HHH',args);assert (off,seg,count)==(0x1006,0x7000,length)
   if real_payload:assert bytes(uc.mem_read(seg*16+off,length))==source[offset:offset+length]
   uc.reg_write(UC_X86_REG_AX,append_result&65535);uc.reg_write(UC_X86_REG_DX,append_result>>16)
 handle=u.hook_add(UC_HOOK_CODE,hook)
 for reg,val in [(UC_X86_REG_CS,load+0x768),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 u.mem_write(ds*16+0xf000,struct.pack('<HHH',0x100,0x5000,index));u.emu_start((load+0x768)*16+0x580,0x50100,count=10000);u.hook_del(handle)
 assert state==(['read','append'] if attempt else []) and bytes(u.mem_read(ds*16+0x3f64,474))==expected
 assert struct.unpack('<HH',bytes(u.mem_read(ds*16+0xe026,4)))==((counters[0]+int(oversized or failed))&65535,(counters[1]+int(attempt and not failed))&65535)
 for reg,value in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xf004),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)]:assert u.reg_read(reg)==value
 return attempt and not failed

#742KiB is inferred from the first native converted record. It is not an
#independent observation of the allocator's state before the sound phase.
for load in (0,0x1000):
 u,ds=session(load,original);u.mem_write(ds*16+0xe026,b'\0'*4);used=742;allocations=0
 for index in range(79):
  length=struct.unpack('<H',bytes(u.mem_read(ds*16+0x3f64+index*6,2)))[0];accepted=execute(u,ds,load,index,used*1024,True)
  if accepted:used+=(length+1023)//1024;allocations+=1
  cases.append(dict(kind='real_SND_sequence',load=load,index=index,length=length,append_result=None,duplicate_mode=None,passed=True))
 assert bytes(u.mem_read(ds*16+0x3f64,474))==native and used==1074 and allocations==66 and bytes(u.mem_read(ds*16+0xe026,4))==struct.pack('<HH',4,66)
for load,length,index,append_result,duplicate in itertools.product((0,0x1000),(0,1,8192,8193,65535),(0,1,78),(0,1024,0x7fffffff,0xffffffff),(0,1,2)):
 table=bytearray(474)
 for k in range(79):struct.pack_into('<HI',table,k*6,33,0x123400+k*64)
 offset=0x223344;struct.pack_into('<HI',table,index*6,length,offset)
 if index and duplicate:struct.pack_into('<HI',table,0,length if duplicate==1 else (length+1)&65535,offset)
 if index<78:struct.pack_into('<HI',table,78*6,(length+7)&65535,offset)
 u,ds=session(load,table);u.mem_write(ds*16+0xe026,b'\xff'*4);execute(u,ds,load,index,append_result)
 cases.append(dict(kind='synthetic_boundary',load=load,index=index,length=length,append_result=append_result,duplicate_mode=duplicate,passed=True))
save('cases',cases)
s=dict(functions=[dict(name='sound_xms_cache_record',start=0x7c00,end_exclusive=0x7d04,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows))],cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,native_directory_bytes_reconstructed=474,converted_records=68,native_field_bytes_changed=272,native_allocations=66,native_oversize_skips=4,inferred_initial_used_kib=742,final_used_kib=1074,scope='original cache record function; file helper and XMS append callee stubbed, original SND bytes copied through scratch;2x79 sequential original records plus360 synthetic boundary cases; initial used742 inferred from native offset, endpoint1074 and counters checked separately; no full XMS or audio-output closure',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,snd,native_path,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
