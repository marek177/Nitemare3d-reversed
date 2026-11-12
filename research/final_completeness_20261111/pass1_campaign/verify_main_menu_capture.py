"""python verify_main_menu_capture.py IMAGE RELOCS MAP OUT WORK"""
import csv,hashlib,json,re,struct,sys
from pathlib import Path
image,relocs,mapping,out,work=map(lambda p:Path(p).resolve(),sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest();s=json.loads((out/'summary.json').read_text())
assert s['success'] and s['main_menu_runtime'] and s['runtime_tests']==1 and s['watch_events']==0 and s['autotype_command']=='autotype -w 15 -p 10 space space space'
inputs=list(csv.DictReader((out/'inputs.csv').open()));assert len(inputs)==23
for r in inputs:assert sha(Path(r['source']).read_bytes())==sha(Path(r['copy']).read_bytes())==r['sha256']
assert s['game_source_sha256']=='552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301' and s['exe_sha256']=='a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832'
support=Path(__file__).with_name('dosbox_watch_support_menu_v2.py');harness=Path(__file__).with_name('runtime_watch_main_menu.py');assert sha(support.read_bytes())==s['support_sha256'] and sha(harness.read_bytes())==s['harness_sha256']
launch=json.loads((out/'launch_arguments.json').read_text());assert launch.count(s['autotype_command'])==1 and launch.index(s['autotype_command'])<launch.index('debugbox N3D20.EXE')
b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';load=s['load_segment'];expected=bytearray(b)
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',expected,int(r['image_offset']),(int(r['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==expected
assert sha(mapping.read_bytes())=='3021969d4e4348715816361fa387631e7d6cfd9fc9dcc136e26073f0f9984d1b';unknown=set()
for row in csv.DictReader(mapping.open(encoding='utf-8-sig')):
 if row['status']=='UNKNOWN':unknown.update(range(int(row['start']),int(row['end_exclusive'])))
assert len(unknown)==44;physical={load*16+n for n in unknown};initial={int(k):v for k,v in s['initial'].items()};final={int(k):v for k,v in s['final'].items()};cache={int(k):v for k,v in s['cache_initial'].items()}
assert initial==final and set(cache)==physical and all(initial[a]==cache[a]==0 for a in physical) and set(s['calibrated_addresses'])==physical
assert bytes(initial[load*16+0x29a66+n] for n in range(4))==struct.pack('<HH',0x2c0,load+0x11ee)
t=json.loads((out/'transcript.json').read_text());commands=[r['command'] for r in t];ports=['EXEC OUTP 03CE 0004']+['EXEC OUTP 03CF %04X'%n for n in range(4)]+['EXEC OUTP 03CF 0000','EXEC OUTP 03CE 0006'];queries=['EXEC VGA '+n for n in ('GC','SEQ','MODE','AC','DAC','DACPAL')]
allowed=('EXEC EV ','EXEC BP ','EXEC BPLM ','EXEC BPLIST','EXEC BPDEL ','EXEC RUN','EXEC MEMDUMPBIN ')
assert all(c=='PING' or c.startswith(allowed) or c in ports+queries for c in commands) and [c for c in commands if c.startswith('EXEC OUTP ')]==ports
assert commands.count('EXEC BPDEL *')==2 and commands[-1]=='EXEC BPDEL *' and not any(c=='EXEC RUN' for c in commands[commands.index(ports[0]):])
installed=[int(c.split()[-1],16) for c in commands if c.startswith('EXEC BPLM ')];assert len(installed)==44 and set(installed)==physical
for row in t:
 if row['command']!='EXEC BPLIST':continue
 values={}
 for line in row['response']:
  m=re.search(r'\bBPLM\s+([0-9A-Fa-f]+)\s+\(([0-9A-Fa-f]{2})\)',line)
  if m:values[int(m[1],16)]=int(m[2],16)
 assert values==cache
stops=json.loads((out/'input_stops.json').read_text());expected_stages=[]
for name in ('cd','info','title'):expected_stages+=['wait_entry']+['irq_entry','irq_after_port_read','irq_before_iret']*2+['after_wait_'+name]
expected_stages+=['menu_descriptor_ready','menu_initial_draw'];assert [p['stage'] for p in stops]==expected_stages and len(stops)==26 and commands.count('EXEC RUN')==27
snaps=json.loads((out/'snapshots.json').read_text());assert snaps[1:]==stops and (snaps[0]['registers']['CS'],snaps[0]['registers']['IP'])==(load+0x11ee,0x18)
points={'wait_entry':(load+0xd29,0x424),'irq_entry':(load+0x6b0,0),'irq_after_port_read':(load+0x6b0,0x12),'irq_before_iret':(load+0x6b0,0x133),'after_wait_cd':(load+0xd29,0x7c5),'after_wait_info':(load+0xd29,0x7e6),'after_wait_title':(load+0xd29,0x80d),'menu_descriptor_ready':(load+0xd29,0x2787),'menu_initial_draw':(load+0xd29,0x19e4)}
for cs,ip in points.values():assert 'EXEC BP %04X:%08X'%(cs,ip) in commands
states=[]
for n,stop in enumerate(stops):
 reg=stop['registers'];assert (reg['CS'],reg['IP'])==points[stop['stage']] and reg['DS']==load+0x2771 and stop['prefix']=='stop_%02d_'%n
 if not stop['stage'].startswith('irq_'):assert reg['SS']==load+0x2771
 p=stop['prefix'];flags=(work/(p+'game_key_flags.bin')).read_bytes();prev=(work/(p+'previous_scan.bin')).read_bytes();bios=(work/(p+'bios_queue.bin')).read_bytes();assert (len(flags),len(prev),len(bios))==(2,1,36)
 states.append(dict(flags=int.from_bytes(flags,'little'),prev=prev[0],head=struct.unpack_from('<H',bios)[0],tail=struct.unpack_from('<H',bios,2)[0],bios=bios))
for phase,ret in enumerate((0x7c5,0x7e6,0x80d)):
 n=8*phase;head=0x1e+phase*2
 assert struct.unpack('<HH',(work/(stops[n]['prefix']+'wait_return.bin')).read_bytes())==(ret,load+0xd29)
 assert states[n]['head']==states[n]['tail']==head and states[n+3]['head']==head and states[n+3]['tail']==head+2 and states[n+3]['flags']==0x200 and states[n+3]['prev']==0x39
 assert struct.unpack_from('<H',states[n+3]['bios'],head-0x1a)[0]==0x3920
 assert states[n+6]['head']==head and states[n+6]['tail']==head+2 and states[n+6]['flags']==0 and states[n+6]['prev']==0xb9
 assert states[n+7]['head']==states[n+7]['tail']==head+2 and states[n+7]['flags']==0
 assert [stops[n+i]['registers']['AX']&255 for i in (2,5)]==[0x39,0xb9]
 for enter,exit in ((n+1,n+3),(n+4,n+6)):
  for key in ('AX','BX','CX','DX','DS','ES','SS','SP'):assert stops[enter]['registers'][key]==stops[exit]['registers'][key]
menus=stops[-2:];assert menus[0]['extra_registers']['SI']==menus[1]['extra_registers']['SI']==0xe10
for stop in menus:
 actual=(work/(stop['prefix']+'menu_tables.bin')).read_bytes();assert actual==expected[0x219a0:0x219a0+414]
ready_frame=(work/(menus[0]['prefix']+'menu_frame.bin')).read_bytes();draw_frame=(work/(menus[1]['prefix']+'menu_frame.bin')).read_bytes();assert len(ready_frame)==len(draw_frame)==20
assert struct.unpack_from('<H',ready_frame,6)[0]==load+0x20b9 and struct.unpack_from('<HH',draw_frame,14)==(0xe10,load+0x20b9) and struct.unpack_from('<H',draw_frame)[0]==load+0x20b9
uif=Path(next(r['source'] for r in inputs if Path(r['source']).name.upper()=='UIF.DAT')).read_bytes();assert sha(uif)=='d5964c31144a67da8b2524e545488fe243f1394e5e4e231b439284c55276c45d' and (work/'uif_directory_runtime.bin').read_bytes()==uif[:192]
for group in (0,1,2):
 length,offset=struct.unpack_from('<HI',uif,group*6);raw=uif[offset:offset+length];transformed=bytearray(raw);q=2;pointers=[(1200*group,load+0x20b9)]
 for n in range(1,128):
  h,w=raw[q:q+2];size=h*((w+7)//8);pointers.append((1200*group+q,load+0x20b9))
  for j in range(q+2,q+2+size):transformed[j]=int(format(raw[j],'08b')[::-1],2)
  q+=2+size
 assert q==length and (work/('font%d_block_runtime.bin'%group)).read_bytes()==transformed+bytes(1200-length) and (work/('font%d_pointers_runtime.bin'%group)).read_bytes()==b''.join(struct.pack('<HH',*p) for p in pointers)
assert (work/'font_flags_runtime.bin').read_bytes()==b'\1\1\1' and (work/'font_selected_runtime.bin').read_bytes()==b'\2'
sound=Path(next(r['source'] for r in inputs if Path(r['source']).name.upper()=='SND.DAT')).read_bytes();assert sha(sound)=='f3434984d315531602d32285cb8ff55990bba786f5fb37f53710e88379388614' and (work/'sound_directory_runtime.bin').read_bytes()==sound[192:666]
before=json.loads((out/'vga_state.json').read_text());after=json.loads((out/'vga_state_restored.json').read_text())
for name in ('GC','SEQ','MODE','AC'):
 assert [row['response'] for row in t if row['command']=='EXEC VGA '+name]==[before[name],after[name]] and before[name][1:-1]==after[name][1:-1]
mode='\n'.join(before['MODE']);gc='\n'.join(before['GC']);ac='\n'.join(before['AC']);assert 'disp-start=4000h real-start=4000h' in mode and 'rd-mode=0 wr-mode=0 rdmap-sel=0' in mode and 'chained=0' in mode and 'index=06h' in gc and 'rdmapsel=00h' in gc and 'color-plane-en=0fh' in ac and 'disabled-by-index=0' in ac
assert struct.unpack('<HH',(work/'vga_page_words.bin').read_bytes())==(0xa400,0xa000)
dac=json.loads((out/'menu_dac_readback.json').read_text());decoded=bytearray()
for name in ('DAC','DACPAL'):assert [row['response'] for row in t if row['command']=='EXEC VGA '+name]==[dac[name]]
for line in dac['DACPAL']:
 m=re.match(r'^([0-9A-Fa-f]{2}):\s+(.+)$',line)
 if not m:continue
 assert int(m[1],16)*3==len(decoded);entries=re.findall(r'[0-9A-Fa-f]{6}',m[2]);assert len(entries)==8;decoded.extend(bytes.fromhex(''.join(entries)))
pal=Path(next(r['source'] for r in inputs if Path(r['source']).name.upper()=='GAME.PAL')).read_bytes();assert sha(pal)=='efd52442cbee3327d8cec045b31559049e8767b298c25674a557eb6e096a759f' and decoded==bytes(v>>2 for v in pal[-768:])==(work/'palette_buffer_runtime.bin').read_bytes() and 'bits=6' in '\n'.join(dac['DAC'])
pages={}
for page in (0xa000,0xa400):
 planes=[(work/('menu_page_%04x_plane_%d.bin'%(page,n))).read_bytes() for n in range(4)];assert all(len(raw)==16000 for raw in planes);pixels=bytes(planes[n%4][n//4] for n in range(64000));pages[str(page)]=dict(pixel_sha256=sha(pixels),plane_sha256=[sha(raw) for raw in planes])
for region in s['regions']:
 a,n=region['image_start'],region['length']
 for phase,values in [('initial',initial),('final',final)]:assert (work/(phase+'_%05x.bin'%a)).read_bytes()==bytes(values[load*16+a+j] for j in range(n))
assert len(s['capture_files'])==len(set(s['capture_files']))==118
files=[Path(p) for p in s['capture_files']]+[out/name for name in ('summary.json','transcript.json','snapshots.json','watch_events.json','inputs.csv','runtime.conf','input_stops.json','launch_arguments.json','vga_state.json','vga_state_restored.json','menu_dac_readback.json')]+[support,harness,Path(__file__)]
result=dict(verified=True,summary_sha256=sha((out/'summary.json').read_bytes()),runtime_tests=1,new_deep_verified_bytes=0,main_menu_initial_draw_verified=True,menu_pointer_offset=0xe10,menu_pointer_segment=load+0x20b9,menu_record_stride=18,menu_table_bytes_verified=414,menu_table_changes_between_stops=0,initial_focus_id=1,wait_returns_verified=[0x7c5,0x7e6,0x80d],port_scan_bytes_verified=[0x39,0xb9]*3,BIOS_key_word=0x3920,keyboard_queue_consumptions=3,font_groups_runtime_verified=[0,1,2],dac_components_verified=768,programmed_and_latched_display_start=0x4000,pages=pages,watch_addresses=44,value_change_events=0,runtime_image_sha256=sha((work/'unpacked_runtime.bin').read_bytes()),scope='original packedDOS2 plus explicit CDasset; supported three-key AUTOTYPE progresses all intro waits to main menu initial draw, six actual IRQ make/break reads, three BIOS dequeue events, fixed relocated414B descriptor tables and selectedfirst item; VGA planes/DAC are paused readback with read-map restore after endpoint, no host screenshot/pixel golden/gameplay/save-load/Win16 parity; UNKNOWN44 cached-change only',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in files])
(out/'independent_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
