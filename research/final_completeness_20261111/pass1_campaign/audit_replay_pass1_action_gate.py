"""python audit_replay_pass1_action_gate.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);pending=[0xc56];decoded={};instructions=[];contexts=[]
while pending:
    ip=pending.pop()
    if ip in decoded:continue
    assert 0xc56<=ip<0xcac
    i=Decoder(16,b[0x83d0+ip:0x907c],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.near_branch_target)
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.next_ip)
for ip,i in sorted(decoded.items()):
    raw=b[0x83d0+ip:0x83d0+i.next_ip];assert lookup[(0x83d,ip)]['bytes']==raw.hex()
    instructions.append(dict(cs=0x83d,ip=ip,image_offset=0x83d0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
for cs,a,e in [(0x6b0,0xb3d,0xb60),(0xbde,0x3ae,0x3b8)]:
    for r in old:
        if r['cs']==cs and a<=r['ip']<e:
            raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw
            i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw)
            contexts.append(dict(cs=cs,ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
thresholds=list(b[0x28b4e:0x28b52]);assert thresholds==[2,1,3,1] and b[0x28b52]==0
fields=[]
for name,a,e,t in [('action_gate_thresholds',0x28b4e,0x28b52,'BYTE_array_4_nominal_selector_threshold'),('action_gate_counter',0x28b52,0x28b53,'mutable_saturating_BYTE_initial_0')]:fields.append(dict(name=name,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e])))
inputs=[(0,s,c,v) for s in range(4) for c in range(256) for v in (0,1,255,256,257)]
inputs += [(1,0,c,0) for c in range(256)]
inputs += [(mode,0,c,v) for mode in (2,65535) for c in (0,255) for v in (0,257)]
cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x83d;ds=load+0x2771
    for mode,selector,counter,event in inputs:
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.mem_write(0x5ff00,struct.pack('<4H',0x4000,cs,mode,event));u.mem_write(ds*16+0x418f,bytes([selector]));u.mem_write(ds*16+0x1442,bytes([counter]))
        result=(1 if selector==3 else event&255) if mode==0 and counter>=thresholds[selector] else 0
        new_counter=0 if result else min(counter+1,255) if mode==1 else counter
        u.emu_start(cs*16+0xc56,cs*16+0x4000,count=150)
        assert u.reg_read(UC_X86_REG_AL)==result and u.mem_read(ds*16+0x1442,1)[0]==new_counter
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_DS)==ds
        cases.append(dict(load_segment=load,mode=mode,selector=selector,counter_before=counter,event_word=event,result_al=result,counter_after=new_counter,passed=True))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('instructions',instructions),('caller_context',contexts),('data_fields',fields),('cases',cases)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),function_start=0x9026,function_end_exclusive=0x907c,function_span_bytes=86,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in instructions),instructions=len(instructions),typed_bytes=5,cases=len(cases),failures=0,scope='original complete gate; no mocked callees; selector 0..3 seeded; event low BYTE tested incl nonboolean and ignored high BYTE',natural_selector_bounds_closed=False,call_frequency_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
