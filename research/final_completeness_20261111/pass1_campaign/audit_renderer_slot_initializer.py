"""python audit_renderer_slot_initializer.py IMAGE INVENTORY DECODER EMULATOR VERSIONS OUT"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,versions,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
raw=bytes.fromhex('bbf250c6070183c31281fbfa5772f4cb');assert b[0x201a:0x202a]==raw
old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};fmt=Formatter(FormatterSyntax.INTEL);rows=[];p=0x201a
for i in Decoder(16,raw,ip=0xa):
 assert not i.is_invalid and lookup[p]['bytes']==b[p:p+i.len].hex()
 rows.append(dict(cs=0x201,ip=i.ip,image_offset=p,bytes=b[p:p+i.len].hex(),instruction=fmt.format(i)));p+=i.len
assert p==0x202a and len(rows)==6
caller=lookup[0x4888];assert caller['bytes']=='9a0a000102' # 0476:0128
out.mkdir(parents=True,exist_ok=True)
def save(name,rs):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
save('renderer_slot_byte_init',rows);cases=[];writes=[]
for load,df,cf,seed in itertools.product((0,0x1000),(0,1),(0,1),range(8)):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0x201
 start=0x50f2;end=0x57fa;initial=bytes(((n*73+seed*31)&255) for n in range(end-start+2));expected=bytearray(initial)
 for n in range(100):expected[1+n*18]=1
 u.mem_write(ds*16+start-1,initial);u.mem_write(0x5ff00,struct.pack('<HH',0x6000,cs));actual=[]
 u.hook_add(UC_HOOK_MEM_WRITE,lambda uc,access,address,size,value,user:actual.append((address,size,value)))
 preserved={UC_X86_REG_AX:0x1234,UC_X86_REG_CX:0x2345,UC_X86_REG_DX:0x3456,UC_X86_REG_SI:0x4567,UC_X86_REG_DI:0x5678,UC_X86_REG_BP:0x6789,UC_X86_REG_ES:0x7777}
 for reg,val in list(preserved.items())+[(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_EFLAGS,2|(df<<10)|cf)]:u.reg_write(reg,val)
 u.emu_start(cs*16+0xa,cs*16+0x6000,count=1000)
 wanted=[(ds*16+start+n*18,1,1) for n in range(100)]
 assert actual==wanted and bytes(u.mem_read(ds*16+start-1,len(initial)))==bytes(expected)
 assert all(u.reg_read(reg)==v for reg,v in preserved.items()) and u.reg_read(UC_X86_REG_BX)==end and u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SP)==0xff04
 flags=u.reg_read(UC_X86_REG_EFLAGS);assert flags&0x41==0x40 and bool(flags&0x400)==bool(df)
 cases.append(dict(load=load,DF=df,initial_CF=cf,seed=seed,writes=100,first_offset=start,last_offset=end-18,final_BX=end,passed=True))
save('cases',cases);cross=[]
for label in ('10','11','12','15','17','18','19','20'):
 f=versions/('N3D-'+label)/'unpacked_image.bin';vb=f.read_bytes();matches=[];a=0
 while True:
  a=vb.find(raw,a)
  if a<0:break
  matches.append(a);a+=1
 structural=[]
 for q in range(len(vb)-15):
  if vb[q]==0xbb and vb[q+3:q+11]==raw[3:11] and vb[q+13:q+16]==raw[13:16]:
   lo=struct.unpack_from('<H',vb,q+1)[0];hi=struct.unpack_from('<H',vb,q+11)[0]
   if hi>lo and (hi-lo)%18==0:structural.append(dict(image_offset=q,ds_start=lo,ds_end=hi,slots=(hi-lo)//18))
 cross.append(dict(version=label,path=str(f),image_sha256=sha(vb),exact_matches=len(matches),image_offsets=';'.join('%X'%a for a in matches),normalized_candidates=json.dumps(structural,sort_keys=True),scope='two address immediates normalized; DS identity, natural caller and other version behavior not proved'))
save('cross_version_exact_matches',cross)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=[dict(name='renderer_slot_byte_init',start=0x201a,end_exclusive=0x202a,instruction_bytes=16,instructions=6)],cases=len(cases),failures=0,cases_sha256=sha((out/'cases.csv').read_bytes()),versions=len(cross),unique_version_images=len({x['image_sha256'] for x in cross}),bss_stride=18,bss_nominal_slots=100,bytes_written_per_call=100,bss_first_image=0x2c802,bss_nominal_end_image=0x2cf0a,original_NONCODE_bytes_added=0,runtime_tests=0,new_deep_verified_bytes=0,scope='native bounded one-BYTE-per-18B-slot initializer; nominal envelope not a fully typed 1800B record table; seeded replay not natural runtime; exact cross-version match not behavior parity')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
