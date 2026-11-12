"""python audit_main_menu_fields.py IMAGE RUNTIME WORK OUT"""
import csv,hashlib,json,struct,sys,zlib
from pathlib import Path
image,runtime,work,out=map(Path,sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();proof=json.loads((runtime/'independent_verification.json').read_text());assert proof['main_menu_initial_draw_verified'] and sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
for item in proof['files']:assert sha(Path(item['path']).read_bytes())==item['sha256']
out.mkdir(parents=True,exist_ok=True);load=json.loads((runtime/'summary.json').read_text())['load_segment'];stops=json.loads((runtime/'input_stops.json').read_text());last=stops[-1];tables=(work/(last['prefix']+'menu_tables.bin')).read_bytes();rows=[];focus=[];intervals=[]
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for table,end in ((0xe10,0xe8e),(0xe8e,0xf1e),(0xf1e,0xfae)):
 pos=table;count=0
 while tables[pos-0xe10]:
  raw=tables[pos-0xe10:pos-0xe10+18];label_off,label_seg=struct.unpack_from('<HH',raw,14);assert label_seg==load+0x2771
  start=0x27710+label_off;label=b[start:b.index(0,start)].decode('ascii');rows.append(dict(table_offset=table,index=count,image_start=0x20b90+pos,length=18,id=raw[0],initial_focus_marker=raw[4],style_byte=raw[5],x=struct.unpack_from('<H',raw,10)[0],y=struct.unpack_from('<H',raw,12)[0],runtime_label_offset=label_off,runtime_label_segment=label_seg,static_label=label,status='PARTIAL',scope='runtime descriptor/pointer exact; static label decoded from canonical source, no fresh final string dump'))
  focus.append(dict(start=0x20b90+pos+4,end_exclusive=0x20b90+pos+5,length=1,type='BYTE_initial_focus_marker_consumed_by_1946_and_colour174C',value=raw[4],status='PARTIAL',scope='not a universal enabled/disabled flag; caller domains remain open'))
  count+=1;pos+=18
 assert pos+18==end and not any(tables[pos-0xe10:pos-0xe10+18])
 intervals.append(dict(start=0x20b90+table,end_exclusive=0x20b90+end,length=end-table,type='%d_menu_records18_plus_sentinel18'%count,status='PARTIAL'))
save('menu_records',rows);save('focus_fields',focus);save('runtime_field_intervals',intervals);(out/'runtime_field_intervals.json').write_text(json.dumps(intervals,indent=2)+'\n')
palette=(work/'palette_buffer_runtime.bin').read_bytes();assert len(palette)==768 and max(palette)<=63
for page in (0xa000,0xa400):
 planes=[(work/('menu_page_%04x_plane_%d.bin'%(page,n))).read_bytes() for n in range(4)];pixels=bytes(planes[n%4][n//4] for n in range(64000));assert sha(pixels)==proof['pages'][str(page)]['pixel_sha256']
 def chunk(k,p):return struct.pack('>I',len(p))+k+p+struct.pack('>I',zlib.crc32(k+p)&0xffffffff)
 filtered=b''.join(b'\0'+pixels[y*320:(y+1)*320] for y in range(200));png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',320,200,8,3,0,0,0))+chunk(b'PLTE',bytes(v*255//63 for v in palette))+chunk(b'IDAT',zlib.compress(filtered))+chunk(b'IEND',b'');(out/('runtime_menu_page_%04x.png'%page)).write_bytes(png)
summary=dict(runtime_scenarios_added=1,menu_records=len(rows),tables=3,sentinel_records=3,descriptor_bytes_verified=414,focus_marker_fields=20,initial_focus_id=1,visible_page=0xa400,descriptor_changes_between_captures=0,typed_bytes_added_to_pass1=0,new_deep_verified_bytes=0,scope='main menu initialized/initially drawn through native path; fixed descriptors and firstfocus, paused planes/DAC reconstructed, not host screenshot or independent renderer golden; save metadata calls not executed in this startup mode',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,runtime/'independent_verification.json',Path(__file__))])
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
