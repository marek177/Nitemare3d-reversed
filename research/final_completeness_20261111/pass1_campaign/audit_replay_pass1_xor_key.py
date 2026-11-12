"""python audit_replay_pass1_xor_key.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,functools,operator
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,OpKind
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
functions=[]
for name,start,end in [('xor_buffer_with_input_checksum',0x1b2,0x1f0),('timestamped_message_wrapper',0x36,0x57)]:
    todo=[start];decoded={}
    while todo:
        ip=todo.pop()
        if ip in decoded:continue
        assert start<=ip<end;i=Decoder(16,b[0xfba0+ip:0xfba0+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
        if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
        if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
    rows=[];missing=0
    for ip,i in sorted(decoded.items()):
        raw=b[0xfba0+ip:0xfba0+i.next_ip];prior=lookup.get((0xfba,ip))
        if prior:assert prior['bytes']==raw.hex()
        else:missing+=1
        rows.append(dict(cs=0xfba,ip=ip,image_offset=0xfba0+ip,bytes=raw.hex(),instruction=fmt.format(i),in_old_inventory=prior is not None))
    save(name,rows);functions.append(dict(name=name,start=0xfba0+start,end_exclusive=0xfba0+end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows),starts_absent_from_old_inventory=missing))
key=b[0x29755:0x29789];assert len(key)==52 and key==b'Copyright 1992, David P Gray, Gray Design Associates' and b[0x29789]==0
fields=[dict(name=n,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e])) for n,a,e,t in [('xor_repeating_key_52',0x29755,0x29789,'BYTE_array_52_ASCII_repeating_key_index_mod52_SS_based'),('timestamp_message_format',0x2974d,0x29755,'NUL_ASCII_percent_s_colon_percent_s_LF'),('fatal_message_suffix',0x2974a,0x2974d,'NUL_ASCII_dot_LF')]]
assert b[0x2974d:0x29755]==b'%s: %s\n\0' and b[0x2974a:0x2974d]==b'.\n\0';save('data_fields',fields)
callers=[]
for r in old:
    i=Decoder(16,bytes.fromhex(r['bytes']),ip=r['ip']).decode()
    if i.flow_control==FlowControl.CALL and i.op0_kind==OpKind.FAR_BRANCH16 and i.far_branch_selector==0xfba and i.far_branch16 in (0x36,0x1b2):callers.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],instruction=fmt.format(i),target_ip=i.far_branch16))
if callers:save('inventory_direct_callers',callers)
contexts=[]
for r in old:
    if any(r['cs']==cs and a<=r['ip']<e for cs,a,e in [(0xfba,0x22,0x2a),(0x11ee,0x2eb4,0x2eef),(0x277,0x1b70,0x1b9a),(0x83d,0x2a1b,0x2a4f)]):
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw);contexts.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
save('related_contexts',contexts)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0xfba;ss=load+0x2771
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    for length in (0,1,2,51,52,53,104,255,256,4096):
        for pattern in range(4):
            plain=bytes((0 if pattern==0 else 255 if pattern==1 else i&255 if pattern==2 else (i*73+19)&255) for i in range(length));cipher=bytes(c^key[i%52] for i,c in enumerate(plain))
            for initial_ds in (ss,0x4000):
                u.mem_write(0x61000,plain or b'\0')
                for phase,source,expected in [('forward',plain,cipher),('reverse',cipher,plain)]:
                    for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_SS,ss),(UC_X86_REG_DS,initial_ds),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
                    u.mem_write(ss*16+0xff00,struct.pack('<HHHHH',0x6000,cs,0x1000,0x6000,length));u.emu_start(cs*16+0x1b2,cs*16+0x6000,count=100000)
                    assert bytes(u.mem_read(0x61000,length))==expected and u.reg_read(UC_X86_REG_AL)==functools.reduce(operator.xor,source,0)
                    assert u.reg_read(UC_X86_REG_DS)==(ss if length else initial_ds) and u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DI)==0x9abc
                    cases.append(dict(load=load,length=length,pattern=pattern,initial_ds=initial_ds,phase=phase,checksum=functools.reduce(operator.xor,source,0),passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,typed_bytes=63,cases=len(cases),failures=0,old_inventory_direct_callers=len(callers),scope='original complete XOR routine, SS=canonical DGROUP, bounded input buffers; no mocks; timestamp wrapper newly decoded statically only; key trailing NUL unpromoted',timestamp_wrapper_executed=False,full_count_pointer_domain_closed=False,natural_codec_use_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
