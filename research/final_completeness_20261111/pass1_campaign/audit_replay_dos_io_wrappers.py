"""python audit_replay_dos_io_wrappers.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);functions=[];callers=[];cases=[]
out.mkdir(parents=True,exist_ok=True)
for name,start,end,ah in [('dos_read_wrapper',0x9e,0xb7,0x3f),('dos_write_wrapper',0xb8,0xd1,0x40)]:
    instructions=[]
    for i in Decoder(16,b[0xfba0+start:0xfba0+end],ip=start):
        assert not i.is_invalid;raw=b[0xfba0+i.ip:0xfba0+i.next_ip];assert lookup[(0xfba,i.ip)]['bytes']==raw.hex()
        instructions.append(dict(cs=0xfba,ip=i.ip,image_offset=0xfba0+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(instructions[0]));w.writeheader();w.writerows(instructions)
    functions.append(dict(name=name,start=0xfba0+start,end_exclusive=0xfba0+end,instruction_bytes=end-start,instructions=len(instructions)))
    for r in old:
        if r['mnemonic']=='lcall' and r['operands']=='0xfba, '+hex(start):
            raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw
            i=Decoder(16,raw,ip=r['ip']).decode();assert i.far_branch_selector==0xfba and i.far_branch16==start
            callers.append(dict(wrapper=name,cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex()))
    for load in (0,0x1000):
        u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0xfba;ds=load+0x2771;dest=load+0x6000;state={}
        def interrupt(uc,n,data):
            assert n==0x21 and uc.reg_read(UC_X86_REG_AH)==ah
            assert (uc.reg_read(UC_X86_REG_BX),uc.reg_read(UC_X86_REG_DS),uc.reg_read(UC_X86_REG_DX),uc.reg_read(UC_X86_REG_CX))==(7,dest,0xfff0,state['count'])
            state['seen']+=1;uc.reg_write(UC_X86_REG_AX,state['returned_ax']);uc.reg_write(UC_X86_REG_EFLAGS,0x402|state['carry'])
        u.hook_add(UC_HOOK_INTR,interrupt)
        for count in (0,1,8192,65535):
            for carry in (0,1):
                for returned in (0,1,5,8192,65535):
                    for r,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x4444),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,2)]:u.reg_write(r,v)
                    u.mem_write(0x5ff00,struct.pack('<6H',0x4000,cs,7,0xfff0,dest,count));state.update(count=count,carry=carry,returned_ax=returned,seen=0)
                    u.emu_start(cs*16+start,cs*16+0x4000,count=100)
                    actual=u.reg_read(UC_X86_REG_AX);flags=u.reg_read(UC_X86_REG_EFLAGS)
                    assert actual==(65535 if carry else returned) and flags&1==carry and flags&0x400
                    assert state['seen']==1 and u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x4444 and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DI)==0x9abc
                    cases.append(dict(wrapper=name,load_segment=load,count=count,interrupt_cf=carry,interrupt_ax=returned,wrapper_ax=actual,wrapper_cf=flags&1,passed=True))
for name,rows in [('direct_far_callers',callers),('cases',cases)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,cases=len(cases),failures=0,direct_far_callers=len(callers),scope='original wrapper instructions; INT 21h outputs explicitly seeded; no original DOS/filesystem operation',dos_callee_behavior_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
