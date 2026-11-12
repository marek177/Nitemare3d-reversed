"""python audit_replay_pass1_audio_state.py IMAGE INVENTORY DECODER EMULATOR OUT"""
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
todo=[0xdc];decoded={}
while todo:
    ip=todo.pop()
    if ip in decoded:continue
    assert 0xdc<=ip<0x26a;i=Decoder(16,b[0xc2b0+ip:0xc51a],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
rows=[]
for ip,i in sorted(decoded.items()):
    raw=b[0xc2b0+ip:0xc2b0+i.next_ip];assert lookup[(0xc2b,ip)]['bytes']==raw.hex();rows.append(dict(cs=0xc2b,ip=ip,image_offset=0xc2b0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
save('audio_state_manager',rows)
fields=[dict(name=n,start=a,end_exclusive=a+1,length=1,type='mutable_BYTE_initial_zero_audio_state',status='PARTIAL',range_sha256=sha(b[a:a+1])) for n,a in [('audio_initialized_state',0x28edd),('audio_dsp_state',0x28ede),('audio_backend_state',0x28edf)]]
assert not any(b[0x28edd:0x28ee0]);save('data_fields',fields)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
targets={'init':0xc2b6,'probe':0xc2d0,'resource':0xc548,'volume':0xc35a,'stop_music':0x11ab2,'stop_effect':0x11ae1,'close_dsp':0x112fe,'close_all':0x10c5f,'backend_init':0x111d2,'handle_a':0x11236,'handle_b':0x11268,'capability':0x1129a}
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0xc2b
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    reverse={load*16+v:k for k,v in targets.items()};state={}
    for a in reverse:u.mem_write(a,b'\xcb')
    def hook(uc,a,size,data):
        if a not in reverse:return
        name=reverse[a];state['trace'].append(name)
        if name=='probe':uc.reg_write(UC_X86_REG_AX,state['probe']&65535)
        elif name=='capability':uc.reg_write(UC_X86_REG_AX,state['capability'])
        elif name in ('handle_a','handle_b'):uc.reg_write(UC_X86_REG_AX,0xcafe if name=='handle_a' else 0xbeef)
        if name=='resource':assert struct.unpack('<H',uc.mem_read(0x50000+uc.reg_read(UC_X86_REG_SP)+4,2))[0]==0
    u.hook_add(UC_HOOK_CODE,hook)
    def run(mode,flags,active,c7,probe,enable=1,capability=1):
        desired=list(flags);s=list(active);trace=[];ha=0x1234;hb=0x5678;expected_c7=c7
        if mode==0:
            if not enable:desired=[0,0,0]
            else:
                trace=['init','probe','capability','backend_init','handle_a','handle_b'];s[0]=s[2]=1;ha=0xcafe;hb=0xbeef
                if capability==0:desired[0]=0
                if probe<=0:expected_c7=0
                s[1]=int(bool(desired[1] and expected_c7))
                if not s[1]:trace.append('close_dsp')
                if capability:trace.append('resource')
                if desired[0]:trace.append('volume')
        elif mode==1:
            if s[0]:
                trace.append('stop_music')
                if s[1]:trace+=['stop_effect','close_dsp']
                trace.append('close_all');s=[0,0,0]
            desired=[0,0,0]
        elif mode==2:
            if any(desired) and not s[0]:trace+=['init','resource'];s[0]=1
            if desired[2] and not s[2]:trace+=['backend_init','handle_a','handle_b'];ha=0xcafe;hb=0xbeef;s[2]=1
            if desired[1] and c7:
                if not s[1]:
                    trace.append('probe')
                    if probe>0:s[1]=1
            elif not desired[1] and s[1]:trace.append('close_dsp');s[1]=0
            if desired[0]:trace.append('volume')
        u.mem_write(ds*16+0x414d,bytes(flags));u.mem_write(ds*16+0x17cd,bytes(active));u.mem_write(ds*16+0x3cc6,bytes([enable,c7]));u.mem_write(ds*16+0x367a,struct.pack('<HH',0x1234,0x5678))
        state.clear();state.update(trace=[],probe=probe,capability=capability)
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x9876),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.mem_write(0x5ff00,struct.pack('<HHH',0x6000,cs,mode));u.emu_start(cs*16+0xdc,cs*16+0x6000,count=1000)
        assert bytes(u.mem_read(ds*16+0x414d,3))==bytes(desired) and bytes(u.mem_read(ds*16+0x17cd,3))==bytes(s)
        assert bytes(u.mem_read(ds*16+0x3cc6,2))==bytes([enable,expected_c7])
        assert struct.unpack('<HH',u.mem_read(ds*16+0x367a,4))==(ha,hb) and state['trace']==trace,(mode,flags,active,c7,probe,state['trace'],trace)
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x9876 and u.reg_read(UC_X86_REG_DS)==ds
        cases.append(dict(load=load,mode=mode,desired=bytes(flags).hex(),active=bytes(active).hex(),c7=c7,probe=probe,enable=enable,capability=capability,result_active=bytes(s).hex(),result_desired=bytes(desired).hex(),result_c7=expected_c7,trace=';'.join(trace),passed=True))
    combinations=list(itertools.product((0,1,255),repeat=3))
    for flags,active in itertools.product(combinations,combinations):
        run(1,flags,active,1,1)
        for c7,probe in itertools.product((0,1),(-1,0,1)):run(2,flags,active,c7,probe)
    for mode in (3,255,65535):run(mode,(255,1,255),(1,255,0),1,1)
    for flags,active,enable,c7,probe,capability in itertools.product(combinations,[(0,0,0),(1,1,1),(255,255,255)],(0,1,255),(0,1,255),(-1,0,1),(0,1,255)):
        run(0,flags,active,c7,probe,enable,capability)
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=[dict(name='audio_state_manager',start=0xc38c,end_exclusive=0xc51a,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows))],typed_bytes=3,cases=len(cases),mode_zero_cases=sum(c['mode']==0 for c in cases),failures=0,mocked_dependencies=targets,scope='full static CFG; modes 0/1/2 and unsupported modes replayed; dependency bodies mocked with trace checks',mode_zero_replayed=True,original_worx_closed=False,natural_audio_lifecycle_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))

