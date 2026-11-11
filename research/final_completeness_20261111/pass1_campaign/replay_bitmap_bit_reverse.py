"""Replay every BYTE through the original FAR bit reversal helper.
Usage: python replay_bitmap_bit_reverse.py IMAGE UNICORN_DIR DECODER_DIR OUT
"""
import csv,hashlib,json,sys
from pathlib import Path
image,emu,decoder,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(emu.resolve()),str(decoder.resolve())]
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();assert hashlib.sha256(b).hexdigest()=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
assert b[0xfc72:0xfcab].hex()=='c80400005756c47e06c646ff80c646fe01c646fd00be08008a46ff26840574068a46fe0846fdd06effd066fe4e75e98a46fd2688055e5fc9cb'
out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);rows=[];p=0xfc72
for ins in Decoder(16,b[p:0xfcab],ip=0xd2):
    assert not ins.is_invalid;rows.append(dict(image_offset=p,cs=0xfba,ip=ins.ip,bytes=b[p:p+ins.len].hex(),instruction=fmt.format(ins)));p+=ins.len
assert p==0xfcab
with (out/'instructions.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b)
    cs=load+0xfba
    for offset in (0x33,0xfffe):
        address=0x60000+offset
        for value in range(256):
            expected=int(format(value,'08b')[::-1],2)
            for r,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,load+0x2771),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_AX,0xa500),(UC_X86_REG_EFLAGS,2)]:u.reg_write(r,v)
            u.mem_write(address-1,bytes([0x5a,value,0xc3]));u.mem_write(0x5ff00,b''.join(v.to_bytes(2,'little') for v in [0x4000,cs,offset,0x6000]))
            u.emu_start(load*16+0xfc72,cs*16+0x4000,count=200)
            actual=bytes(u.mem_read(address-1,3))
            assert actual==bytes([0x5a,expected,0xc3])
            for r,v in [(UC_X86_REG_SP,0xff04),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_DS,load+0x2771),(UC_X86_REG_ES,0x6000),(UC_X86_REG_AX,0xa500|expected)]:assert u.reg_read(r)==v
            cases.append(dict(load_segment=load,pointer_offset=offset,input=value,expected=expected,actual=actual[1],guards_preserved=True,abi_checks_passed=True))
(out/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
s=dict(image_sha256=hashlib.sha256(b).hexdigest(),function_start=0xfc72,function_end_exclusive=0xfcab,function_bytes=57,instructions=len(rows),cases=len(cases),failures=0,original_runtime_tests=0,scope='seeded original instruction replay; all bytes, two loads, two far pointers; no natural reachability proof',deep_verified=False)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
