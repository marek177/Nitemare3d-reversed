"""python audit_replay_near_heap_scan.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
out.mkdir(parents=True,exist_ok=True);lookup={(r['cs'],r['ip']):r for r in json.loads(inventory.read_text())};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
todo=[0x2168];decoded={};edges=[]
while todo:
    ip=todo.pop()
    if ip in decoded:continue
    assert 0x2168<=ip<0x21e4;i=Decoder(16,b[0x11ee0+ip:0x140c4],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough'))
rows=[]
for ip,i in sorted(decoded.items()):
    raw=b[0x11ee0+ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,ip)]['bytes']==raw.hex();rows.append(dict(cs=0x11ee,ip=ip,image_offset=0x11ee0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
save('near_heap_next_fit_scan',rows);save('cfg_edges',edges);cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x11ee
    for n in (1,2,3):
        for sizes in itertools.product((0,2,8),repeat=n):
            positions=[];p=0x4000
            for size in sizes:positions.append(p);p+=size+2
            tail=p
            for free in itertools.product((0,1),repeat=n):
                for cursor,request in itertools.product(positions+[tail],(0,1,2,3,7,8,15,16,0xfff0,0xffff)):
                    raw=bytearray(b'\xa5'*256)
                    for pos,size,tag in zip(positions,sizes,free):struct.pack_into('<H',raw,pos-0x4000,size+tag)
                    struct.pack_into('<H',raw,tail-0x4000,0xfffe);expected=raw[:];wanted=((request+1)&65535)&0xfffe;merges=0;passes=0;found=None;newcursor=0x4000
                    def readword(pos):return struct.unpack_from('<H',expected,pos-0x4000)[0]
                    def writeword(pos,v):struct.pack_into('<H',expected,pos-0x4000,v&65535)
                    starts=[(cursor,tail)]+([] if cursor==0x4000 else [(0x4000,cursor-1)])
                    for start,bound in starts:
                        passes+=1;pos=start
                        for step in range(50):
                            tag=readword(pos)
                            if tag&1:
                                size=tag-1
                                if size>=wanted:
                                    found=pos+2;writeword(pos,wanted);newcursor=found+wanted
                                    if size!=wanted:writeword(newcursor,size-wanted-1)
                                    break
                                nextpos=pos+2+size;nexttag=readword(nextpos)
                                if nexttag&1:writeword(pos,size+nexttag+2);merges+=1;continue
                                pos=nextpos;tag=nexttag
                            if pos>=bound:break
                            pos+=2+tag
                        else:raise AssertionError('model loop')
                        if found is not None:break
                    root=struct.pack('<HHHHHH',ds,5,tail+2,0x4000,cursor,tail);expectedroot=struct.pack('<HHHHHH',ds,5,tail+2,0x4000,newcursor,tail)
                    u.mem_write(ds*16+0x3fff,b'\x5a'+bytes(raw)+b'\x6b');u.mem_write(ds*16+0x20e2,root)
                    for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_BX,0x20e2),(UC_X86_REG_CX,request),(UC_X86_REG_EFLAGS,0x402)]:u.reg_write(reg,v)
                    u.mem_write(0x5ff00,struct.pack('<H',0x6000));u.emu_start(cs*16+0x2168,cs*16+0x6000,count=1000)
                    context=(load,sizes,free,cursor,request)
                    assert bytes(u.mem_read(ds*16+0x3fff,258))==b'\x5a'+bytes(expected)+b'\x6b',context
                    assert bytes(u.mem_read(ds*16+0x20e2,12))==expectedroot,context
                    assert u.reg_read(UC_X86_REG_AX)==(found if found is not None else 0x4000) and u.reg_read(UC_X86_REG_EFLAGS)&1==int(found is None),context
                    if found is not None:assert u.reg_read(UC_X86_REG_DX)==ds,context
                    assert u.reg_read(UC_X86_REG_SP)==0xff02 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_BX)==0x20e2 and u.reg_read(UC_X86_REG_CX)==wanted and not u.reg_read(UC_X86_REG_EFLAGS)&0x400,context
                    cases.append(dict(load=load,sizes=';'.join(map(str,sizes)),free=';'.join(map(str,free)),cursor=cursor,request=request,rounded=wanted,result=found if found is not None else 0,success=found is not None,passes=passes,merges=merges,new_cursor=newcursor,passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=[dict(name='near_heap_next_fit_scan',start=0x14048,end_exclusive=0x140c4,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows))],cases=len(cases),failures=0,coalescing_cases=sum(c['merges']>0 for c in cases),second_pass_cases=sum(c['passes']==2 for c in cases),scope='native allocator scan, independent graph model, all one-to-three small valid block chains; no OS mocks/calls; corrupt chains/wrap/whole malloc and natural reachability open',runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
