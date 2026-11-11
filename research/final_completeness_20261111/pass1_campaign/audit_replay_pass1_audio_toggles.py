"""python audit_replay_pass1_audio_toggles.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);instructions=[]
for r in sorted((r for r in old if r['cs']==0x6b0 and 0x6b6<=r['ip']<0x71c),key=lambda r:r['ip']):
    raw=bytes.fromhex(r['bytes']);assert b[0x6b00+r['ip']:0x6b00+r['ip']+len(raw)]==raw
    i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw)
    instructions.append(dict(cs=0x6b0,ip=i.ip,image_offset=0x6b00+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
fields=[]
for off,name,text in [(0xb5f,'music_on',b'Music on\0'),(0xb68,'music_off',b'Music off\0'),(0xb72,'sound_on',b'Sound on\0'),(0xb7b,'sound_off',b'Sound off\0')]:
    a=0x27710+off;assert b[a:a+len(text)]==text
    fields.append(dict(name=name,start=a,end_exclusive=a+len(text),length=len(text),type='NUL_ASCII_UI_status',status='PARTIAL',range_sha256=sha(text)))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x6b0;ds=load+0x2771
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    targets={load*16+0xc532:'stop_dependency',load*16+0xc38c:'audio_dependency_2',load*16+0xac5c:'music_selector',load*16+0xd9b0:'prompt'}
    for a in targets:u.mem_write(a,b'\xcb')
    trace=[]
    def hook(uc,a,size,data):
        if a not in targets:return
        name=targets[a];sp=uc.reg_read(UC_X86_REG_SP);arg=''
        if name=='audio_dependency_2':arg=struct.unpack('<H',uc.mem_read(0x50000+sp+4,2))[0]
        if name=='prompt':arg=struct.unpack('<HH',uc.mem_read(0x50000+sp+4,4));assert arg[1]==ds
        trace.append((name,arg))
    u.hook_add(UC_HOOK_CODE,hook)
    for kind,start,off,on,off_text in [('music',0x6b6,0x414d,0xb5f,0xb68),('sound',0x6fa,0x414e,0xb72,0xb7b)]:
        for before in range(256):
            for r,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_EFLAGS,2)]:u.reg_write(r,v)
            u.mem_write(ds*16+off,bytes([before]));trace.clear();u.emu_start(cs*16+start,cs*16+0x7a0,count=200)
            after=before^1;selected=on if after else off_text
            expected=[]
            if kind=='music' and before:expected.append(('stop_dependency',''))
            expected.append(('audio_dependency_2',2))
            if kind=='music' and after:expected.append(('music_selector',''))
            expected.append(('prompt',(selected,ds)))
            assert trace==expected and u.mem_read(ds*16+off,1)[0]==after and u.reg_read(UC_X86_REG_SP)==0xff00,(load,kind,before,trace,expected)
            cases.append(dict(load_segment=load,kind=kind,before=before,after=after,text_ds_offset=selected,trace=json.dumps(trace)))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('branch_instructions',instructions),('data_fields',fields),('cases',cases)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),branch_entry_ips=[0x6b6,0x6fa],exit_ip=0x7a0,instructions=len(instructions),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in instructions),typed_bytes=sum(r['length'] for r in fields),cases=len(cases),failures=0,scope='two interior dispatcher paths; four dependencies mocked with RETF; flags preserved by mocks',callee_side_effects_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
