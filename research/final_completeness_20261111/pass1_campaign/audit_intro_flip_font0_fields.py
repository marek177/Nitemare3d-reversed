"""python audit_intro_flip_font0_fields.py IMAGE UIF GAMEPAL CD FLIP_OUT FLIP_WORK FONT_OUT FONT_WORK OUT"""
import csv,hashlib,json,re,struct,sys,zlib,urllib.request
from pathlib import Path
image,uif_path,pal_path,cd_path,flip,fw,font,gw,out=map(Path,sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest();out.mkdir(parents=True,exist_ok=True)
b=image.read_bytes();uif=uif_path.read_bytes();gamepal=pal_path.read_bytes();cd=cd_path.read_bytes()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297' and sha(uif)=='d5964c31144a67da8b2524e545488fe243f1394e5e4e231b439284c55276c45d'
assert sha(gamepal)=='efd52442cbee3327d8cec045b31559049e8767b298c25674a557eb6e096a759f' and sha(cd)=='af574568089f1998ca50ceeba310ff068c728279ff470cd39f47a8919228b95a'
proofs=[]
for runtime in (flip,font):
 p=json.loads((runtime/'independent_verification.json').read_text());assert p['optional_intro_display_branch_verified'] and p['used_pixel_dac6_matches_cd']
 for item in p['files']:assert sha(Path(item['path']).read_bytes())==item['sha256']
 proofs.append(p)
assert proofs[0]['latched_display_start']==0 and proofs[1]['latched_display_start']==0x4000 and proofs[1]['font0_runtime_verified']
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
load=json.loads((font/'summary.json').read_text())['load_segment'];length,offset=struct.unpack_from('<HI',uif,0);assert (length,offset)==(900,192)
raw=uif[offset:offset+length];block=(gw/'font0_block_runtime.bin').read_bytes();pointer=(gw/'font0_pointers_runtime.bin').read_bytes();q=2;expected=bytearray(raw);glyphs=[];slots=[]
for n in range(128):
 pos=0 if n==0 else q;off,seg=struct.unpack_from('<HH',pointer,n*4);assert (off,seg)==(pos,load+0x20b9)
 slots.append(dict(index=n,ds_offset=0x3690+4*n,offset=off,segment=seg,image_target=0x20b90+pos,status='PARTIAL',scope='actual natural FAR pointer; caller-domain closure pending'))
 if n==0:continue
 height,width=raw[q:q+2];stride=(width+7)//8;size=height*stride
 for j in range(q+2,q+2+size):expected[j]=int(format(raw[j],'08b')[::-1],2)
 glyphs.append(dict(index=n,source_file_start=offset+q,resource_relative_start=q,image_start=0x20b90+q,image_end_exclusive=0x20b90+q+2+size,height=height,width=width,row_bytes=stride,bitmap_bytes=size,source_bitmap_sha256=sha(raw[q+2:q+2+size]),runtime_bitmap_sha256=sha(block[q+2:q+2+size]),status='PARTIAL'))
 q+=2+size
assert q==900 and block==expected+bytes(300) and sum(g['bitmap_bytes'] for g in glyphs)==644
save('glyph_records',glyphs);save('runtime_pointer_slots',slots)
save('runtime_field_intervals',[dict(start=0x20b90,end_exclusive=0x20b92,length=2,type='header_values_06_07_index0_semantics_partial',status='PARTIAL'),dict(start=0x20b92,end_exclusive=0x20f14,length=898,type='127_height_width_bitmap_records_254_header_644_bitmap_bytes',status='PARTIAL'),dict(start=0x20f14,end_exclusive=0x21040,length=300,type='observed_zero_capacity_tail_not_proven_padding',status='PARTIAL')])
(out/'runtime_field_intervals.json').write_text(json.dumps(list(csv.DictReader((out/'runtime_field_intervals.csv').open())),indent=2)+'\n')
save('external_bss_tables',[dict(name='font0_FAR128_runtime_pointer_table',ds_start=0x3690,ds_end_exclusive=0x3890,image_start=0x2ada0,image_end_exclusive=0x2afa0,length=512,type='FAR16_pointer128_group0_glyphs',status='PARTIAL',runtime_sha256=sha(pointer),outside_original_file_image=True,original_NONCODE_bytes_added=0)])
def png(name,width,height,data,channels,palette=None):
 def chunk(k,p):return struct.pack('>I',len(p))+k+p+struct.pack('>I',zlib.crc32(k+p)&0xffffffff)
 row=width*channels;filtered=b''.join(b'\0'+data[y*row:(y+1)*row] for y in range(height));content=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,3 if palette else 0,0,0,0))
 if palette:content+=chunk(b'PLTE',palette)
 (out/name).write_bytes(content+chunk(b'IDAT',zlib.compress(filtered))+chunk(b'IEND',b''))
