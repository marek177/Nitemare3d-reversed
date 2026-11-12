"""python audit_scheduler_runtime_fields.py IMAGE RUNTIME WORK OUT"""
import collections,csv,hashlib,json,re,struct,sys,zlib
from pathlib import Path
image,runtime,work,out=map(Path,sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest();proof=json.loads((runtime/'independent_verification.json').read_text());assert proof['scheduler_first_return_verified']
for x in proof['files']:assert sha(Path(x['path']).read_bytes())==x['sha256']
out.mkdir(exist_ok=True);stops=json.loads((runtime/'input_stops.json').read_text());rows=[]
for x in stops:
 if not x['stage'].startswith('scheduler_'):continue
 p=x['prefix'];d=struct.unpack('<III',(work/(p+'scheduler_deadlines.bin')).read_bytes());b=struct.unpack('<II',(work/(p+'scheduler_buckets.bin')).read_bytes());v=struct.unpack('<HH',(work/(p+'vga_page_words.bin')).read_bytes());reg=x['registers']
 rows.append(dict(stage=x['stage'],cs=reg['CS'],ip=reg['IP'],AX=reg['AX'],DX=reg['DX'],DS=reg['DS'],SS=reg['SS'],SP=reg['SP'],last_raw_sample=d[0],next_bucket8=d[1],next_bucket_config=d[2],current_bucket8=b[0],current_bucket_config=b[1],world_counter=int.from_bytes((work/(p+'world_counter.bin')).read_bytes(),'little'),page_word_012c=v[0],page_word_012e=v[1],stack_top4_hex=(work/(p+'scheduler_stack.bin')).read_bytes().hex()))
with (out/'native_scheduler_trace.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
palette=bytearray();dac=json.loads((runtime/'menu_dac_readback.json').read_text())
for line in dac['DACPAL']:
 m=re.match(r'^([0-9A-Fa-f]{2}):\s+(.+)$',line)
 if m:assert int(m[1],16)*3==len(palette);palette.extend(bytes.fromhex(''.join(re.findall(r'[0-9A-Fa-f]{6}',m[2]))))
assert len(palette)==768 and max(palette)<=63
def chunk(k,p):return struct.pack('>I',len(p))+k+p+struct.pack('>I',zlib.crc32(k+p)&0xffffffff)
previews=[]
for page in (0xa000,0xa400):
 planes=[(work/('menu_page_%04x_plane_%d.bin'%(page,p))).read_bytes() for p in range(4)];pixels=bytes(planes[n%4][n//4] for n in range(64000));assert sha(pixels)==proof['pages'][str(page)]['pixel_sha256']
 filtered=b''.join(b'\0'+pixels[y*320:(y+1)*320] for y in range(200));png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',320,200,8,3,0,0,0))+chunk(b'PLTE',bytes(v*255//63 for v in palette))+chunk(b'IDAT',zlib.compress(filtered))+chunk(b'IEND',b'');path=out/('runtime_first_scheduler_%04x.png'%page);path.write_bytes(png)
 previews.append(dict(path=out.name+'/'+path.name,bytes=len(png),sha256=sha(png),git_blob_sha=hashlib.sha1(b'blob '+str(len(png)).encode()+b'\0'+png).hexdigest(),page=page,visible=page==proof['visible_page'],pixel_sha256=sha(pixels),palette_sha256=sha(palette),pixels_using_dac227=pixels.count(227),pixels_using_dac235=pixels.count(235),scope='derived320x200 VGA planes plus actual6bit DAC readback scaled255/63; not original distributed asset, host screenshot, timing/scanout proof or independent renderer golden'))
(out/'generated_preview_manifest.json').write_text(json.dumps(previews[0],indent=2)+'\n');(out/'all_page_previews.json').write_text(json.dumps(previews,indent=2)+'\n')
s=dict(native_scheduler_stages=len(rows),new_functions=0,new_replay_cases=0,runtime_scenarios_added=1,new_deep_verified_bytes=0,new_typed_pass1_bytes=0,visible_page=0xa000,elapsed=proof['elapsed'],palette_source='actual DACPAL, not RAM palette',dac_ram_changed_indices=[227,235],scope='first post-map scheduler return, native timing branch and state; existing scheduler fields refined without double counting; current DOSBox planes reconstructed with actual DAC, no independent pixel parity claim',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,runtime/'independent_verification.json',Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
