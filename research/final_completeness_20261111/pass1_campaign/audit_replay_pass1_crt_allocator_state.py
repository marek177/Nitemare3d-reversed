"""python audit_replay_pass1_crt_allocator_state.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,Register,MemorySizeExt,OpKind
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);refs=[];instructions=[]
for r in old:
    raw=bytes.fromhex(r['bytes']);i=Decoder(16,raw,ip=r['ip']).decode()
    if any(i.op_kind(n)==OpKind.MEMORY for n in range(i.op_count)) and i.memory_segment==Register.DS and i.memory_base==Register.NONE and i.memory_index==Register.NONE and 0x232b<=i.memory_displacement<0x2346:
        assert b[r['image_offset']:r['image_offset']+len(raw)]==raw and not i.is_invalid and i.len==len(raw)
        refs.append(dict(ds_offset=i.memory_displacement,width=MemorySizeExt.size(i.memory_size),cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
for i in Decoder(16,b[0x13f45:0x13fde],ip=0x2065):
    assert not i.is_invalid;raw=b[0x11ee0+i.ip:0x11ee0+i.next_ip];assert lookup[(0x11ee,i.ip)]['bytes']==raw.hex()
    instructions.append(dict(cs=0x11ee,ip=i.ip,image_offset=0x11ee0+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
assert instructions[-1]['ip']==0x20fd
fields=[]
for off,width,name,typ,ips in [(0x232d,1,'crt_open_option_byte','BYTE_bitflags_test_80h',[0x1c90]),(0x232e,1,'crt_io_state_byte','BYTE_state_loaded_into_AL',[0xa26]),(0x2330,2,'crt_io_mode_word','WORD_zero_test_state',[0x1bea]),(0x2332,4,'crt_allocation_retry_callback','FAR16_code_pointer_initial_NULL',[0x20eb]),(0x2336,4,'crt_heap_root_pointer','FAR16_data_pointer_initial_NULL',[0x20a2]),(0x233a,4,'crt_heap_cached_pointer','FAR16_data_pointer_initial_NULL',[0x2081,0x209a]),(0x2340,2,'crt_heap_walk_word','WORD_heap_walk_comparison_state',[0x207d]),(0x2344,2,'crt_allocation_control_word','mutable_WORD_initial_2000h_temporarily_0010h',[0x32d2])]:
    a=0x27710+off;e=a+width
    for ip in ips:assert any(r['ds_offset']==off and r['ip']==ip and r['cs']==0x11ee and r['width']==width for r in refs)
    fields.append(dict(name=name,start=a,end_exclusive=e,length=width,type=typ,status='PARTIAL',initial_bytes=b[a:e].hex(),range_sha256=sha(b[a:e])))
assert sum(f['length'] for f in fields)==20
cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x11ee;ds=load+0x2771;callback_seg=load+0x7000;callback=callback_seg*16+0x100;u.mem_write(callback,b'\xcb');state={}
    def hook(uc,a,size,data):
        if a!=callback:return
        arg=struct.unpack('<H',uc.mem_read(0x50000+uc.reg_read(UC_X86_REG_SP)+4,2))[0];assert arg==state['request']
        n=state['calls'];assert n<len(state['returns']);uc.reg_write(UC_X86_REG_AX,state['returns'][n]);state['calls']+=1
    u.hook_add(UC_HOOK_CODE,hook)
    for request in range(0xffe9,0x10000):
        for mode,returns in [('null',[]),('stop',[0]),('retry_once',[1,0])]:
            for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
            u.mem_write(0x5ff00,struct.pack('<HHH',0x6000,cs,request));u.mem_write(ds*16+0x2332,struct.pack('<HH',0,0) if mode=='null' else struct.pack('<HH',0x100,callback_seg));state.clear();state.update(request=request,returns=returns,calls=0)
            u.emu_start(cs*16+0x2065,cs*16+0x6000,count=500)
            assert u.reg_read(UC_X86_REG_AX)==0 and u.reg_read(UC_X86_REG_DX)==0 and state['calls']==len(returns)
            assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DI)==0x9abc
            cases.append(dict(load_segment=load,request=request,callback_mode=mode,callback_calls=state['calls'],return_offset=0,return_segment=0,passed=True))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('data_fields',fields),('consumer_instructions',refs),('allocator_instructions',instructions),('cases',cases)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=20,fields=len(fields),consumer_instructions=len(refs),function_start=0x13f45,function_end_exclusive=0x13fde,instruction_bytes=153,instructions=len(instructions),cases=len(cases),failures=0,scope='original allocator oversized-request rejection path; callback explicitly stubbed; no heap traversal or OS allocation executed',remaining_untyped_in_focus_block=7,heap_allocation_algorithm_closed=False,caller_ds_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
