"""python audit_replay_sound_priority.py IMAGE INVENTORY DECODER EMULATOR OUT"""
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
todo=[0x3d6];decoded={};edges=[];calls=[]
while todo:
    ip=todo.pop()
    if ip in decoded:continue
    assert 0x3d6<=ip<0x4c9;i=Decoder(16,b[0xc2b0+ip:0xc779],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
        todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):
        todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
rows=[]
for ip,i in sorted(decoded.items()):
    raw=b[0xc2b0+ip:0xc2b0+i.next_ip];assert lookup[(0xc2b,ip)]['bytes']==raw.hex();rows.append(dict(cs=0xc2b,ip=ip,image_offset=0xc2b0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    if i.flow_control in (FlowControl.CALL,FlowControl.INDIRECT_CALL):calls.append(rows[-1])
save('sound_priority_dispatch',rows);save('cfg_edges',edges);save('calls',calls)
targets={'dsp_busy':0x11b71,'dsp_stop':0x11ae1,'other_busy':0x11ba3,'other_stop':0x11b10,'resource_get':0x7d04,'resource_load':0xc64e,'gain':0x1113c,'dsp_play':0x11601,'other_play':0x1154b}
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];visited=set()
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0xc2b
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    reverse={load*16+v:k for k,v in targets.items()};state={}
    for a in reverse:u.mem_write(a,b'\xcb')
    def hook(uc,a,size,data):
        if cs*16+0x3d6<=a<cs*16+0x4c9:visited.add(a-cs*16)
        if a not in reverse:return
        n=reverse[a];sp=uc.reg_read(UC_X86_REG_SP);arg=lambda count:struct.unpack('<'+'H'*count,uc.mem_read(0x50000+sp+4,2*count))
        if n.endswith('busy'):uc.reg_write(UC_X86_REG_AX,state['busy'])
        if n in ('resource_get','resource_load'):
            assert arg(1)==(2,);ptr=state['get'] if n=='resource_get' else state['fallback'];uc.reg_write(UC_X86_REG_AX,ptr&65535);uc.reg_write(UC_X86_REG_DX,ptr>>16)
        args=arg(2) if n in ('gain','dsp_play','other_play') else ()
        state['trace'].append((n,args))
    u.hook_add(UC_HOOK_CODE,hook)
    for enabled,length,dsp,busy,old,priority,resource,pan,volume in itertools.product((0,1),(0,1),(0,1),(0,1),(0,1,2,255),(0,1,2,255),(0,1,2),(0,1,2,65535),(0,100,255)):
        get=0x60001234 if resource==0 else 0;fallback=0x60005678 if resource==1 else 0
        state.clear();state.update(trace=[],busy=busy,get=get,fallback=fallback)
        expected=[];new=old
        if enabled and length:
            expected.append(('dsp_busy' if dsp else 'other_busy',()))
            if not busy or old<=priority:
                if busy:expected.append(('dsp_stop' if dsp else 'other_stop',()))
                new=priority;expected.append(('resource_get',()));ptr=get
                if not ptr:expected.append(('resource_load',()));ptr=fallback
                if dsp:
                    gain=volume*15//100;expected.append(('gain',(0 if pan==1 else gain,0 if pan==2 else gain)))
                expected.append(('dsp_play' if dsp else 'other_play',(ptr&65535,ptr>>16)))
        for off,v in [(0x414e,enabled),(0x3cc7,dsp),(0x17e6,old),(0x414b,volume)]:u.mem_write(ds*16+off,bytes([v]))
        u.mem_write(ds*16+0x3f64+12,struct.pack('<H',length))
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x3333),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x9876),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
        u.mem_write(0x5ff00,struct.pack('<HHHHH',0x6000,cs,2,pan,priority));u.emu_start(cs*16+0x3d6,cs*16+0x6000,count=400)
        assert state['trace']==expected,(load,enabled,length,dsp,busy,old,priority,resource,pan,volume,state['trace'],expected)
        assert u.mem_read(ds*16+0x17e6,1)[0]==new
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x9876 and u.reg_read(UC_X86_REG_DS)==ds
        cases.append(dict(load=load,enabled=enabled,length=length,dsp=dsp,busy=busy,old_priority=old,priority=priority,resource=resource,pan=pan,volume=volume,trace=json.dumps(expected),passed=True))
save('cases',cases);assert visited==set(decoded),(set(decoded)-visited)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=[dict(name='sound_priority_dispatch',start=0xc686,end_exclusive=0xc779,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows))],cases=len(cases),failures=0,mocked_dependencies=targets,visited_instruction_starts=len(visited),static_instruction_starts=len(decoded),scope='original full dispatcher CFG with nine dependency stubs; sound ID 2, seeded DS, no original WORX playback or natural runtime',runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
