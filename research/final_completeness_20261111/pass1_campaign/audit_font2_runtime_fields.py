"""python audit_font2_runtime_fields.py IMAGE INVENTORY DECODER UIF RUNTIME WORK OUT"""
import csv,hashlib,json,struct,sys,zlib
from pathlib import Path
image,inventory,dep,uif,runtime,work,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();source=uif.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';assert sha(source)=='d5964c31144a67da8b2524e545488fe243f1394e5e4e231b439284c55276c45d';proof=json.loads((runtime/'independent_verification.json').read_text());assert proof['font2_runtime_verified']
for item in proof['files']:assert sha(Path(item['path']).read_bytes())==item['sha256']
capture=json.loads((runtime/'summary.json').read_text());load=capture['load_segment'];block=(work/'font2_block_runtime.bin').read_bytes();pointers=(work/'font2_pointers_runtime.bin').read_bytes();length,offset=struct.unpack_from('<HI',source,12);raw=source[offset:offset+length];assert (length,offset)==(907,2237)
out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};fmt=Formatter(FormatterSyntax.INTEL);decoded={};todo=[0x16a];rows=[]
while todo:
 ip=todo.pop()
 if ip in decoded:continue
 assert 0x16a<=ip<0x24c;i=Decoder(16,b[0xd290+ip:0xd4dc],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
 if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
 if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
for ip,i in sorted(decoded.items()):
 pos=0xd290+ip;code=b[pos:0xd290+i.next_ip];assert lookup[pos]['bytes']==code.hex();rows.append(dict(cs=0xd29,ip=ip,image_offset=pos,bytes=code.hex(),instruction=fmt.format(i)))
def save(name,rs):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
save('font_group_init',rows);expected=bytearray(raw);q=2;glyphs=[];pointerrows=[]
for n in range(128):
 location=0 if n==0 else q;off,seg=struct.unpack_from('<HH',pointers,n*4);assert (off,seg)==(0x960+location,load+0x20b9)
 pointerrows.append(dict(index=n,ds_offset=0x3a90+n*4,offset=off,segment=seg,image_target=0x214f0+location,status='PARTIAL',scope='actual relocated runtime pointer, no global caller-domain closure'))
 if n==0:continue
 height,width=raw[q:q+2];stride=(width+7)//8;size=height*stride
 for j in range(q+2,q+2+size):expected[j]=int(format(raw[j],'08b')[::-1],2)
 glyphs.append(dict(index=n,resource_relative_start=q,image_start=0x214f0+q,image_end_exclusive=0x214f0+q+2+size,source_file_start=offset+q,height=height,width=width,row_bytes=stride,bitmap_bytes=size,source_bitmap_sha256=sha(raw[q+2:q+2+size]),runtime_bitmap_sha256=sha(block[q+2:q+2+size]),status='PARTIAL',evidence='native loader dimensions/bitreverse and renderer/advance consumers; actual buffer match'))
 q+=2+size
assert q==907 and block==expected+b'\0'*293
save('glyph_records',glyphs);save('runtime_pointer_slots',pointerrows)
atlas=bytearray(160*88)
for g in glyphs:
    base=g['resource_relative_start']+2;ox=(g['index']%16)*10;oy=(g['index']//16)*11
    assert g['width']<=8 and g['height']<=9
    for y in range(g['height']):
        for x in range(g['width']):
            if block[base+y*g['row_bytes']+x//8]&(1<<(x%8)):atlas[(oy+y)*160+ox+x]=255
def chunk(kind,payload):return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
filtered=b''.join(b'\0'+atlas[y*160:(y+1)*160] for y in range(88));png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',160,88,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(filtered))+chunk(b'IEND',b'');(out/'font2_bitmap_atlas.png').write_bytes(png)
contexts=[]
for r in old:
 if (r['cs']==0xd29 and (0xe<=r['ip']<0x30 or 0xcb<=r['ip']<0x107)) or (r['cs']==0x156 and 0x9fe<=r['ip']<0xa3a):
  code=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(code)]==code;i=Decoder(16,code,ip=r['ip']).decode();assert i.len==len(code) and not i.is_invalid;contexts.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=code.hex(),instruction=fmt.format(i)))
save('dimension_consumer_contexts',contexts)
save('runtime_field_intervals',[dict(start=0x214f0,end_exclusive=0x214f2,length=2,type='BYTE2_block_header_values_09_08_semantics_partial',status='PARTIAL'),dict(start=0x214f2,end_exclusive=0x2187b,length=905,type='127_variable_height_width_bitmap_records',status='PARTIAL'),dict(start=0x2187b,end_exclusive=0x219a0,length=293,type='buffer_capacity_tail_zero_observed_not_proven_padding',status='PARTIAL_inherited_buffer_classification')])
directory=[]
for n in range(32):
 count,pos=struct.unpack_from('<HI',source,n*6);assert pos+count<=len(source);directory.append(dict(index=n,length=count,file_offset=pos,payload_end_exclusive=pos+count,runtime_record_hex=(work/'uif_directory_runtime.bin').read_bytes()[n*6:n*6+6].hex(),status='PARTIAL_directory_metadata; unanalysed_payload_semantics'))
save('runtime_uif_directory',directory)
save('external_bss_tables',[dict(name='font2_FAR128_runtime_pointer_table',ds_start=0x3a90,ds_end_exclusive=0x3c90,image_start=0x2b1a0,image_end_exclusive=0x2b3a0,length=512,type='FAR16_pointer128_group2_glyphs',status='PARTIAL',runtime_sha256=sha(pointers),outside_original_file_image=True,original_NONCODE_bytes_added=0)])
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),uif_path=str(uif.resolve()),uif_sha256=sha(source),runtime_proof_sha256=sha((runtime/'independent_verification.json').read_bytes()),functions=[dict(name='font_group_init',start=0xd3fa,end_exclusive=0xd4dc,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows))],group=2,source_resource_index=2,source_offset=offset,source_bytes=length,glyph_records=127,pointer_slots=128,metadata_bytes=256,bitmap_bytes=sum(g['bitmap_bytes'] for g in glyphs),capacity_tail=293,runtime_block_sha256=sha(block),source_block_sha256=sha(raw),runtime_tests=0,new_deep_verified_bytes=0,scope='actual group2 byte-exact source/bitreverse/128pointer capture, native dimension consumers; PARTIAL glyph semantics/caller bounds, session counted separately')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
