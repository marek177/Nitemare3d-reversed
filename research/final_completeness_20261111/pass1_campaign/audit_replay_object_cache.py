"""IMAGE INVENTORY DECODER EMULATOR OUT: original04D8/0350/07FE,external transfer fixtures."""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
todo=[0x4d8];dec={};edges=[]
while todo:
 ip=todo.pop()
 if ip in dec:continue
 assert 0x4d8<=ip<0x580;i=Decoder(16,b[0x7680+ip:0x7c00],ip=ip).decode();assert not i.is_invalid;dec[ip]=i
 if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
 if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
rows=[]
for ip,i in sorted(dec.items()):
 pos=0x7680+ip;raw=b[pos:0x7680+i.next_ip];assert old[pos]['bytes']==raw.hex();rows.append(dict(cs=0x768,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
save('object_image_cyclic_cache_fill',rows);save('object_image_cyclic_cache_fill_cfg',edges);starts=set(r['image_offset'] for r in rows);visited=set();rel=list(csv.DictReader((image.parent/'relocations.csv').open()));runtime={};cases=[]
for load in (0x824,0x1000):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 runtime[load]=bytes(raw)
def run(load,count,index,width,height,tag,owner,ok,error):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,runtime[load]);ds=load+0x2771;record=0x7100;oldrecord=0x7000;reqseg=load+0x1be7;request=reqseg*16+0x200
 dg=bytearray([0x66]*0xe030);struct.pack_into('<H',dg,0x2560,reqseg);struct.pack_into('<H',dg,0xc9c,index);struct.pack_into('<H',dg,0x3504,count);struct.pack_into('<H',dg,0x3506,7);struct.pack_into('<HH',dg,0x350e,0x100,0xf000);struct.pack_into('<I',dg,0xe012,0xffffffff);dg[record:record+10]=struct.pack('<BBII',width,height,tag,0)
 table=bytearray();slots=[]
 for n in range(128):
  base=0x60000+n*0x1000;seg=(base>>4)-0x10;off=0x100;table.extend(struct.pack('<HH',off,seg));raw=bytearray([0x5a]*0xc02);struct.pack_into('<H',raw,0,oldrecord if n==index and owner else 0);slots.append((base,raw));u.mem_write(base,bytes(raw))
 base,slot=slots[index];seg=(base>>4)-0x10;off=0x102;destfar=off|seg<<16;struct.pack_into('<I',dg,oldrecord+6,destfar);u.mem_write(ds*16,bytes(dg));u.mem_write(reqseg*16,bytes(table));u.mem_write(request,b'\xa5'*16);u.mem_write(0xf0100,b'\xcb')
 frame=struct.pack('<3H',0x100,0x5000,record);u.mem_write(ds*16+0xf000,frame)
 for reg,val in [(UC_X86_REG_CS,load+0x768),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 area=width*height;rounded=((area+1023)//1024)*1024;fromfile=0<tag<0x80000000;fatal=not fromfile and not ok and error>=128;length=area if fromfile else rounded;pixels=bytes((j*13+index+width)&255 for j in range(length));expected=bytearray(dg);next_index=index+1 if index+1<count else 0;struct.pack_into('<H',expected,0xc9c,next_index)
 if owner:struct.pack_into('<I',expected,oldrecord+6,0);struct.pack_into('<I',expected,0xe012,0)
 if not fatal:
  struct.pack_into('<I',expected,record+6,destfar);struct.pack_into('<H',slot,0,record)
  if fromfile or ok:slot[2:2+length]=pixels
 done=[];diagnostic=[];calls=[]
 def hook(emu,address,size,data):
  p=address-load*16
  if p in starts:visited.add(p)
  if address==0x50100:done.append(True);emu.emu_stop();return
  if address==0xf0100:
   assert not fromfile and emu.reg_read(UC_X86_REG_AH)==11 and emu.reg_read(UC_X86_REG_DS)==reqseg and emu.reg_read(UC_X86_REG_SI)==0x200
   assert bytes(emu.mem_read(request,16))==struct.pack('<IHIHI',rounded,7,(-tag)&0xffffffff,0,destfar);calls.append('manager')
   if ok and length:emu.mem_write(base+2,pixels)
   emu.reg_write(UC_X86_REG_AX,ok);emu.reg_write(UC_X86_REG_BL,error);return
  if address not in ((load+0x277)*16+2,(load+0xfba)*16+0xc):return
  sp=emu.reg_read(UC_X86_REG_SP);args=bytes(emu.mem_read(ds*16+sp+4,10))
  if address==(load+0xfba)*16+0xc:
   assert fatal and struct.unpack('<3H',args[:6])==(0xc83,0,error<<8);diagnostic.append(True);emu.emu_stop();return
  assert fromfile and struct.unpack('<IIH',args)==(destfar,tag,area);calls.append('file')
  if length:emu.mem_write(base+2,pixels)
  emu.reg_write(UC_X86_REG_DX,0x6a6a);retip,retcs=struct.unpack('<HH',bytes(emu.mem_read(ds*16+sp,4)));emu.reg_write(UC_X86_REG_SP,sp+4);emu.reg_write(UC_X86_REG_CS,retcs);emu.reg_write(UC_X86_REG_IP,retip)
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((load+0x768)*16+0x4d8,0xfffff,count=3000)
 assert bool(done)==(not fatal) and bool(diagnostic)==fatal and calls==(['file'] if fromfile else ['manager'])
 assert bytes(u.mem_read(ds*16,len(dg)))==expected and bytes(u.mem_read(reqseg*16,512))==table
 for a,raw in slots:assert bytes(u.mem_read(a,len(raw)))==raw,(load,count,index,width,height,hex(tag),owner,ok,error,hex(a))
 if not fatal:
  assert u.reg_read(UC_X86_REG_AX)==off and u.reg_read(UC_X86_REG_DX)==(0x6a6a if fromfile else 0 if ok else error<<8)
  for reg,val in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_SP,0xf004)]:assert u.reg_read(reg)==val
  assert bytes(u.mem_read(ds*16+0xf000,6))==frame
 cases.append(dict(load=load,slot_count=count,index=index,next_index=next_index,width=width,height=height,area=area,tag_hex='%08X'%tag,old_owner=owner,manager_AX=ok,manager_BL=error,requested_length=length,path='file' if fromfile else 'XMS',diagnostic=fatal,status='PASS'))
for load,count,(width,height),tag,owner,(ok,error) in itertools.product((0x824,0x1000),(1,2,5,128),((0,0),(1,1),(16,24),(48,64),(64,48)),(0,0xfffffc00,0xffffe000,0xbc0a),(0,1),((1,0),(0,0x7f),(0,0x80))):
 if 0<tag<0x80000000 and (ok,error)!=(1,0):continue
 for index in sorted({0,count-1}):run(load,count,index,width,height,tag,owner,ok,error)
save('cases',cases);save('instruction_execution_coverage',[dict(function='object_image_cyclic_cache_fill',image_offset=p,executed=p in visited) for p in sorted(starts)])
s=dict(functions=[dict(name='object_image_cyclic_cache_fill',start=0x7b58,end_exclusive=0x7c00,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows))],cases=len(cases),failures=0,executed_instruction_starts=len(visited),unexecuted_starts=sorted(starts-visited),runtime_tests=0,new_deep_verified_bytes=0,scope='Whole original04D8+0350+07FE; external file/XMSmanager fixtures only. FullDGROUP,128 allocated3074B slots,pointer512B table,request/records/index/counter/return checked. Valid0..3072B helper cases;zero-area synthetic. File DX poison proves no FAR-return contract. No native/renderer/invalid-large-image safety claim.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,image.parent/'relocations.csv',Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
