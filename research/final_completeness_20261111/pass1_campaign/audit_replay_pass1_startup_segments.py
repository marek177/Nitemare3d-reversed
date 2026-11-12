"""python audit_replay_pass1_startup_segments.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
rows=[]
for r in old:
    if r['cs']==0x11ee and 0x18<=r['ip']<0xb3:
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw);rows.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
save('startup_prefix_context',rows)
fields=[]
for off,name in [(0x20dc,'startup_stack_snapshot_WORD'),(0x2120,'DOS_version_WORD_major_high_minor_low'),(0x2122,'DOS_version_WORD_major_low_minor_high_refined')]:
    a=0x27710+off;fields.append(dict(name=name,start=a,end_exclusive=a+2,length=2,type='mutable_WORD_'+name,status='PARTIAL',range_sha256=sha(b[a:a+2])))
save('data_fields',fields);rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];state={}
for load in (0x1000,0x2000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x11ee;ds=load+0x2771;psp=load-0x10
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    def intr(uc,n,data):
        assert n==0x21 and uc.reg_read(UC_X86_REG_AH)==0x4a
        assert uc.reg_read(UC_X86_REG_DS)==psp and uc.reg_read(UC_X86_REG_ES)==psp and uc.reg_read(UC_X86_REG_SS)==ds
        state['resize'].append(uc.reg_read(UC_X86_REG_BX));uc.reg_write(UC_X86_REG_EFLAGS,uc.reg_read(UC_X86_REG_EFLAGS)&~1)
    u.hook_add(UC_HOOK_INTR,intr)
    for sp,available,version,initial_if in itertools.product((0x10,0x11,0x100,0x1000,0x1fd0,0x1fd1),(1,0x10,0xfff,0x1000,0x1001,0xffff),(0x0002,0x0003,0x0106,0x070a,0xffff),(0,1)):
        cap=min(available,0x1000);aligned=(sp+0xe02e)&0xfffe;snapshot=aligned-4;top=(ds+cap)&65535
        u.mem_write(psp*16+2,struct.pack('<H',(ds+available)&65535));u.mem_write(ds*16+0x264f,b'\x5a'+b'\xa5'*(0xe030-0x2650)+b'\x6b');state.clear();state['resize']=[]
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,psp),(UC_X86_REG_ES,psp),(UC_X86_REG_SS,0x6000),(UC_X86_REG_SP,sp),(UC_X86_REG_AX,version),(UC_X86_REG_EFLAGS,2|(initial_if<<9)|0x400)]:u.reg_write(reg,v)
        u.emu_start(cs*16+0x25,cs*16+0xb3,count=100000)
        expected={0x20dc:snapshot,0x20e0:((cap<<4)-1)&65535,0x20e2:ds,0x20e6:aligned,0x20e8:snapshot,0x20ea:snapshot,0x20ec:aligned-2,0x211e:psp,0x2122:version,0x2120:((version&255)<<8)|(version>>8)}
        assert all(struct.unpack('<H',u.mem_read(ds*16+o,2))[0]==v for o,v in expected.items())
        assert bytes(u.mem_read(ds*16+0x264f,0xe030-0x2650+2))==b'\x5a'+b'\0'*(0xe030-0x2650)+b'\x6b'
        assert struct.unpack('<H',u.mem_read(psp*16+2,2))[0]==top and state['resize']==[(top-psp)&65535]
        assert u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SS)==ds and u.reg_read(UC_X86_REG_ES)==ds and u.reg_read(UC_X86_REG_SP)==snapshot
        assert u.reg_read(UC_X86_REG_EFLAGS)&0x600==0x200
        cases.append(dict(load=load,initial_sp=sp,available_paragraphs=available,version_ax=version,initial_if=initial_if,final_segment=ds,final_sp=snapshot,bss_zero_bytes=0xe030-0x2650,passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=6,fields=3,previously_typed_bytes_refined=2,cases=len(cases),failures=0,scope='original startup interior prefix25..B3, DOS resize interrupt modeled; post-version-success seeded context, no packed EXE entry, error path, optional hook or full startup',runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
