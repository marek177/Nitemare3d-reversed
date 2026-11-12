"""python audit_replay_pass1_vga_pages.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,Register,OpKind
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INSN
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
functions=[]
for name,start,end in [('vga_page_flip_immediate',0x8e,0xa7),('vga_page_flip_synchronized',0xa8,0xd7)]:
    todo=[start];decoded={}
    while todo:
        ip=todo.pop()
        if ip in decoded:continue
        assert start<=ip<end;i=Decoder(16,b[0x1560+ip:0x1560+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
        if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
        if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
    rows=[]
    for ip,i in sorted(decoded.items()):
        raw=b[0x1560+ip:0x1560+i.next_ip];assert lookup[(0x156,ip)]['bytes']==raw.hex();rows.append(dict(cs=0x156,ip=ip,image_offset=0x1560+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    save(name,rows);functions.append(dict(name=name,start=0x1560+start,end_exclusive=0x1560+end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows)))
assert struct.unpack('<HH',b[0x2783c:0x27840])==(0xa000,0xa400)
save('data_fields',[dict(name=n,start=a,end_exclusive=a+2,length=2,type='mutable_WORD_VGA_page_segment',status='PARTIAL',range_sha256=sha(b[a:a+2])) for n,a in [('vga_page_segment_12C',0x2783c),('vga_draw_page_segment_12E',0x2783e)]])
refs=[]
for r in old:
    i=Decoder(16,bytes.fromhex(r['bytes']),ip=r['ip']).decode()
    if any(i.op_kind(k)==OpKind.MEMORY for k in range(i.op_count)) and i.memory_segment==Register.DS and i.memory_base==Register.NONE and i.memory_index==Register.NONE and i.memory_displacement in (0x12c,0x12e):refs.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=r['bytes'],instruction=fmt.format(i),scope='inventory only; default DS conditional'))
save('direct_references',refs);rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x156
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    state={}
    def port_in(uc,port,size,data):
        assert port==0x3da and size==1 and state['input'];state['read_count']+=1;return state['input'].pop(0)
    def port_out(uc,port,size,value,data):state['writes'].append((port,size,value, bool(uc.reg_read(UC_X86_REG_EFLAGS)&0x200)))
    u.hook_add(UC_HOOK_INSN,port_in,None,1,0,UC_X86_INS_IN);u.hook_add(UC_HOOK_INSN,port_out,None,1,0,UC_X86_INS_OUT)
    for high,low,entry,initial_if in itertools.product(range(256),(0,255),(0x8e,0xa8),(0,1)):
        back=high*256+low;front=back^65535
        for inputs in ([[]] if entry==0x8e else [[0,8],[1,0,0,8],[1,1,0,0,0,8]]):
            u.mem_write(ds*16+0x12c,struct.pack('<HH',front,back));state.clear();state.update(input=list(inputs),writes=[],read_count=0)
            for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_EFLAGS,2|(initial_if<<9))]:u.reg_write(reg,val)
            u.mem_write(0x5ff00,struct.pack('<HH',0x6000,cs));u.emu_start(cs*16+entry,cs*16+0x6000,count=200)
            assert struct.unpack('<HH',u.mem_read(ds*16+0x12c,4))==(back,front)
            expected=((back>>8<<4)&255)*256+12
            assert state['writes']==[(0x3d4,2,expected,bool(initial_if) if entry==0x8e else False)] and state['input']==[] and state['read_count']==len(inputs)
            final_if=bool(u.reg_read(UC_X86_REG_EFLAGS)&0x200);assert final_if==(bool(initial_if) if entry==0x8e else True)
            assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_DS)==ds
            cases.append(dict(load=load,entry=entry,initial_front=front,initial_back=back,initial_if=initial_if,input_sequence=bytes(inputs).hex(),out_word=expected,final_if=final_if,passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,typed_bytes=4,cases=len(cases),failures=0,direct_reference_count=len(refs),scope='original complete two FAR page-flip bodies; port inputs scripted and port outputs observed; no real VGA model or display',hardware_vga_verified=False,natural_page_invariants_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
