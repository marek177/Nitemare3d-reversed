"""python verify_unknown_watch_capture.py IMAGE RELOCS MAP OUT WORK"""
import csv,hashlib,json,re,struct,sys
from pathlib import Path
image,relocs,mapping,out,work=map(lambda p:Path(p).resolve(),sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest();s=json.loads((out/'summary.json').read_text());assert s['success'] and s['runtime_tests']==1 and s['watch_events']==0 and s['watched_bytes']==44
b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';assert sha(mapping.read_bytes())=='3021969d4e4348715816361fa387631e7d6cfd9fc9dcc136e26073f0f9984d1b'
unknown=set()
for r in csv.DictReader(mapping.open(encoding='utf-8-sig')):
 if r['status']=='UNKNOWN':unknown.update(range(int(r['start']),int(r['end_exclusive'])))
assert len(unknown)==44;load=s['load_segment'];physical={load*16+i for i in unknown};initial={int(k):v for k,v in s['initial'].items()};final={int(k):v for k,v in s['final'].items()};cache={int(k):v for k,v in s['cache_initial'].items()};assert set(cache)==physical and all(v==0 for v in cache.values());assert set(s['calibrated_addresses'])==physical
assert initial==final and all(initial[a]==0 for a in physical)
expected=bytearray(b);rr=list(csv.DictReader(relocs.open()))
for r in rr:struct.pack_into('<H',expected,int(r['image_offset']),(int(r['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==expected
assert bytes(initial[load*16+0x29a66+n] for n in range(4))==struct.pack('<HH',0x2c0,load+0x11ee)
t=json.loads((out/'transcript.json').read_text());assert json.loads((out/'watch_events.json').read_text())==[]
commands=[r['command'] for r in t];installs=[int(c.split()[-1],16) for c in commands if c.startswith('EXEC BPLM ')];assert len(installs)==44 and set(installs)==physical
allowed=('EXEC EV ','EXEC BP ','EXEC BPLM ','EXEC BPLIST','EXEC BPDEL ','EXEC RUN','EXEC MEMDUMPBIN ')
trace_manifest_path=out/'trace_manifest.json';trace_present=trace_manifest_path.exists()
loaded_intro=bool(s.get('optional_intro_loaded_branch'))
display_intro=bool(s.get('optional_intro_display_branch'))
font0_intro=bool(s.get('font0_runtime_branch'))
loaded_queries=('EXEC VGA GC','EXEC VGA SEQ','EXEC VGA MODE')+(('EXEC VGA AC',) if display_intro else ())
loaded_ports=('EXEC OUTP 03CE 0004','EXEC OUTP 03CE 0006')+tuple('EXEC OUTP 03CF %04X'%n for n in range(4))
assert all(c=='PING' or c.startswith(allowed) or c in ('EXEC VGA DAC','EXEC VGA DACPAL') or loaded_intro and c in loaded_queries+loaded_ports or trace_present and c=='EXEC LOGL 00010000' for c in commands)
assert commands.count('EXEC RUN')==2 and commands.count('EXEC BPDEL *')==2
install_end=max(n for n,c in enumerate(commands) if c.startswith('EXEC BPLM '));run_watch=next(n for n in range(install_end,len(commands)) if commands[n]=='EXEC RUN');assert all(not c.startswith('EXEC BPDEL') or trace_present and c=='EXEC BPDEL 0' for c in commands[run_watch:-1])
assert commands[-1]=='EXEC BPDEL *'
for response in t:
 if response['command']!='EXEC BPLIST':continue
 values={}
 for line in response['response']:
  m=re.search(r'\bBPLM\s+([0-9A-Fa-f]+)\s+\(([0-9A-Fa-f]{2})\)',line)
  if m:values[int(m[1],16)]=int(m[2],16)
 assert values==cache
stages=s['snapshots'];assert len(stages)==(3 if trace_present else 2)
sound_path=work/'sound_directory_runtime.bin';sound_present=sound_path.exists();font_present=(work/'font2_block_runtime.bin').exists();optional_intro=bool(s.get('optional_intro_missing_branch'));endpoint=(0x7c1 if font0_intro else 0x7ae if display_intro else 0x7a2 if loaded_intro else 0x7dd if optional_intro else 0x7d9) if font_present else 0x190 if sound_present else 0x17c;endpoint_cs=load+(0xd29 if font_present else 0x476)
a,z=stages[0]['registers'],stages[-1]['registers'];assert (a['CS'],a['IP'])==(load+0x11ee,0x18) and (z['CS'],z['IP'])==(endpoint_cs,endpoint) and z['DS']==z['SS']==load+0x2771
if optional_intro:
 assert font_present and z['AX']&255==0 and stages[-1]['stage']=='after_optional_intro_missing'
 assert not (work/'drive_c/DSTOPEN.IMG').exists()
 assert 'DSTOPEN.IMG' not in {name.upper() for name in s['drive_filenames']}
 assert 'EXEC BP %04X:000007DD'%endpoint_cs in commands
files=[Path(p) for p in s['capture_files']]+[out/name for name in ('summary.json','transcript.json','snapshots.json','watch_events.json','inputs.csv','runtime.conf')]
dac_path=out/'dac_readback.json';dac_present=dac_path.exists();assert len(s['capture_files'])==13+int(dac_present)+int(sound_present)+5*int(font_present)+7*int(loaded_intro)+int(display_intro)+2*int(font0_intro)
for r in csv.DictReader((out/'inputs.csv').open()):
 assert sha(Path(r['source']).read_bytes())==sha(Path(r['copy']).read_bytes())==r['sha256']
for region in s['regions']:
 start,n=region['image_start'],region['length']
 for phase,values in [('initial',initial),('final',final)]:
  raw=(work/(phase+'_%05x.bin'%start)).read_bytes();assert len(raw)==n and raw==bytes(values[load*16+start+i] for i in range(n))
dac_checks=False
if dac_present:
    dac=json.loads(dac_path.read_text());info=[r for r in t if r['command']=='EXEC VGA DAC'];pal=[r for r in t if r['command']=='EXEC VGA DACPAL'];assert len(info)==len(pal)==1
    assert info[0]['response']==dac['info_response'] and pal[0]['response']==dac['palette_response']
    decoded=bytearray()
    for line in pal[0]['response']:
        m=re.match(r'^([0-9A-Fa-f]{2}):\s+(.+)$',line)
        if not m:continue
        assert int(m[1],16)*3==len(decoded);entries=re.findall(r'[0-9A-Fa-f]{6}',m[2]);assert len(entries)==8
        decoded.extend(bytes.fromhex(''.join(entries)))
    assert len(decoded)==768 and max(decoded)<=63 and 'bits=6' in '\n'.join(info[0]['response']) and 'pel_mask=ffh' in '\n'.join(info[0]['response'])
    assetrow=next(r for r in csv.DictReader((out/'inputs.csv').open()) if Path(r['source']).name.upper()=='GAME.PAL');asset=Path(assetrow['source']).read_bytes();assert sha(asset)=='efd52442cbee3327d8cec045b31559049e8767b298c25674a557eb6e096a759f'
    expected_dac=bytes(v>>2 for v in asset[-768:]);assert decoded==expected_dac==(work/'palette_buffer_runtime.bin').read_bytes()==bytes.fromhex(dac['actual_hex'])
    assert sha(decoded)==dac['actual_sha256']==dac['buffer_sha256']==dac['expected_sha256'];files.append(dac_path);dac_checks=True
result=dict(verified=True,summary_sha256=sha((out/'summary.json').read_bytes()),runtime_image_sha256=sha((work/'unpacked_runtime.bin').read_bytes()),runtime_tests=1,new_deep_verified_bytes=0,unknown_baseline_membership_exact=True,watch_addresses=44,value_change_events=0,open_hook_dump_bytes=4,dac_register_readback_verified=dac_checks,dac_components_verified=768 if dac_checks else 0,scope=('one original DOS2 DOSBox-X session: read-only emulated DAC768component state equals actual palette buffer and GAME.PAL tail>>2; not physical hardware or rendered-frame parity; ' if dac_checks else 'one original DOS2 DOSBox-X session:')+'44UNKNOWN BYTE cached-value breakpoints from CRT0018 to main017C, no events; no read/same-value-write/host-callback internal write proof, hook4B endpoint dumps only',files=[dict(path=str(p),sha256=sha(p.read_bytes())) for p in files])
if sound_present:
    soundrow=next(r for r in csv.DictReader((out/'inputs.csv').open()) if Path(r['source']).name.upper()=='SND.DAT');sound=Path(soundrow['source']).read_bytes();assert sha(sound)=='f3434984d315531602d32285cb8ff55990bba786f5fb37f53710e88379388614'
    assert sound_path.read_bytes()==sound[192:666] and len(sound_path.read_bytes())==474
    result['sound_directory_runtime_verified']=True;result['sound_directory_bytes']=474;result['scope']='one original DOS2 DOSBox-X session: sound directory474B equals SND.DAT[192:666] at main0190; '+result['scope'].replace('main017C','main0190')
if font_present:
    uifrow=next(r for r in csv.DictReader((out/'inputs.csv').open()) if Path(r['source']).name.upper()=='UIF.DAT');uif=Path(uifrow['source']).read_bytes();assert sha(uif)=='d5964c31144a67da8b2524e545488fe243f1394e5e4e231b439284c55276c45d'
    assert (work/'uif_directory_runtime.bin').read_bytes()==uif[:192]
    length,offset=struct.unpack_from('<HI',uif,12);assert (length,offset)==(907,2237);original=uif[offset:offset+length];expected_font=bytearray(original);q=2;pointers=[(0x960,load+0x20b9)]
    for glyph in range(1,128):
        height,width=original[q:q+2];size=height*((width+7)//8);pointers.append((0x960+q,load+0x20b9))
        for j in range(q+2,q+2+size):expected_font[j]=int(format(original[j],'08b')[::-1],2)
        q+=2+size
    assert q==907 and (work/'font2_block_runtime.bin').read_bytes()==expected_font+b'\0'*293
    assert (work/'font2_pointers_runtime.bin').read_bytes()==b''.join(struct.pack('<HH',*pair) for pair in pointers)
    assert (work/'font_flags_runtime.bin').read_bytes()[2]==1 and (work/'font_selected_runtime.bin').read_bytes()==(b'\0' if font0_intro else b'\2')
    result['font2_runtime_verified']=True;result['font2_records']=127;result['font2_pointer_slots']=128;result['scope']='one original DOS2 DOSBox-X session: UIF192B directory and font2 transformed907B/pointer128 exact at UI07D9; '+result['scope'].replace('main0190','UI07D9').replace('main017C','UI07D9')
    if optional_intro:
        result['optional_intro_missing_branch_verified']=True
        result['scope']=result['scope'].replace('UI07D9','UI07DD')+'; optional intro returns AL0 with DSTOPEN.IMG absent in retained isolated drive; no successful intro decode or VGA frame proof'
if trace_present:
    middle=stages[1]['registers'];assert (middle['CS'],middle['IP'])==(load+0x476,0x17c)
    manifest=json.loads(trace_manifest_path.read_text());trace_path=Path(manifest['path']);raw=trace_path.read_bytes();assert sha(raw)==manifest['sha256'] and len(raw)==manifest['bytes'] and raw.endswith(b'\n')
    lines=raw.decode('ascii').splitlines();assert len(lines)<65536 and '%04X:0000017C'%(load+0x476) in lines[0] and '%04X:00000190'%(load+0x476) in lines[-1]
    assert commands.count('EXEC LOGL 00010000')==1 and commands.count('EXEC BPDEL 0')==1
    result['cpu_trace_manifest_verified']=True;result['cpu_trace_records']=len(lines);result['scope']='bounded original CPU pre-instruction trace main017C..0190 (terminal record not executed); '+result['scope'];result['files'] += [dict(path=str(path),sha256=sha(path.read_bytes())) for path in (trace_manifest_path,trace_path)]
if loaded_intro:
    assert font_present and not optional_intro and (font0_intro or z['AX']&255==(12 if display_intro else 1)) and stages[-1]['stage']==('after_optional_intro_font0' if font0_intro else 'after_optional_intro_flip' if display_intro else 'after_optional_intro_loaded')
    assert 'EXEC BP %04X:%08X'%(endpoint_cs,endpoint) in commands and len(s['drive_filenames'])==23
    assetrow=next(r for r in csv.DictReader((out/'inputs.csv').open()) if Path(r['source']).name.upper()=='DSTOPEN.IMG');asset=Path(assetrow['source']).read_bytes()
    assert sha(asset)=='af574568089f1998ca50ceeba310ff068c728279ff470cd39f47a8919228b95a' and (work/'drive_c/DSTOPEN.IMG').read_bytes()==asset
    q=128;pixels=bytearray()
    while len(pixels)<64000:
        value=asset[q];q+=1;count=1
        if value&192==192:count=value&63;value=asset[q];q+=1
        pixels.extend(bytes([value])*count)
    assert len(pixels)==64000 and q==19909
    assert struct.unpack('<HH',(work/'vga_page_words.bin').read_bytes())==((0xa400,0xa000) if display_intro else (0xa000,0xa400))
    before=json.loads((out/'vga_state.json').read_text());after=json.loads((out/'vga_state_restored.json').read_text())
    for name in (('GC','SEQ','MODE','AC') if display_intro else ('GC','SEQ','MODE')):
        rows=[row['response'] for row in t if row['command']=='EXEC VGA '+name]
        assert rows==[before[name],after[name]] and before[name][1:-1]==after[name][1:-1]
    gc='\n'.join(before['GC']);mode='\n'.join(before['MODE']);assert 'index=06h' in gc and 'rdmapsel=00h' in gc and 'bitmask=ffh' in gc
    assert 'rd-mode=0 wr-mode=0 rdmap-sel=0' in mode and 'chained=0' in mode and ('disp-start=4000h' if display_intro else 'disp-start=0h') in mode
    first_port=commands.index('EXEC OUTP 03CE 0004');last_port=commands.index('EXEC OUTP 03CE 0006')
    assert first_port>run_watch and not any(c=='EXEC RUN' for c in commands[first_port:])
    assert [c for c in commands if c.startswith('EXEC OUTP ')]==['EXEC OUTP 03CE 0004']+['EXEC OUTP 03CF %04X'%n for n in range(4)]+['EXEC OUTP 03CF 0000','EXEC OUTP 03CE 0006']
    plane_hashes=[]
    for plane in range(4):
        actual=(work/('vga_plane_%d.bin'%plane)).read_bytes();assert actual==pixels[plane::4] and len(actual)==16000;plane_hashes.append(sha(actual))
    assert (work/'vga_read_page_a400.bin').read_bytes()==pixels[0::4] and (work/'vga_read_page_a000.bin').read_bytes()==bytes(16000)
    result.update(optional_intro_loaded_branch_verified=True,runtime_vga_planes_verified=True,runtime_vga_plane_bytes=64000,runtime_vga_page=0xa400,runtime_vga_plane_sha256=plane_hashes,read_map_and_index_restored=True,asset_pixels_sha256=sha(pixels))
    result['scope']=result['scope'].replace('UI07D9','UI%04X'%endpoint)+'; original DOS2 EXE with explicit added CD asset: native decoded '+('page selected by programmed display start' if display_intro else 'back-page')+' four planes equal64000asset pixels; paused OUTP read-map intervention only after endpoint, original GC/index restored, no RUN after intervention; A000 page plane0 iszero; VGA read latches not restored or verified; not host-surface/physical-monitor/gameplay parity'
    result['files'] += [dict(path=str(path),sha256=sha(path.read_bytes())) for path in (out/'vga_state.json',out/'vga_state_restored.json')]
    if display_intro:
        dac_path=out/'intro_dac_readback.json';dac=json.loads(dac_path.read_text());info=[row['response'] for row in t if row['command']=='EXEC VGA DAC'];palette=[row['response'] for row in t if row['command']=='EXEC VGA DACPAL']
        assert info==[dac['info_response']] and palette==[dac['palette_response']]
        decoded=bytearray()
        for line in palette[0]:
            match=re.match(r'^([0-9A-Fa-f]{2}):\s+(.+)$',line)
            if not match:continue
            assert int(match[1],16)*3==len(decoded);entries=re.findall(r'[0-9A-Fa-f]{6}',match[2]);assert len(entries)==8;decoded.extend(bytes.fromhex(''.join(entries)))
        assert len(decoded)==768 and max(decoded)<=63 and 'bits=6' in '\n'.join(info[0]) and 'pel_mask=ffh' in '\n'.join(info[0])
        palrow=next(r for r in csv.DictReader((out/'inputs.csv').open()) if Path(r['source']).name.upper()=='GAME.PAL');game_palette=Path(palrow['source']).read_bytes();assert sha(game_palette)=='efd52442cbee3327d8cec045b31559049e8767b298c25674a557eb6e096a759f'
        assert decoded==bytes(n>>2 for n in game_palette[-768:])==(work/'palette_buffer_runtime.bin').read_bytes()
        cd_palette=bytes(n>>2 for n in asset[-768:]);used=set(pixels);different=[n for n in range(256) if decoded[n*3:n*3+3]!=cd_palette[n*3:n*3+3]]
        assert different==[255] and 255 not in used and all(decoded[n*3:n*3+3]==cd_palette[n*3:n*3+3] for n in used)
        ac='\n'.join(before['AC']);assert 'color-plane-en=0fh' in ac and 'disabled-by-index=0' in ac and 'disabled-by-idx1-bit5=0' in ac
        real_start=int(re.search(r'\breal-start=([0-9a-f]+)h',mode).group(1),16);assert real_start==(0x4000 if font0_intro else 0)
        result.update(optional_intro_display_branch_verified=True,display_start=0x4000,programmed_display_segment=0xa400,latched_display_start=real_start,display_selected_segment=0xa400 if font0_intro else 0xa000,latched_scanout_page_matches_asset=font0_intro,dac_register_readback_verified=True,dac_components_verified=768,dac_sha256=sha(decoded),used_palette_entries=len(used),used_pixel_dac6_matches_cd=True,unused_different_palette_indices=different)
        result['scope']+='; native page flip programs4000h plane offset; actual latched real-start=%04Xh; AC enabled, actualDAC768 components equal GAME.PALtail>>2 and all used CD colors quantized6bit; unused index255 differs; paused device-state evidence, no host screenshot or full scanout trace'%real_start
        result['files'].append(dict(path=str(dac_path),sha256=sha(dac_path.read_bytes())))
if font0_intro:
    assert display_intro and result['font2_runtime_verified'] and (work/'font_flags_runtime.bin').read_bytes()[0]==1
    length,offset=struct.unpack_from('<HI',uif,0);assert (length,offset)==(900,192);raw=uif[offset:offset+length];expected0=bytearray(raw);q=2;pointers0=[(0,load+0x20b9)]
    for glyph in range(1,128):
        height,width=raw[q:q+2];size=height*((width+7)//8);pointers0.append((q,load+0x20b9))
        for j in range(q+2,q+2+size):expected0[j]=int(format(raw[j],'08b')[::-1],2)
        q+=2+size
    assert q==900 and (work/'font0_block_runtime.bin').read_bytes()==expected0+b'\0'*300
    assert (work/'font0_pointers_runtime.bin').read_bytes()==b''.join(struct.pack('<HH',*pair) for pair in pointers0)
    result.update(font0_runtime_verified=True,font0_records=127,font0_pointer_slots=128,font0_source_bytes=900)
    result['scope']+='; font0 transformed900B plus300B observed tail and128FAR pointers exact at UI07C1 before wait0424; selected group0, cache flags0/2 set; no font1 or keyboard event proof'
(out/'independent_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
