"""Synthetic minimization only: not Nitemare bytes or an original-runtime test.
Usage: python diagnose_unicorn_smc_adc.py UNICORN_DIR OUT_DIR
"""
import hashlib,json,struct,sys
from pathlib import Path
dep,out=map(Path,sys.argv[1:3]);mode=sys.argv[3] if len(sys.argv)>3 else "memory_add"
assert mode in ("explicit_flags","memory_add","flags_barrier")
sys.path.insert(0,str(dep.resolve()))
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
cases=[]
for target_kind,target in [('future_operand',0x110),('same_code_page_data',0x800),('other_page_data',0x1800)]:
    for before_cf,incoming_cf in [(1,0),(0,1),(0,0),(1,1)]:
        # CMP/JAE creates old CF and a flow boundary; memory ADD supplies ADC CF.
        prefix=bytes([0xf9 if before_cf else 0xf8,0xf9 if incoming_cf else 0xf8]) if mode=='explicit_flags' else bytes.fromhex('39d873002e81060003')+struct.pack('<H',incoming_cf)
        if mode=='flags_barrier':prefix+=bytes.fromhex('9c9d')
        if target_kind=='future_operand':target=0x100+len(prefix)+7+6+1
        code=prefix+bytes.fromhex('2e8116')+struct.pack('<HH',target,1)+b'\x90'*6+bytes.fromhex('a00002f4')
        stop_address=0x10100+len(code)-1
        u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x10100,code)
        for reg,value in [(UC_X86_REG_CS,0x1000),(UC_X86_REG_DS,0x2000),(UC_X86_REG_SS,0x3000),(UC_X86_REG_SP,0x8000)]:u.reg_write(reg,value)
        u.reg_write(UC_X86_REG_AX,0 if before_cf else 1);u.reg_write(UC_X86_REG_BX,1 if before_cf else 0)
        u.mem_write(0x10300,struct.pack('<H',0xffff if incoming_cf else 0))
        u.mem_write(0x10000+target,struct.pack('<H',0x200));u.mem_write(0x20200,b'\x11\x22\x33')
        trace=[];stopped=[]
        def hook(uc,address,size,user):
            trace.append(dict(offset=address-0x10000,cf=uc.reg_read(UC_X86_REG_EFLAGS)&1,target_word=struct.unpack('<H',bytes(uc.mem_read(0x10000+target,2)))[0]))
            if address==stop_address:stopped.append(True);uc.emu_stop()
        u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x10100,stop_address+1,count=100)
        actual=struct.unpack('<H',bytes(u.mem_read(0x10000+target,2)))[0];expected=0x201+incoming_cf
        assert stopped
        cases.append(dict(target_kind=target_kind,target_offset=target,before_cf=before_cf,incoming_cf=incoming_cf,expected_word=expected,actual_word=actual,model_match=actual==expected,synthetic_code_sha256=hashlib.sha256(code).hexdigest(),synthetic_code_hex=code.hex(),trace=trace))
out.mkdir(parents=True,exist_ok=True)
r=dict(mode=mode,experiment='synthetic CMP/JAE, ADD lazy-flags, ADC future-operand write',unicorn_version=unicorn.__version__,native_libraries=[dict(name=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in dep.rglob('*.dll')],cases=cases,attempted_cases=len(cases),mismatches=sum(not c['model_match'] for c in cases),original_game_replay_cases=0,runtime_tests=0,scope='synthetic minimization; cannot certify original CPU/prefetch behavior')
(out/'evidence.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(attempted_cases=len(cases),mismatches=r['mismatches'],results=[{k:c[k] for k in ['target_kind','before_cf','incoming_cf','expected_word','actual_word']} for c in cases]),indent=2))
