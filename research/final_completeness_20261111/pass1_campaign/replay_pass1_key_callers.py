"""Original dispatch->wrapper->selector path; synthetic entry args/DS only.
Usage: python replay_pass1_key_callers.py IMAGE UNICORN_DIR OUT_DIR
"""
import hashlib,json,struct,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();h=hashlib.sha256(b).hexdigest();assert h=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
expected={0x142c:'83fe19',0x142f:'7c13',0x1431:'83fe1c',0x1434:'7f0e',0x143d:'9a1a1e290d',0xf0b0:'8b7e088d45e7508bf8',0xf0b9:'9a361f3d08'}
for a,v in expected.items():assert b[a:a+len(bytes.fromhex(v))]==bytes.fromhex(v)
cases=[]
for item,entry_ds in [(v,0x2771) for v in (24,25,26,27,28,29)]+[(25,0x2222)]:
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,b)
    for reg,v in [(UC_X86_REG_CS,0xf7),(UC_X86_REG_DS,entry_ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0x8000),(UC_X86_REG_BP,0x1234)]:u.reg_write(reg,v)
    u.mem_write(0x78000,struct.pack('<HHHHH',0x6000,0xf7,0x100,0x4000,item));u.mem_write(0x40100,b'\x03')
    trace=[];events=[]
    def hook(uc,a,size,user):
        trace.append(a)
        if a==0xa306:
            sp=uc.reg_read(UC_X86_REG_SP);ss=uc.reg_read(UC_X86_REG_SS);arg=struct.unpack('<H',bytes(uc.mem_read(ss*16+sp+4,2)))[0]
            events.append(dict(event='selector_entry',index=arg,ds=uc.reg_read(UC_X86_REG_DS),ss=ss,cs=uc.reg_read(UC_X86_REG_CS),ip=uc.reg_read(UC_X86_REG_IP)));uc.emu_stop()
        elif a in (0x1424,0x1453,0x1469,0x1475):events.append(dict(event='other_dispatch_call',image_offset=a));uc.emu_stop()
    u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x13f4,0x100000,count=1000)
    assert len(events)==1
    if 25<=item<=28:assert events[0]['event']=='selector_entry' and events[0]['index']==item-25 and events[0]['ds']==entry_ds
    else:assert events[0]['event']=='other_dispatch_call' and events[0]['image_offset']==(0x1424 if item==24 else 0x1453)
    cases.append(dict(item_code=item,entry_DS=entry_ds,entry_SS=0x7000,events=events,instruction_trace=trace,assertions_passed=True))
out.mkdir(parents=True,exist_ok=True)
r=dict(image_sha256=h,unicorn_version=unicorn.__version__,native_libraries=[dict(name=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in dep.rglob('*.dll')],cases=cases,controlled_replay_cases=len(cases),key_route_signed_bounds=[25,28],selector_index_formula='(item_code-25) & FFFFh',known_route_preserves_incoming_DS=True,global_incoming_DS_proven=False,all_indirect_callers_excluded=False,new_deep_verified_bytes=0,runtime_tests=0,scope='actual dispatch and FAR calls up to selector entry; external entry state synthetic; no dialog/game runtime execution')
(out/'evidence.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(controlled_replay_cases=len(cases),assertions_passed=True,runtime_tests=0)))
