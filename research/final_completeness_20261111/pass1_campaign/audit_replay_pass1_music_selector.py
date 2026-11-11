"""python audit_replay_pass1_music_selector.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
relocations=list(csv.DictReader((image.parent/'relocations.csv').open()))
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);instructions=[]
pending=[0x288c];decoded={}
while pending:
    ip=pending.pop()
    if ip in decoded:continue
    assert 0x288c<=ip<0x28c8
    i=Decoder(16,b[0x83d0+ip:0xac98],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.near_branch_target)
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.next_ip)
for i in [decoded[ip] for ip in sorted(decoded)]:
    assert not i.is_invalid;raw=b[0x83d0+i.ip:0x83d0+i.next_ip];assert lookup[(0x83d,i.ip)]['bytes']==raw.hex()
    instructions.append(dict(cs=0x83d,ip=i.ip,image_offset=0x83d0+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
assert instructions[-1]['ip']==0x28c7
fields=[]
for name,a,e,t in [('episode_level_selection_nominal',0x28cd8,0x28cf6,'BYTE_matrix_3x10_conditional_episode_1_3_level_0_9'),('special_cycle_ids',0x28cf6,0x28cfa,'BYTE_array_4'),('special_cycle_counter',0x28cfa,0x28cfb,'mutable_wrapping_BYTE')]:fields.append(dict(name=name,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e])))
cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x83d;ds=load+0x2771;target=load*16+0xc548
    for r in relocations:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    u.mem_write(target,b'\xcb') # explicit mocked dependency: FAR return only
    observed=[]
    def hook(uc,address,size,data):
        if address==target:observed.append(struct.unpack('<H',uc.mem_read(0x50000+uc.reg_read(UC_X86_REG_SP)+4,2))[0])
    u.hook_add(UC_HOOK_CODE,hook)
    inputs=[(1,0,0,c) for c in range(256)]+[(0,e,l,173) for e in range(1,4) for l in range(10)]
    for mode,episode,level,counter in inputs:
        for r,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_SI,0x5678),(UC_X86_REG_BX,0xab00),(UC_X86_REG_EFLAGS,2)]:u.reg_write(r,v)
        u.mem_write(0x5ff00,struct.pack('<HH',0x4000,cs));u.mem_write(ds*16+0x3cd6,struct.pack('<H',mode));u.mem_write(ds*16+0x626a,struct.pack('<HH',episode,level));u.mem_write(ds*16+0x15ea,bytes([counter]))
        expected=b[0x28cf6+(counter&3)] if mode else b[0x27710+0x15be+10*episode+level]
        observed.clear();u.emu_start(cs*16+0x288c,cs*16+0x4000,count=200)
        actual_counter=u.mem_read(ds*16+0x15ea,1)[0]
        assert observed==[expected] and actual_counter==((counter+1)&255 if mode else counter),(load,mode,episode,level,counter,observed,expected,actual_counter)
        assert u.reg_read(UC_X86_REG_AX)==expected and u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DS)==ds
        cases.append(dict(load_segment=load,mode=mode,episode=episode,level=level,counter_before=counter,counter_after=actual_counter,selected_id=expected,callee_argument=observed[0]))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('instructions',instructions),('data_fields',fields),('cases',cases)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),function_start=0xac5c,function_end_exclusive=0xac98,function_span_bytes=60,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in instructions),instructions=len(instructions),typed_bytes=35,cases=len(cases),failures=0,mocked_callee='0C2B:0298 replaced by RETF; stack argument observed',natural_episode_level_bounds_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
