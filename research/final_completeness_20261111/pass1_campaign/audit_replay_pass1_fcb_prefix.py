"""python audit_replay_pass1_fcb_prefix.py IMAGE INVENTORY DECODER EMULATOR SOURCE_DIR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,reference,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
out.mkdir(parents=True,exist_ok=True);manifest=json.loads((reference/'source_manifest.json').read_text())
for f in manifest:assert sha((reference/f['name']).read_bytes())==f['sha256']
source=(reference/'FCB.ASM').read_bytes().decode('latin1');assert all(x in source for x in ['MOV     CX,8','MOV     CL,3','SUB     DI,16','STOSW                   ; Initialize two words after to zero'])
fields=[]
for index,base in enumerate((0x24d0,0x24e0)):
    for delta,n,typ in [(0,1,'drive_BYTE'),(1,8,'name_8_BYTE'),(9,3,'extension_3_BYTE'),(12,2,'zero_initialized_WORD12'),(14,2,'zero_initialized_WORD14')]:
        a=0x27710+base+delta;assert not any(b[a:a+n]);fields.append(dict(name='exec_parsed_fcb%d_'%index+typ,start=a,end_exclusive=a+n,length=n,type='parsed_FCB_prefix_'+typ,status='PARTIAL',range_sha256=sha(b[a:a+n]),external_reference_sha256=sha((reference/'FCB.ASM').read_bytes())))
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
save('data_fields',fields);old=json.loads(inventory.read_text());fmt=Formatter(FormatterSyntax.INTEL);rows=[]
for r in old:
    if r['cs']==0x11ee and 0x34de<=r['ip']<0x34f5:
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw);rows.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
assert sum(len(bytes.fromhex(r['bytes'])) for r in rows)==23;save('parse_call_prefix',rows)
cases=[];state={}
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x11ee
    def intr(uc,n,data):
        k=len(state['calls']);assert n==0x21 and uc.reg_read(UC_X86_REG_AX)==0x2901 and uc.reg_read(UC_X86_REG_DS)==ds and uc.reg_read(UC_X86_REG_ES)==ds
        assert uc.reg_read(UC_X86_REG_DI)==(0x24d0 if k==0 else 0x24e0)
        assert uc.reg_read(UC_X86_REG_SI)==(0x3001 if k==0 else state['after_first'])
        uc.mem_write(ds*16+uc.reg_read(UC_X86_REG_DI),bytes([k+1])*16);uc.reg_write(UC_X86_REG_SI,state['after_first'] if k==0 else 0x7777);uc.reg_write(UC_X86_REG_AL,state['status'][k]);state['calls'].append(k)
    u.hook_add(UC_HOOK_INTR,intr)
    for first_status,second_status,after_first in itertools.product((0,1,255),(0,1,255),(0,1,0x300a,65535)):
        state.clear();state.update(calls=[],status=(first_status,second_status),after_first=after_first)
        u.mem_write(ds*16+0x24c4,struct.pack('<H',0x3000));u.mem_write(ds*16+0x24cf,b'\x5a'+b'\xa5'*32+b'\x6b')
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x3333),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
        u.emu_start(cs*16+0x34de,cs*16+0x34f5,count=100)
        assert bytes(u.mem_read(ds*16+0x24cf,34))==b'\x5a'+b'\x01'*16+b'\x02'*16+b'\x6b' and state['calls']==[0,1]
        assert u.reg_read(UC_X86_REG_SP)==0xff00 and u.reg_read(UC_X86_REG_ES)==ds and u.reg_read(UC_X86_REG_SI)==0x7777 and u.reg_read(UC_X86_REG_AL)==second_status
        cases.append(dict(load=load,first_status=first_status,second_status=second_status,after_first_si=after_first,passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),external_source_manifest_sha256=sha((reference/'source_manifest.json').read_bytes()),typed_bytes=32,fields=10,cases=len(cases),failures=0,scope='native two-INT29 caller prefix; parser writes/status/SI modeled; 16B external MS-DOS2 source contract, no actual DOS parser execution or universal DOS bound proof',runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
