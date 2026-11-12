"""python audit_replay_pass1_class44_cache.py IMAGE INVENTORY DECODER EMULATOR MAP_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,mapdir,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
lookup={(r['cs'],r['ip']):r for r in json.loads(inventory.read_text())};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
functions=[]
for name,start,end in [('class_primary_search',4,0x4d),('class44_relative_id',0x176,0x1b5)]:
    todo=[start];decoded={}
    while todo:
        ip=todo.pop()
        if ip in decoded:continue
        assert start<=ip<end;i=Decoder(16,b[0xf70+ip:0xf70+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
        if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
        if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
    rows=[]
    for ip,i in sorted(decoded.items()):
        raw=b[0xf70+ip:0xf70+i.next_ip];assert lookup[(0xf7,ip)]['bytes']==raw.hex();rows.append(dict(cs=0xf7,ip=ip,image_offset=0xf70+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    save(name,rows);functions.append(dict(name=name,start=0xf70+start,end_exclusive=0xf70+end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows)))
assert b[0x2783a:0x2783c]==b'\xff\xff';save('data_fields',[dict(name='class44_cached_episode',start=0x2783a,end_exclusive=0x2783c,length=2,type='mutable_WORD_initial_FFFF_episode_cache_key',status='PARTIAL',range_sha256=sha(b[0x2783a:0x2783c]))])
assets=[];tables={}
for ep in (1,2,3):
    p=mapdir/('MAP.%d'%ep);raw=p.read_bytes();assert len(raw)>=514;classes=raw[2:258];matches=[i for i,v in enumerate(classes) if v==0x44];assert matches and matches==list(range(matches[0],matches[-1]+1));tables[ep]=classes
    assets.append(dict(episode=ep,path=str(p),bytes=len(raw),sha256=sha(raw),header_sha256=sha(raw[:514]),primary_classes_sha256=sha(classes),class44_first=matches[0],class44_last=matches[-1],class44_count=len(matches)))
save('assets',assets);rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0xf7;state={}
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    def hook(uc,a,size,data):
        if a==load*16+0xf74:state['searches']+=1
        assert a!=load*16+0xfbac,'unexpected error path'
    u.hook_add(UC_HOOK_CODE,hook)
    for ep,classes in tables.items():
        first=classes.index(0x44);u.mem_write(ds*16+0xd30e,classes);u.mem_write(ds*16+0x626a,struct.pack('<H',ep))
        for kind in ('cache_miss','cache_hit','seeded_stale_base'):
            for tile in range(256):
                key=65535 if kind=='cache_miss' else ep;base=first if kind=='cache_hit' else 255
                u.mem_write(ds*16+0x12a,struct.pack('<H',key));u.mem_write(ds*16+0x2650,bytes([base]));u.mem_write(0x61000,bytes([tile]));state['searches']=0
                for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
                u.mem_write(0x5ff00,struct.pack('<HHHH',0x6000,cs,0x1000,0x6000));u.emu_start(cs*16+0x176,cs*16+0x6000,count=5000)
                newbase=first if kind=='cache_miss' else base;expected=(tile-newbase)&65535 if classes[tile]==0x44 else 65535
                actual=u.reg_read(UC_X86_REG_AX);assert actual==expected and state['searches']==int(kind=='cache_miss')
                assert bytes(u.mem_read(ds*16+0x2650,1))==bytes([newbase]) and struct.unpack('<H',u.mem_read(ds*16+0x12a,2))[0]==ep
                assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_DS)==ds
                cases.append(dict(load=load,episode=ep,kind=kind,tile=tile,tile_class=classes[tile],base=newbase,result=actual,search_calls=state['searches'],passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,typed_bytes=2,cases=len(cases),failures=0,assets=assets,scope='original relative-ID function and native class search; real MAP primary class bytes seeded; no mocks; not natural file I/O or all search error cases',search_missing_class_replayed=False,natural_cache_invariant_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
