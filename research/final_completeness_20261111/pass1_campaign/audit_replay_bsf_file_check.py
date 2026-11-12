"""python audit_replay_bsf_file_check.py IMAGE INVENTORY DECODER EMULATOR ASSET_DIR OUT"""
import csv,hashlib,json,struct,sys,functools,operator
from pathlib import Path
image,inventory,dep,emu,assets,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
functions=[]
for name,seg,start,end in [('bsf_file_checksum_check',0x83d,0x28ee,0x29c9),('crt_fread_for_checksum',0x11ee,0x6fc,0x7df)]:
    todo=[start];decoded={};rows=[]
    while todo:
        ip=todo.pop()
        if ip in decoded:continue
        assert start<=ip<end;i=Decoder(16,b[seg*16+ip:seg*16+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
        if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
        if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
    for ip,i in sorted(decoded.items()):
        raw=b[seg*16+ip:seg*16+i.next_ip];assert lookup[(seg,ip)]['bytes']==raw.hex();rows.append(dict(cs=seg,ip=ip,image_offset=seg*16+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    save(name,rows);functions.append(dict(name=name,start=seg*16+start,end_exclusive=seg*16+end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows)))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];manifest=[]
sources=[('empty',b''),('one_nonzero',b'\x80'),('three_nonzero',b'\x01\x02\x83'),('ends_zero',b'\x01\x02\0')]
for name in ('n3d.exe','MAP.1'):
    p=assets/name;raw=p.read_bytes();sources.append((name,raw));manifest.append(dict(path=str(p),bytes=len(raw),sha256=sha(raw),whole_xor_seed123=functools.reduce(operator.xor,raw,123),last_byte=raw[-1]))
save('assets',manifest)
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x83d;state={}
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    targets={load*16+a:n for a,n in [(0x125c6,'open'),(0x124da,'close'),(0xfbac,'error'),(0x13cf4,'read')]}
    assert 0x11ee0+0x6e6==0x125c6 and 0x11ee0+0x5fa==0x124da
    for a in targets:u.mem_write(a,b'\xcb')
    def hook(uc,a,size,data):
        if a not in targets:return
        name=targets[a];sp=uc.reg_read(UC_X86_REG_SP);arg=lambda n:struct.unpack('<'+'H'*n,uc.mem_read(ds*16+sp+4,n*2))
        if name=='open':
            assert arg(2)==(0x1000,0x15f6);uc.reg_write(UC_X86_REG_AX,0x217a)
        elif name=='read':
            handle,dest,count=arg(3);assert handle==3 and count==1;state['reads']+=1
            if state['position']<len(state['source']):uc.mem_write(ds*16+dest,state['source'][state['position']:state['position']+1]);state['position']+=1;uc.reg_write(UC_X86_REG_AX,1)
            else:uc.reg_write(UC_X86_REG_AX,0)
        elif name=='error':state['errors']+=1;assert arg(2)==(0x160f,0x1000)
        elif name=='close':assert arg(1)==(0x217a,);state['closed']+=1
    u.hook_add(UC_HOOK_CODE,hook)
    for label,source in sources:
        counts=(0,) if label in ('n3d.exe','MAP.1') else (0,1,2,3,5,0xffffffff)
        if label=='one_nonzero':counts+=(65535,65536)
        for count in counts:
            reads=(len(source)+1 if count==0 else 0 if count&0x80000000 else count)
            checksum=123
            if count==0:
                checksum=functools.reduce(operator.xor,source,checksum)^(source[-1] if source else 0xa5)
            elif not count&0x80000000:
                checksum=functools.reduce(operator.xor,source[:count],checksum)
                if count>len(source) and (count-len(source))&1:checksum^=source[-1] if source else 0xa5
            for mismatch in (0,1):
                expected=checksum^mismatch;state.clear();state.update(source=source,position=0,reads=0,errors=0,closed=0)
                u.mem_write(ds*16+0x217a,struct.pack('<HHHBB',0,0,0,4,3));u.mem_write(ds*16+0x221a,b'\0\0\x01\0');u.mem_write(ds*16+0xfe00,b'\xa5'*0x120)
                for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_SS,ds),(UC_X86_REG_DS,ds),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
                u.mem_write(ds*16+0xff00,struct.pack('<HHHIH',0x6000,cs,0x1000,count,expected|0xab00));u.emu_start(cs*16+0x28ee,cs*16+0x6000,count=30000000)
                assert state['reads']==reads and state['errors']==mismatch and state['closed']==1,(label,count,state,checksum)
                assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DI)==0x9abc
                cases.append(dict(load=load,source=label,source_bytes=len(source),count=count,checksum=checksum,mismatch=mismatch,read_calls=reads,error_calls=state['errors'],passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,cases=len(cases),failures=0,scope='native checksum helper and native fread with buffer-size1 stream; open/close/error and lower read modeled; actual main EXE/MAP bytes plus EOF/stale-byte fixtures; only this fread path replayed, not all its branches',runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
