"""python audit_replay_pass1_crt_scan_templates.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
assert b[0x299d2:0x299da]==b' \t-\r]\0]\0'
old=json.loads(inventory.read_text());fmt=Formatter(FormatterSyntax.INTEL);context=[];memset=[]
for r in old:
    if r['cs']!=0x11ee or not (0xed3<=r['ip']<0x1007 or 0x2fb0<=r['ip']<0x2fdd):continue
    raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw
    i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw)
    row=dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i))
    (memset if r['ip']>=0x2fb0 else context).append(row)
fields=[]
for name,a,e,t in [('crt_scan_whitespace_template',0x299d2,0x299d8,'NUL_ASCII_scanset_template_space_TAB_range_CR_close'),('crt_scan_empty_template',0x299d8,0x299da,'NUL_ASCII_scanset_close_only')]:fields.append(dict(name=name,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e])))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x11ee;ds=load+0x2771
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    frame=ds*16+0xff00
    for name,entry,members,cursor in [('whitespace',0xedc,{9,10,11,12,13,32},0x22c6),('empty',0xed3,set(),0x22c8)]:
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_BP,0xff00),(UC_X86_REG_SP,0xf000),(UC_X86_REG_DI,0x73),(UC_X86_REG_CX,0),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.mem_write(frame-0x1a6,b'\0');u.mem_write(frame-0x1a8,b'\0');u.mem_write(frame-0x21,b'Z'+b'\xaa'*32+b'Q')
        u.emu_start(cs*16+entry,cs*16+0x1007,count=3000)
        bitmap=bytes(u.mem_read(frame-0x20,32));expected=bytearray(32)
        for c in members:expected[c//8]|=1<<(c&7)
        assert bitmap==expected and u.mem_read(frame-0x21,1)==b'Z' and u.mem_read(frame,1)==b'Q'
        assert struct.unpack('<H',u.mem_read(frame-0x18c,2))[0]==cursor and u.mem_read(frame-0x1a8,1)[0]==255 and u.reg_read(UC_X86_REG_SP)==0xf000
        cases.append(dict(load_segment=load,template=name,members=' '.join(map(str,sorted(members))),bitmap_hex=bitmap.hex(),bitmap_sha256=sha(bitmap),cursor_at_close=cursor,inversion_byte=255,passed=True))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('scanner_context',context),('memset_instructions',memset),('data_fields',fields),('cases',cases)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=8,cases=len(cases),failures=0,scope='original template selection/bitmap builder and memset; DS=SS, DF=0; stop at 1007 before input loop',scanner_context_instructions=len(context),memset_instructions=len(memset),full_scanner_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
