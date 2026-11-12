"""python audit_replay_pass1_sprite_positions.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);instructions=[]
pending=[0x4ec];decoded={}
while pending:
    ip=pending.pop()
    if ip in decoded:continue
    assert 0x4ec<=ip<0x5d2
    i=Decoder(16,b[0x83d0+ip:0x89a2],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.near_branch_target)
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.next_ip)
for i in [decoded[ip] for ip in sorted(decoded)]:
    assert not i.is_invalid;raw=b[0x83d0+i.ip:0x83d0+i.next_ip];assert lookup[(0x83d,i.ip)]['bytes']==raw.hex()
    instructions.append(dict(cs=0x83d,ip=i.ip,image_offset=0x83d0+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
assert instructions[-1]['ip']==0x5d1
xs=list(b[0x28b16:0x28b20]);ys=list(b[0x28b20:0x28b2a]);limit=struct.unpack_from('<H',b,0x28b2a)[0];assert xs==[146]*10 and limit==9
fields=[]
for name,a,e,t in [('sprite_frame_x',0x28b16,0x28b20,'BYTE_array_10_position'),('sprite_frame_y',0x28b20,0x28b2a,'BYTE_array_10_position'),('sprite_frame_limit',0x28b2a,0x28b2c,'WORD_terminal_index_9')]:fields.append(dict(name=name,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e])))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x83d;ds=load+0x2771
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    targets={load*16+0x89a2:'transition',load*16+0x1d3e:'blit'}
    for a in targets:u.mem_write(a,b'\xcb')
    state={}
    def hook(uc,a,size,data):
        if a not in targets:return
        args=struct.unpack('<10H',uc.mem_read(0x50000+uc.reg_read(UC_X86_REG_SP)+4,20));name=targets[a]
        if name=='transition':state['transition'].append(args[0])
        else:state['blit'].append(list(args))
    u.hook_add(UC_HOOK_CODE,hook)
    descriptors=b''.join(bytes([20,30,0,0,0,0])+struct.pack('<HH',0x100+n*32,0x7000) for n in range(4));u.mem_write(ds*16+0x8000,descriptors)
    for selector,mode,index,bonus,orientation,max_y in itertools.product((0,2),range(4),range(10),(0,1),(1,2),(100,170,200)):
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.mem_write(0x5ff00,struct.pack('<HHH',0x4000,cs,0x8000));u.mem_write(ds*16+0x418f,bytes([selector]));u.mem_write(ds*16+0x4190,struct.pack('<H',orientation));u.mem_write(ds*16+0x419a,bytes([bonus]));u.mem_write(ds*16+0x41a4,b'\x02');u.mem_write(ds*16+0x41a6,struct.pack('<HH',mode,index));u.mem_write(ds*16+0x454e,struct.pack('<H',max_y))
        state.clear();state.update(transition=[],blit=[]);u.emu_start(cs*16+0x4ec,cs*16+0x4000,count=500)
        new_index=index;new_mode=mode;new_selector=selector;new_orientation=orientation;new_bonus=bonus;y=ys[index]
        if mode==0:
            if bonus:y+=6 if orientation==1 else 3
            new_bonus=0
        elif mode==1:
            new_index=(index+1)&65535
            if new_index==limit:new_mode=0
        elif mode==2:
            new_index=(index-1)&65535
            if new_index==0:new_mode=1;new_selector=2;new_orientation=1
        expected_transition=[12] if mode==1 and new_index==limit else []
        height=min(30,max_y-y+1);expected_blit=[] if height<=0 else [[0x100+selector*32,0x7000,xs[index],y,20,30,20,height,0,31]]
        assert state['transition']==expected_transition and state['blit']==expected_blit
        assert struct.unpack('<4H',u.mem_read(ds*16+0x41a6,8))==(new_mode,new_index,xs[index],ys[index])
        assert u.mem_read(ds*16+0x418f,1)[0]==new_selector and struct.unpack('<H',u.mem_read(ds*16+0x4190,2))[0]==new_orientation and u.mem_read(ds*16+0x419a,1)[0]==new_bonus
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x5678
        cases.append(dict(load_segment=load,selector=selector,mode=mode,index=index,bonus=bonus,orientation=orientation,max_y=max_y,new_mode=new_mode,new_index=new_index,new_selector=new_selector,y_for_this_call=y,blit_height=max(0,height),transition=bool(expected_transition),passed=True))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('instructions',instructions),('data_fields',fields),('cases',cases)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),function_start=0x88bc,function_end_exclusive=0x89a2,function_span_bytes=230,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in instructions),instructions=len(instructions),typed_bytes=22,cases=len(cases),failures=0,scope='original positioning/animation wrapper; transition and blit replaced by RETF; seeded 10-byte sprite descriptors',disabled_selector_replayed=False,natural_state_invariants_closed=False,renderer_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
