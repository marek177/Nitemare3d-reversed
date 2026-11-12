"""python audit_replay_pass1_crt_format_table.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);table=b[0x299da:0x29a33]
assert len(table)==89 and max(v&15 for v in table)==8 and max(v>>4 for v in table[:72])<=7
instructions=[]
for i in Decoder(16,b[0x13556:0x1357f],ip=0x1676):
    assert not i.is_invalid;raw=b[0x11ee0+i.ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,i.ip)]['bytes']==raw.hex()
    instructions.append(dict(cs=0x11ee,ip=i.ip,image_offset=0x11ee0+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
assert instructions[-1]['ip']==0x169a
dispatch=[]
for state,target in enumerate(struct.unpack_from('<8H',b,0x13518)):
    r=lookup[(0x11ee,target)];raw=bytes.fromhex(r['bytes']);assert b[0x11ee0+target:0x11ee0+target+len(raw)]==raw
    i=Decoder(16,raw,ip=target).decode();assert not i.is_invalid and i.len==len(raw)
    dispatch.append(dict(state=state,table_image=0x13518+state*2,target_cs=0x11ee,target_ip=target,target_instruction=fmt.format(i),target_bytes=raw.hex()))
rows=[]
for n,v in enumerate(table):rows.append(dict(image_offset=0x299da+n,ds_offset=0x22ca+n,byte=v,character_code=0x20+n,low_nibble_character_class=v&15,high_nibble_next_state=v>>4,transition_class=n//8 if n<72 else '',transition_old_state=n%8 if n<72 else ''))
cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x11ee;ds=load+0x2771
    for ch in range(256):
        index=(ch-32)&255;cl=table[index]&15 if index<=88 else 0
        for previous in range(8):
            new=table[cl*8+previous]>>4
            for r,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_BP,0xff00),(UC_X86_REG_SP,0xfe00),(UC_X86_REG_AX,0xab00|ch),(UC_X86_REG_EFLAGS,2)]:u.reg_write(r,v)
            u.mem_write(0x5fefb,bytes([previous]));u.emu_start(cs*16+0x1676,cs*16+0x169a,count=100)
            assert u.mem_read(0x5fefb,1)[0]==new and u.reg_read(UC_X86_REG_AX)==new and u.reg_read(UC_X86_REG_BX)==2*new
            cases.append(dict(load_segment=load,character=ch,old_state=previous,character_class=cl,transition_index=cl*8+previous,new_state=new,dispatch_target=dispatch[new]['target_ip']))
field=dict(name='crt_format_shared_class_transition_table',start=0x299da,end_exclusive=0x29a33,length=89,type='packed_BYTE_low4_charclass_high4_DFA_state',status='PARTIAL',range_sha256=sha(table))
out.mkdir(parents=True,exist_ok=True)
for name,data in [('prefix_instructions',instructions),('table_bytes',rows),('dispatch_targets',dispatch),('data_fields',[field]),('cases',cases)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=89,prefix_start=0x13556,prefix_end_exclusive=0x1357f,executed_stop_before_image=0x1357a,decoded_prefix_instructions=len(instructions),states=8,classes=9,cases=len(cases),failures=0,dispatch_targets=8,scope='seeded classifier/transition prefix, stop before indirect JMP; full formatter handlers not replayed',full_formatter_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
