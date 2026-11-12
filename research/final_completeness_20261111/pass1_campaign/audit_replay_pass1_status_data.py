"""python audit_replay_pass1_status_data.py IMAGE INVENTORY DECODER EMULATOR MAP_DIR OUT"""
import csv,hashlib,json,struct,sys,re
from pathlib import Path
image,inventory,dep,emu,mapdir,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
fields=[]
def add(n,a,e,t,ips):
    fields.append(dict(name=n,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e]),evidence_ips=';'.join('083D:%04X'%ip for ip in ips)))
assert b[0x28c26:0x28c29]==bytes([100,10,2]);add('secondary_class7_values',0x28c26,0x28c29,'BYTE_array_3_real_MAP_secondary_class7_IDs',[0x212f])
assert b[0x28c2a:0x28c2e]==bytes.fromhex('ffff0000');add('secondary_class7_cached_episode',0x28c2a,0x28c2c,'mutable_WORD_initial_FFFF_episode_cache_key',[0x20fd,0x2103]);add('status_cadence_counter',0x28c2c,0x28c2e,'mutable_WORD_initial_zero_increment_modulo_signed_IDIV20',[0x2520,0x2524])
for n,a,e,raw,ips in [('status_none_text_a',0x28c2e,0x28c33,b'none\0',[0x25e4]),('status_none_text_b',0x28c33,0x28c38,b'none\0',[0x25f5]),('status_none_text_c',0x28c38,0x28c3d,b'none\0',[0x25fe]),('registered_marker',0x28c3d,0x28c3f,b'R\0',[0x2786]),('shareware_marker',0x28c3f,0x28c41,b'S\0',[0x278c]),('status_version',0x28c41,0x28c46,b'V2.0\0',[0x2790])]:
    assert b[a:e]==raw;add(n,a,e,'NUL_ASCII_static_text',ips)
assert b[0x28cc3]==0 and b'\0' not in b[0x28c46:0x28cc3];add('level_status_format',0x28c46,0x28cc4,'NUL_ASCII_status_format',[0x2793,0x279b])
assert sum(f['length'] for f in fields)==157
contexts=[]
for r in old:
    if r['cs']==0x83d and any(a<=r['ip']<e for a,e in [(0x20ed,0x214b),(0x2512,0x2531),(0x25de,0x2616),(0x2762,0x27b0)]):
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw);contexts.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
save('static_contexts',contexts);save('data_fields',fields)
assets=[]
for ep in (1,2,3):
    p=mapdir/('MAP.%d'%ep);raw=p.read_bytes();secondary=raw[258:514];ids=[i for i,c in enumerate(secondary) if c==7];assert ids==[59,60,61]
    assets.append(dict(episode=ep,path=str(p),file_sha256=sha(raw),secondary_sha256=sha(secondary),class7_ids=';'.join(map(str,ids)),relative_indices='0;1;2'))
save('assets',assets);prefix=[]
for i in Decoder(16,b[0xa8f0:0xa8ff],ip=0x2520):
    raw=b[0x83d0+i.ip:0x83d0+i.next_ip];assert lookup[(0x83d,i.ip)]['bytes']==raw.hex();prefix.append(dict(cs=0x83d,ip=i.ip,image_offset=0x83d0+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
assert i.next_ip==0x252f;save('cadence_prefix',prefix);cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x83d
    for oldcounter in (range(65536) if load==0 else [0,18,19,20,32759,32760,32766,32767,32768,65515,65516,65535]):
        value=(oldcounter+1)&65535;signed=value if value<32768 else value-65536;q=abs(signed)//20*(-1 if signed<0 else 1);rem=signed-q*20
        u.mem_write(ds*16+0x151c,struct.pack('<H',oldcounter))
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.emu_start(cs*16+0x2520,cs*16+0x252f,count=100)
        assert struct.unpack('<H',u.mem_read(ds*16+0x151c,2))[0]==value and u.reg_read(UC_X86_REG_AX)==(q&65535) and u.reg_read(UC_X86_REG_DX)==(rem&65535)
        due=bool(u.reg_read(UC_X86_REG_EFLAGS)&0x40);assert due==(rem==0)
        cases.append(dict(load=load,old_counter=oldcounter,new_signed=signed,quotient=q,remainder=rem,due=due,passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=157,fields=len(fields),cases=len(cases),failures=0,prefix_instruction_bytes=15,prefix_instructions=len(prefix),scope='static data consumers and real MAP class7 IDs; original six-instruction cadence prefix replayed; stop before JNE, no callbacks; full UI/status and class7 behavior not executed',natural_class7_domain_closed=False,full_status_closed=False,runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))