atlas=bytearray(160*80)
for g in glyphs:
 assert g['height']<=8 and g['width']<=8;ox=(g['index']%16)*10;oy=(g['index']//16)*10
 for y in range(g['height']):
  for x in range(g['width']):
   if block[g['resource_relative_start']+2+y*g['row_bytes']+x//8]&(1<<(x%8)):atlas[(oy+y)*160+ox+x]=255
png('font0_bitmap_atlas.png',160,80,atlas,1)
planes=[(gw/('vga_plane_%d.bin'%p)).read_bytes() for p in range(4)];pixels=bytes(planes[n%4][n//4] for n in range(64000));assert sha(pixels)==proofs[1]['asset_pixels_sha256']
dac=(gw/'palette_buffer_runtime.bin').read_bytes();assert dac==bytes(v>>2 for v in gamepal[-768:])
colors=[];used=set(pixels)
for n in range(256):
 raw_cd=cd[-768+n*3:len(cd)-768+n*3+3] if n<255 else cd[-3:]
 raw_game=gamepal[-768+n*3:len(gamepal)-768+n*3+3] if n<255 else gamepal[-3:]
 actual=dac[n*3:n*3+3];expect=bytes(v>>2 for v in raw_cd);assert len(raw_cd)==len(raw_game)==len(actual)==3
 colors.append(dict(index=n,used_pixel_count=pixels.count(n),cd_rgb8=raw_cd.hex(),game_rgb8=raw_game.hex(),actual_dac_rgb6=actual.hex(),cd_quantized_rgb6=expect.hex(),equal_at6bit=actual==expect,status='PARTIAL',scope='actual emulator DAC at paused endpoint; no physical monitor gamma'))
assert sum(row['used_pixel_count'] for row in colors)==64000 and [c['index'] for c in colors if not c['equal_at6bit']]==[255] and colors[255]['used_pixel_count']==0
save('palette_entries',colors);rgb6=bytes(dac[index*3+c] for index in pixels for c in range(3));expected_rgb6=bytes(cd[len(cd)-768+index*3+c]>>2 for index in pixels for c in range(3));assert rgb6==expected_rgb6
png('runtime_page_dac6_reconstruction.png',320,200,pixels,1,bytes(v*255//63 for v in dac))
states=[]
for name,runtime in [('after_immediate_flip',flip),('after_font0_before_wait',font)]:
 state=json.loads((runtime/'vga_state.json').read_text());mode='\n'.join(state['MODE']);display=int(re.search(r'\bdisp-start=([0-9a-f]+)h',mode).group(1),16);real=int(re.search(r'\breal-start=([0-9a-f]+)h',mode).group(1),16)
 states.append(dict(stage=name,programmed_display_start=display,latched_real_start=real,programmed_page_segment=0xa400,latched_page_segment=0xa000 if real==0 else 0xa400,source_sha256=sha((runtime/'vga_state.json').read_bytes()),status='PARTIAL',scope='separate natural runs to successive stops, not a continuous sampled scanout trace'))
save('display_start_stages',states)
url='https://raw.githubusercontent.com/joncampbell123/dosbox-x/dosbox-x-v2026.10.01/src/hardware/vga_draw.cpp';reference=out/'dosbox_vga_draw_reference.cpp'
if not reference.exists():reference.write_bytes(urllib.request.urlopen(url,timeout=30).read())
reference_bytes=reference.read_bytes();assert sha(reference_bytes)=='bfab8185fe66b3a3583e4b12be35c8a3e0a8224f690dc14e3d3d1bac07776d6f';lines=reference_bytes.decode('utf-8').splitlines();latch=[n for n,line in enumerate(lines,1) if 'vga.config.real_start = vga.config.display_start & vga.mem.memmask;' in line];draw=[n for n,line in enumerate(lines,1) if 'vga.draw.address = vga.config.real_start;' in line];assert len(latch)==len(draw)==1
source_manifest=dict(url=url,sha256=sha(reference_bytes),bytes=len(reference_bytes),line_display_start_latch=latch[0],line_draw_address=draw[0],scope='official matching release source, separate from captured executable; two field assignments support interpretation, not build equivalence')
(out/'source_manifest.json').write_text(json.dumps(source_manifest,indent=2)+'\n')
summary=dict(runtime_scenarios_added=2,functions_added=0,source_length=900,glyph_records=127,pointer_slots=128,bitmap_bytes=644,capacity_tail=300,selected_group=0,max_height=max(g['height'] for g in glyphs),max_width=max(g['width'] for g in glyphs),header_hex=raw[:2].hex(),runtime_bss_bytes_added_outside_file=512,file_backed_noncode_bytes_refined=1200,used_palette_entries=len(used),raw_palette_component_differences=sum(a!=z for a,z in zip(cd[-768:],gamepal[-768:])),quantized_palette_component_differences=sum((a>>2)!=(z>>2) for a,z in zip(cd[-768:],gamepal[-768:])),used_pixel_rgb6_component_differences=0,quantized_frame_rgb6_sha256=sha(rgb6),new_deep_verified_bytes=0,scope='font0 natural buffer/pointers and display-start+DAC state refinement; all PARTIAL, no full host scanout, physical VGA or Win16 parity',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,uif_path,pal_path,cd_path,flip/'independent_verification.json',font/'independent_verification.json',Path(__file__))])
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
