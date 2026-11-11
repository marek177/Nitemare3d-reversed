"""Controlled sample-IRQ replay with patched operand state, not device runtime."""
import hashlib,json,struct,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:4]);mode=sys.argv[4] if len(sys.argv)>4 else "continuous"
assert mode in ("continuous","single_instruction")
sys.path.insert(0,str(dep.resolve()))
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_INSN
from unicorn.x86_const import *
b=image.read_bytes();h=hashlib.sha256(b).hexdigest();assert h=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
base=0x15bf0;cases=[]
for sample_offset,end_offset,accum,frac,integer,countdown in [(0x100,0x200,0,0,1,100),(0x100,0x200,1,0xffff,0,63),(0x100,0x101,0,0,2,100)]:
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,b)
    for offset,value in [(0x364f,accum),(0x366c,end_offset),(0x3675,frac),(0x367c,integer),(0x367f,0x3000),(0x3684,sample_offset)]:u.mem_write(base+offset,struct.pack('<H',value))
    u.mem_write(base+0x2c4b,struct.pack('<I',countdown));u.mem_write(base+0x2c53,b'\0')
    carry=int(accum+frac>65535);next_offset=(sample_offset+integer+carry)&65535
    u.mem_write(0x30000+next_offset,b'\x2a')
    for reg,value in [(UC_X86_REG_CS,0x15bf),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0x8000),(UC_X86_REG_DS,0x2222),(UC_X86_REG_AX,0x1234)]:u.reg_write(reg,value)
    u.mem_write(0x78000,struct.pack('<HHH',0x6000,0x15bf,0x0202))
    ports=[];interrupts=[];returned=[];trace=[]
    def code(uc,a,size,user):
        trace.append(dict(address=a,cf=uc.reg_read(UC_X86_REG_EFLAGS)&1,sample_offset=struct.unpack("<H",bytes(uc.mem_read(base+0x3684,2)))[0]))
        if a==base+0x6000:returned.append(True);uc.emu_stop()
    def intr(uc,n,user):interrupts.append(n);uc.emu_stop()
    def port(uc,p,size,v,user):ports.append(dict(port=p,size=size,value=v))
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_INSN,port,None,1,0,UC_X86_INS_OUT)
    if mode=="continuous":u.emu_start(0x19241,base+0x6001,count=1000)
    else:
        u.reg_write(UC_X86_REG_IP,0x3651)
        for step in range(64):
            if returned or interrupts:break
            current=u.reg_read(UC_X86_REG_CS)*16+u.reg_read(UC_X86_REG_IP)
            u.emu_start(current,0x100000,count=1)
        # Bounded diagnostic: an unfinished state is evidence, not accepted replay.
    word=lambda a:struct.unpack('<H',bytes(u.mem_read(a,2)))[0]
    structural_return_ok=bool(returned) and not interrupts and u.reg_read(UC_X86_REG_AX)==0x1234 and u.reg_read(UC_X86_REG_DS)==0x2222 and u.reg_read(UC_X86_REG_SP)==0x8006
    actual_offset=word(base+0x3684);actual_accum=word(base+0x364f);actual_lookup=word(base+0x3691)
    expected_ports=[dict(port=0x42,size=1,value=b[base+0x33e3]),dict(port=0x42,size=1,value=0),dict(port=0x20,size=1,value=0x20)]
    checks=dict(return_state=structural_return_ok,offset=actual_offset==next_offset,accumulator=actual_accum==((accum+frac)&65535),lookup=actual_lookup==0x33e3,ports=ports==expected_ports)
    counter=struct.unpack('<I',bytes(u.mem_read(base+0x2c4b,4)))[0];flag=bytes(u.mem_read(base+0x2c53,1))[0]
    checks['countdown']=counter==((countdown-64)&0xffffffff);checks['borrow_counter']=flag==int(countdown<64)
    cases.append(dict(initial_sample_offset=sample_offset,end_offset=end_offset,fractional_accumulator=accum,fractional_step=frac,integer_step=integer,initial_countdown=countdown,expected_next_sample_offset=next_offset,actual_next_sample_offset=actual_offset,actual_accumulator=actual_accum,actual_lookup=actual_lookup,checks=checks,read_offset_beyond_declared_end=next_offset>=end_offset,ports=ports,final_countdown=counter,borrow_counter=flag,returned_by_iret=bool(returned),step_limit_hit=mode=="single_instruction" and not returned and not interrupts,instruction_trace=trace))
out.mkdir(parents=True,exist_ok=True)
r=dict(execution_mode=mode,image_sha256=h,unicorn_version=unicorn.__version__,native_libraries=[dict(name=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in dep.rglob('*.dll')],cases=cases,attempted_replay_cases=len(cases),controlled_replay_cases=0,semantic_replay_accepted=False,all_checks_match=all(all(c['checks'].values()) for c in cases),runtime_tests=0,natural_reachability_proven=False,scope='prepared operands and memory; normal IRQ output path only; no PIT/PIC or original runtime')
(out/'evidence.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(attempted_replay_cases=len(cases),accepted_cases=0,all_checks_match=r['all_checks_match'],runtime_tests=0)))
