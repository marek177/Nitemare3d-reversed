"""python audit_replay_pass1_game_input_history.py IMAGE INVENTORY DECODER EMULATOR OUT"""
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
spec=[('game_input_anchor_once',0x5eb,0x617),('game_action_histories',0xb3d,0xb80)];prefixes=[];rows=[]
for name,start,end in spec:
    todo=[start];decoded={};items=[]
    while todo:
        ip=todo.pop()
        if ip==end or ip in decoded:continue
        assert start<=ip<end;i=Decoder(16,b[0x6b00+ip:0x6b00+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
        if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
        if i.flow_control!=FlowControl.UNCONDITIONAL_BRANCH:todo.append(i.next_ip)
    for ip,i in sorted(decoded.items()):
        raw=b[0x6b00+ip:0x6b00+i.next_ip];assert lookup[(0x6b0,ip)]['bytes']==raw.hex();items.append(dict(cs=0x6b0,ip=ip,image_offset=0x6b00+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    rows.extend(items);prefixes.append(dict(name=name,start=0x6b00+start,end_exclusive=0x6b00+end,instruction_bytes=sum(len(bytes.fromhex(x['bytes'])) for x in items),instructions=len(items),scope='interior prefix, dependencies mocked, not complete function'))
save('instructions',rows)
fields=[dict(name=n,start=a,end_exclusive=a+1,length=1,type='mutable_BYTE_game_input_state_initial_'+str(b[a]),status='PARTIAL',range_sha256=sha(b[a:a+1])) for n,a in [('game_input_anchor_once',0x2826c),('game_secondary_action_history',0x2826d),('game_primary_action_history',0x2826e)]]
assert b[0x2826c:0x2826f]==bytes([1,0,0]);save('data_fields',fields)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x6b0
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    targets={load*16+0x8350:'input',load*16+0x9026:'gate',load*16+0x696c:'primary_action',load*16+0x704:'secondary_action'};state={}
    for addr in targets:u.mem_write(addr,b'\xcb')
    def hook(uc,a,size,data):
        if a not in targets:return
        name=targets[a];state['calls'].append(name);sp=uc.reg_read(UC_X86_REG_SP)
        if name=='input':
            args=struct.unpack('<HHH',uc.mem_read(0x50000+sp+4,6));assert args==(0xfefc,0xfefa,0xfef6)
            for p,v in zip(args,(0x1234,0xabcd,0x00ff)):uc.mem_write(0x50000+p,struct.pack('<H',v))
        elif name=='gate':
            args=struct.unpack('<HH',uc.mem_read(0x50000+sp+4,4));assert args==(0,0xab00|state['event']);uc.reg_write(UC_X86_REG_AX,0xab00|state['permit'])
    u.hook_add(UC_HOOK_CODE,hook)
    def execute(start,end):
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xfe00),(UC_X86_REG_BP,0xff00),(UC_X86_REG_AX,0xab55),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.emu_start(cs*16+start,cs*16+end,count=200)
        assert u.reg_read(UC_X86_REG_SP)==0xfe00 and u.reg_read(UC_X86_REG_BP)==0xff00 and u.reg_read(UC_X86_REG_DS)==ds
    for flag in range(256):
        u.mem_write(ds*16+0xb5c,bytes([flag]));u.mem_write(ds*16+0x34c8,struct.pack('<HH',0x5555,0xaaaa));state.clear();state['calls']=[];execute(0x5eb,0x617)
        assert bytes(u.mem_read(ds*16+0xb5c,1))==b'\0' and state['calls']==(['input'] if flag else [])
        assert struct.unpack('<HH',u.mem_read(ds*16+0x34c8,4))==((0x1234,0xabcd) if flag else (0x5555,0xaaaa))
        cases.append(dict(load=load,kind='anchor_once',inputs=str(flag),calls=';'.join(state['calls']),passed=True))
    for p,s,oldp,olds,permit in itertools.product((0,1,2,255),repeat=5):
        u.mem_write(0x5fefe,bytes([p,s]));u.mem_write(ds*16+0xb5d,bytes([olds,oldp]));state.clear();state.update(calls=[],event=int(oldp==0),permit=permit)
        expected=[]
        if p:expected.append('gate')
        if p and permit:expected.append('primary_action')
        if s and s!=olds:expected.append('secondary_action')
        execute(0xb3d,0xb80)
        assert state['calls']==expected and bytes(u.mem_read(ds*16+0xb5d,2))==bytes([s,p])
        cases.append(dict(load=load,kind='action_histories',inputs=','.join(map(str,(p,s,oldp,olds,permit))),calls=';'.join(expected),passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),prefixes=prefixes,prefix_instruction_bytes=sum(x['instruction_bytes'] for x in prefixes),prefix_instructions=len(rows),typed_bytes=3,cases=len(cases),failures=0,scope='two original interior input prefixes; input callback, action gate and actions mocked; no whole input loop or hardware',natural_input_domain_closed=False,full_game_input_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
