"""python audit_replay_map_level_loader.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR GAME_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,game,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);instructions=[]
for i in Decoder(16,b[0x285c:0x28f8],ip=0xec):
    assert not i.is_invalid;raw=b[0x2770+i.ip:0x2770+i.next_ip];assert lookup[(0x277,i.ip)]['bytes']==raw.hex()
    instructions.append(dict(cs=0x277,ip=i.ip,image_offset=0x2770+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
assert instructions[-1]['ip']==0x187
assets={}
for ep in (1,2,3):
    p=game/('MAP.%d'%ep);data=p.read_bytes();n=struct.unpack_from('<H',data)[0];assert len(data)==514+n*8192;assets[ep]=(data,n,str(p))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];events=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x277;ds=load+0x2771
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    targets={load*16+0x13b52:'open',load*16+0x13ab6:'seek',load*16+0xfc3e:'read',load*16+0xfbac:'error',load*16+0x13a96:'close'}
    for a in targets:u.mem_write(a,b'\xcb')
    state={}
    def hook(uc,a,size,data):
        if a not in targets:return
        name=targets[a];sp=uc.reg_read(UC_X86_REG_SP);stack=bytes(uc.mem_read(0x50000+sp+4,12));args=struct.unpack('<6H',stack)
        state['trace'].append(name)
        if name=='error':raise AssertionError(('unexpected error',state['episode'],state['level'],args))
        if name=='open':
            assert args==(0x627c,0x8000,*args[2:]);uc.reg_write(UC_X86_REG_AX,7)
        elif name=='seek':
            handle,lo,hi,whence=args[:4];offset=lo+(hi<<16);assert handle==7 and whence==0
            state['offset']=offset;uc.reg_write(UC_X86_REG_AX,lo);uc.reg_write(UC_X86_REG_DX,hi)
        elif name=='read':
            handle,off,seg,count=args[:4];assert handle==7 and count==8192 and (off,seg)==(0x373e,load+0x21fd)
            payload=state['asset'][state['offset']:state['offset']+count];assert len(payload)==count
            uc.mem_write(seg*16+off,payload);uc.reg_write(UC_X86_REG_AX,count)
        elif name=='close':assert args[0]==7
    u.hook_add(UC_HOOK_CODE,hook)
    for ep,(asset,n,path) in assets.items():
        for level in range(n):
            for r,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_SI,0x5678),(UC_X86_REG_EFLAGS,2)]:u.reg_write(r,v)
            u.mem_write(0x5ff00,struct.pack('<HH',0x4000,cs));u.mem_write(ds*16+0xd30c,struct.pack('<H',n));u.mem_write(ds*16+0x626c,struct.pack('<h',level))
            state.clear();state.update(episode=ep,level=level,asset=asset,trace=[])
            u.emu_start(cs*16+0xec,cs*16+0x4000,count=300)
            expected=asset[514+level*8192:514+(level+1)*8192];actual=bytes(u.mem_read(load*16+0x2570e,8192))
            assert actual==expected and state['offset']==514+level*8192 and state['trace']==['open','seek','read','close'],(load,ep,level,state.get('offset'),state['trace'],sha(actual),sha(expected))
            assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DS)==ds
            cases.append(dict(load_segment=load,episode=ep,level=level,declared_levels=n,offset=state['offset'],payload_sha256=sha(actual),trace=' '.join(state['trace']),passed=True))
guards=[]
for count in (10,11):
    for level in (-32768,-1,0,9,10,11,32767):
        guards.append(dict(level=level,count=count,signed_upper_guard_passes=level<count,signed_seek_offset=514+level*8192,method='static instruction semantics; not additional replay case'))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('instructions',instructions),('cases',cases),('guard_boundary_model',guards),('assets',[dict(episode=ep,path=p,length=len(a),sha256=sha(a),levels=n) for ep,(a,n,p) in assets.items()])]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),function_start=0x285c,function_end_exclusive=0x28f8,instruction_bytes=156,instructions=len(instructions),cases=len(cases),failures=0,scope='original loader instructions; open/seek/read/close/error explicitly mocked; actual MAP payloads copied by mock read',negative_levels_replayed=False,natural_runtime_tests=0,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
