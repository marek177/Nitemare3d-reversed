"""python runtime_dosbox_startup.py DOSBOX_EXE GAME_DIR IMAGE RELOCATIONS OUT WORK [startup|game_entry|initialization]"""
import ctypes,csv,hashlib,json,os,re,shutil,socket,struct,subprocess,sys,time
from pathlib import Path
exe,source,image,relocations,out,work=map(lambda x:Path(x).resolve(),sys.argv[1:7]);mode=sys.argv[7] if len(sys.argv)>7 else 'startup';assert mode in ('startup','game_entry','initialization','post_vga','input_init','episode_init','palette_init');out.mkdir(parents=True,exist_ok=True);work.mkdir(parents=True,exist_ok=True);drive=work/'drive_c';drive.mkdir(exist_ok=True)
sha=lambda x:hashlib.sha256(x).hexdigest();canonical=image.read_bytes();assert sha(canonical)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
names=['N3D-UNFU.exe','N3d.exe','NITE3D.BSF','GAME.PAL','SND.DAT','UIF.DAT','ENDING.FLI']+[prefix+'.'+str(ep) for prefix in ('MAP','IMG','DEMO','WALLS','OBJECTS') for ep in (1,2,3)]
inputs=[]
for name in names:
    p=source/name;raw=p.read_bytes();target=drive/('N3D20.EXE' if name=='N3D-UNFU.exe' else name);target.write_bytes(raw);inputs.append(dict(source=str(p),copy=str(target),bytes=len(raw),sha256=sha(raw)))
