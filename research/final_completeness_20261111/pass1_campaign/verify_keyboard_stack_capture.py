"""python verify_keyboard_font1_capture.py IMAGE RELOCS MAP OUT WORK"""
import csv,hashlib,json,re,struct,sys
from pathlib import Path
image,relocs,mapping,out,work=map(lambda p:Path(p).resolve(),sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest()
s=json.loads((out/'summary.json').read_text());assert s['success'] and s['keyboard_font1_runtime'] and s['runtime_tests']==1 and s['watch_events']==0 and s['interrupt_stack_probe'];window=bool(s.get('worx_stack_window_probe'))
assert s['autotype_command']=='autotype -w 15 -p 1 space' and len(s['drive_filenames'])==23
inputs=list(csv.DictReader((out/'inputs.csv').open()));assert len(inputs)==23
for r in inputs:assert sha(Path(r['source']).read_bytes())==sha(Path(r['copy']).read_bytes())==r['sha256']
assert s['game_source_sha256']=='552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301' and s['exe_sha256']=='a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832'
launch=json.loads((out/'launch_arguments.json').read_text());assert launch.count(s['autotype_command'])==1 and launch.index(s['autotype_command'])<launch.index('debugbox N3D20.EXE')
support=Path(__file__).with_name('dosbox_watch_support_autotype_v1.py');harness=Path(__file__).with_name('runtime_watch_worx_stack_window.py' if window else 'runtime_watch_keyboard_stack.py');assert sha(support.read_bytes())==s['support_sha256'] and sha(harness.read_bytes())==s['harness_sha256']
b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';load=s['load_segment'];expected=bytearray(b)
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',expected,int(r['image_offset']),(int(r['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==expected
assert sha(mapping.read_bytes())=='3021969d4e4348715816361fa387631e7d6cfd9fc9dcc136e26073f0f9984d1b';unknown=set()
for r in csv.DictReader(mapping.open(encoding='utf-8-sig')):
 if r['status']=='UNKNOWN':unknown.update(range(int(r['start']),int(r['end_exclusive'])))
assert len(unknown)==44;addresses={load*16+n for n in unknown};initial={int(k):v for k,v in s['initial'].items()};final={int(k):v for k,v in s['final'].items()};cache={int(k):v for k,v in s['cache_initial'].items()}
assert initial==final and set(cache)==addresses and set(s['calibrated_addresses'])==addresses and all(initial[a]==cache[a]==0 for a in addresses)
assert bytes(initial[load*16+0x29a66+n] for n in range(4))==struct.pack('<HH',0x2c0,load+0x11ee)
assert json.loads((out/'watch_events.json').read_text())==[];t=json.loads((out/'transcript.json').read_text());commands=[r['command'] for r in t]
allowed=('EXEC EV ','EXEC BP ','EXEC BPLM ','EXEC BPLIST','EXEC BPDEL ','EXEC RUN','EXEC MEMDUMPBIN ');assert all(c=='PING' or c.startswith(allowed) for c in commands)
installed=[int(c.split()[-1],16) for c in commands if c.startswith('EXEC BPLM ')];assert len(installed)==44 and set(installed)==addresses
assert commands.count('EXEC BPDEL *')==2 and commands[-1]=='EXEC BPDEL *'
for row in t:
 if row['command']!='EXEC BPLIST':continue
 values={}
 for line in row['response']:
  match=re.search(r'\bBPLM\s+([0-9A-Fa-f]+)\s+\(([0-9A-Fa-f]{2})\)',line)
  if match:values[int(match[1],16)]=int(match[2],16)
 assert values==cache
all_stops=json.loads((out/'input_stops.json').read_text());stops=[stop for stop in all_stops if stop['stage']!='worx_stack_window'];stages=[r['stage'] for r in stops]
assert stages==['wait_entry','irq_entry','irq_after_port_read','irq_before_iret','irq_entry','irq_after_port_read','irq_before_iret','after_wait','font1_ready']
points={'wait_entry':(load+0xd29,0x424),'irq_entry':(load+0x6b0,0),'irq_after_port_read':(load+0x6b0,0x12),'irq_before_iret':(load+0x6b0,0x133),'after_wait':(load+0xd29,0x7c5),'font1_ready':(load+0x83d,0x54)}
assert commands.count('EXEC RUN')==len(all_stops)+1
for cs,ip in points.values():assert 'EXEC BP %04X:%08X'%(cs,ip) in commands
snaps=json.loads((out/'snapshots.json').read_text());assert len(snaps)==len(all_stops)+1 and snaps[1:]==all_stops and (snaps[0]['registers']['CS'],snaps[0]['registers']['IP'])==(load+0x11ee,0x18)
states=[]
for n,stop in enumerate(stops):
 reg=stop['registers'];assert (reg['CS'],reg['IP'])==points[stop['stage']] and reg['DS']==load+0x2771 and stop['prefix']=='stop_%02d_'%all_stops.index(stop)
 if not stop['stage'].startswith('irq_'):assert reg['SS']==load+0x2771
 prefix=stop['prefix'];flags=(work/(prefix+'game_key_flags.bin')).read_bytes();prev=(work/(prefix+'previous_scan.bin')).read_bytes();bios=(work/(prefix+'bios_queue.bin')).read_bytes();assert (len(flags),len(prev),len(bios))==(2,1,36)
 states.append(dict(flags=int.from_bytes(flags,'little'),previous=prev[0],head=struct.unpack_from('<H',bios)[0],tail=struct.unpack_from('<H',bios,2)[0],word0=struct.unpack_from('<H',bios,4)[0]))
assert [stops[n]['registers']['AX']&255 for n in (2,5)]==[0x39,0xb9]
assert states[0]==dict(flags=0,previous=0,head=0x1e,tail=0x1e,word0=0)
assert states[3]==dict(flags=0x200,previous=0x39,head=0x1e,tail=0x20,word0=0x3920)
assert states[6]==dict(flags=0,previous=0xb9,head=0x1e,tail=0x20,word0=0x3920)
assert states[7]==states[8]==dict(flags=0,previous=0xb9,head=0x20,tail=0x20,word0=0x3920)
for enter,exit in ((1,3),(4,6)):
 for key in ('AX','BX','CX','DX','DS','ES','SS','SP'):assert stops[enter]['registers'][key]==stops[exit]['registers'][key]
 assert stops[enter+1]['registers']['SS']==stops[enter]['registers']['SS'] and stops[enter+1]['registers']['SP']==(stops[enter]['registers']['SP']-40)&65535
frames=[]
for enter,exit in ((1,3),(4,6)):
 raw=(work/(stops[enter]['prefix']+'interrupt_frame.bin')).read_bytes();after=(work/(stops[exit]['prefix']+'interrupt_frame.bin')).read_bytes();assert raw==after and len(raw)==6
 context=(work/(stops[enter]['prefix']+'interrupt_stack.bin')).read_bytes();assert len(context)==128 and context[:6]==raw
 ip,cs,flags=struct.unpack('<HHH',raw);assert (cs,ip)==(load+0xbde,0xc6) and flags&512
 frames.append(dict(ss=stops[enter]['registers']['SS'],sp=stops[enter]['registers']['SP'],interrupted_cs=cs,interrupted_ip=ip,saved_flags=flags))
if window:
 ws=[stop for stop in all_stops if stop['stage']=='worx_stack_window'];assert len(ws)==1 and all_stops.index(ws[0])==1
 w=ws[0];reg=w['registers'];assert (reg['CS'],reg['IP'],reg['SS'],reg['SP'])==(load+0x15bf,0x40fd,load+0x15bf,0x40e1)
 control=(work/(w['prefix']+'worx_stack_control.bin')).read_bytes();saved_sp,saved_ss,private_sp,private_ss=struct.unpack('<HHHH',control);assert saved_ss==load+0x2771 and (private_sp,private_ss)==(0x40e1,load+0x15bf)
 assert len((work/(w['prefix']+'worx_private_stack.bin')).read_bytes())==512
 assert 'EXEC BP %04X:000040FD'%(load+0x15bf) in commands and commands.count('EXEC BPDEL 00')==1
else:assert len(all_stops)==9 and all(c=='EXEC BPDEL *' for c in commands if c.startswith('EXEC BPDEL '))
uif=Path(next(r['source'] for r in inputs if Path(r['source']).name.upper()=='UIF.DAT')).read_bytes();assert sha(uif)=='d5964c31144a67da8b2524e545488fe243f1394e5e4e231b439284c55276c45d'
assert (work/'uif_directory_runtime.bin').read_bytes()==uif[:192]
for group in (0,1,2):
 length,offset=struct.unpack_from('<HI',uif,group*6);raw=uif[offset:offset+length];expected=bytearray(raw);q=2;pointers=[(1200*group,load+0x20b9)]
 for glyph in range(1,128):
  height,width=raw[q:q+2];size=height*((width+7)//8);pointers.append((1200*group+q,load+0x20b9))
  for j in range(q+2,q+2+size):expected[j]=int(format(raw[j],'08b')[::-1],2)
  q+=2+size
 assert q==length and (work/('font%d_block_runtime.bin'%group)).read_bytes()==expected+bytes(1200-length)
 assert (work/('font%d_pointers_runtime.bin'%group)).read_bytes()==b''.join(struct.pack('<HH',*p) for p in pointers)
assert (work/'font_flags_runtime.bin').read_bytes()==b'\1\1\1' and (work/'font_selected_runtime.bin').read_bytes()==b'\1'
sound=Path(next(r['source'] for r in inputs if Path(r['source']).name.upper()=='SND.DAT')).read_bytes();assert sha(sound)=='f3434984d315531602d32285cb8ff55990bba786f5fb37f53710e88379388614' and (work/'sound_directory_runtime.bin').read_bytes()==sound[192:666]
assert len(s['capture_files'])==(61 if window else 56) and len(set(s['capture_files']))==len(s['capture_files'])
for region in s['regions']:
 a,n=region['image_start'],region['length']
 for phase,values in [('initial',initial),('final',final)]:assert (work/(phase+'_%05x.bin'%a)).read_bytes()==bytes(values[load*16+a+j] for j in range(n))
files=[Path(p) for p in s['capture_files']]+[out/name for name in ('summary.json','transcript.json','snapshots.json','watch_events.json','inputs.csv','runtime.conf','input_stops.json','launch_arguments.json')]+[support,harness,Path(__file__)]
result=dict(verified=True,summary_sha256=sha((out/'summary.json').read_bytes()),runtime_tests=1,new_deep_verified_bytes=0,keyboard_port_bytes_verified=[0x39,0xb9],native_irq_entries=2,native_pre_iret_stops=2,bios_key_word=0x3920,bios_queue_tail_advance=2,bios_queue_consumed_after_wait=True,font_groups_runtime_verified=[0,1,2],font1_records=127,font1_pointer_slots=128,font1_source_bytes=1145,unknown_baseline_membership_exact=True,watch_addresses=44,value_change_events=0,runtime_image_sha256=sha((work/'unpacked_runtime.bin').read_bytes()),scope='one original packed DOS2 with added CD asset and supported AUTOTYPE space; actual IRQ1 make/break port reads, game bit0200, BIOS3920 queue/consumption and natural wait return; original font1 transformed1145B/128FAR plus font0/2 exact; breakpoints pause CPU and can affect timing; no host scanout, arbitrary keyboard/DEMO, gameplay or Win16 parity; UNKNOWN44 cached-change only',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in files])
result['interrupt_frames_verified']=frames;result['worx_stack_window_verified']=window
if window:result.update(worx_private_ss=private_ss,worx_private_sp=private_sp,worx_saved_ss=saved_ss,worx_saved_sp=saved_sp)
result['scope']+='; entry/exit hardware interrupt frames exact, both interrupted canonical0BDE:00C6 in this run; '+('explicit paused WORX window proves SS/privateSP/control words, not an IRQ nested on that stack' if window else 'no alternate IRQ stack observed in this run')
(out/'independent_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
