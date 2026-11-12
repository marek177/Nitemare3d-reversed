"""python audit_replay_pass1_getenv.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
lookup={(r['cs'],r['ip']):r for r in json.loads(inventory.read_text())};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
functions=[]
for name,start,end in [('crt_strlen_near',0x2398,0x23b3),('crt_strncmp_near',0x23dc,0x2416),('crt_getenv_near',0x248a,0x24ea)]:
    todo=[start];decoded={}
    while todo:
        ip=todo.pop()
        if ip in decoded:continue
        assert start<=ip<end;i=Decoder(16,b[0x11ee0+ip:0x11ee0+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
        if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
        if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
    rows=[]
    for ip,i in sorted(decoded.items()):
        raw=b[0x11ee0+ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,ip)]['bytes']==raw.hex();rows.append(dict(cs=0x11ee,ip=ip,image_offset=0x11ee0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    save(name,rows);functions.append(dict(name=name,start=0x11ee0+start,end_exclusive=0x11ee0+end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows)))
fields=[dict(name=n,start=a,end_exclusive=a+2,length=2,type=t,status='PARTIAL',range_sha256=sha(b[a:a+2])) for n,a,t in [('crt_argument_count',0x2984e,'mutable_WORD_initial_zero_startup_argument_count'),('crt_argument_vector',0x29850,'mutable_NEAR16_pointer_initial_zero_startup_argument_vector'),('crt_environment_vector',0x29852,'mutable_NEAR16_pointer_initial_zero_NUL_terminated_NEAR16_pointer_vector')]]
assert not any(b[0x2984e:0x29854]);save('data_fields',fields)
contexts=[]
for r in lookup.values():
    if r['cs']==0x11ee and any(a<=r['ip']<e for a,e in [(0xcc,0xdf),(0x3cf,0x3ef),(0x4d0,0x4e5)]):
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw);contexts.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
save('startup_contexts',contexts)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
tables=[None,[],[b'TZ=ABC3DEF'],[b'TZ='],[b'TZ',b'TZ=XYZ'],[b'tz=lower',b'TZ=upper'],[b'TZ=first',b'TZ=second'],[b'PATH=C:\\DOS',b'COMSPEC=COMMAND.COM'],[b'=drive',b'ABC=V'],[b'A=B=V',b'A=short'],[b'\x80=high',b'Z=last']]
queries=[None,b'',b'TZ',b'tz',b'T',b'TZ=',b'PATH',b'COMSPEC',b'ABC',b'A',b'A=B',b'\x80',b'Z',b'ABSENT']
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x11ee
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    def environment(entries):
        pointers=[];offset=0x8100
        for entry in entries or []:pointers.append(offset);u.mem_write(ds*16+offset,entry+b'\0');offset+=len(entry)+1
        u.mem_write(ds*16+0x8000,struct.pack('<'+'H'*(len(pointers)+1),*(pointers+[0])));u.mem_write(ds*16+0x2142,struct.pack('<H',0 if entries is None else 0x8000));return pointers
    def execute(entry,args):
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.mem_write(0x5ff00,struct.pack('<HH',0x6000,cs)+struct.pack('<'+'H'*len(args),*args));u.emu_start(cs*16+entry,cs*16+0x6000,count=10000)
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DI)==0x9abc and u.reg_read(UC_X86_REG_DS)==ds
        return u.reg_read(UC_X86_REG_AX)
    for entries,key in itertools.product(tables,queries):
        pointers=environment(entries);arg=0 if key is None else 0x9000
        if key is not None:u.mem_write(ds*16+arg,key+b'\0')
        expected=0
        if entries is not None and key is not None:
            for pointer,text in zip(pointers,entries):
                if len(text)>len(key) and text[len(key):len(key)+1]==b'=' and text[:len(key)]==key:expected=pointer+len(key)+1;break
        actual=execute(0x248a,[arg]);assert actual==expected,(entries,key,actual,expected)
        cases.append(dict(load=load,kind='getenv',environment=repr(entries),key=repr(key),expected=expected,passed=True))
    for entries,expected in [(None,(28800,1)),([b'OTHER=0'],(28800,1)),([b'TZ='],(28800,1)),([b'TZ=ABC3DEF'],(10800,68)),([b'TZ=XYZ-5GHI'],(-18000,71)),([b'tz=ABC1DEF'],(28800,1))]:
        environment(entries);u.mem_write(ds*16+0x24a2,b[0x29bb2:0x29bc8]);execute(0x2c06,[])
        actual=struct.unpack('<iH',u.mem_read(ds*16+0x24a6,6));assert actual==expected
        cases.append(dict(load=load,kind='native_TZ_parser_integration',environment=repr(entries),key="b'TZ'",expected=str(expected),passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,typed_bytes=6,cases=len(cases),failures=0,scope='original getenv, strlen, strncmp and six TZ integration scenarios; no mocks; synthetic DS near vector, DF=0; no DOS environment construction',original_startup_environment_closed=False,full_strncmp_domain_closed=False,natural_environment_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
