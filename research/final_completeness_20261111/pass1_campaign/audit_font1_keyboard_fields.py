"""python audit_font1_keyboard_fields.py IMAGE UIF RUNTIME WORK OUT"""
import csv,hashlib,json,struct,sys,zlib
from pathlib import Path
image,uif_path,runtime,work,out=map(Path,sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();uif=uif_path.read_bytes();out.mkdir(parents=True,exist_ok=True)
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297' and sha(uif)=='d5964c31144a67da8b2524e545488fe243f1394e5e4e231b439284c55276c45d'
proof=json.loads((runtime/'independent_verification.json').read_text());assert proof['verified'] and proof['font_groups_runtime_verified']==[0,1,2]
for item in proof['files']:assert sha(Path(item['path']).read_bytes())==item['sha256']
load=json.loads((runtime/'summary.json').read_text())['load_segment'];length,offset=struct.unpack_from('<HI',uif,6);assert (length,offset)==(1145,1092)
raw=uif[offset:offset+length];block=(work/'font1_block_runtime.bin').read_bytes();pointers=(work/'font1_pointers_runtime.bin').read_bytes();q=2;glyphs=[];slots=[];expected=bytearray(raw)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for n in range(128):
 pos=0 if n==0 else q;off,seg=struct.unpack_from('<HH',pointers,n*4);assert (off,seg)==(0x4b0+pos,load+0x20b9)
 slots.append(dict(index=n,ds_offset=0x3890+n*4,offset=off,segment=seg,image_target=0x21040+pos,status='PARTIAL'))
 if n==0:continue
 h,w=raw[q:q+2];stride=(w+7)//8;size=h*stride
 for j in range(q+2,q+2+size):expected[j]=int(format(raw[j],'08b')[::-1],2)
 glyphs.append(dict(index=n,source_file_start=offset+q,resource_relative_start=q,image_start=0x21040+q,image_end_exclusive=0x21040+q+2+size,height=h,width=w,row_bytes=stride,bitmap_bytes=size,runtime_bitmap_sha256=sha(block[q+2:q+2+size]),status='PARTIAL'));q+=2+size
assert q==1145 and block==expected+bytes(55) and sum(g['bitmap_bytes'] for g in glyphs)==889
save('glyph_records',glyphs);save('runtime_pointer_slots',slots)
fields=[dict(start=0x21040,end_exclusive=0x21042,length=2,type='header_0B_0B_index0_semantics_partial',status='PARTIAL'),dict(start=0x21042,end_exclusive=0x214b9,length=1143,type='127_height_width_records_254header_889bitmap_bytes',status='PARTIAL'),dict(start=0x214b9,end_exclusive=0x214f0,length=55,type='observed_zero_capacity_tail_not_proven_padding',status='PARTIAL')]
save('runtime_field_intervals',fields);(out/'runtime_field_intervals.json').write_text(json.dumps(fields,indent=2)+'\n')
save('external_bss_tables',[dict(name='font1_FAR128_runtime_pointer_table',ds_start=0x3890,ds_end_exclusive=0x3a90,image_start=0x2afa0,image_end_exclusive=0x2b1a0,length=512,type='FAR16_pointer128_group1_glyphs',status='PARTIAL',runtime_sha256=sha(pointers),outside_original_file_image=True,original_NONCODE_bytes_added=0)])
consumers=[]
for ds,size,role in [(0x34ba,1,'previous_raw_scan_byte_E0_shift_filter'),(0x3f50,2,'game_key_bits_low_and_high_byte'),(0x3f52,4,'saved_original_keyboard_ISR_FAR'),(0x3cd1,1,'conditional_keyboard_drain_flag'),(0x3cd4,2,'mode4_reset_word'),(0x3cd6,2,'input_mode_selector')]:consumers.append(dict(ds_offset=ds,image_start=0x27710+ds,length=size,role=role,outside_original_file_image=True,status='PARTIAL',scope='original ISR dataflow; pointer target and mode owner not fully closed'))
save('irq_consumer_fields',consumers)
stops=json.loads((runtime/'input_stops.json').read_text());rows=[]
for stop in stops:
 p=stop['prefix'];bios=(work/(p+'bios_queue.bin')).read_bytes();reg=stop['registers'];rows.append(dict(stage=stop['stage'],cs=reg['CS'],ip=reg['IP'],ds=reg['DS'],ss=reg['SS'],sp=reg['SP'],ax=reg['AX'],game_flags=int.from_bytes((work/(p+'game_key_flags.bin')).read_bytes(),'little'),previous_scan=(work/(p+'previous_scan.bin')).read_bytes()[0],bios_head=struct.unpack_from('<H',bios)[0],bios_tail=struct.unpack_from('<H',bios,2)[0],bios_first_word=struct.unpack_from('<H',bios,4)[0],status='PARTIAL'))
save('native_keyboard_stages',rows)
atlas=bytearray(224*112)
for g in glyphs:
 assert g['height']<=12 and g['width']<=12;ox=(g['index']%16)*14;oy=(g['index']//16)*14
 for y in range(g['height']):
  for x in range(g['width']):
   if block[g['resource_relative_start']+2+y*g['row_bytes']+x//8]&(1<<(x%8)):atlas[(oy+y)*224+ox+x]=255
def chunk(k,p):return struct.pack('>I',len(p))+k+p+struct.pack('>I',zlib.crc32(k+p)&0xffffffff)
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',224,112,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\0'+atlas[y*224:(y+1)*224] for y in range(112))))+chunk(b'IEND',b'');(out/'font1_bitmap_atlas.png').write_bytes(png)
summary=dict(runtime_scenarios_added=1,source_length=1145,glyph_records=127,pointer_slots=128,bitmap_bytes=889,capacity_tail=55,runtime_bss_table_bytes_added=512,file_backed_buffer_bytes_refined_already_in_pass1=1200,max_height=max(g['height'] for g in glyphs),max_width=max(g['width'] for g in glyphs),header_hex=raw[:2].hex(),native_keyboard_stops=len(rows),irq_entry_stack_segments=[rows[n]['ss'] for n in (1,4)],bios_word=0x3920,port_make=0x39,port_break=0xb9,new_deep_verified_bytes=0,scope='native supported AUTOTYPE through IRQ/BDA/wait and font1 exact source/bitreverse/FAR table; inherited PARTIAL refinement, not full text/input semantics',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,uif_path,runtime/'independent_verification.json',Path(__file__))])
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
