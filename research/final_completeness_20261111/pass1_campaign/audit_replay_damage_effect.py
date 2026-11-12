"""python audit_replay_damage_effect.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);targets=struct.unpack_from('<20H',b,0x85d6);pending=[0x1c0];decoded={};instructions=[]
while pending:
    ip=pending.pop()
    if ip in decoded:continue
    assert 0x1c0<=ip<0x2e3 and not 0x206<=ip<0x22e
    i=Decoder(16,b[0x83d0+ip:0x86b3],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control==FlowControl.INDIRECT_BRANCH:
        assert ip==0x200;pending.extend(targets)
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.near_branch_target)
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH,FlowControl.INDIRECT_BRANCH):pending.append(i.next_ip)
for ip,i in sorted(decoded.items()):
    raw=b[0x83d0+ip:0x83d0+i.next_ip];assert lookup[(0x83d,ip)]['bytes']==raw.hex()
    instructions.append(dict(cs=0x83d,ip=ip,image_offset=0x83d0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
def signed(v):return ((v+32768)&65535)-32768
def model(kind,selector,control,episode,delta,remainder):
    v=signed((delta<<3)+remainder)
    if kind in (12,29):v>>=3
    elif kind==13:v>>=1 if selector==1 else 3
    elif kind in (14,17,20):v>>=1 if selector==2 else 3
    elif kind in (15,16):v>>=8 if selector==1 else 1
    elif kind in (18,19):v>>=2
    elif kind in (21,25):v=0
    elif kind==22:v=3 if episode==3 else 0
    elif kind==23:v>>=8 if selector==1 else 2
    elif kind==24:v>>=8 if selector==1 else 4 if selector==2 else 3
    elif kind==26:v=v>>1 if selector==1 else 0
    elif kind in (27,28):v>>=1
    elif kind==30:v=0 if selector==1 else v>>3
    elif kind==31:v=0 if selector==1 else v>>2
    if control==2:v>>=1
    elif control==0:v=signed(v*2)
    return 255 if v>255 else v&65535
seeds={}
for seed in range(65536):
    state=(seed*214013+2531011)&0xffffffff;value=(state>>16)&32767;seeds.setdefault(value%25,(seed,state,value))
    if len(seeds)==25:break
assert len(seeds)==25
inputs=list(itertools.product([0,11,*range(12,32),32,255],range(4),(0,1,2),(1,),(-4096,-33,-1,0,1,32,4095,4096),range(25)))
inputs += list(itertools.product((22,),(0,),(0,1,2),(2,3),(-1,0,4096),range(25)))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));count=0;message_count=0;negative=0
out.mkdir(parents=True,exist_ok=True)
with (out/'cases.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f);w.writerow(['load','type','selector','control','episode','raw_delta','rand_remainder','rng_seed','return_ax','consumed_low_byte','message_calls'])
    for load in (0,0x1000):
        u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x83d;ds=load+0x2771;obj=load+0x6000
        for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
        callback=load*16+0xd9e0;u.mem_write(callback,b'\xcb');seen=[]
        def hook(uc,a,size,data):
            if a==callback:seen.append(True)
        u.hook_add(UC_HOOK_CODE,hook)
        for kind,selector,control,episode,delta,remainder in inputs:
            seed,expected_state,rand_value=seeds[remainder]
            for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
            u.mem_write(0x5ff00,struct.pack('<6H',0x4000,cs,0,0,0x1000,obj));u.mem_write(obj*16+0x1006,bytes([kind]));u.mem_write(obj*16+0x1018,struct.pack('<H',delta&65535));u.mem_write(ds*16+0x4552,b'\0\0');u.mem_write(ds*16+0x418f,bytes([selector]));u.mem_write(ds*16+0x4180,struct.pack('<H',control));u.mem_write(ds*16+0x626a,struct.pack('<H',episode));u.mem_write(ds*16+0x24b8,struct.pack('<I',seed));seen.clear()
            u.emu_start(cs*16+0x1c0,cs*16+0x4000,count=1000)
            expected=model(kind,selector,control,episode,delta,remainder);actual=u.reg_read(UC_X86_REG_AX)
            assert actual==expected and len(seen)==int(kind==21),(kind,selector,control,episode,delta,remainder,actual,expected)
            assert struct.unpack('<I',u.mem_read(ds*16+0x24b8,4))[0]==expected_state
            assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DI)==0x9abc and u.reg_read(UC_X86_REG_DS)==ds
            w.writerow([load,kind,selector,control,episode,delta,remainder,seed,actual,actual&255,len(seen)]);count+=1;message_count+=len(seen);negative+=actual>=32768
for name,rows in [('instructions',instructions),('dispatch_table',[dict(type=12+n,table_image=0x85d6+2*n,target_ip=ip,word_sha256=sha(b[0x85d6+2*n:0x85d8+2*n])) for n,ip in enumerate(targets)])]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
consumer=[]
for r in old:
    if r['cs']!=0x4c7 or not (0x1320<=r['ip']<0x1337 or 0x13d8<=r['ip']<0x13e0):continue
    raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw
    i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw)
    consumer.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
role=[dict(record='record26',offset=16,width=1,role='zero-extended BYTE compared to effect low BYTE; zeroed when not greater',consumer='04C7:1320..1333')]
for name,rows in [('consumer_context',consumer),('consumer_field_roles',role)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),function_start=0x8590,function_end_exclusive=0x86b3,function_span_bytes=291,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in instructions),instructions=len(instructions),dispatch_table_start=0x85d6,dispatch_table_end_exclusive=0x85fe,dispatch_table_sha256=sha(b[0x85d6:0x85fe]),cases=count,failures=0,negative_word_results=negative,message_calls=message_count,cases_sha256=sha((out/'cases.csv').read_bytes()),scope='original effect function plus native RNG/multiply; only type-21 message callback mocked; all 25 RNG remainders',natural_metric_domains_closed=False,full_target_health_update_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
