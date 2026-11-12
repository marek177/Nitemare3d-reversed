"""python audit_replay_rtc_irq.py IMAGE INVENTORY DECODER EMULATOR OUT
Original registered RTC interrupt0002; controlled IN/OUT, true IRET frame.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INSN
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};rows=[]
for i in Decoder(16,b[0xbcc2:0xbce7],ip=2):
 assert not i.is_invalid;raw=b[0xbcc0+i.ip:0xbcc0+i.next_ip];rows.append(dict(cs=0xbcc,ip=i.ip,image_offset=0xbcc0+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
assert rows[-1]['instruction']=='iret' and rows[-1]['ip']==0x26
def save(name,rs):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
save('rtc_irq8_increment_cached_clock',rows);save('rtc_irq8_increment_cached_clock_cfg',[dict(source=r['ip'],target=rows[n+1]['ip'],kind='fallthrough') for n,r in enumerate(rows[:-1])])
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];visited=set()
for load,count,rtc,variant in itertools.product((0x824,0x1000),(0,0xffff,0xffffffff,0x7fffffff,0x80000000),(0,0x40,0x80,0xc0,0xff),(0,1)):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);code=bytearray(b)
 for r in rel:struct.pack_into('<H',code,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(code));ds=load+0x2771;ss=0x9000;dg=bytearray([0x5a]*0xe030);struct.pack_into('<I',dg,0x81e,count);pred=bytearray(dg);struct.pack_into('<I',pred,0x81e,(count+1)&0xffffffff);u.mem_write(ds*16,bytes(dg));frame=struct.pack('<HHH',0x100,0x5000,0x246+variant*0x400);u.mem_write(ss*16+0xf000,frame)
 regs={UC_X86_REG_EAX:0x1234abcd^(variant*0xffffffff),UC_X86_REG_EBX:0x22334455,UC_X86_REG_ECX:0x33445566,UC_X86_REG_EDX:0x44556677,UC_X86_REG_EBP:0x55667788,UC_X86_REG_ESI:0x66778899,UC_X86_REG_EDI:0x778899aa}
 for q,v in regs.items():u.reg_write(q,v)
 for q,v in [(UC_X86_REG_CS,load+0xbcc),(UC_X86_REG_DS,0x7777),(UC_X86_REG_ES,0x6666),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,0xf000),(UC_X86_REG_EFLAGS,0x46+variant*0x400)]:u.reg_write(q,v)
 io=[];done=[]
 def output(emu,port,size,value,data):io.append(('OUT',port,size,value))
 def inp(emu,port,size,data):io.append(('IN',port,size,rtc));return rtc
 def hook(emu,address,size,data):
  if address==0x50100:done.append(True);emu.emu_stop();return
  ip=address-(load+0xbcc)*16;assert 2<=ip<0x27;visited.add(ip)
 u.hook_add(UC_HOOK_INSN,output,None,1,0,UC_X86_INS_OUT);u.hook_add(UC_HOOK_INSN,inp,None,1,0,UC_X86_INS_IN);u.hook_add(UC_HOOK_CODE,hook);u.emu_start((load+0xbcc)*16+2,0,count=100)
 assert done and io==[('OUT',0x70,1,0xc),('IN',0x71,1,rtc),('OUT',0xa0,1,0x20),('OUT',0x20,1,0x20)]
 assert bytes(u.mem_read(ds*16,len(dg)))==pred and bytes(u.mem_read(ss*16+0xf000,6))==frame
 assert u.reg_read(UC_X86_REG_DS)==0x7777 and u.reg_read(UC_X86_REG_ES)==0x6666 and u.reg_read(UC_X86_REG_SS)==ss and u.reg_read(UC_X86_REG_SP)==0xf006 and u.reg_read(UC_X86_REG_EFLAGS)==0x246+variant*0x400
 for q,v in regs.items():assert u.reg_read(q)==v
 cases.append(dict(load=load,old_counter=count,new_counter=(count+1)&0xffffffff,RTC_C_result=rtc,register_variant=variant,status='PASS'))
assert visited==set(r['ip'] for r in rows);save('cases',cases)
result=dict(functions=[dict(name='rtc_irq8_increment_cached_clock',start=0xbcc2,end_exclusive=0xbce7,instructions=len(rows),instruction_bytes=37)],cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,original_inventory_missing_starts=sum(r['image_offset'] not in old for r in rows),executed_instruction_starts=len(visited),scope='whole original registeredRTC vector70handler0002, true interrupt frame/IRET; controlled RTC IN result and recorded OUTs; increments canonicalDS081E modulo2^32, saves32bit general registers andDS/ES; no natural IRQ writerPC captured in producer run, no physicalRTC correctness proof',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
