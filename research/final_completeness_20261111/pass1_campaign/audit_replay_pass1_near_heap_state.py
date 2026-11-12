"""python audit_replay_pass1_near_heap_state.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
spec=[(0x20e0,'startup_shifted_limit_WORD_SS_write'),(0x20e2,'startup_stack_segment_WORD_SS_write'),(0x20e6,'startup_aligned_SP_WORD_SS_write'),(0x20e8,'near_heap_lower_bound_WORD'),(0x20ea,'near_heap_minimum_tagged_offset_WORD'),(0x20ec,'startup_sentinel_SP_WORD_SS_write')]
fields=[dict(name=n,start=0x27710+o,end_exclusive=0x27712+o,length=2,type='mutable_WORD_'+n,status='PARTIAL',range_sha256=sha(b[0x27710+o:0x27712+o])) for o,n in spec];save('data_fields',fields)
rows=[];contexts=[]
for r in old:
    if r['cs']==0x11ee and (0x5d<=r['ip']<0x88 or 0x3cae<=r['ip']<0x3ccf):
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw)
        row=dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i));contexts.append(row)
        if r['ip']>=0x3cae:rows.append(row)
assert sum(len(bytes.fromhex(r['bytes'])) for r in rows)==33;save('near_heap_mark_free',rows);save('startup_and_consumer_contexts',contexts)
cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x11ee
    for ptr,floor,minimum,tag in itertools.product((0,1,2,3,0x100,0x1fff,0x2000,0x2001,0x2002,0x4000,0x7fff,0x8000,0xfffe,0xffff),(0,1,2,0x2000,0x8000,0xffff),(0,1,0x2000,0xffff),(0,2,0xfe,0xff)):
        address=(ptr-2)&65535;assert not 0x20e2<=address<0x20ee
        state=bytearray(struct.pack('<HHHHHH',0x4444,5,0x7777,floor,minimum,0x8888));expected=state[:]
        active=ptr>floor;newtag=tag|1 if active else tag
        if active and minimum>address:expected[8:10]=struct.pack('<H',address)
        u.mem_write(ds*16+0x20e2,bytes(state));u.mem_write(ds*16+address,bytes([tag]))
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x3333),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x9876),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
        u.mem_write(0x5ff00,struct.pack('<HHH',0x6000,cs,ptr));u.emu_start(cs*16+0x3cae,cs*16+0x6000,count=100)
        assert bytes(u.mem_read(ds*16+0x20e2,12))==bytes(expected) and u.mem_read(ds*16+address,1)[0]==newtag
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x9876 and u.reg_read(UC_X86_REG_DS)==ds
        cases.append(dict(load=load,pointer=ptr,lower_bound=floor,minimum=minimum,old_tag=tag,new_tag=newtag,new_minimum=struct.unpack('<H',expected[8:10])[0],passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=12,fields=6,functions=[dict(name='near_heap_mark_free',start=0x15b8e,end_exclusive=0x15baf,instruction_bytes=33,instructions=len(rows))],cases=len(cases),failures=0,scope='native near-heap marker with independent SS; startup fields static SS writers only, requires separate DS/SS alias proof; no allocator lifecycle or OS calls',runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
