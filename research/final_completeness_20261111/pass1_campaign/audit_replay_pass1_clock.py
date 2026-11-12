"""python audit_replay_pass1_clock.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
lookup={(r['cs'],r['ip']):r for r in json.loads(inventory.read_text())};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True);functions=[]
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for name,cs,start,end in [('game_clock_sample',0xbde,0x18,0x94),('game_clock_cached',0xbde,0x94,0xae),('game_option_defaults',0x476,0,0x5e)]:
    pending=[start];decoded={}
    while pending:
        ip=pending.pop()
        if ip in decoded:continue
        assert start<=ip<end
        i=Decoder(16,b[cs*16+ip:cs*16+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
        if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.near_branch_target)
        if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.next_ip)
    rows=[]
    for ip,i in sorted(decoded.items()):
        raw=b[cs*16+ip:cs*16+i.next_ip];assert lookup[(cs,ip)]['bytes']==raw.hex()
        rows.append(dict(cs=cs,ip=ip,image_offset=cs*16+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    save(name,rows);functions.append(dict(name=name,start=cs*16+start,end_exclusive=cs*16+end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows)))
fields=[]
for name,a,e,t in [('game_clock_cached_value',0x27f2e,0x27f32,'mutable_DWORD_unsigned_time_comparisons'),('game_options_first_init',0x27f3a,0x27f3b,'mutable_BYTE_initial_1_cleared_by_defaults'),('game_bios_clock_origin',0x28e02,0x28e06,'mutable_DWORD_BIOS_tick_origin_zero_is_uninitialized')]:
    fields.append(dict(name=name,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e])))
refs=[]
for r in lookup.values():
    i=Decoder(16,bytes.fromhex(r['bytes']),ip=r['ip']).decode()
    from iced_x86 import OpKind,Register,MemorySizeExt
    if any(i.op_kind(n)==OpKind.MEMORY for n in range(i.op_count)) and i.memory_segment==Register.DS and i.memory_base==Register.NONE and i.memory_index==Register.NONE:
        a=0x27710+i.memory_displacement;e=a+MemorySizeExt.size(i.memory_size)
        for f in fields:
            if a<f['end_exclusive'] and e>f['start']:refs.append(dict(field=f['name'],cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=r['bytes'],instruction=fmt.format(i),scope='default DS conditional; supplied inventory only'))
save('data_fields',fields);save('direct_references',refs)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    mocked=load*16+0x149ca;u.mem_write(mocked,b'\xcb');state={}
    def hook(uc,a,size,data):
        if a!=mocked:return
        state['calls']+=1;sp=uc.reg_read(UC_X86_REG_SP);arg=struct.unpack('<H',uc.mem_read(0x50000+sp+4,2))[0]
        uc.mem_write(0x50000+arg,struct.pack('<IH',3,999));uc.reg_write(UC_X86_REG_AX,0)
    u.hook_add(UC_HOOK_CODE,hook)
    def put(off,value,size=2):u.mem_write(ds*16+off,value.to_bytes(size,'little'))
    def get(off,size=2):return int.from_bytes(u.mem_read(ds*16+off,size),'little')
    def run(cs,ip):
        state['calls']=0;cs+=load
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.mem_write(0x5ff00,struct.pack('<HH',0x6000,cs));u.emu_start(cs*16+ip,cs*16+0x6000,count=1000)
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_DS)==ds
        return (u.reg_read(UC_X86_REG_DX)<<16)|u.reg_read(UC_X86_REG_AX)
    for flag in range(256):
        for off,size in [(0x3cca,4),(0x3cc6,1),(0x3cc7,1),(0x3cce,1),(0x3ccf,1),(0x3cbc,2),(0x3cbe,2),(0x3cc0,2),(0x3cc8,1),(0x3cd0,1),(0x3cc2,2),(0x3cd6,2),(0x3cdc,1)]:put(off,0x55 if size==1 else 0x5555,size)
        put(0x82a,flag,1);run(0x476,0)
        expected=[(0x3cca,4,0x70220),(0x3cc6,1,1),(0x3cc7,1,1),(0x3cce,1,1),(0x3ccf,1,1),(0x3cbc,2,65535),(0x3cbe,2,65535),(0x3cc0,2,65535),(0x3cc8,1,0),(0x3cd0,1,0),(0x3cc2,2,25),(0x3cd6,2,0),(0x3cdc,1,0)]
        for off,size,value in expected:assert get(off,size)==(value if flag else 0x55 if size==1 else 0x5555)
        assert get(0x82a,1)==0 and get(0x3cd1,1)==1 and get(0x3cd2,1)==0 and get(0x3cd8,4)==0 and get(0x3cc4)==65535 and state['calls']==0
        cases.append(dict(load=load,kind='option_defaults',flag_cf=flag,flag_c7='',ticks='',origin='',result='',clock_calls=0,passed=True))
    for cf,c7,ticks,origin,entry in itertools.product((0,1,2,255),(0,1,2),(0,1,65535,65536,0x1800af,0xffffffff),(0,1,0xfffffff0),(0x18,0x94)):
        put(0x3ccf,cf,1);put(0x3cc7,c7,1);put(0x16f2,origin,4);put(0x81e,0x89abcdef,4);u.mem_write(0x46c,struct.pack('<I',ticks))
        frozen=entry==0x94 and cf!=0;bios=cf!=0 and c7==0
        expected=0x89abcdef if frozen else (((ticks-(origin or ticks))*55)&0xffffffff) if bios else 3999
        result=run(0xbde,entry);assert result==expected,(cf,c7,ticks,origin,entry,result,expected)
        assert state['calls']==(0 if frozen or bios else 1)
        assert get(0x81e,4)==(expected if entry==0x94 and not frozen else 0x89abcdef)
        assert get(0x16f2,4)==(ticks if bios and not frozen and origin==0 else origin)
        cases.append(dict(load=load,kind='sample' if entry==0x18 else 'cached',flag_cf=cf,flag_c7=c7,ticks=ticks,origin=origin,result=result,clock_calls=state['calls'],passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,typed_bytes=sum(f['length'] for f in fields),cases=len(cases),failures=0,scope='original option defaults and clock sampling/cache instructions; BIOS memory seeded; CRT ftime dependency mocked writing SS local output; hardware timing not tested',natural_scheduler_closed=False,bios_tick_rollover_closed=False,original_crt_time_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))

