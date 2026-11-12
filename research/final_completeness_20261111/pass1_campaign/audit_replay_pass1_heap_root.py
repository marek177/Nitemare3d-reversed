"""python audit_replay_pass1_heap_root.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);functions=[]
out.mkdir(parents=True,exist_ok=True)
for name,start,end in [('heap_block_initialize',0x20fe,0x2132),('heap_root_append',0x2132,0x2168),('heap_os_allocate',0x22e2,0x2326)]:
    pending=[start];decoded={};rows=[]
    while pending:
        ip=pending.pop()
        if ip in decoded:continue
        assert start<=ip<end
        i=Decoder(16,b[0x11ee0+ip:0x11ee0+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
        if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.near_branch_target)
        if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.next_ip)
    for ip,i in sorted(decoded.items()):
        raw=b[0x11ee0+ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,ip)]['bytes']==raw.hex()
        rows.append(dict(cs=0x11ee,ip=ip,image_offset=0x11ee0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    functions.append(dict(name=name,start=0x11ee0+start,end_exclusive=0x11ee0+end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows)))
fields=[]
for name,a,e,t in [('crt_heap_last_block',0x29a4e,0x29a52,'FAR16_last_heap_block_pointer_initial_NULL'),('crt_heap_block_header_tag',0x29a52,0x29a54,'WORD_initial_3_copied_to_heap_header_plus_2'),('crt_heap_high_segment',0x29806,0x29808,'WORD_segment_high_watermark_initial_0'),('crt_heap_low_segment_limit',0x29808,0x2980a,'WORD_segment_lower_bound_initial_0')]:fields.append(dict(name=name,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e])))
cases=0
with (out/'cases.csv').open('w',encoding='utf-8',newline='') as f:
    writer=csv.writer(f);writer.writerow(['load','kind','request','tag','paragraphs','size_word','interrupt_calls','new_segment','passed'])
    for load in (0,0x1000):
        u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x11ee;ds=load+0x2771;frame=ds*16+0x2336;state={}
        def interrupt(uc,n,data):
            assert n==0x21 and uc.reg_read(UC_X86_REG_AH)==0x48 and uc.reg_read(UC_X86_REG_BX)==state['paragraphs']
            k=state['calls'];assert k<len(state['returns']);value,carry=state['returns'][k];state['calls']+=1
            uc.reg_write(UC_X86_REG_AX,value);uc.reg_write(UC_X86_REG_EFLAGS,(uc.reg_read(UC_X86_REG_EFLAGS)&~1)|carry)
        u.hook_add(UC_HOOK_INTR,interrupt)
        def run(request,tag,kind,returns,reset=True,initial_high=0x2000):
            global cases
            size=(request+39)&0xfff0;paragraphs=(size>>4) if size else 4096
            if reset:u.mem_write(frame,b'\0'*12+struct.pack('<HH',tag,0x2000))
            else:u.mem_write(frame+12,struct.pack('<H',tag))
            oldroot=bytes(u.mem_read(frame,16));u.mem_write(ds*16+0x20f8,struct.pack('<H',0x1000));u.mem_write(ds*16+0x20f6,struct.pack('<H',initial_high))
            for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_DI,0x2336),(UC_X86_REG_CX,request),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
            u.mem_write(0x5ff00,struct.pack('<H',0x6000));state.clear();state.update(paragraphs=paragraphs,returns=returns,calls=0)
            u.emu_start(cs*16+0x22e2,cs*16+0x6000,count=500)
            assert state['calls']==len(returns) and u.reg_read(UC_X86_REG_SP)==0xff02 and u.reg_read(UC_X86_REG_ES)==ds and u.reg_read(UC_X86_REG_DI)==0x2336
            newseg,carry=returns[-1]
            if carry:
                assert u.reg_read(UC_X86_REG_EFLAGS)&1 and u.reg_read(UC_X86_REG_DS)==ds and bytes(u.mem_read(frame,16))==oldroot
                assert u.reg_read(UC_X86_REG_AX)==newseg and struct.unpack('<H',u.mem_read(ds*16+0x20f6,2))[0]==initial_high
            else:
                assert not u.reg_read(UC_X86_REG_EFLAGS)&1 and u.reg_read(UC_X86_REG_DS)==newseg and u.reg_read(UC_X86_REG_BX)==0
                h=struct.unpack('<10H',u.mem_read(newseg*16,20));end=(size-2)&65535
                assert h[:6]==(newseg,tag,size,20,20,end) and struct.unpack('<H',u.mem_read(newseg*16+end,2))[0]==0xfffe and struct.unpack('<H',u.mem_read(newseg*16+20,2))[0]==((size-23)&65535)
                root=struct.unpack('<8H',u.mem_read(frame,16));assert root[2:6]==(0,newseg,0,newseg) and root[6:]==(tag,0x2000)
                assert struct.unpack('<H',u.mem_read(ds*16+0x20f6,2))[0]==max(initial_high,newseg)
                if reset:assert root[:2]==(0,newseg) and h[6:]==(0,0,0,0)
                else:
                    first_off,first_seg=struct.unpack('<HH',oldroot[:4]);assert root[:2]==(first_off,first_seg)
                    oldoff,oldseg=struct.unpack('<HH',oldroot[8:12]);assert struct.unpack('<HH',u.mem_read(oldseg*16+oldoff+12,4))==(0,newseg) and h[8:]==(oldoff,oldseg)
            writer.writerow([load,kind,request,tag,paragraphs,size,state['calls'],newseg,True]);cases+=1
        seg=load+0x6000
        for request in range(0xffe9):run(request,3,'fresh',[(seg,0)])
        for tag in (0,65535):
            for request in (0,1,15,16,8192,65512):run(request,tag,'tag_copy',[(seg,0)])
        run(16,3,'append_first',[(seg,0)]);run(32,3,'append_second',[(load+0x7000,0)],False)
        run(16,3,'os_failure',[(8,1)]);run(16,3,'low_segment_retry',[(0x800,0),(seg,0)])
        run(16,3,'high_watermark_unchanged',[(seg,0)],initial_high=0x8000)
with (out/'data_fields.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(fields[0]));w.writeheader();w.writerows(fields)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,typed_field_bytes=10,expected_new_partial_bytes=8,cases=cases,failures=0,request_domain_inclusive=[0,65512],scope='original OS heap helper, block initializer and root append; INT 21h/48h explicitly modeled preserving other registers; no real DOS allocation',natural_os_abi_closed=False,full_malloc_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
