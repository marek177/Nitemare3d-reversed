"""Independent verification: python verify_dosbox_startup_capture.py IMAGE RELOCS RUNTIME_OUT WORK"""
import hashlib,json,struct,csv,sys
from pathlib import Path
image,relocs,out,work=map(lambda x:Path(x).resolve(),sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest();summary_path=out/'summary.json';s=json.loads(summary_path.read_text());assert s['success'] and s['runtime_tests']==1
stages={x['stage']:x for x in s['snapshots']};load=stages['packed_entry']['load_segment'];expected=bytearray(image.read_bytes());assert sha(expected)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';rows=list(csv.DictReader(relocs.open()))
for r in rows:struct.pack_into('<H',expected,int(r['image_offset']),(int(r['original_word'])+load)&65535)
actual=(work/'unpacked_runtime.bin').read_bytes();assert actual==expected and len(actual)==171360
bss=(work/'bss_runtime.bin').read_bytes();assert len(bss)==47584 and not any(bss)
entry=stages['crt_entry']['registers'];post=stages['post_crt_prefix']['registers'];packed=stages['packed_entry']['registers'];dg=load+0x2771
assert entry['CS']==post['CS']==load+0x11ee and entry['IP']==0x18 and post['IP']==0xb3
assert entry['SS']==load+0x3574 and entry['SP']==0x800 and entry['DS']==packed['DS']==load-0x10
assert post['DS']==post['SS']==post['ES']==dg and post['SP']==((0x800+0xe02e)&0xfffe)-4
state=(work/'state_runtime.bin').read_bytes();word=lambda off:struct.unpack_from('<H',state,off-0x20dc)[0]
assert word(0x20dc)==post['SP'] and word(0x20e2)==dg and word(0x211e)==load-0x10
assert word(0x2120)==((word(0x2122)&255)<<8)|(word(0x2122)>>8)
transcript=json.loads((out/'transcript.json').read_text());mode=s.get('mode','startup');expected_dumps={'startup':9,'game_entry':21,'initialization':37,'post_vga':56,'input_init':68,'episode_init':74,'palette_init':78}[mode]
assert any(x['command']=='EXEC RUN' for x in transcript) and sum('MEMDUMPBIN' in x['command'] for x in transcript)==expected_dumps
assert all(x['command']=='PING' or x['command'].startswith(('EXEC EV ','EXEC BP ','EXEC BPDEL ','EXEC RUN','EXEC MEMDUMPBIN ')) for x in transcript)
game_checks=False
if mode in ('game_entry','initialization','post_vga','input_init','episode_init','palette_init'):
    main=stages['game_main_entry']['registers'];after=stages['after_defaults_and_windir']['registers']
    assert main['CS']==after['CS']==load+0x476 and main['IP']==0x326 and after['IP']==0x35c
    assert main['DS']==main['SS']==dg and after['DS']==after['ES']==after['SS']==dg
    main_data=(work/'main_data.bin').read_bytes();argc,argv,envp,program_off,program_seg=struct.unpack_from('<5H',main_data)
    stack=(work/'main_stack.bin').read_bytes();assert struct.unpack('<5H',stack)==(0xdf,load+0x11ee,argc,argv,envp) and argc==1
    pointer,end=struct.unpack('<HH',(work/'argv_table.bin').read_bytes());assert pointer and end==0
    arg0=(work/'argv0.bin').read_bytes().split(b'\0',1)[0];program=(work/'program_name.bin').read_bytes().split(b'\0',1)[0]
    assert arg0==program==b'C:\\N3D20.EXE' and main['ES']==program_seg
    assert (work/'ivt_before.bin').read_bytes()==(work/'saved_ivt.bin').read_bytes() and struct.unpack('<HH',(work/'ivt_after.bin').read_bytes())==(0xe5,load+0x11ee)
    assert struct.unpack_from('<H',(work/'optional_init.bin').read_bytes(),4)[0]==0
    assert (work/'default_flag_before.bin').read_bytes()==b'\1' and (work/'default_flag_after.bin').read_bytes()==b'\0'
    config=(work/'config_state.bin').read_bytes();assert struct.unpack_from('<H',config,6)[0]==25 and config[19]==1 and after['AX']==0
    game_checks=True
init_checks=False
if mode in ('initialization','post_vga','input_init','episode_init','palette_init'):
    main_cs=load+0x476;bsf_cs=load+0x83d
    assert struct.unpack('<3H',(work/'bsf_entry_stack.bin').read_bytes())==(0xdf,main_cs,0)
    assert struct.unpack('<5H',(work/'bsf_xor_stack.bin').read_bytes())==(0x2a3a,bsf_cs,0x3638,dg,54)
    source_bsf=next(x for x in csv.DictReader((out/'inputs.csv').open()) if Path(x['source']).name.upper()=='NITE3D.BSF');original=Path(source_bsf['source']).read_bytes();assert sha(original)==source_bsf['sha256']
    encoded=(work/'bsf_encoded_runtime.bin').read_bytes();decoded=(work/'bsf_decoded_runtime.bin').read_bytes();key=image.read_bytes()[0x29755:0x29789]
    assert encoded==original[:54] and decoded==bytes(x^key[i%52] for i,x in enumerate(encoded)) and (work/'bsf_final_runtime.bin').read_bytes()==decoded
    assert stages['bsf_after_xor']['registers']['AX']&255==0 and stages['after_bsf_mode0']['registers']['IP']==0xdf
    ret,seg,name,count,expect=struct.unpack('<HHHIH',(work/'bsf_checksum_stack.bin').read_bytes());assert (ret,seg,name,count,expect&255)==(0x2a5d,bsf_cs,0x1663,0,decoded[1]) and decoded[3]==1
    assert (work/'bsf_checksum_filename.bin').read_bytes()==b'n3d.exe\0'
    assert struct.unpack('<3H',(work/'audio_entry_stack.bin').read_bytes())==(0xf3,main_cs,0)
    assert (work/'audio_active_before.bin').read_bytes()==b'\0\0\0' and (work/'audio_active_after.bin').read_bytes()==b'\1\1\1'
    assert struct.unpack('<3H',(work/'vga_entry_stack.bin').read_bytes())==(0x11b,main_cs,0)
    assert (work/'video_bda_before.bin').read_bytes()[0]==3 and (work/'video_bda_after.bin').read_bytes()[0]==0x13
    assert struct.unpack('<HH',(work/'video_page_segments.bin').read_bytes())==(0xa000,0xa400)
    table=(work/'vga_reciprocal_runtime.bin').read_bytes();assert table==b''.join(struct.pack('<I',0x400000//i) for i in range(1,512));init_checks=True
files=[work/'unpacked_runtime.bin',work/'bss_runtime.bin',work/'state_runtime.bin',out/'transcript.json',out/'snapshots.json',out/'inputs.csv',out/'runtime.conf',summary_path]
if game_checks:files += [work/(name+'.bin') for name in ['main_data','main_stack','argv_table','argv0','program_name','ivt_before','saved_ivt','ivt_after','optional_init','default_flag_before','default_flag_after','config_state']]
if init_checks:files += [work/(name+'.bin') for name in ['bsf_entry_stack','bsf_xor_stack','bsf_encoded_runtime','bsf_decoded_runtime','bsf_checksum_stack','bsf_checksum_filename','bsf_final_runtime','audio_entry_stack','audio_active_before','audio_options','audio_active_after','vga_entry_stack','video_bda_before','video_bda_after','video_page_segments','vga_reciprocal_runtime']]
post_checks=False
if mode in ('post_vga','input_init','episode_init','palette_init'):
    main_cs=load+0x476
    assert struct.unpack('<HH',(work/'slot_init_stack.bin').read_bytes())==(0x12d,main_cs)
    before=(work/'slots_before_init.bin').read_bytes();after=(work/'slots_after_init.bin').read_bytes();assert len(before)==len(after)==1800
    expected_slots=bytearray(before)
    for n in range(100):expected_slots[n*18]=1
    assert after==expected_slots and sum(a!=b for a,b in zip(before,after))==100
    for name,cs,ip in [('slot_initializer_entry',load+0x201,0xa),('after_slot_initializer',main_cs,0x12d),('resource_mode0_entry',load+0x768,0x24),('after_resource_mode0',main_cs,0x134)]:
        reg=stages[name]['registers'];assert reg['CS']==cs and reg['IP']==ip and reg['DS']==reg['SS']==dg
    assert struct.unpack('<HHH',(work/'resource_init_stack.bin').read_bytes())==(0x134,main_cs,0)
    pointers=(work/'resource_pointers.bin').read_bytes();assert len(pointers)==56
    addresses=[]
    for n in range(14):
        off,seg=struct.unpack_from('<HH',pointers,n*4);assert off or seg;addresses.append(seg*16+off)
        header=work/('resource_header_%02d.bin'%n);assert header.read_bytes()==b'\0'*6;files.append(header)
    assert len(set(addresses))==14
    files += [work/(name+'.bin') for name in ['slot_init_stack','slots_before_init','slots_after_init','resource_init_stack','resource_pointers']];post_checks=True
input_checks=False
if mode in ('input_init','episode_init','palette_init'):
    main_cs=load+0x476;input_cs=load+0x6b0
    assert struct.unpack('<HHH',(work/'keyboard_entry_stack.bin').read_bytes())==(0x148,main_cs,0)
    assert (work/'input_flags_before.bin').read_bytes()==b'\0\0' and (work/'input_flags_after_keyboard.bin').read_bytes()==b'\1\0'
    assert (work/'ivt9_before.bin').read_bytes()==(work/'saved_ivt9.bin').read_bytes() and struct.unpack('<HH',(work/'ivt9_after.bin').read_bytes())==(0,input_cs)
    assert struct.unpack('<HHH',(work/'aux_entry_stack.bin').read_bytes())==(0x15c,main_cs,0)
    probe=struct.unpack_from('<H',(work/'aux_regs_after_probe.bin').read_bytes())[0]
    assert stages['after_aux_probe']['registers']['AX']==probe and (work/'aux_available_after.bin').read_bytes()==bytes([int(probe>=1)])
    assert (work/'input_flags_after_aux.bin').read_bytes()==b'\1\1'
    for name,cs,ip in [('keyboard_mode0_entry',input_cs,0x134),('after_keyboard_mode0',main_cs,0x148),('aux_mode0_entry',input_cs,0x18c),('after_aux_probe',input_cs,0x1a8),('after_aux_mode0',main_cs,0x15c)]:
        reg=stages[name]['registers'];assert reg['CS']==cs and reg['IP']==ip and reg['DS']==reg['SS']==dg
    files += [work/(name+'.bin') for name in ['keyboard_entry_stack','ivt9_before','input_flags_before','ivt9_after','saved_ivt9','input_flags_after_keyboard','aux_entry_stack','aux_regs_before','aux_available_before','aux_regs_after_probe','input_flags_after_aux','aux_available_after']];input_checks=True
episode_checks=False
if mode in ('episode_init','palette_init'):
    main_cs=load+0x476;ui_cs=load+0xd29
    assert struct.unpack('<HH',(work/'episode_probe_stack.bin').read_bytes())==(0x16e,main_cs)
    filename_offset=(stages['episode_probe_entry']['registers']['SP']-18)&65535
    assert (work/'episode_filename.bin').read_bytes().split(b'\0',1)[0]==b'map.1'
    assert struct.unpack('<HHHH',(work/'episode_access_stack.bin').read_bytes())==(0x26bc,ui_cs,filename_offset,4)
    assert stages['episode_access_return']['registers']['AX']==0
    probe=stages['episode_bsf_mode1_return']['registers'];assert (probe['AX'],probe['DX'])==(0x363b,dg)
    assert stages['episode_probe_return']['registers']['AX']==1
    assert struct.unpack('<HHH',(work/'episode_prepare_stack.bin').read_bytes())==(0x174,main_cs,1)
    assert (work/'episode_global.bin').read_bytes()==b'\1\0'
    names=(work/'episode_asset_names.bin').read_bytes();assert [names[n:n+16].split(b'\0',1)[0] for n in (0,16,32)]==[b'map.1',b'img.1',b'demo.1']
    for name,cs,ip in [('episode_probe_entry',ui_cs,0x2696),('episode_filename_formatted',ui_cs,0x26ae),('episode_access_entry',load+0x11ee,0x3990),('episode_access_return',ui_cs,0x26bc),('episode_bsf_mode1_return',ui_cs,0x26ca),('episode_probe_return',main_cs,0x16e),('episode_prepare_entry',load+0x277,0x336),('episode_prepare_return',main_cs,0x174)]:
        reg=stages[name]['registers'];assert reg['CS']==cs and reg['IP']==ip and reg['DS']==reg['SS']==dg
    files += [work/(name+'.bin') for name in ['episode_probe_stack','episode_filename','episode_access_stack','episode_prepare_stack','episode_global','episode_asset_names']];episode_checks=True
palette_checks=False
if mode=='palette_init':
    main_cs=load+0x476;data_cs=load+0x277
    assert struct.unpack('<HH',(work/'palette_loader_stack.bin').read_bytes())==(0x17c,main_cs)
    retip,retcs,handle,lo,hi,origin=struct.unpack('<6H',(work/'palette_seek_stack.bin').read_bytes());assert (retip,retcs,lo,hi,origin)==(0x2dd,data_cs,0xfd00,0xffff,2)
    source=next(x for x in csv.DictReader((out/'inputs.csv').open()) if Path(x['source']).name.upper()=='GAME.PAL');asset=Path(source['source']).read_bytes();assert sha(asset)==source['sha256']=='efd52442cbee3327d8cec045b31559049e8767b298c25674a557eb6e096a759f'
    reg=stages['palette_seek_return']['registers'];assert (reg['DX']<<16)|reg['AX']==len(asset)-768==1156
    assert struct.unpack('<3H',(work/'palette_dac_stack.bin').read_bytes())==(0x31d,data_cs,0x4a64)
    assert (work/'palette_converted_runtime.bin').read_bytes()==bytes(n>>2 for n in asset[-768:])
    for name,cs,ip in [('palette_loader_entry',data_cs,0x2a6),('palette_seek_entry',load+0x11ee,0x1bd6),('palette_seek_return',data_cs,0x2dd),('palette_dac_entry',load+0x156,0x12a),('palette_loader_return',main_cs,0x17c)]:
        reg=stages[name]['registers'];assert reg['CS']==cs and reg['IP']==ip and reg['DS']==reg['SS']==dg
    files += [work/(name+'.bin') for name in ['palette_loader_stack','palette_seek_stack','palette_dac_stack','palette_converted_runtime']];palette_checks=True
result=dict(verified=True,summary_sha256=sha(summary_path.read_bytes()),game_exe_sha256=s['game_source_sha256'],dosbox_exe_sha256=s['exe_sha256'],load_segment=load,relocations=len(rows),runtime_image_bytes=len(actual),runtime_image_sha256=sha(actual),bss_zero_bytes=len(bss),register_checks_passed=True,game_entry_checks_passed=game_checks,initialization_checks_passed=init_checks,post_vga_checks_passed=post_checks,input_initialization_checks_passed=input_checks,episode_checks_passed=episode_checks,palette_checks_passed=palette_checks,runtime_tests=1,new_deep_verified_bytes=0,files=[dict(path=str(p),sha256=sha(p.read_bytes())) for p in files],scope='one actual DOSBox-X built-in-DOS original EXE '+('palette tail seek/conversion and DAC routine return' if palette_checks else 'episode selection/access/BSFmode1 and asset-name preparation' if episode_checks else 'keyboard/auxiliary initialization' if input_checks else 'post-VGA slot/resource initialization' if post_checks else 'BSF/audio/VGA initialization' if init_checks else 'game-entry/CRT/defaults' if game_checks else 'startup')+' capture, not full gameplay, audio-output, rendered-frame or original hardware parity')
(out/'independent_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
