"""python audit_replay_pass1_literal_consumers.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,json,struct,sys,itertools
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
spec=[(0x349,0x277,0x52c,'diagnostic_argument'),(0x3e9,0x277,0x59c,'conditional_diagnostic_argument'),(0x3ee,0x277,0x5a2,'conditional_diagnostic_argument'),(0x598,0x277,0xca9,'path_suffix_open'),(0x5d2,0x277,0xd0b,'path_suffix_open'),(0x64b,0x277,0x1612,'CRT_stream_mode'),(0x6bd,0x277,0x180e,'CRT_stream_mode'),(0x6c0,0x277,0x1811,'CRT_stream_filename'),(0x7e9,0x430,0x398,'CRT_stream_mode'),(0x1d55,0xd29,0x10da,'integer_scan_format'),(0x1d1f,0xd29,0x111c,'integer_scan_format'),(0x1d3a,0xd29,0x114c,'integer_scan_format'),(0x1d8b,0xd29,0x11c6,'decimal_scan_format'),(0x1d70,0xd29,0x1204,'decimal_scan_format'),(0x1dbe,0xd29,0x12c9,'formatted_string_output'),(0x1e42,0xd29,0x165c,'character_printf_format')]
fields=[];contexts=[]
for off,cs,ip,role in spec:
    ref=next(r for r in old if r['cs']==cs and r['ip']==ip)
    assert bytes.fromhex(ref['bytes'])[-2:]==struct.pack('<H',off)
    a=0x27710+off;e=b.index(0,a)+1
    fields.append(dict(name=role+'_'+hex(off),start=a,end_exclusive=e,length=e-a,type='NUL_ASCII_'+role,status='PARTIAL',range_sha256=sha(b[a:e]),text=b[a:e-1].decode('ascii'),reference_cs=cs,reference_ip=ip))
    for r in old:
        if r['cs']==cs and ip-8<=r['ip']<ip+35:
            raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert i.len==len(raw) and not i.is_invalid
            contexts.append(dict(field_offset=off,cs=cs,ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
save('data_fields',fields);save('consumer_contexts',contexts)
rows=[]
for r in old:
    if r['cs']==0x277 and 0xc20<=r['ip']<0xc6e:
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert i.len==len(raw) and not i.is_invalid
        rows.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
assert sum(len(bytes.fromhex(r['bytes'])) for r in rows)==0x4e;save('config_path_concat',rows)
cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x277
    for prefix,off in itertools.product((b'',b'C:\\',b'C:\\N3D\\',b'NO_SEPARATOR',bytes(range(65,96)),b'x'*127,b'y'*255),(0x598,0x5d2)):
        suffix=b[0x27710+off:b.index(0,0x27710+off)+1];expected=prefix+suffix
        u.mem_write(ds*16+0x3cdc,prefix+b'\0');u.mem_write(ds*16+0x3466,b'\xa5'*(len(expected)+2))
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x3333),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x9876),(UC_X86_REG_DI,0x8765),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
        u.mem_write(0x5ff00,struct.pack('<HHH',0x6000,cs,off));u.emu_start(cs*16+0xc20,cs*16+0x6000,count=3000)
        assert bytes(u.mem_read(ds*16+0x3466,len(expected)+2))==expected+b'\xa5\xa5'
        assert u.reg_read(UC_X86_REG_AX)==0x3466 and u.reg_read(UC_X86_REG_ES)==ds and u.reg_read(UC_X86_REG_DS)==ds
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x9876 and u.reg_read(UC_X86_REG_DI)==0x8765
        cases.append(dict(load=load,prefix_hex=prefix.hex(),suffix_offset=off,result_hex=expected.hex(),passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=sum(f['length'] for f in fields),fields=len(fields),context_rows=len(contexts),functions=[dict(name='config_path_concat',start=0x3390,end_exclusive=0x33de,instruction_bytes=78,instructions=len(rows))],cases=len(cases),failures=0,scope='16 literal consumer paths static; native path concatenation with DF0, nonoverlapping seeded buffers, no OS/file I/O or original CRT formatter execution',runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
