"""python audit_replay_near_heap_grow.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
functions=[]
for name,start,end in [('near_heap_grow',0x21e4,0x2270),('near_heap_last_block',0x22c1,0x22e1)]:
    todo=[start];decoded={};rows=[];edges=[]
    while todo:
        ip=todo.pop()
        if ip in decoded:continue
        assert start<=ip<end;i=Decoder(16,b[0x11ee0+ip:0x11ee0+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
        if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
        if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
    for ip,i in sorted(decoded.items()):
        raw=b[0x11ee0+ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,ip)]['bytes']==raw.hex();rows.append(dict(cs=0x11ee,ip=ip,image_offset=0x11ee0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    save(name,rows);save(name+'_cfg',edges);functions.append(dict(name=name,start=0x11ee0+start,end_exclusive=0x11ee0+end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows)))
state={};cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x11ee;psp=load+0x1000
    def interrupt(uc,n,data):
        assert n==0x21 and uc.reg_read(UC_X86_REG_AH)==0x4a
        k=len(state['calls']);state['calls'].append((uc.reg_read(UC_X86_REG_ES),uc.reg_read(UC_X86_REG_BX)));fail=state['policy']==2 or(state['policy']==1 and k==0)
        uc.reg_write(UC_X86_REG_AX,8 if fail else 0x1234);f=uc.reg_read(UC_X86_REG_EFLAGS);uc.reg_write(UC_X86_REG_EFLAGS,(f|1) if fail else (f&~1))
    u.hook_add(UC_HOOK_INTR,interrupt)
    for flags,request,current,free,quantum,policy,limit,cursor_at_tail in itertools.product((0,1,4,5),(0,1,15,16,17,32,0xfff0,0xffff),(0x4014,0xfff0),(0,1),(0,8,9,16,0x1000,0x2000,0xffff),(0,1,2),(0,0xffff),(0,1)):
        tail=current-2;header=current-20;cursor=tail if cursor_at_tail else header;tag=16+free
        expected_calls=[];newcurrent=current;newtail=tail;newcursor=cursor;newlimit=limit;expected_writes={header:tag,tail:0xfffe};success=False
        def resize(desired):
            if flags&4 and ((desired-1)&65535)>((current-1)&65535) and limit>=((desired-1)&65535):return True,limit
            paragraphs=desired>>4 or 0x1000;expected_calls.append((psp,(paragraphs+ds-psp)&65535) if flags&4 else (ds,paragraphs))
            k=len(expected_calls)-1;fail=policy==2 or(policy==1 and k==0)
            return not fail,((desired-1)&65535 if flags&4 and not fail else limit)
        if flags&1:
            adjusted=(request-18)&65535 if free else request
            needed=((adjusted+2)&65535)+current;overflow=needed>65535;needed&=65535
            candidate=None;mask=None
            if overflow:
                if needed==0:candidate=0;mask=0xfff0
            else:
                if quantum==0x2000:alignment=0x2000
                else:
                    lower=0x8000
                    while lower and lower>=quantum:lower>>=1
                    alignment=(lower<<1)&65535 if lower>=8 else 16
                mask=(~((alignment-1)&65535))&65535
                total=((alignment-1)&65535)+needed;candidate=0 if total>65535 else total&mask
            if candidate is not None:
                success,newlimit=resize(candidate)
                if not success and mask!=0xfff0:
                    total=15+needed;candidate=0 if total>65535 else total&0xfff0;success,newlimit=resize(candidate)
                if success:
                    newcurrent=candidate;newtail=(tail+candidate-current)&65535;newcursor=header
                    expected_writes[tail]=((candidate-current)&65535)-1&65535;expected_writes[newtail]=0xfffe
        root=struct.pack('<HHHHHH',ds,flags,current,header,cursor,tail);expected_root=struct.pack('<HHHHHH',ds,flags,newcurrent,header,newcursor,newtail)
        u.mem_write(ds*16+0x20e0,struct.pack('<H',limit)+root);u.mem_write(ds*16+header,struct.pack('<H',tag));u.mem_write(ds*16+tail,struct.pack('<H',0xfffe));u.mem_write(ds*16+0x211e,struct.pack('<H',psp))
        u.mem_write(0x50000+0x2344,struct.pack('<H',quantum));u.mem_write(ds*16+0x2344,struct.pack('<H',quantum^0xffff));state.clear();state.update(calls=[],policy=policy)
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BX,0x20e2),(UC_X86_REG_CX,request),(UC_X86_REG_DI,0xbeef),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
        u.mem_write(0x5ff00,struct.pack('<H',0x6000));u.emu_start(cs*16+0x21e4,cs*16+0x6000,count=1000)
        details=(load,flags,request,current,free,quantum,policy,limit,cursor_at_tail)
        assert state['calls']==expected_calls and u.reg_read(UC_X86_REG_EFLAGS)&1==int(not success),(details,state['calls'],expected_calls,success)
        assert bytes(u.mem_read(ds*16+0x20e0,14))==struct.pack('<H',newlimit)+expected_root,details
        assert all(struct.unpack('<H',u.mem_read(ds*16+o,2))[0]==v for o,v in expected_writes.items()),details
        assert u.reg_read(UC_X86_REG_SP)==0xff02 and u.reg_read(UC_X86_REG_CX)==request and u.reg_read(UC_X86_REG_DI)==0xbeef and u.reg_read(UC_X86_REG_DS)==ds,details
        cases.append(dict(load=load,flags=flags,request=request,current=current,free=free,quantum=quantum,policy=policy,limit=limit,cursor_at_tail=cursor_at_tail,success=success,new_current=newcurrent,new_tail=newtail,dos_calls=len(expected_calls),passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,cases=len(cases),failures=0,scope='native grow+last-block finder+existing resize helper, single seeded block chain, SS quantum deliberately different from DS, only DOS AH4A modeled; no full malloc or natural heap proof',runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
