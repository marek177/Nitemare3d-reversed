"""python audit_replay_near_malloc.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
out.mkdir(parents=True,exist_ok=True);lookup={(r['cs'],r['ip']):r for r in json.loads(inventory.read_text())};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
todo=[0x3ccf];decoded={};edges=[]
while todo:
    ip=todo.pop()
    if ip in decoded:continue
    assert 0x3ccf<=ip<0x3d0a;i=Decoder(16,b[0x11ee0+ip:0x15bea],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
rows=[]
for ip,i in sorted(decoded.items()):
    raw=b[0x11ee0+ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,ip)]['bytes']==raw.hex();rows.append(dict(cs=0x11ee,ip=ip,image_offset=0x11ee0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
save('near_malloc_retry',rows);save('cfg_edges',edges);rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];state={}
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x11ee
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    u.mem_write(0x60100,b'\xcb')
    def intr(uc,n,data):
        assert n==0x21 and uc.reg_read(UC_X86_REG_AH)==0x4a and uc.reg_read(UC_X86_REG_ES)==ds
        state['dos'].append(uc.reg_read(UC_X86_REG_BX));uc.reg_write(UC_X86_REG_AX,8 if state['dos_failure'] else 0x1234);f=uc.reg_read(UC_X86_REG_EFLAGS);uc.reg_write(UC_X86_REG_EFLAGS,(f|1) if state['dos_failure'] else(f&~1))
    def hook(uc,a,size,data):
        if a==cs*16+0x3cae:state['native_free_calls']+=1
        if a!=0x60100:return
        sp=uc.reg_read(UC_X86_REG_SP);assert struct.unpack('<H',uc.mem_read(0x50000+sp+4,2))[0]==state['request'];state['callbacks']+=1
        again=state['policy'] in ('free_once','enable_once','nonzero_once') and state['callbacks']==1
        if again and state['policy']=='enable_once':uc.mem_write(ds*16+0x20e4,bytes([uc.mem_read(ds*16+0x20e4,1)[0]|1]))
        uc.reg_write(UC_X86_REG_AX,0xffff if again else 0)
    u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_CODE,hook)
    for flags,initial_free,request,dos_failure,policy in itertools.product((0,1),(0,1),(0,1,16,17,128,0xffe8,0xffe9,0xffff),(0,1),('absent','zero','free_once','enable_once','nonzero_once')):
        expected_callbacks=expected_dos=0;expected_dos_sizes=[];is_free=initial_free;can_grow=flags&1;expected_ptr=0;want=((request+1)&65535)&0xfffe;finalflags=flags
        for attempt in range(3):
            if request<=0xffe8:
                if is_free and want<=16:expected_ptr=0x4002;break
                if can_grow and request<=128:
                    expected_dos+=1
                    needed=0x4014+request+(2 if not is_free else -16);expected_dos_sizes.append(((needed+15)&0xfff0)>>4)
                    if not dos_failure:expected_ptr=0x4002 if is_free else 0x4014;break
            if policy=='absent':break
            expected_callbacks+=1
            if policy=='zero' or expected_callbacks>1:break
            if policy=='free_once':is_free=1
            if policy=='enable_once':can_grow=1;finalflags|=1
        else:raise AssertionError('model retry')
        u.mem_write(ds*16+0x20e0,struct.pack('<HHHHHHH',0,ds,flags,0x4014,0x4000,0x4000,0x4012));u.mem_write(ds*16+0x3fff,b'\x5a'+b'\xa5'*512+b'\x6b');u.mem_write(ds*16+0x4000,struct.pack('<H',16+initial_free));u.mem_write(ds*16+0x4002,bytes(range(16)));u.mem_write(ds*16+0x4012,struct.pack('<H',0xfffe));u.mem_write(0x50000+0x2344,struct.pack('<H',16));u.mem_write(ds*16+0x252e,struct.pack('<HH',0,0) if policy=='absent' else struct.pack('<HH',0x100,0x6000))
        callback_body=b'\x68\x02\x40\x9a'+struct.pack('<HH',0x3cae,cs)+b'\x83\xc4\x02\xcb' if policy=='free_once' else b'\xcb'
        u.mem_write(0x60100,callback_body)
        u.ctl_remove_cache(0x60100,0x60140)
        state.clear();state.update(request=request,policy=policy,dos_failure=dos_failure,callbacks=0,dos=[],native_free_calls=0)
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
        u.mem_write(0x5ff00,struct.pack('<HHH',0x7000,cs,request));u.emu_start(cs*16+0x3ccf,cs*16+0x7000,count=3000)
        context=(load,flags,initial_free,request,dos_failure,policy)
        assert u.reg_read(UC_X86_REG_AX)==expected_ptr and u.reg_read(UC_X86_REG_DX)==(ds if expected_ptr else 0),(context,u.reg_read(UC_X86_REG_AX),u.reg_read(UC_X86_REG_DX),state,bytes(u.mem_read(ds*16+0x4000,2)).hex())
        assert state['callbacks']==expected_callbacks and len(state['dos'])==expected_dos,context
        assert state['dos']==expected_dos_sizes and state['native_free_calls']==(expected_callbacks if policy=='free_once' else 0),context
        assert u.mem_read(ds*16+0x20e4,1)[0]==finalflags and bytes(u.mem_read(ds*16+0x3fff,1))==b'\x5a' and bytes(u.mem_read(ds*16+0x4200,1))==b'\x6b',context
        if expected_ptr==0x4014:assert bytes(u.mem_read(ds*16+0x4002,16))==bytes(range(16)),context
        if expected_ptr:assert struct.unpack('<H',u.mem_read(ds*16+expected_ptr-2,2))[0]==want,context
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DI)==0x9abc and u.reg_read(UC_X86_REG_DS)==ds,context
        cases.append(dict(load=load,flags=flags,initial_free=initial_free,request=request,dos_failure=dos_failure,policy=policy,pointer=expected_ptr,callback_calls=expected_callbacks,dos_calls=expected_dos,dos_paragraphs=';'.join(map(str,expected_dos_sizes)),native_free_calls=state['native_free_calls'],passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=[dict(name='near_malloc_retry',start=0x15baf,end_exclusive=0x15bea,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows))],cases=len(cases),failures=0,successful_allocations=sum(c['pointer']!=0 for c in cases),callback_cases=sum(c['callback_calls']>0 for c in cases),native_free_calls=sum(c['native_free_calls'] for c in cases),scope='native malloc+scan+grow+last-block+resize plus original free in synthetic retry callback; single initial block, DOS AH4A and callback policy modeled; no natural runtime or full lifetime closure',runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
