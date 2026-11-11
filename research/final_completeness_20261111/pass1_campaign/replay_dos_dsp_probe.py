"""Original probe/wait instructions with explicit synthetic BIOS and port adapters.
Usage: python replay_dos_dsp_probe.py IMAGE UNICORN_DIR OUT_DIR
"""
import collections,hashlib,json,struct,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_INSN
from unicorn.x86_const import *
b=image.read_bytes();h=hashlib.sha256(b).hexdigest();assert h=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
base=0x15bf0;cases=[]
specs=[('all_absent',{},0x300,1),('success_220',{0x220:(1,0xaa)},0x220,0),('bad220_then230',{0x220:(1,0x55),0x230:(1,0xaa)},0x230,0),('ready_on_poll200',{0x220:(200,0xaa)},0x220,0),('last_candidate',{0x2f0:(1,0xaa)},0x2f0,0),('all_wrong_reply',{p:(1,0x55) for p in range(0x200,0x300,0x10)},0x300,1)]
def setup():
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,b)
    for reg,v in [(UC_X86_REG_CS,0x15bf),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0x8000),(UC_X86_REG_DS,0x2222),(UC_X86_REG_ES,0x3333),(UC_X86_REG_BP,0x4444),(UC_X86_REG_SI,0x5555),(UC_X86_REG_DI,0x6666)]:u.reg_write(reg,v)
    u.mem_write(0x78000,struct.pack('<H',0x6000));return u
for name,responses,expected_base,expected_cf in specs:
    u=setup();polls=collections.Counter();data_reads=[];outs=[];ticks=[];visited=set();returned=[]
    def code(uc,a,size,user):
        visited.add(a)
        if a==base+0x6000:returned.append(True);uc.emu_stop()
    def interrupt(uc,n,user):
        assert n==0x1a and uc.reg_read(UC_X86_REG_AH)==0
        tick=len(ticks);ticks.append(tick);uc.reg_write(UC_X86_REG_CX,0);uc.reg_write(UC_X86_REG_DX,tick);uc.reg_write(UC_X86_REG_AL,0)
    def port_in(uc,p,size,user):
        assert size==1
        if p&15==14:
            portbase=p-14;polls[portbase]+=1
            return 0x80 if portbase in responses and polls[portbase]>=responses[portbase][0] else 0
        assert p&15==10;portbase=p-10;assert portbase in responses;data_reads.append(portbase);return responses[portbase][1]
    def port_out(uc,p,size,v,user):assert size==1 and p&15==6 and v in (0,1);outs.append(dict(port=p,value=v))
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,interrupt);u.hook_add(UC_HOOK_INSN,port_in,None,1,0,UC_X86_INS_IN);u.hook_add(UC_HOOK_INSN,port_out,None,1,0,UC_X86_INS_OUT)
    u.emu_start(0x1b768,base+0x6001,count=100000)
    final=struct.unpack('<H',bytes(u.mem_read(base+0x2df0,2)))[0];cf=u.reg_read(UC_X86_REG_EFLAGS)&1
    assert returned and final==expected_base and cf==expected_cf and u.reg_read(UC_X86_REG_SP)==0x8002
    attempted=list(range(0x200,(expected_base if expected_cf else expected_base+0x10),0x10))
    assert data_reads==[p for p in attempted if p in responses]
    assert len(outs)==2*len(attempted)
    for i,p in enumerate(attempted):assert outs[2*i:2*i+2]==[dict(port=p+6,value=1),dict(port=p+6,value=0)]
    for p in attempted:assert polls[p]==(responses[p][0] if p in responses else 200)
    assert all(u.reg_read(reg)==v for reg,v in [(UC_X86_REG_DS,0x2222),(UC_X86_REG_ES,0x3333),(UC_X86_REG_BP,0x4444),(UC_X86_REG_SI,0x5555),(UC_X86_REG_DI,0x6666)])
    cases.append(dict(name=name,adapter_responses={str(p):list(v) for p,v in responses.items()},final_base=final,final_cf=cf,status_reads=dict(polls),data_read_bases=data_reads,reset_writes=outs,bios_tick_values=ticks,visited_instruction_starts=sorted(visited-{base+0x6000}),returned=True))
wait_cases=[]
for name,start,bx,should_return in [('normal',10,1,True),('wrapped_target',0xfffe,3,True),('target_ffff',0xfffe,1,False)]:
    u=setup();u.reg_write(UC_X86_REG_BX,bx);ticks=[];returned=[];executed=[]
    def code(uc,a,size,user):
        executed.append(a)
        if a==base+0x6000:returned.append(True);uc.emu_stop()
    def interrupt(uc,n,user):
        assert n==0x1a and uc.reg_read(UC_X86_REG_AH)==0
        tick=(start+len(ticks))&65535;ticks.append(tick);uc.reg_write(UC_X86_REG_DX,tick);uc.reg_write(UC_X86_REG_CX,0);uc.reg_write(UC_X86_REG_AL,0)
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,interrupt);u.emu_start(0x18a31,base+0x6001,count=1000)
    assert bool(returned)==should_return
    if not should_return:assert len(executed)==1000
    if name=='normal':assert ticks==[10,11,12]
    if name=='wrapped_target':assert ticks==[0xfffe,0xffff]
    if should_return:assert u.reg_read(UC_X86_REG_BX)==bx and u.reg_read(UC_X86_REG_SP)==0x8002
    wait_cases.append(dict(name=name,start_tick=start,input_bx=bx,target=(start+bx)&65535,returned=bool(returned),instruction_budget_exhausted=not returned,observed_instruction_hooks=len(executed),final_cs=u.reg_read(UC_X86_REG_CS),final_ip=u.reg_read(UC_X86_REG_IP),bios_tick_values=ticks))
out.mkdir(parents=True,exist_ok=True)
r=dict(image_sha256=h,unicorn_version=unicorn.__version__,native_libraries=[dict(name=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in dep.rglob('*.dll')],probe_cases=cases,wait_cases=wait_cases,controlled_replay_cases=len(cases)+len(wait_cases),runtime_tests=0,natural_hardware_or_tick_reachability_proven=False,new_deep_verified_bytes=0,scope='synthetic port responses and monotonically advancing BIOS low WORD ticks; not physical devices or DOS runtime')
(out/'evidence.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(probe_cases=len(cases),wait_cases=len(wait_cases),assertions_passed=True,runtime_tests=0)))
