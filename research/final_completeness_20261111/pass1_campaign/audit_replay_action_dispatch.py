"""python audit_replay_action_dispatch.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);pending=[0x5fc];decoded={};instructions=[]
while pending:
    ip=pending.pop()
    if ip in decoded:continue
    assert 0x5fc<=ip<0x6ff
    i=Decoder(16,b[0x6370+ip:0x6a6f],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.near_branch_target)
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.next_ip)
for ip,i in sorted(decoded.items()):
    raw=b[0x6370+ip:0x6370+i.next_ip];assert lookup[(0x637,ip)]['bytes']==raw.hex()
    instructions.append(dict(cs=0x637,ip=ip,image_offset=0x6370+ip,bytes=raw.hex(),instruction=fmt.format(i)))
fixtures=[('empty',[],0),('negative_count',[],-1),('mismatch',[(1,False,True)],1),('predicate_false',[(1,True,False)],1)]
fixtures += [('state_%d'%s,[(s,True,True)],1) for s in (0,1,2,3,9,10,255)]
fixtures.append(('mixed',[(1,True,True),(9,True,True),(2,False,True),(2,True,False),(3,True,True)],5))
inputs=[(255,0,1,1,1,'empty')]
for selector in (0,2,3):
    inputs += [(selector,1,1,1,1,'empty'),(selector,0,0,1,1,'empty'),(selector,0,3,1,1,'empty'),(selector,0,1,0,1,'empty'),(selector,0,2,1,0,'empty'),(selector,0,2,1,1,'empty')]
    inputs += [(selector,0,1,1,1,name) for name,rows,count in fixtures]
fixtures={name:(rows,count) for name,rows,count in fixtures};rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];calls=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x637;ds=load+0x2771;record_seg=load+0x21fd
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    targets={load*16+0xf9d0:'special',load*16+0x8f12:'permission',load*16+0xbb60:'predicate',load*16+0x5f74:'record_action',load*16+0x7ede:'alternate',load*16+0x5510:'finalize',load*16+0x9be6:'refresh'}
    for a in targets:u.mem_write(a,b'\xcb')
    state={}
    def hook(uc,a,size,data):
        if a not in targets:return
        name=targets[a];sp=uc.reg_read(UC_X86_REG_SP);args=struct.unpack('<6H',uc.mem_read(0x50000+sp+4,12));state['trace'].append(name)
        if name=='permission':uc.reg_write(UC_X86_REG_AL,state['permission'])
        elif name=='alternate':uc.reg_write(UC_X86_REG_AL,state['alternate'])
        elif name=='predicate':
            n=(uc.reg_read(UC_X86_REG_SI)-0x264e)//26;assert list(args)==[10,20,(n+3-10)&65535,(-n-1-20)&65535,16,1]
            state['predicates'].append(n);uc.reg_write(UC_X86_REG_AL,int(state['rows'][n][2]))
        elif name=='record_action':
            n=(args[0]-0x264e)//26;assert list(args[:4])==[0x264e+26*n,record_seg,6+28*n,record_seg];state['actions'].append(n)
        elif name=='finalize':assert args[0]==7
        calls.append(dict(case=state['case'],load_segment=load,callee=name,si=uc.reg_read(UC_X86_REG_SI),arguments=' '.join(map(str,args)) if name in ('predicate','record_action','finalize') else ''))
    u.hook_add(UC_HOOK_CODE,hook)
    for selector,special,mode,permission,alternate,fixture in inputs:
        rows,count=fixtures[fixture]
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.mem_write(0x5ff00,struct.pack('<HH',0x4000,cs));u.mem_write(ds*16+0x418f,bytes([selector]));u.mem_write(ds*16+0x4198,bytes([special]));u.mem_write(ds*16+0x4190,struct.pack('<H',mode));u.mem_write(ds*16+0x6276,struct.pack('<h',count));u.mem_write(ds*16+0x4540,struct.pack('<I',0x11223344));u.mem_write(ds*16+0x415e,struct.pack('<hh',10,20));u.mem_write(ds*16+0x4188,b'\x07');u.mem_write(ds*16+0x419a,b'\0')
        for n,(kind,match,predicate) in enumerate(rows):
            p=record_seg*16+0x264e+n*26;u.mem_write(p,b'\0'*26);u.mem_write(p+2,struct.pack('<I',0x11223344 if match else 0x55667788));u.mem_write(p+8,struct.pack('<h',n));u.mem_write(p+11,bytes([kind]));u.mem_write(record_seg*16+6+28*n+16,struct.pack('<hh',64*(n+3),64*(-n-1)))
        state.clear();state.update(case=len(cases),permission=permission,alternate=alternate,rows=rows,trace=[],predicates=[],actions=[])
        u.emu_start(cs*16+0x5fc,cs*16+0x4000,count=3000)
        expected=[];preds=[];actions=[];completed=False
        if selector!=255:
            if special:expected=['special']
            elif mode==1:
                expected=['permission']
                if permission:
                    for n,(kind,match,pred) in enumerate(rows):
                        if match and kind not in (0,9,10):
                            preds.append(n);expected.append('predicate')
                            if pred:actions.append(n);expected.append('record_action')
                    completed=True
            elif mode==2:expected=['alternate'];completed=bool(alternate)
        if completed:expected += ['finalize','refresh']
        assert state['trace']==expected and state['predicates']==preds and state['actions']==actions
        assert u.mem_read(ds*16+0x419a,1)[0]==int(completed)
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DI)==0x9abc and u.reg_read(UC_X86_REG_DS)==ds
        cases.append(dict(load_segment=load,selector=selector,special=special,mode=mode,permission=permission,alternate=alternate,fixture=fixture,count=count,predicate_records=' '.join(map(str,preds)),action_records=' '.join(map(str,actions)),completed=completed,passed=True))
schema=[dict(record='record26',offset=2,width=4,role='DWORD equality filter against DS:4540',consumer='0637:0657'),dict(record='record26',offset=8,width=2,role='signed WORD multiplied by 28 to construct linked object offset',consumer='0637:0673'),dict(record='record26',offset=11,width=1,role='BYTE state excludes 0,9,10',consumer='0637:065E..0671'),dict(record='record28',offset=16,width=2,role='signed WORD SAR 6 before relative X subtraction',consumer='0637:0688..068F'),dict(record='record28',offset=18,width=2,role='signed WORD SAR 6 before relative Y subtraction',consumer='0637:0693..069A')]
out.mkdir(parents=True,exist_ok=True)
for name,data in [('instructions',instructions),('cases',cases),('callee_trace',calls),('record_field_roles',schema)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),function_start=0x696c,function_end_exclusive=0x6a6f,function_span_bytes=259,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in instructions),instructions=len(instructions),cases=len(cases),failures=0,scope='original action dispatcher; seven callees mocked; record filters, arguments, coordinates and finalize effects tested',predicate_algorithm_closed=False,damage_algorithm_closed=False,natural_record_count_bounds_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
