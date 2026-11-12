"""python audit_replay_pass1_tick_buckets.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,OpKind
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
functions=[]
for name,start,end in [('game_tick_bucket_8',0xd4,0x113),('game_tick_bucket_configured',0x114,0x155)]:
    todo=[start];decoded={}
    while todo:
        ip=todo.pop()
        if ip in decoded:continue
        assert start<=ip<end;i=Decoder(16,b[0xbde0+ip:0xbde0+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
        if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
        if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
    rows=[]
    for ip,i in sorted(decoded.items()):
        raw=b[0xbde0+ip:0xbde0+i.next_ip];assert lookup[(0xbde,ip)]['bytes']==raw.hex();rows.append(dict(cs=0xbde,ip=ip,image_offset=0xbde0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    save(name,rows);functions.append(dict(name=name,start=0xbde0+start,end_exclusive=0xbde0+end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows)))
fields=[]
for name,a in [('game_tick_8_counter',0x28e06),('game_tick_8_last_bucket',0x28e0a),('game_tick_config_counter',0x28e0e),('game_tick_config_last_bucket',0x28e12)]:fields.append(dict(name=name,start=a,end_exclusive=a+4,length=4,type='mutable_DWORD_initial_zero',status='PARTIAL',range_sha256=sha(b[a:a+4])))
assert not any(b[0x28e06:0x28e16]);save('data_fields',fields)
callers=[]
for r in old:
    i=Decoder(16,bytes.fromhex(r['bytes']),ip=r['ip']).decode()
    if i.flow_control==FlowControl.CALL:
        target=(r['cs'],i.near_branch_target) if i.op0_kind==OpKind.NEAR_BRANCH16 else (i.far_branch_selector,i.far_branch16) if i.op0_kind==OpKind.FAR_BRANCH16 else None
        if target in ((0xbde,0xd4),(0xbde,0x114)):callers.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],target_ip=target[1],bytes=r['bytes'],instruction=fmt.format(i)))
save('direct_callers',callers);cases=[];rel=list(csv.DictReader((image.parent/'relocations.csv').open()))
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0xbde
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    def put(off,x):u.mem_write(ds*16+off,struct.pack('<I',x))
    def get(off):return struct.unpack('<I',u.mem_read(ds*16+off,4))[0]
    def run(entry,value,rate):
        u.mem_write(ds*16+0x3cc2,struct.pack('<h',rate))
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.mem_write(0x5ff00,struct.pack('<HHI',0x6000,cs,value));u.emu_start(cs*16+entry,cs*16+0x6000,count=100)
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_DS)==ds
        return u.reg_read(UC_X86_REG_DX)*65536+u.reg_read(UC_X86_REG_AX)
    sequences=[('consecutive_milliseconds',list(range(5001)),0,0),('jumps_and_reverse',[0,125,125,1000,999,0,0xffffffff,0x20000000,0x1fffffff,0x80000000,0],0,0),('counter_wrap',[125,250,250,0],0xfffffffe,0),('unchanged_nonzero',[1000,1000],27,8)]
    for entry,rate in [(0xd4,8)]+[(0x114,r) for r in (-32768,-1,0,1,8,25,1000,32767)]:
        counter_off,last_off=(0x16f6,0x16fa) if entry==0xd4 else (0x16fe,0x1702)
        for kind,values,counter,last in sequences:
            put(counter_off,counter);put(last_off,last)
            for step,value in enumerate(values):
                bucket=((value*(8 if entry==0xd4 else rate&0xffffffff))&0xffffffff)//1000
                if bucket!=last:counter=(counter+1)&0xffffffff;last=bucket
                actual=run(entry,value,rate);assert actual==counter and get(counter_off)==counter and get(last_off)==last,(entry,rate,value,bucket,last,counter,actual)
                cases.append(dict(load=load,entry=entry,rate=rate,sequence=kind,step=step,input=value,bucket=bucket,counter=counter,passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,typed_bytes=16,cases=len(cases),failures=0,direct_caller_count=len(callers),scope='original complete FAR functions; no mocked dependencies; DWORD args and mutable state seeded; finite sequences, not full input/state closure',natural_call_sequence_closed=False,scheduler_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