packed=(drive/'N3D20.EXE').read_bytes();assert sha(packed)=='552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301';entry_ip,entry_cs=struct.unpack_from('<HH',packed,0x14)
with (out/'inputs.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(inputs[0]));w.writeheader();w.writerows(inputs)
server=socket.socket();server.bind(('127.0.0.1',0));port=server.getsockname()[1];server.listen(1);server.settimeout(10)
conf=out/'runtime.conf';conf.write_text('[sdl]\nfullscreen=false\noutput=surface\nwaitonerror=false\n[log]\nlogfile='+str(out/'dosbox.log')+'\n[dosbox]\nmachine=svga_s3\nmemsize=16\nmcp_server='+str(port)+'\n[cpu]\ncore=normal\ncycles=fixed 20000\n[mixer]\nnosound=true\n[dos]\nautomount=false\nautomountall=false\n',encoding='ascii')
args=[str(exe),'-defaultconf','-conf',str(conf),'-nogui','-console','-fastlaunch','-log-con','-log-fileio','-time-limit','30','-c','mount c "'+str(drive)+'"','-c','c:','-c','debugbox N3D20.EXE','-c','exit']
env=dict(os.environ);env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software');startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0;ctypes.windll.kernel32.SetErrorMode(0x8003)
p=subprocess.Popen(args,cwd=str(work),env=env,startupinfo=startup,creationflags=0x10);transcript=[];snapshots=[];conn=None;error=None;success=False;nextid=0;buffer=b'';checks={}
def request(command):
    global nextid,buffer
    nextid+=1;key=str(nextid);conn.sendall(('REQ '+key+' '+command+'\n').encode('ascii'));data=[]
    while True:
        while b'\n' not in buffer:
            piece=conn.recv(65536)
            if not piece:raise RuntimeError('debug control connection closed')
            buffer+=piece
        line,buffer=buffer.split(b'\n',1);line=line.decode('utf-8',errors='replace').rstrip('\r');data.append(line)
        if line=='END '+key:break
    transcript.append(dict(id=key,command=command,response=data));assert 'BEGIN '+key+' OK' in data,(command,data);return data
def regs():
    response=request('EXEC EV CS EIP DS ES SS SP AX BX CX DX')
    values=next((line.split() for line in reversed(response) if re.fullmatch(r'[0-9a-fA-F]+(?: [0-9a-fA-F]+){9}',line)),None)
    if not values:raise RuntimeError('unrecognized register response '+repr(response))
    return dict(zip(('CS','IP','DS','ES','SS','SP','AX','BX','CX','DX'),map(lambda x:int(x,16),values)))
def wait_for(cs,ip,seconds=6):
    until=time.monotonic()+seconds;latest=None
    while time.monotonic()<until:
        latest=regs()
        if latest['CS']==cs and latest['IP']==ip:return latest
        time.sleep(.05)
    raise RuntimeError('breakpoint not reached '+repr((cs,ip,latest)))
def dump(seg,off,n,name):
    result=bytearray();linear=(seg<<4)+off
    while len(result)<n:
        address=linear+len(result);count=min(0x8000,n-len(result));path=work/(name+'.part%d'%len(result))
        request('EXEC MEMDUMPBIN %04X:%08X %08X %s'%(address>>4,address&15,count,str(path)));raw=path.read_bytes();assert len(raw)==count;result.extend(raw)
    (work/name).write_bytes(result);return bytes(result)
try:
    conn,address=server.accept();conn.settimeout(6);request('PING');time.sleep(1)
    assert p.poll() is None,('emulator exited before register request',p.returncode)
    # DEBUGBOX should stop at the packed executable entry before running its stub.
    deadline=time.monotonic()+6;initial=None
    while time.monotonic()<deadline:
        r=regs();load=(r['DS']+0x10)&65535
        if r['CS']==load+entry_cs and r['IP']==entry_ip:initial=r;break
        time.sleep(.05)
    assert initial is not None,('packed entry not reached',r,entry_cs,entry_ip)
    snapshots.append(dict(stage='packed_entry',registers=initial,load_segment=load));crt=load+0x11ee
    request('EXEC BP %04X:00000018'%crt);request('EXEC RUN');entry=wait_for(crt,0x18);snapshots.append(dict(stage='crt_entry',registers=entry))
    actual=dump(load,0,len(canonical),'unpacked_runtime.bin');expected=bytearray(canonical)
    for row in csv.DictReader(relocations.open()):struct.pack_into('<H',expected,int(row['image_offset']),(int(row['original_word'])+load)&65535)
    differences=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
    assert not differences,('runtime unpack image differs',differences[:20]);checks['unpacked_image_exact_after_relocations']=True;checks['runtime_unpacked_sha256']=sha(actual)
    request('EXEC BPDEL *');request('EXEC BP %04X:000000B3'%crt);request('EXEC RUN');post=wait_for(crt,0xb3);snapshots.append(dict(stage='post_crt_prefix',registers=post))
    dg=load+0x2771;assert post['DS']==post['ES']==post['SS']==dg
    bss=dump(dg,0x2650,0xe030-0x2650,'bss_runtime.bin');assert not any(bss);state=dump(dg,0x20dc,0x48,'state_runtime.bin')
    get=lambda off:struct.unpack_from('<H',state,off-0x20dc)[0]
    assert get(0x20dc)==post['SP'] and get(0x20e2)==dg and get(0x211e)==initial['DS'];checks.update(segment_equality_at_B3=True,bss_zero_bytes=len(bss),bss_sha256=sha(bss),stack_snapshot=get(0x20dc),saved_psp=get(0x211e),dos_version_ax=get(0x2122),dos_version_swapped=get(0x2120))
    assert get(0x2120)==((get(0x2122)&255)<<8)|(get(0x2122)>>8)
    if mode in ('game_entry','initialization','post_vga','input_init','episode_init','palette_init'):
        ivt_before=dump(0,0,4,'ivt_before.bin');optional=dump(dg,0x252e,0x22,'optional_init.bin');assert struct.unpack_from('<H',optional,4)[0]==0
        request('EXEC BPDEL *');main_cs=load+0x476;request('EXEC BP %04X:00000326'%main_cs);request('EXEC RUN');main=wait_for(main_cs,0x326);snapshots.append(dict(stage='game_main_entry',registers=main))
        assert main['DS']==main['SS']==dg
        main_data=dump(dg,0x213e,0x1a,'main_data.bin');argc,argv,envp,program_off,program_seg=struct.unpack_from('<5H',main_data)
        stack=dump(main['SS'],main['SP'],10,'main_stack.bin');return_ip,return_cs,arg_argc,arg_argv,arg_envp=struct.unpack('<5H',stack)
        assert (return_ip,return_cs,arg_argc,arg_argv,arg_envp)==(0xdf,crt,argc,argv,envp) and argc==1
        argv_table=dump(dg,argv,4,'argv_table.bin');arg0,end=struct.unpack('<HH',argv_table);assert end==0
        argv_bytes=dump(dg,arg0,80,'argv0.bin');argv0=argv_bytes.split(b'\0',1)[0].decode('ascii');assert argv0.upper().endswith('N3D20.EXE')
        program_bytes=dump(program_seg,program_off,80,'program_name.bin');program_name=program_bytes.split(b'\0',1)[0].decode('ascii');assert program_name.upper().endswith('N3D20.EXE')
        ivt_after=dump(0,0,4,'ivt_after.bin');saved_ivt=dump(dg,0x210a,4,'saved_ivt.bin');assert saved_ivt==ivt_before and struct.unpack('<HH',ivt_after)==(0xe5,crt)
        flag_before=dump(dg,0x82a,1,'default_flag_before.bin');assert flag_before==b'\x01'
        request('EXEC BPDEL *');request('EXEC BP %04X:0000035C'%main_cs);request('EXEC RUN');defaults=wait_for(main_cs,0x35c);snapshots.append(dict(stage='after_defaults_and_windir',registers=defaults))
        flag_after=dump(dg,0x82a,1,'default_flag_after.bin');config_state=dump(dg,0x3cbc,0x22,'config_state.bin');assert flag_after==b'\0'
        assert struct.unpack_from('<H',config_state,0x3cc2-0x3cbc)[0]==25 and config_state[0x3ccf-0x3cbc]==1 and defaults['AX']==0
        checks.update(game_main_arguments_match_globals=True,argc=argc,argv=argv,envp=envp,argv0=argv0,program_name=program_name,optional_init_pointer_zero=True,int0_saved_and_replaced=True,int0_old_hex=ivt_before.hex(),int0_new_hex=ivt_after.hex(),default_flag_before=1,default_flag_after=0,default_rate=25,windir_getenv_result=0,mode=mode)
    if mode in ('initialization','post_vga','input_init','episode_init','palette_init'):
        bsf_cs=load+0x83d;xor_cs=load+0xfba;audio_cs=load+0xc2b;vga_cs=load+0x156
        def advance(seg,ip,stage,seconds=8):
            request('EXEC BPDEL *');request('EXEC BP %04X:%08X'%(seg,ip));request('EXEC RUN');reg=wait_for(seg,ip,seconds);snapshots.append(dict(stage=stage,registers=reg));return reg
        bsf_entry=advance(bsf_cs,0x29ca,'bsf_mode0_entry');bsf_args=dump(bsf_entry['SS'],bsf_entry['SP'],6,'bsf_entry_stack.bin');assert struct.unpack('<3H',bsf_args)==(0xdf,main_cs,0)
        xor_entry=advance(xor_cs,0x1b2,'bsf_header_xor_entry');xor_args=dump(xor_entry['SS'],xor_entry['SP'],10,'bsf_xor_stack.bin');assert struct.unpack('<5H',xor_args)==(0x2a3a,bsf_cs,0x3638,dg,54)
        encoded_header=dump(dg,0x3638,54,'bsf_encoded_runtime.bin');asset=(drive/'NITE3D.BSF').read_bytes();assert encoded_header==asset[:54]
        xor_after=advance(bsf_cs,0x2a3d,'bsf_after_xor');assert xor_after['AX']&255==0
        decoded_header=dump(dg,0x3638,54,'bsf_decoded_runtime.bin');key=canonical[0x29755:0x29789];assert decoded_header==bytes(x^key[i%52] for i,x in enumerate(encoded_header))
        checksum_entry=advance(bsf_cs,0x28ee,'bsf_exe_checksum_entry');checksum_args=dump(checksum_entry['SS'],checksum_entry['SP'],12,'bsf_checksum_stack.bin');ret_ip,ret_cs,filename,count,expected_checksum=struct.unpack('<HHHIH',checksum_args)
        assert (ret_ip,ret_cs,filename,count)==(0x2a5d,bsf_cs,0x1663,0) and expected_checksum&255==decoded_header[1]
        checksum_name=dump(dg,filename,8,'bsf_checksum_filename.bin');assert checksum_name==b'n3d.exe\0'
        after_bsf=advance(main_cs,0xdf,'after_bsf_mode0',12);bsf_final=dump(dg,0x3638,54,'bsf_final_runtime.bin');assert bsf_final==decoded_header and decoded_header[3]!=0
        audio_entry=advance(audio_cs,0xdc,'audio_mode0_entry');audio_args=dump(audio_entry['SS'],audio_entry['SP'],6,'audio_entry_stack.bin');assert struct.unpack('<3H',audio_args)==(0xf3,main_cs,0)
        audio_before=dump(dg,0x17cd,3,'audio_active_before.bin');audio_options=dump(dg,0x414a,8,'audio_options.bin')
        audio_after=advance(main_cs,0xf3,'after_audio_mode0',12);audio_state=dump(dg,0x17cd,3,'audio_active_after.bin')
        vga_entry=advance(vga_cs,0xd8,'vga_mode0_entry');vga_args=dump(vga_entry['SS'],vga_entry['SP'],6,'vga_entry_stack.bin');assert struct.unpack('<3H',vga_args)==(0x11b,main_cs,0)
        video_before=dump(0x40,0x49,3,'video_bda_before.bin')
        vga_after=advance(main_cs,0x11b,'after_vga_mode0',12);video_after=dump(0x40,0x49,3,'video_bda_after.bin');assert video_after[0]==0x13
        pages=dump(dg,0x12c,4,'video_page_segments.bin');assert struct.unpack('<HH',pages)==(0xa000,0xa400)
        reciprocal=dump(dg,0x2656,0x7fc,'vga_reciprocal_runtime.bin');expected_table=b''.join(struct.pack('<I',0x400000//i) for i in range(1,512));assert reciprocal==expected_table
        checks.update(bsf_encoded_header_sha256=sha(encoded_header),bsf_decoded_header_sha256=sha(decoded_header),bsf_header_xor_result=0,bsf_registered_flag=decoded_header[3],bsf_exe_checksum_expected=expected_checksum&255,bsf_checksum_file='n3d.exe',bsf_mode0_returned=True,audio_active_before=list(audio_before),audio_active_after=list(audio_state),audio_options_hex=audio_options.hex(),video_mode_before=video_before[0],video_mode_after=video_after[0],video_page_segments=[0xa000,0xa400],vga_reciprocal_entries=511,vga_reciprocal_bytes=len(reciprocal),vga_reciprocal_sha256=sha(reciprocal))
    if mode in ('post_vga','input_init','episode_init','palette_init'):
        slot_entry=advance(load+0x201,0xa,'slot_initializer_entry');assert slot_entry['DS']==slot_entry['SS']==dg
        slot_stack=dump(dg,slot_entry['SP'],4,'slot_init_stack.bin');assert struct.unpack('<HH',slot_stack)==(0x12d,main_cs)
        slot_before=dump(dg,0x50f2,1800,'slots_before_init.bin')
        slot_after_regs=advance(main_cs,0x12d,'after_slot_initializer');slot_after=dump(dg,0x50f2,1800,'slots_after_init.bin');expected=bytearray(slot_before)
        for n in range(100):expected[n*18]=1
        assert slot_after==expected
        resource_entry=advance(load+0x768,0x24,'resource_mode0_entry');resource_stack=dump(resource_entry['SS'],resource_entry['SP'],6,'resource_init_stack.bin');assert struct.unpack('<HHH',resource_stack)==(0x134,main_cs,0)
        resource_after=advance(main_cs,0x134,'after_resource_mode0',12);resource_pointers=dump(dg,0x34cc,56,'resource_pointers.bin');pointer_values=[]
        for n in range(14):
            off,seg=struct.unpack_from('<HH',resource_pointers,n*4);assert off or seg
            header=dump(seg,off,6,'resource_header_%02d.bin'%n);assert header==b'\0'*6;pointer_values.append(dict(index=n,offset=off,segment=seg,header_sha256=sha(header)))
        checks.update(slot_initializer_exact=True,slot_initializer_slots=100,slot_bytes_changed=sum(a!=b for a,b in zip(slot_before,slot_after)),slot_before_sha256=sha(slot_before),slot_after_sha256=sha(slot_after),resource_mode0_returned=True,resource_pointers=pointer_values)
    if mode in ('input_init','episode_init','palette_init'):
        input_cs=load+0x6b0
        key_entry=advance(input_cs,0x134,'keyboard_mode0_entry');key_stack=dump(dg,key_entry['SP'],6,'keyboard_entry_stack.bin');assert struct.unpack('<HHH',key_stack)==(0x148,main_cs,0)
        ivt9_before=dump(0,0x24,4,'ivt9_before.bin');flags_before=dump(dg,0xb3e,2,'input_flags_before.bin');assert flags_before==b'\0\0'
        key_after=advance(main_cs,0x148,'after_keyboard_mode0');ivt9_after=dump(0,0x24,4,'ivt9_after.bin');saved9=dump(dg,0x3f52,4,'saved_ivt9.bin');key_flags=dump(dg,0xb3e,2,'input_flags_after_keyboard.bin');assert saved9==ivt9_before and struct.unpack('<HH',ivt9_after)==(0,input_cs) and key_flags==b'\1\0'
        aux_entry=advance(input_cs,0x18c,'aux_mode0_entry');aux_stack=dump(dg,aux_entry['SP'],6,'aux_entry_stack.bin');assert struct.unpack('<HHH',aux_stack)==(0x15c,main_cs,0)
        aux_before=dump(dg,0x3f56,16,'aux_regs_before.bin');available_before=dump(dg,0x414c,1,'aux_available_before.bin')
        aux_probe=advance(input_cs,0x1a8,'after_aux_probe');aux_result=dump(dg,0x3f56,16,'aux_regs_after_probe.bin');probe_value=struct.unpack_from('<H',aux_result)[0];assert aux_probe['AX']==probe_value
        aux_after=advance(main_cs,0x15c,'after_aux_mode0');aux_flags=dump(dg,0xb3e,2,'input_flags_after_aux.bin');available_after=dump(dg,0x414c,1,'aux_available_after.bin');assert aux_flags==b'\1\1' and available_after==bytes([int(probe_value>=1)])
        checks.update(keyboard_ivt9_saved_and_installed=True,ivt9_old_hex=ivt9_before.hex(),ivt9_new_hex=ivt9_after.hex(),input_flags_after_aux=list(aux_flags),aux_probe_ax=probe_value,aux_available_before=available_before[0],aux_available_after=available_after[0])
    if mode in ('episode_init','palette_init'):
        ui_cs=load+0xd29;data_cs=load+0x277
        episode_entry=advance(ui_cs,0x2696,'episode_probe_entry');assert episode_entry['DS']==episode_entry['SS']==dg
        episode_stack=dump(dg,episode_entry['SP'],4,'episode_probe_stack.bin');assert struct.unpack('<HH',episode_stack)==(0x16e,main_cs)
        formatted=advance(ui_cs,0x26ae,'episode_filename_formatted');filename_offset=(formatted['SP']+0x0a)&65535
        # ENTER16 + saved SI + eight arguments; BP=SP+26 before ADD SP,8.
        filename_offset=(formatted['SP']+0x0a)&65535
        episode_filename=dump(dg,filename_offset,16,'episode_filename.bin');assert episode_filename.split(b'\0',1)[0]==b'map.1'
        access_entry=advance(crt,0x3990,'episode_access_entry');access_stack=dump(dg,access_entry['SP'],8,'episode_access_stack.bin');assert struct.unpack('<HHHH',access_stack)==(0x26bc,ui_cs,filename_offset,4)
        after_access=advance(ui_cs,0x26bc,'episode_access_return');assert after_access['AX']==0
        after_bsf_probe=advance(ui_cs,0x26ca,'episode_bsf_mode1_return');assert (after_bsf_probe['AX'],after_bsf_probe['DX'])==(0x363b,dg)
        episode_result=advance(main_cs,0x16e,'episode_probe_return');assert episode_result['AX']==1
        prepare_entry=advance(data_cs,0x336,'episode_prepare_entry');prepare_stack=dump(dg,prepare_entry['SP'],6,'episode_prepare_stack.bin');assert struct.unpack('<HHH',prepare_stack)==(0x174,main_cs,1)
        prepared=advance(main_cs,0x174,'episode_prepare_return',12);episode_global=dump(dg,0x626a,2,'episode_global.bin');episode_names=dump(dg,0x627c,48,'episode_asset_names.bin');assert episode_global==b'\1\0'
        names=[episode_names[i:i+16].split(b'\0',1)[0].decode('ascii') for i in (0,16,32)];assert names==['map.1','img.1','demo.1']
        checks.update(episode_probe_result=1,episode_access_return=0,episode_filename_offset=filename_offset,episode_filename='map.1',episode_bsf_pointer=[0x363b,dg],episode_asset_names=names)
    if mode=='palette_init':
        palette_entry=advance(data_cs,0x2a6,'palette_loader_entry');palette_stack=dump(dg,palette_entry['SP'],4,'palette_loader_stack.bin');assert struct.unpack('<HH',palette_stack)==(0x17c,main_cs)
        palette_seek=advance(crt,0x1bd6,'palette_seek_entry');palette_seek_stack=dump(dg,palette_seek['SP'],12,'palette_seek_stack.bin');retip,retcs,handle,lo,hi,origin=struct.unpack('<6H',palette_seek_stack);assert (retip,retcs,lo,hi,origin)==(0x2dd,data_cs,0xfd00,0xffff,2)
        palette_seek_return=advance(data_cs,0x2dd,'palette_seek_return');palette_source=(drive/'GAME.PAL').read_bytes();position=len(palette_source)-768;assert (palette_seek_return['DX']<<16)|palette_seek_return['AX']==position
        palette_dac_entry=advance(vga_cs,0x12a,'palette_dac_entry');palette_dac_stack=dump(dg,palette_dac_entry['SP'],6,'palette_dac_stack.bin');assert struct.unpack('<3H',palette_dac_stack)==(0x31d,data_cs,0x4a64)
        palette_runtime=dump(dg,0x4a64,768,'palette_converted_runtime.bin');assert palette_runtime==bytes(n>>2 for n in palette_source[-768:])
        palette_after=advance(main_cs,0x17c,'palette_loader_return');checks.update(palette_seek_offset=-768,palette_seek_origin=2,palette_file_position=position,palette_buffer_sha256=sha(palette_runtime),palette_dac_routine_returned=True,palette_io_handle=handle)
    success=True
except Exception as e:error=repr(e)
finally:
    if conn:conn.close()
    server.close()
    terminated_by_harness=p.poll() is None
    if terminated_by_harness:p.terminate()
    try:stdout,stderr=p.communicate(timeout=5)
    except subprocess.TimeoutExpired:p.kill();stdout,stderr=p.communicate()
    (out/'stdout.txt').write_bytes(stdout or b'');(out/'stderr.txt').write_bytes(stderr or b'');(out/'transcript.json').write_text(json.dumps(transcript,indent=2)+'\n');(out/'snapshots.json').write_text(json.dumps(snapshots,indent=2)+'\n')
    source_unchanged=all(sha(Path(x['source']).read_bytes())==x['sha256'] for x in inputs);assert source_unchanged
    stop_scope={'startup':'CRT B3','game_entry':'game main entry and first defaults/getenv','initialization':'BSF/audio/VGA initialization and all511 reciprocal entries','post_vga':'post-VGA slot initializer and resource mode0 return','input_init':'keyboard IRQ9 installation and auxiliary probe/mode0 return','episode_init':'episode probe/access/BSFmode1 and asset-name preparation','palette_init':'palette tail seek, converted768B buffer, native DAC routine and return'}[mode]
    result=dict(success=success,error=error,mode=mode,harness_sha256=sha(Path(__file__).read_bytes()),exe_sha256=sha(exe.read_bytes()),game_source_sha256=sha(packed),config_sha256=sha(conf.read_bytes()),args=args,snapshots=snapshots,checks=checks,source_files_unchanged=source_unchanged,terminated_by_harness=terminated_by_harness,process_returncode=p.returncode,runtime_tests=1 if success else 0,scope='original packed DOS2 EXE under actual DOSBox-X built-in DOS; debugger stops through '+stop_scope+'; no seeded game registers, mocked game functions, or patched file; not gameplay/renderer/audio-output/Win16 parity')
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
