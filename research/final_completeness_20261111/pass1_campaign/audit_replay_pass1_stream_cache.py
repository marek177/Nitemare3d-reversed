"""python audit_replay_pass1_stream_cache.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
todo=[0xb4a];decoded={};edges=[]
while todo:
    ip=todo.pop()
    if ip in decoded:continue
    assert 0xb4a<=ip<0xbbd;i=Decoder(16,b[0x11ee0+ip:0x12a9d],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
rows=[]
for ip,i in sorted(decoded.items()):
    raw=b[0x11ee0+ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,ip)]['bytes']==raw.hex();rows.append(dict(cs=0x11ee,ip=ip,image_offset=0x11ee0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
save('crt_stream_cache_attach',rows);save('cfg_edges',edges)
fields=[]
for k in range(3):
    a=0x299cc+2*k;assert b[a:a+2]==b'\0\0';fields.append(dict(name='crt_stream_buffer_cache_'+str(k),start=a,end_exclusive=a+2,length=2,type='mutable_NEAR16_buffer_pointer_initial_zero',status='PARTIAL',range_sha256=sha(b[a:a+2])))
save('data_fields',fields);rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];state={};visited=set()
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x11ee
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    alloc=load*16+0x15baf;assert alloc==cs*16+0x3ccf;u.mem_write(alloc,b'\xcb')
    def hook(uc,a,size,data):
        if cs*16+0xb4a<=a<cs*16+0xbbd:visited.add(a-cs*16)
        if a==alloc:
            sp=uc.reg_read(UC_X86_REG_SP);assert struct.unpack('<H',uc.mem_read(0x50000+sp+4,2))[0]==512;state['calls']+=1;uc.reg_write(UC_X86_REG_AX,state['result']);uc.reg_write(UC_X86_REG_DX,0xabcd)
    u.hook_add(UC_HOOK_CODE,hook)
    for index,flags,auxflag,cache,result in itertools.product(range(3),range(256),(0,1,2,255),(0,0x1234,0xffff),(0,0x5678)):
        stream=(0x2182,0x218a,0x219a)[index];aux=stream-0x217a+0x221a;slot=0x22bc+2*index
        stream_seed=bytearray(struct.pack('<HHHBB',0x1111,0x2222,0x3333,flags,0x77));aux_seed=bytearray([auxflag,0x88,0x99,0xaa]);expect_stream=stream_seed[:];expect_aux=aux_seed[:]
        eligible=not(flags&12) and not(auxflag&1);expect_calls=int(eligible and cache==0);pointer=cache or result;success=eligible and pointer!=0
        if success:
            expect_stream[:6]=struct.pack('<HHH',pointer,512,pointer);expect_stream[6]|=2;expect_aux[0]=0x11;expect_aux[2:4]=struct.pack('<H',512)
        u.mem_write(ds*16+stream,bytes(stream_seed));u.mem_write(ds*16+aux,bytes(aux_seed));u.mem_write(ds*16+slot,struct.pack('<H',cache));state.clear();state.update(calls=0,result=result)
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x3333),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x9876),(UC_X86_REG_DI,0x8765),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
        u.mem_write(0x5ff00,struct.pack('<HH',0x6000,stream));u.emu_start(cs*16+0xb4a,cs*16+0x6000,count=200)
        assert u.reg_read(UC_X86_REG_AX)==int(success) and state['calls']==expect_calls
        assert bytes(u.mem_read(ds*16+stream,8))==bytes(expect_stream) and bytes(u.mem_read(ds*16+aux,4))==bytes(expect_aux)
        assert struct.unpack('<H',u.mem_read(ds*16+slot,2))[0]==(pointer if success else cache)
        assert u.reg_read(UC_X86_REG_SP)==0xff02 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x9876 and u.reg_read(UC_X86_REG_DI)==0x8765 and u.reg_read(UC_X86_REG_DS)==ds
        cases.append(dict(load=load,stream=stream,flags=flags,auxflag=auxflag,cache=cache,allocator_result=result,success=success,allocator_calls=expect_calls,passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=6,fields=3,functions=[dict(name='crt_stream_cache_attach',start=0x12a2a,end_exclusive=0x12a9d,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows))],cases=len(cases),failures=0,visited_instruction_starts=len(visited),unvisited_instruction_starts=sorted(set(decoded)-visited),scope='original helper three recognized streams all flag BYTE values; allocator modeled, invalid stream branch static only; no natural DOS stream lifecycle',runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
