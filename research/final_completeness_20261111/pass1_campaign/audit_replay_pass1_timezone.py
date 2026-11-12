"""python audit_replay_pass1_timezone.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);functions=[]
out.mkdir(parents=True,exist_ok=True)
for name,start,end in [('crt_timezone_cached_init',0x2bf4,0x2c05),('crt_timezone_parse',0x2c06,0x2d00),('crt_strncpy_near',0x23b4,0x23dc),('crt_atol_near',0x2416,0x246e)]:
    pending=[start];decoded={};rows=[]
    while pending:
        ip=pending.pop()
        if ip in decoded:continue
        assert start<=ip<end
        i=Decoder(16,b[0x11ee0+ip:0x11ee0+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
        if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.near_branch_target)
        if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.next_ip)
    for ip,i in sorted(decoded.items()):
        raw=b[0x11ee0+ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,ip)]['bytes']==raw.hex()
        rows.append(dict(cs=0x11ee,ip=ip,image_offset=0x11ee0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    functions.append(dict(name=name,start=0x11ee0+start,end_exclusive=0x11ee0+end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows)))
fields=[]
for name,a,e,t in [('crt_TZ_environment_name',0x29bb2,0x29bb5,'NUL_ASCII_environment_key'),('crt_timezone_offset',0x29bb6,0x29bba,'mutable_signed_DWORD_initial_28800'),('crt_daylight_flag',0x29bba,0x29bbc,'mutable_WORD_initial_1_suffix_first_byte_sign_extended'),('crt_standard_zone_name',0x29bbc,0x29bc0,'mutable_BYTE_buffer_4_initial_PST_NUL'),('crt_daylight_zone_name',0x29bc0,0x29bc4,'mutable_BYTE_buffer_4_initial_PDT_NUL'),('crt_standard_zone_pointer',0x29bc4,0x29bc6,'NEAR16_pointer_initial_24AC'),('crt_daylight_zone_pointer',0x29bc6,0x29bc8,'NEAR16_pointer_initial_24B0')]:fields.append(dict(name=name,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e])))
assert sum(x['length'] for x in fields)==21
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x11ee;ds=load+0x2771
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    getenv=load*16+0x1436a;u.mem_write(getenv,b'\xcb');state={}
    def hook(uc,a,size,data):
        if a!=getenv:return
        arg=struct.unpack('<H',uc.mem_read(0x50000+uc.reg_read(UC_X86_REG_SP)+4,2))[0];assert arg==0x24a2 and bytes(uc.mem_read(ds*16+arg,3))==b'TZ\0'
        state['calls']+=1;uc.reg_write(UC_X86_REG_AX,0 if state['value'] is None else 0x8000)
    u.hook_add(UC_HOOK_CODE,hook)
    def run(value,entry=0x2c06):
        state.clear();state.update(value=value,calls=0)
        if value is not None:u.mem_write(ds*16+0x8000,value.encode('ascii')+b'\0'*8)
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.mem_write(0x5ff00,struct.pack('<HH',0x6000,cs));u.emu_start(cs*16+entry,cs*16+0x6000,count=5000)
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DI)==0x9abc
        data=bytes(u.mem_read(ds*16+0x24a6,14));return struct.unpack_from('<iH',data),data[6:10],data[10:14]
    for value in (None,''):
        u.mem_write(ds*16+0x24a2,b[0x29bb2:0x29bc8]);result,std,dst=run(value)
        assert result==(28800,1) and std==b'PST\0' and dst==b'PDT\0' and state['calls']==1
        cases.append(dict(load=load,kind='empty_or_missing',value=repr(value),offset=result[0],daylight_word=result[1],standard=std.hex(),daylight=dst.hex(),environment_calls=1,passed=True))
    for hours,sign,tail,suffix in itertools.product((0,1,8,12,23),('','-','+'),('',':00',':30',':59:59'),('','DEF')):
        value='ABC'+sign+str(hours)+tail+suffix;minutes=59 if tail==':59:59' else 30 if tail==':30' else 0;seconds=59 if tail==':59:59' else 0
        expected=(hours*3600+minutes*60+seconds)*(-1 if sign=='-' else 1)
        u.mem_write(ds*16+0x24a2,b[0x29bb2:0x29bc8]);result,std,dst=run(value)
        assert result==(expected,68 if suffix else 0) and std==b'ABC\0' and dst==(b'DEF\0' if suffix else b'\0DT\0') and state['calls']==1,(value,result,std,dst,expected)
        cases.append(dict(load=load,kind='parsed',value=value,offset=result[0],daylight_word=result[1],standard=std.hex(),daylight=dst.hex(),environment_calls=1,passed=True))
    u.mem_write(ds*16+0x24a2,b[0x29bb2:0x29bc8]);u.mem_write(ds*16+0x3ca8,b'\0\0')
    first=run('ABC3DEF',0x2bf4);assert first[0]==(10800,68) and state['calls']==1
    second=run('XYZ-5GHI',0x2bf4);assert second==first and state['calls']==0 and struct.unpack('<H',u.mem_read(ds*16+0x3ca8,2))[0]==1
    third=run('XYZ-5GHI');assert third[0]==(-18000,71) and state['calls']==1
    for name,result,calls in [('cached_first',first,1),('cached_skip',second,0),('explicit_refresh',third,1)]:cases.append(dict(load=load,kind=name,value='cache sequence',offset=result[0][0],daylight_word=result[0][1],standard=result[1].hex(),daylight=result[2].hex(),environment_calls=calls,passed=True))
for name,rows in [('data_fields',fields),('cases',cases)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,typed_bytes=21,cases=len(cases),failures=0,scope='original TZ parser, strncpy, atol and multiply; only getenv result mocked; DF=0; seeded cache',original_environment_lookup_closed=False,malformed_input_domain_closed=False,full_calendar_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
