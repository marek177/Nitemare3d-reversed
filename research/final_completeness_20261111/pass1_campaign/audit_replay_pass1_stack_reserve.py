"""python audit_replay_pass1_stack_reserve.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
lookup={(r['cs'],r['ip']):r for r in json.loads(inventory.read_text())};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rows=[]
for i in Decoder(16,b[0x121a6:0x121ca],ip=0x2c6):
    assert not i.is_invalid;raw=b[0x11ee0+i.ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,i.ip)]['bytes']==raw.hex();rows.append(dict(cs=0x11ee,ip=i.ip,image_offset=0x11ee0+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
assert i.next_ip==0x2ea;save('crt_stack_reserve',rows)
fields=[dict(name=n,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e])) for n,a,e,t in [('crt_stack_overflow_handler',0x29866,0x2986a,'mutable_FAR16_pointer_initial_FFFF_FFFF_offset_FFFF_is_sentinel'),('crt_stack_lower_bound',0x2986a,0x2986c,'mutable_WORD_initial_E130_unsigned_stack_limit')]]
assert b[0x29866:0x2986c]==bytes.fromhex('ffffffff30e1');save('data_fields',fields)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x11ee;ds=load+0x2771
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    def run(amount,sp,limit,handler):
        top=sp+4;candidate=(top-amount)&65535;success=top>=amount and candidate>=limit
        u.mem_write(ds*16+0x2156,struct.pack('<HHH',handler,0x6000,limit))
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,sp),(UC_X86_REG_AX,amount),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.mem_write(0x50000+sp,struct.pack('<HH',0x6000,cs))
        stop=cs*16+0x6000 if success else cs*16+0xf4 if handler==65535 else 0x60000+handler
        u.emu_start(cs*16+0x2c6,stop,count=100)
        assert u.reg_read(UC_X86_REG_CS)*16+u.reg_read(UC_X86_REG_IP)==stop
        assert u.reg_read(UC_X86_REG_SP)==(candidate if success else sp) and u.reg_read(UC_X86_REG_DS)==ds
        if not success:
            assert bytes(u.mem_read(0x50000+sp,4))==struct.pack('<HH',0x6000,cs)
            if handler==65535:assert u.reg_read(UC_X86_REG_AX)==0
        cases.append(dict(load=load,amount=amount,entry_sp=sp,limit=limit,handler_offset=handler,outcome='return' if success else 'shared_error_entry' if handler==65535 else 'handler_entry',final_sp=u.reg_read(UC_X86_REG_SP),passed=True))
    if load==0:
        for amount in range(65536):run(amount,0xff00,0xe130,65535)
    for sp,limit,handler in itertools.product((0x100,0xb000,0xf000,0xff00),(0,0xe130,65535),(65535,0x100)):
        top=sp+4;amounts=sorted({0,1,2,3,4,65535,top,top+1,max(0,top-limit),max(0,top-limit+1)})
        for amount in amounts:run(amount,sp,limit,handler)
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=[dict(name='crt_stack_reserve',start=0x121a6,end_exclusive=0x121ca,instruction_bytes=36,instructions=len(rows))],typed_bytes=6,cases=len(cases),failures=0,scope='original compiler stack-reserve helper; success return executed, error/handler paths stop at their entry without execution; seeded SS and DS',shared_error_handler_closed=False,custom_handler_closed=False,natural_callers_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
