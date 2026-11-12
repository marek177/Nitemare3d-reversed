"""python audit_replay_pass1_progress_ui.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
functions=[]
for name,start,end in [('ui_resource_selector',0,0xe),('ui_progress_draw',0x8aa,0x959)]:
    todo=[start];decoded={}
    while todo:
        ip=todo.pop()
        if ip in decoded:continue
        assert start<=ip<end;i=Decoder(16,b[0xd290+ip:0xd290+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
        if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
        if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
    rows=[]
    for ip,i in sorted(decoded.items()):
        raw=b[0xd290+ip:0xd290+i.next_ip];assert lookup[(0xd29,ip)]['bytes']==raw.hex();rows.append(dict(cs=0xd29,ip=ip,image_offset=0xd290+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    save(name,rows);functions.append(dict(name=name,start=0xd290+start,end_exclusive=0xd290+end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows)))
fields=[]
for name,a,raw,typ,refs in [('ui_resource_selector_words',0x29376,struct.pack('<3H',5,7,8),'WORD_array_3_no_local_index_guard',[0x8]),('ui_resource_loaded_flags',0x2937c,bytes(3),'mutable_BYTE_array_3_initial_zero_nominal_resource_groups',[0x179,0x181]),('ui_press_key_text_a',0x2937f,b'Press a key\0','NUL_ASCII',[0x480,0x48a]),('ui_press_key_text_b',0x2938b,b'Press a key\0','NUL_ASCII',[0x4d0,0x4da]),('ui_opening_image_name',0x29397,b'dstopen.img\0','NUL_ASCII_filename',[0x79a,0x79d]),('ui_progress_endpoints',0x293a3,bytes([0,0,40,80,100]),'BYTE_array_5_indexed_interpolation_endpoints',[0x8c7,0x8e2,0x905]),('ui_progress_current',0x293a8,bytes(2),'mutable_WORD_initial_zero',[0x922,0x93c]),('ui_progress_previous',0x293aa,bytes(2),'mutable_WORD_initial_zero_redraw_cache',[0x925,0x952]),('ui_startup_once',0x293ac,bytes([1]),'mutable_BYTE_initial_one',[0x95d,0x968,0x975])]:
    assert b[a:a+len(raw)]==raw
    fields.append(dict(name=name,start=a,end_exclusive=a+len(raw),length=len(raw),type=typ,status='PARTIAL',range_sha256=sha(raw),evidence_ips=';'.join('0D29:%04X'%ip for ip in refs)))
assert sum(f['length'] for f in fields)==55;save('data_fields',fields)
contexts=[]
for r in old:
    if r['cs']==0xd29 and any(a<=r['ip']<e for a,e in [(0x170,0x1ae),(0x470,0x48d),(0x4c0,0x4dd),(0x79a,0x7a9),(0x95a,0x980)]):
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert i.len==len(raw) and not i.is_invalid;contexts.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
save('static_contexts',contexts);rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0xd29;ds=load+0x2771;state={}
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    query=load*16+0x28f8;draw=load*16+0x1e34;u.mem_write(query,b'\xcb');u.mem_write(draw,b'\xcb')
    def code(uc,a,size,data):
        sp=uc.reg_read(UC_X86_REG_SP)
        if a==query:
            value=struct.unpack('<I',uc.mem_read(0x50000+sp+4,4))[0];state['queries'].append(value);uc.reg_write(UC_X86_REG_AX,0x42)
        elif a==draw:state['draws'].append(struct.unpack('<6H',uc.mem_read(0x50000+sp+4,12)))
    u.hook_add(UC_HOOK_CODE,code)
    def execute(ip,args):
        state.clear();state.update(queries=[],draws=[])
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.mem_write(0x5ff00,struct.pack('<HH',0x6000,cs)+struct.pack('<'+'H'*len(args),*args));u.emu_start(cs*16+ip,cs*16+0x6000,count=1000)
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_DS)==ds
    for index,expected in enumerate((5,7,8)):
        execute(0,[index]);assert u.reg_read(UC_X86_REG_AX)==expected and not state['queries'] and not state['draws'];cases.append(dict(load=load,kind='selector',stage=index,current='',total='',previous='',draws='',passed=True))
    endpoints=[0,0,40,80,100]
    for stage,current,total,same in itertools.product(range(4),(-32768,-1,0,1,2,49,99,100,32767),(-32768,-1,0,1,2,3,50,100,32767),(0,1)):
        numerator=(endpoints[stage+1]-endpoints[stage])*current;denominator=max(total,2)-1;v=abs(numerator)//denominator*(-1 if numerator<0 else 1);v&=65535
        prev=v if same else v^65535;u.mem_write(ds*16+0x1c98,struct.pack('<HH',0x7777,prev));execute(0x8aa,[stage,current&65535,total&65535])
        expected_draws=[(110,160,102,20,0x42,1)] if stage==0 else [] if same else [(endpoints[stage]+111,161,v,18,0x42,1)]
        assert state['draws']==expected_draws and state['queries']==([0x10006] if stage==0 else [] if same else [0x1000e])
        assert struct.unpack('<HH',u.mem_read(ds*16+0x1c98,4))==((0x7777,prev) if stage==0 else (v,v))
        assert u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DI)==0x9abc
        cases.append(dict(load=load,kind='progress',stage=stage,current=current,total=total,previous=prev,draws=str(expected_draws),passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,typed_bytes=55,cases=len(cases),failures=0,scope='original selector nominal indices and complete progress routine stages0..3; query and drawing callbacks mocked; other field consumers static only',natural_stage_domain_closed=False,full_UI_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
