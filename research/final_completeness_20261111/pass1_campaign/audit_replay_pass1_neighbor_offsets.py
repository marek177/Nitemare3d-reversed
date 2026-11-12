"""python audit_replay_pass1_neighbor_offsets.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
lookup={(r['cs'],r['ip']):r for r in json.loads(inventory.read_text())};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
table=struct.unpack('<8b',b[0x27f32:0x27f3a]);assert table==(-64,1,1,64,64,-1,-1,-64)
prefixes=[('neighbor_address_0000_070A',0,0x70a,0x723,'AX_DX'),('neighbor_address_0000_097F',0,0x97f,0x98c,'AX_ES'),('neighbor_address_083D_0D20',0x83d,0xd20,0xd35,'BX_ES'),('neighbor_address_083D_2074',0x83d,0x2074,0x2087,'AX_DX')];rows=[];scopes=[]
for name,cs,start,end,result in prefixes:
    items=[]
    for i in Decoder(16,b[cs*16+start:cs*16+end],ip=start):
        assert not i.is_invalid;raw=b[cs*16+i.ip:cs*16+i.next_ip];assert lookup[(cs,i.ip)]['bytes']==raw.hex()
        items.append(dict(cs=cs,ip=i.ip,image_offset=cs*16+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
    assert i.next_ip==end;rows.extend(items);scopes.append(dict(name=name,start=cs*16+start,end_exclusive=cs*16+end,instruction_bytes=end-start,instructions=len(items),scope='interior prefix only; stop before next instruction, not full function'))
def save(name,items):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
save('instructions',rows);save('data_fields',[dict(name='facing_neighbor_cell_delta',start=0x27f32,end_exclusive=0x27f3a,length=8,type='signed_BYTE_array_8_used_as_WORD_cell_delta',status='PARTIAL',range_sha256=sha(b[0x27f32:0x27f3a]))])
cases=[];rel=list(csv.DictReader((image.parent/'relocations.csv').open()))
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    for (name,seg,start,end,result),index,base in itertools.product(prefixes,list(range(9))+[0x7f,0x80,0xff,0xfffe,0xffff],(0,1,0x7fff,0xffff)):
        cs=seg+load
        u.mem_write(ds*16+0x4158,struct.pack('<H',index));u.mem_write(ds*16+0x417c,struct.pack('<HH',base,0x6000))
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_ES,0x6000),(UC_X86_REG_DI,base),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        source_offset=(0x822+index)&65535;v=bytes(u.mem_read(ds*16+source_offset,1))[0];signed=v-256 if v&128 else v;expected=(base+signed*2)&65535
        u.emu_start(cs*16+start,cs*16+end,count=100)
        actual=u.reg_read(UC_X86_REG_BX if result=='BX_ES' else UC_X86_REG_AX);segment=u.reg_read(UC_X86_REG_DX if result=='AX_DX' else UC_X86_REG_ES)
        assert actual==expected and segment==0x6000 and u.reg_read(UC_X86_REG_SP)==0xff00 and u.reg_read(UC_X86_REG_DS)==ds
        if index<8:assert signed==table[index]
        cases.append(dict(load=load,prefix=name,index=index,in_declared_table=index<8,base_offset=base,source_offset=source_offset,source_signed_byte=signed,result_offset=actual,result_segment=segment,passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),prefixes=scopes,prefix_instruction_bytes=sum(x['instruction_bytes'] for x in scopes),prefix_instructions=len(rows),typed_bytes=8,cases=len(cases),failures=0,scope='four original interior address prefixes; no mocks; no target dereference; index and near offset overflow seeded; not whole functions',index_domain_closed=False,all_callers_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
