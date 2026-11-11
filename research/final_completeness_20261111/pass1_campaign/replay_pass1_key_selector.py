"""Original four-label selector at two synthetic relocated load bases.
Usage: python replay_pass1_key_selector.py IMAGE RELOCATIONS_CSV UNICORN_DIR OUT_DIR
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,relocs,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();h=hashlib.sha256(b).hexdigest();assert h=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
rs=list(csv.DictReader(relocs.open(encoding='utf-8-sig')));assert len(rs)==1670
cases=[]
for load in (0,0x1000):
    relocated=bytearray(b)
    for r in rs:
        pos=int(r['image_offset']);assert struct.unpack_from('<H',b,pos)[0]==int(r['original_word'])
        struct.pack_into('<H',relocated,pos,(int(r['original_word'])+load)&65535)
    for index,off,text in [(0,0xd0a,'Red key'),(1,0xd18,'Green key'),(2,0xd26,'Blue key'),(3,0xd36,'Yellow key')]:
        u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,bytes(relocated));cs=load+0x83d;ds=load+0x2771
        initial={UC_X86_REG_CS:cs,UC_X86_REG_DS:ds,UC_X86_REG_SS:0x7000,UC_X86_REG_SP:0x8000,UC_X86_REG_BP:0x1234,UC_X86_REG_SI:0x5678,UC_X86_REG_BX:0x2345,UC_X86_REG_CX:0x3456,UC_X86_REG_ES:0x4567}
        for reg,value in initial.items():u.reg_write(reg,value)
        u.reg_write(UC_X86_REG_EFLAGS,0x602);u.mem_write(0x78000,struct.pack('<HHH',0x6000,cs,index));returned=[];trace=[]
        def code(uc,a,size,user):
            trace.append(a)
            if a==cs*16+0x6000:returned.append(True);uc.emu_stop()
        u.hook_add(UC_HOOK_CODE,code);u.emu_start(load*16+0xa306,cs*16+0x6001,count=1000)
        expected_offset,expected_segment=struct.unpack_from('<HH',relocated,0x27710+off)
        ax,dx=u.reg_read(UC_X86_REG_AX),u.reg_read(UC_X86_REG_DX)
        assert returned and ax==expected_offset and dx==expected_segment and u.reg_read(UC_X86_REG_SP)==0x8004
        assert all(u.reg_read(reg)==value for reg,value in initial.items() if reg!=UC_X86_REG_SP)
        raw=text.encode()+bytes([0]);target=dx*16+ax;assert bytes(u.mem_read(target,len(raw)))==raw
        cases.append(dict(load_segment=load,index=index,returned_offset=ax,returned_segment=dx,returned_linear_address=target,text=text,caller_argument_bytes_remaining=2,instruction_trace=trace,assertions_passed=True))
out.mkdir(parents=True,exist_ok=True)
r=dict(image_sha256=h,relocations_sha256=hashlib.sha256(relocs.read_bytes()).hexdigest(),unicorn_version=unicorn.__version__,native_libraries=[dict(name=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in dep.rglob('*.dll')],cases=cases,controlled_replay_cases=len(cases),natural_caller_DS_context_proven=False,invalid_indices_tested=False,runtime_tests=0,new_deep_verified_bytes=0,scope='original instructions and actual relocation sites; synthetic load/stack/DS, no original DOS runtime')
(out/'evidence.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(controlled_replay_cases=len(cases),assertions_passed=True,runtime_tests=0)))
