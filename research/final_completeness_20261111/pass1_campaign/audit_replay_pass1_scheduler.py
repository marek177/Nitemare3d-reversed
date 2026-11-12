"""python audit_replay_pass1_scheduler.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
lookup={(r['cs'],r['ip']):r for r in json.loads(inventory.read_text())};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
todo=[0x3c8];decoded={}
while todo:
    ip=todo.pop()
    if ip in decoded:continue
    assert 0x3c8<=ip<0x4d6;i=Decoder(16,b[0xbde0+ip:0xc2b6],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
rows=[]
for ip,i in sorted(decoded.items()):
    raw=b[0xbde0+ip:0xbde0+i.next_ip];assert lookup[(0xbde,ip)]['bytes']==raw.hex();rows.append(dict(cs=0xbde,ip=ip,image_offset=0xbde0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
save('game_scheduler',rows)
fields=[dict(name=n,start=a,end_exclusive=a+4,length=4,type='mutable_DWORD_scheduler_state_initial_zero',status='PARTIAL',range_sha256=sha(b[a:a+4])) for n,a in [('scheduler_last_sample',0x28e44),('scheduler_next_bucket8',0x28e48),('scheduler_next_bucket_config',0x28e4c)]]
assert not any(b[0x28e44:0x28e50]);save('data_fields',fields)
targets={'cached':0xbe74,'sample':0xbdf8,'bucket8':0xbeb4,'bucket_config':0xbef4,'tick_action':0xc150,'prepare':0xc0d8,'step':0xbf36,'update_a':0xa0b8,'update_b':0xa236,'world':0xaea,'update_c':0x8230,'flip_sync':0x1608,'flip_immediate':0x15ee,'input':0x70d6,'poll':0xbde4}
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0xbde;state={}
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    reverse={load*16+v:k for k,v in targets.items()}
    for a in reverse:u.mem_write(a,b'\xcb')
    def put(off,x):u.mem_write(ds*16+off,struct.pack('<I',x))
    def get(off):return struct.unpack('<I',u.mem_read(ds*16+off,4))[0]
    def hook(uc,a,size,data):
        if a not in reverse:return
        n=reverse[a];state['trace'].append(n);sp=uc.reg_read(UC_X86_REG_SP)
        if n in ('cached','sample'):
            v=state[n].pop(0);uc.reg_write(UC_X86_REG_AX,v&65535);uc.reg_write(UC_X86_REG_DX,v>>16)
        elif n in ('bucket8','bucket_config'):
            assert struct.unpack('<I',uc.mem_read(0x50000+sp+4,4))[0]==state['t0'];v=state['tick'];uc.reg_write(UC_X86_REG_AX,v&65535);uc.reg_write(UC_X86_REG_DX,v>>16)
        elif n=='tick_action':assert struct.unpack('<I',uc.mem_read(0x50000+sp+4,4))[0]==state['tick']
        elif n=='poll':state['poll_args'].append(struct.unpack('<H',uc.mem_read(0x50000+sp+4,2))[0])
    u.hook_add(UC_HOOK_CODE,hook)
    for tick,da,db,demo,parity,frame_delta,watch_delta in itertools.product((0,1,65535,65536,0xffffffff),('below','equal','above'),('below','equal','above'),(0,1),(0,1),(0,64,65,0xffffffff),(0,500,501,0xffffffff)):
        a=(tick+{'below':-1,'equal':0,'above':1}[da])&0xffffffff;d=(tick+{'below':-1,'equal':0,'above':1}[db])&0xffffffff
        t0=0x12345678;t1=(t0+frame_delta)&0xffffffff;r0=0x87654321;last=(r0-watch_delta)&0xffffffff;r1=0x13572468
        trace=['cached','sample','bucket8'];newa=a;newd=d;newlast=last
        if a<=tick:
            if not demo:trace.append('tick_action')
            newa=(tick+1)&0xffffffff
        trace.append('bucket_config')
        if d<=tick:
            if demo and parity:trace.append('tick_action')
            trace+=['prepare','step','update_a','update_b','world','update_c','cached','flip_sync' if frame_delta<65 else 'flip_immediate','input'];newd=(tick+1)&0xffffffff;newlast=r0
        watchdog=((r0-newlast)&0xffffffff)>500
        if watchdog:trace+=['poll','poll','sample'];newlast=r1
        put(0x1738,a);put(0x173c,d);put(0x1734,last);put(0x4540,parity);u.mem_write(ds*16+0x3cd6,struct.pack('<H',demo))
        state.clear();state.update(trace=[],poll_args=[],cached=[t0,t1],sample=[r0,r1],tick=tick,t0=t0)
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.mem_write(0x5ff00,struct.pack('<HH',0x6000,cs));u.emu_start(cs*16+0x3c8,cs*16+0x6000,count=1000)
        assert state['trace']==trace and state['poll_args']==([1,0] if watchdog else []),(tick,a,d,demo,parity,frame_delta,watch_delta,state['trace'],trace)
        assert (get(0x1738),get(0x173c),get(0x1734),get(0x3672),get(0x3676))==(newa,newd,newlast,tick,tick)
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_DS)==ds
        cases.append(dict(load=load,tick=tick,deadline8=a,deadline_config=d,demo=demo,parity=parity,frame_delta=frame_delta,watch_delta=watch_delta,trace=';'.join(trace),passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=[dict(name='game_scheduler',start=0xc1a8,end_exclusive=0xc2b6,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows))],typed_bytes=12,cases=len(cases),failures=0,mocked_targets=targets,scope='original complete scheduler control body; all 15 dependencies mocked with ordered trace/argument checks; no actual time, world update or VGA',natural_scheduler_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
