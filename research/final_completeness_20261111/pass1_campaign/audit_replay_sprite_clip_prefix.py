"""python audit_replay_sprite_clip_prefix.py IMAGE INVENTORY DECODER EMULATOR OUT
Execute original renderer only through IP0738, before VGA DS switch/port I/O.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UcError,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_ERR_EXCEPTION
from unicorn.x86_const import *
sha=lambda x:hashlib.sha256(x).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rs):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
rows=[];cfg=[];starts=set();todo=[0x5de];decoded={}
while todo:
 ip=todo.pop()
 if ip in decoded:continue
 assert 0x5de<=ip<0x7dd
 i=Decoder(16,b[0x1560+ip:0x1d3d],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
 if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
 if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
for ip,i in sorted(decoded.items()):
 p=0x1560+ip
 assert not i.is_invalid and lookup[p]['bytes']==b[p:p+i.len].hex();starts.add(i.ip)
 rows.append(dict(cs=0x156,ip=i.ip,image_offset=p,bytes=b[p:p+i.len].hex(),instruction=fmt.format(i)));p+=i.len
 if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):cfg.append(dict(source=i.ip,target=i.near_branch_target,kind='branch'))
 if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):cfg.append(dict(source=i.ip,target=i.next_ip,kind='fallthrough'))
assert p==0x1d3d and rows[-1]['bytes']=='cb'
assert all(e['target'] in starts for e in cfg)
save('sprite_scaled_clip',rows);save('cfg_edges',cfg)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];seen=set();mask=lambda n:n&65535
rects=[(10,20,10,20),(-5,15,5,25),(5,25,-5,15),(-5,25,-5,25),(0,31,0,31),(10,11,10,11)]
clips=[(0,31,0,31),(4,24,4,24),(12,18,12,18)]
for load,width,height,rect,clip,objflag in itertools.product((0,0x1000),(1,7,31),(1,8,63),rects,clips,(0,0x10)):
 x1,x2,y1,y2=rect;left,right,top,bottom=clip;h=y2-y1+1;step=(height<<16)//h
 # Independent expression model retains the instruction branch order and +2 X count.
 visible=h;source=0x9000;acc=0;available=width;nx=x1;ny=y1;columns=x2-x1+2;frac=0
 if y2>bottom:visible+=bottom-y2
 if top>y1:
  ny=top;visible-=top-y1;acc=(step*(top-y1))&0xffffffff;source=mask(source+(acc>>16))
 expected_fault=False
 if x2>=right:columns=right-x1+1
 elif left>x1:
  nx=left;columns=x2-left+2;expected_fault=mask(visible)==0;advance=0 if expected_fault else (((height<<16)//mask(visible))*(left-x1))&0xffffffff;frac=advance&65535
  source=mask(source+height*(advance>>16));available=mask(available-(advance>>16))
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for r in rel:struct.pack_into('<H',runtime,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));ds=load+0x2771;cs=load+0x156;slot=0x50f2;resource=0x8000
 fields={6:resource,8:x1,10:x2,12:y1,14:y2,16:0x1234}
 for off,val in fields.items():u.mem_write(ds*16+slot+off,struct.pack('<H',mask(val)))
 u.mem_write(ds*16+slot+2,struct.pack('<HH',0x100,0x7000));u.mem_write(0x70105,bytes([objflag]))
 u.mem_write(ds*16+resource,bytes([width,height]));u.mem_write(ds*16+resource+6,struct.pack('<HH',0x9000,0x6000))
 for off,val in zip((0x4548,0x454a,0x454c,0x454e),(left,right,top,bottom)):u.mem_write(ds*16+off,struct.pack('<H',mask(val)))
 for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x4567),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x6789),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 u.mem_write(0x5ff00,struct.pack('<HHH',0x6000,cs,slot));hit=set()
 u.hook_add(UC_HOOK_CODE,lambda uc,address,size,user:hit.add(address-cs*16))
 trapped=False
 try:u.emu_start(cs*16+0x5de,cs*16+0x738,count=500)
 except UcError as e:
  assert expected_fault and e.errno==UC_ERR_EXCEPTION and u.reg_read(UC_X86_REG_IP)==0x6ea;trapped=True
 assert trapped==expected_fault
 if trapped:
  cases.append(dict(load=load,width=width,height=height,x1=x1,x2=x2,y1=y1,y2=y2,left=left,right=right,top=top,bottom=bottom,object_bit4=bool(objflag),source_offset=None,x_start=None,y_start=None,columns=None,rows=None,step=step,available_columns=None,expected_divide_fault=True,passed=True));continue
 assert u.reg_read(UC_X86_REG_IP)==0x738
 bp=u.reg_read(UC_X86_REG_BP);local=lambda off:struct.unpack('<H',bytes(u.mem_read(0x50000+mask(bp+off),2)))[0]
 expected={-2:source,-4:0x6000,-8:resource,-10:mask(nx),-12:mask(ny),-14:mask(columns),-16:mask(visible),-18:height,-20:available,-22:0x1234,-24:0,-26:mask(0x47e4+2*nx),-34:step&65535,-36:step>>16,-38:frac,-40:acc&65535}
 for off,val in expected.items():assert local(off)==val,(load,width,height,rect,clip,off,local(off),val)
 assert bytes(u.mem_read(0x50000+mask(bp-42),1))==bytes([objflag>>4]) and u.reg_read(UC_X86_REG_DS)==ds
 seen.update(hit);cases.append(dict(load=load,width=width,height=height,x1=x1,x2=x2,y1=y1,y2=y2,left=left,right=right,top=top,bottom=bottom,object_bit4=bool(objflag),source_offset=source,x_start=nx,y_start=ny,columns=mask(columns),rows=mask(visible),step=step,available_columns=available,expected_divide_fault=False,passed=True))
save('cases',cases);save('prefix_visited_starts',[dict(cs=0x156,ip=ip,image_offset=0x1560+ip) for ip in sorted(seen)])
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=[dict(name='sprite_scaled_clip',start=0x1b3e,end_exclusive=0x1d3d,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows))],cases=len(cases),expected_divide_fault_cases=sum(r['expected_divide_fault'] for r in cases),failures=0,cases_sha256=sha((out/'cases.csv').read_bytes()),prefix_visited_instruction_starts=len(seen),prefix_stop_ip=0x738,full_function_cfg_edges=len(cfg),runtime_tests=0,new_deep_verified_bytes=0,scope='static full renderer boundaries/CFG; native prefix only to0738 before VGA port I/O and pixel loop; includes expected zero-visible-height divide faults, not full draw or natural runtime proof')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
