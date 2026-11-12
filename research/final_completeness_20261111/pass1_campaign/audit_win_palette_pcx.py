"""python audit_win_palette_pcx.py WIN_GAME_PAL DOS_GAME_PAL OUT
Strict per-scanline PCX RLE decode with exact input/output boundaries.
"""
import csv,hashlib,json,struct,sys,zlib
from pathlib import Path
win,dos,out=map(Path,sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest();b=win.read_bytes();d=dos.read_bytes();assert sha(b)=='b6b71824a73a74c79e0f3ae12c9a423f2ae500ca956fe156f1f0d4d2307d24fc';assert sha(d)=='efd52442cbee3327d8cec045b31559049e8767b298c25674a557eb6e096a759f';out.mkdir(parents=True,exist_ok=True)
assert b[:4]==bytes([10,5,1,8]);xmin,ymin,xmax,ymax=struct.unpack_from('<4H',b,4);planes=b[65];linebytes=struct.unpack_from('<H',b,66)[0];width=xmax-xmin+1;height=ymax-ymin+1;assert (width,height,planes,linebytes)==(320,200,1,320)
palette_start=len(b)-768;marker=palette_start-1;assert marker==4690 and b[marker]==12
pos=128;pixels=bytearray();rows=[];packets=[]
for y in range(height):
 start=pos;row=bytearray()
 while len(row)<linebytes*planes:
  assert pos<marker;packet_start=pos;tag=b[pos];pos+=1
  if tag&0xc0==0xc0:
   count=tag&63;assert count and pos<marker;value=b[pos];pos+=1
  else:count=1;value=tag
  assert len(row)+count<=linebytes*planes
  packets.append(dict(start=packet_start,end_exclusive=pos,row=y,decoded_column=len(row),count=count,value=value))
  row.extend(bytes([value])*count)
 assert len(row)==320;pixels.extend(row);rows.append(dict(row=y,encoded_start=start,encoded_end_exclusive=pos,encoded_bytes=pos-start,decoded_bytes=len(row),decoded_sha256=sha(row)))
assert pos==marker and len(pixels)==64000
intervals=[dict(start=0,end_exclusive=128,length=128,type='PCX_v5_header',status='PARTIAL',range_sha256=sha(b[:128])),dict(start=128,end_exclusive=marker,length=marker-128,type='PCX_RLE_200_scanlines_320_bytes',status='PARTIAL',range_sha256=sha(b[128:marker])),dict(start=marker,end_exclusive=palette_start,length=1,type='BYTE_0C_256palette_marker',status='PARTIAL',range_sha256=sha(b[marker:palette_start])),dict(start=palette_start,end_exclusive=len(b),length=768,type='RGB_BYTE256x3_palette',status='PARTIAL',range_sha256=sha(b[palette_start:]))]
assert sum(r['length'] for r in intervals)==len(b)
colors=[]
for n in range(256):
 wr,wg,wb=b[palette_start+3*n:palette_start+3*n+3];dr,dg,db=d[-768+3*n:][:3] if n<255 else d[-3:]
 colors.append(dict(index=n,win_r=wr,win_g=wg,win_b=wb,dos_r=dr,dos_g=dg,dos_b=db,equal=(wr,wg,wb)==(dr,dg,db),image_pixel_count=pixels.count(n)))
def save(name,rs):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
for name,rs in [('asset_intervals',intervals),('scanlines',rows),('rle_packets',packets),('palette_comparison',colors)]:save(name,rs)
# Export reconstructed image as PNG; no source image data are modified.
rgb=b''.join(b[palette_start+3*n:palette_start+3*n+3] for n in pixels)
def chunk(kind,payload):return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
filtered=b''.join(b'\0'+rgb[y*960:(y+1)*960] for y in range(height));png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(filtered))+chunk(b'IEND',b'');(out/'reconstructed_win_game_pal.png').write_bytes(png)
s=dict(win_path=str(win.resolve()),win_sha256=sha(b),dos_path=str(dos.resolve()),dos_sha256=sha(d),width=width,height=height,bytes_per_line=linebytes,planes=planes,header_palette_info=struct.unpack_from('<H',b,68)[0],header_reserved=b[64],rle_start=128,rle_end_exclusive=marker,rle_bytes=marker-128,rle_packets=len(packets),scanlines=height,decoded_pixels=len(pixels),decoded_sha256=sha(pixels),marker_offset=marker,palette_start=palette_start,file_bytes=len(b),byte_partition_exact=True,unconsumed_encoded_bytes=0,rows_without_packet_overrun=True,palette_equal_entries=sum(c['equal'] for c in colors),palette_different_bytes=sum(a!=v for a,v in zip(b[-768:],d[-768:])),png_sha256=sha(png),runtime_tests=0,new_deep_verified_bytes=0,scope='actual asset structural decode using ZSoft PCX specification; PARTIAL game semantics, no Win16 executable decoder/runtime parity or original display proof',specification_url='https://www.neperos.com/article/rntibjd550e697a4',specification_attribution='ZSoft Corporation Technical Reference Manual revision5, Dean Ansley; mirrored reproduction')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
