"""python audit_replay_pass1_image_handle_cache.py IMAGE INVENTORY DECODER EMULATOR OUT"""
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
todo=[2];decoded={}
while todo:
    ip=todo.pop()
    if ip in decoded:continue
    assert 2<=ip<0x8a;i=Decoder(16,b[0x2770+ip:0x27fa],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
rows=[]
for ip,i in sorted(decoded.items()):
    raw=b[0x2770+ip:0x2770+i.next_ip];assert lookup[(0x277,ip)]['bytes']==raw.hex();rows.append(dict(cs=0x277,ip=ip,image_offset=0x2770+ip,bytes=raw.hex(),instruction=fmt.format(i)))
save('image_file_cached_read',rows)
fields=[dict(name=n,start=a,end_exclusive=a+2,length=2,type=t,status='PARTIAL',range_sha256=sha(b[a:a+2])) for n,a,t in [('image_file_cached_handle',0x2788c,'mutable_WORD_initial_zero_handle_zero_means_reopen'),('image_file_cached_episode',0x2788e,'mutable_WORD_initial_zero_episode_cache_key')]]
assert not any(b[0x2788c:0x27890]);save('data_fields',fields)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x277;ds=load+0x2771;state={}
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    targets={load*16+0x13a96:'close',load*16+0x13b52:'open',load*16+0x13ab6:'seek',load*16+0xfc3e:'read',load*16+0xfbac:'error'}
    for a in targets:u.mem_write(a,b'\xcb')
    def hook(uc,a,size,data):
        if a not in targets:return
        n=targets[a];sp=uc.reg_read(UC_X86_REG_SP);args=bytes(uc.mem_read(0x50000+sp+4,10))
        if n=='close':state['trace'].append((n,struct.unpack_from('<H',args)[0]));uc.reg_write(UC_X86_REG_AX,5)
        elif n=='open':
            assert struct.unpack_from('<HH',args)==(0x628c,0x8000);state['trace'].append((n,));uc.reg_write(UC_X86_REG_AX,state['open_result'])
        elif n=='seek':
            h,off,mode=struct.unpack_from('<HIH',args);assert off==state['offset'] and mode==0;state['trace'].append((n,h));uc.reg_write(UC_X86_REG_AX,state['seek_result']&65535);uc.reg_write(UC_X86_REG_DX,state['seek_result']>>16)
        elif n=='read':
            h,p,s,count=struct.unpack_from('<4H',args);assert (p,s,count)==(0x1000,0x6000,state['request']);state['trace'].append((n,h));uc.reg_write(UC_X86_REG_AX,state['read_result'])
        else:
            code,p=struct.unpack_from('<HH',args);assert p==0x628c;state['trace'].append((n,code))
    u.hook_add(UC_HOOK_CODE,hook)
    for (old_ep,ep),oldhandle,opened,request,readkind,offset,seek_result in itertools.product([(1,1),(0,1),(65535,1),(65535,65535)],(0,7,65535),(0,7,65535),(0,1,16,65535),('equal','short','minus1'),(0,0x7fffffff,0xffffffff),(0,0xffffffff)):
        handle=oldhandle;trace=[]
        if old_ep!=ep and handle:trace.append(('close',handle));handle=0
        if not handle:
            trace.append(('open',));handle=opened
            if handle==65535:trace.append(('error',0x180))
        trace += [('seek',handle),('read',handle)]
        result=request if readkind=='equal' else (request-1)&65535 if readkind=='short' else 65535
        if result!=request:trace.append(('error',0x196))
        u.mem_write(ds*16+0x17c,struct.pack('<HH',oldhandle,old_ep));u.mem_write(ds*16+0x626a,struct.pack('<H',ep));u.mem_write(ds*16+0x628c,b'img.1\0');state.clear();state.update(trace=[],open_result=opened,request=request,offset=offset,seek_result=seek_result,read_result=result)
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
        u.mem_write(0x5ff00,struct.pack('<HHHHIH',0x6000,cs,0x1000,0x6000,offset,request));u.emu_start(cs*16+2,cs*16+0x6000,count=1000)
        assert state['trace']==trace and struct.unpack('<HH',u.mem_read(ds*16+0x17c,4))==(handle,ep),(old_ep,ep,oldhandle,opened,request,state['trace'],trace)
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_DS)==ds
        cases.append(dict(load=load,old_episode=old_ep,episode=ep,old_handle=oldhandle,open_result=opened,request=request,read_kind=readkind,offset=offset,seek_result=seek_result,trace=str(trace),passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=[dict(name='image_file_cached_read',start=0x2772,end_exclusive=0x27fa,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows))],typed_bytes=4,cases=len(cases),failures=0,scope='original complete cached read control body; close/open/seek/read/error callees mocked with exact argument checks; error hook returns to expose continuation only',real_file_io_closed=False,error_termination_closed=False,natural_handle_domain_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
