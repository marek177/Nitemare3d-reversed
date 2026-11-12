"""python audit_replay_pass1_rng.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
assert b[0x29bc8:0x29bcc]==b'\x01\0\0\0'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);functions=[]
out.mkdir(parents=True,exist_ok=True)
spec=[('crt_srand_word',0x11ee,0x31e6,0x31f7),('crt_rand_lcg',0x11ee,0x31f8,0x3220),('compiler_mul32_low',0x11ee,0x3ad8,0x3b0a),('game_rand_wrapper',0xfba,0x1a0,0x1a6),('game_fixed_seed_wrapper',0xfba,0x1a6,0x1b1),('damage_rng_prefix',0x83d,0x1c0,0x1ea)]
for name,cs,a,e in spec:
    rows=[]
    for i in Decoder(16,b[cs*16+a:cs*16+e],ip=a):
        assert not i.is_invalid;raw=b[cs*16+i.ip:cs*16+i.next_ip];assert lookup[(cs,i.ip)]['bytes']==raw.hex()
        rows.append(dict(cs=cs,ip=i.ip,image_offset=cs*16+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    if name!='damage_rng_prefix':functions.append(dict(name=name,start=cs*16+a,end_exclusive=cs*16+e,instruction_bytes=e-a,instructions=len(rows)))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=0;rand_cases=0;mul_cases=0
targets={'0x%x, 0x%x'%(cs,a):name for name,cs,a,e in spec if name!='damage_rng_prefix'};callers=[]
for r in old:
    if r['mnemonic']!='lcall' or r['operands'] not in targets:continue
    raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw
    i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw)
    callers.append(dict(target=targets[r['operands']],cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
with (out/'direct_far_callers.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(callers[0]));w.writeheader();w.writerows(callers)
sequences=[0,1,2,0x7fff,0x8000,0xffff,0x10000,0x10001,0x7fffffff,0x80000000,0xffffffff,0xfffffffe,0x12345678,0x9abcdef0,0x55555555,0xaaaaaaaa]
with (out/'cases.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f);w.writerow(['load_segment','kind','seed_or_initial_state','step','state_after','rand_ax'])
    for load in (0,0x1000):
        u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771
        for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
        for reg,val in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        def run(cs,ip,args=(),callee_pop=0):
            cs+=load;u.reg_write(UC_X86_REG_CS,cs);u.reg_write(UC_X86_REG_SP,0xff00);u.mem_write(0x5ff00,struct.pack('<'+'H'*(2+len(args)),0x4000,cs,*args));u.emu_start(cs*16+ip,cs*16+0x4000,count=300)
            assert u.reg_read(UC_X86_REG_SP)==0xff04+callee_pop and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DI)==0x9abc
        def rand(expected):
            run(0xfba,0x1a0);state=struct.unpack('<I',u.mem_read(ds*16+0x24b8,4))[0];value=u.reg_read(UC_X86_REG_AX)
            assert state==expected and value==((expected>>16)&0x7fff)
            return value
        for seed in range(65536):
            run(0x11ee,0x31e6,(seed,));assert struct.unpack('<I',u.mem_read(ds*16+0x24b8,4))[0]==seed
            expected=(seed*214013+2531011)&0xffffffff;value=rand(expected);w.writerow([load,'srand_first',seed,1,expected,value]);cases+=1;rand_cases+=1
        for initial in sequences:
            state=initial;u.mem_write(ds*16+0x24b8,struct.pack('<I',state))
            for step in range(1,129):
                state=(state*214013+2531011)&0xffffffff;value=rand(state);w.writerow([load,'sequence',initial,step,state,value]);cases+=1;rand_cases+=1
        operands=[0,1,2,0xffff,0x10000,0x7fffffff,0x80000000,0xffffffff,0x12345678]
        for left in operands:
            for right in operands:
                u.reg_write(UC_X86_REG_BX,0xabcd);run(0x11ee,0x3ad8,(left&65535,left>>16,right&65535,right>>16),8)
                actual=(u.reg_read(UC_X86_REG_DX)<<16)|u.reg_read(UC_X86_REG_AX);expected=(left*right)&0xffffffff
                assert actual==expected and u.reg_read(UC_X86_REG_BX)==0xabcd
                w.writerow([load,'multiply',str(left)+':'+str(right),0,actual,'']);cases+=1;mul_cases+=1
        u.mem_write(ds*16+0x24b8,b'\xff'*4);run(0xfba,0x1a6);assert struct.unpack('<I',u.mem_read(ds*16+0x24b8,4))[0]==1;w.writerow([load,'fixed_reset',0xffffffff,0,1,'']);cases+=1
field=dict(name='crt_rng_state',start=0x29bc8,end_exclusive=0x29bcc,length=4,type='mutable_DWORD_LCG_state_initial_1',status='PARTIAL',range_sha256=sha(b[0x29bc8:0x29bcc]))
with (out/'data_fields.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(field));w.writeheader();w.writerow(field)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,typed_bytes=4,cases=cases,rand_calls_verified=rand_cases,multiply_cases=mul_cases,full_word_seed_domain=65536,arbitrary_state_sequences=16,sequence_steps=128,failures=0,cases_sha256=sha((out/'cases.csv').read_bytes()),scope='original srand, rand, multiplication and wrappers; no mocked callees; seeded DS and states; no natural game scheduling',natural_seed_sources_closed=False,full_damage_algorithm_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
