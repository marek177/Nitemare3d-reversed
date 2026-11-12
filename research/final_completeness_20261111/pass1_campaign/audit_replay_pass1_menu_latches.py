"""python audit_replay_pass1_menu_latches.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
lookup={(r['cs'],r['ip']):r for r in json.loads(inventory.read_text())};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
spec=[('menu_mouse_latches',0x42a,0x46d),('menu_aux_latches',0x4b1,0x4f1)];prefixes=[];rows=[]
for name,start,end in spec:
    items=[];todo=[start];decoded={}
    while todo:
        ip=todo.pop()
        if ip==end or ip in decoded:continue
        assert start<=ip<end;i=Decoder(16,b[0x6b00+ip:0x6b00+end],ip=ip).decode();decoded[ip]=i
        if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
        if i.flow_control!=FlowControl.UNCONDITIONAL_BRANCH:todo.append(i.next_ip)
    for ip,i in sorted(decoded.items()):
        assert not i.is_invalid;raw=b[0x6b00+i.ip:0x6b00+i.next_ip];assert lookup[(0x6b0,i.ip)]['bytes']==raw.hex();items.append(dict(cs=0x6b0,ip=i.ip,image_offset=0x6b00+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
    assert i.next_ip==end;rows.extend(items);prefixes.append(dict(name=name,start=0x6b00+start,end_exclusive=0x6b00+end,instruction_bytes=sum(len(bytes.fromhex(x['bytes'])) for x in items),instructions=len(items),scope='interior no-call menu prefix only'))
save('instructions',rows)
fields=[dict(name=n,start=a,end_exclusive=a+1,length=1,type='mutable_BYTE_menu_input_history_initial_'+str(b[a]),status='PARTIAL',range_sha256=sha(b[a:a+1])) for n,a in [('menu_aux_primary_history',0x28268),('menu_aux_secondary_latch',0x28269),('menu_mouse_primary_history',0x2826a),('menu_mouse_secondary_latch',0x2826b)]]
assert b[0x28268:0x2826c]==bytes([0,1,0,1]);save('data_fields',fields);rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x6b0
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    for name,start,end in spec:
        inputs=itertools.product((0,1,2,3,65535),(0,)) if start==0x42a else itertools.product((0,1,255,256,65535),repeat=2)
        for p,s in inputs:
            for oldp,olds,key in itertools.product((0,1,255),(0,1,255),(0,13,27,65)):
                primary=(p&1) if start==0x42a else p;secondary=bool(p&2) if start==0x42a else bool(s);newkey=key
                if primary==0 and oldp:newkey=13
                if secondary and olds==0:newkey=27
                newp=primary&255;news=int(secondary or newkey==13);off=0xb5a if start==0x42a else 0xb58
                u.mem_write(ds*16+off,bytes([oldp,olds]));u.mem_write(0x5fef0,bytes(32));bp=0xff00
                u.mem_write(0x50000+bp-4,struct.pack('<H',0xab00|key))
                if start==0x42a:u.mem_write(0x50000+bp-6,struct.pack('<H',p))
                else:u.mem_write(0x50000+bp-0x12,struct.pack('<HH',p,s))
                for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xfe00),(UC_X86_REG_BP,bp),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
                u.emu_start(cs*16+start,cs*16+end,count=100)
                actual_key=struct.unpack('<H',u.mem_read(0x50000+bp-4,2))[0]
                assert actual_key==(0xab00|newkey) and bytes(u.mem_read(ds*16+off,2))==bytes([newp,news])
                assert u.reg_read(UC_X86_REG_BP)==bp and u.reg_read(UC_X86_REG_SP)==0xfe00 and u.reg_read(UC_X86_REG_DS)==ds
                cases.append(dict(load=load,prefix=name,input_primary=p,input_secondary=s,old_primary=oldp,old_secondary=olds,input_key=key,result_key=newkey,result_primary=newp,result_secondary=news,passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),prefixes=prefixes,prefix_instruction_bytes=sum(x['instruction_bytes'] for x in prefixes),prefix_instructions=len(rows),typed_bytes=4,cases=len(cases),failures=0,scope='two original no-call interior prefixes only; SS locals and histories seeded; no input driver or menu loop executed',natural_input_domain_closed=False,full_menu_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))

