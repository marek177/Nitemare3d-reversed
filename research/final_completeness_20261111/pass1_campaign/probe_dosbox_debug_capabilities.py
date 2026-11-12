"""python probe_dosbox_debug_capabilities.py DOSBOX_EXE GAME_EXE OUT WORK
Query debug capabilities while DEBUGBOX is paused at packed entry; never RUN.
"""
import ctypes,hashlib,json,os,re,shutil,socket,struct,subprocess,sys,time
from pathlib import Path
exe,game,out,work=map(lambda p:Path(p).resolve(),sys.argv[1:]);out.mkdir(parents=True,exist_ok=True);work.mkdir(parents=True,exist_ok=True);drive=work/'drive_c';drive.mkdir(exist_ok=True);raw=game.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(raw)=='552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301';assert sha(exe.read_bytes())=='a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832';(drive/'N3D20.EXE').write_bytes(raw)
server=socket.socket();server.bind(('127.0.0.1',0));port=server.getsockname()[1];server.listen(1);server.settimeout(10)
conf=out/'runtime.conf';conf.write_text('[sdl]\nfullscreen=false\noutput=surface\nwaitonerror=false\n[dosbox]\nmachine=svga_s3\nmcp_server='+str(port)+'\n[cpu]\ncore=normal\ncycles=fixed 20000\n[mixer]\nnosound=true\n[dos]\nautomount=false\nautomountall=false\n',encoding='ascii')
env=dict(os.environ);env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software');startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0;ctypes.windll.kernel32.SetErrorMode(0x8003)
args=[str(exe),'-defaultconf','-conf',str(conf),'-nogui','-console','-fastlaunch','-time-limit','20','-c','mount c "'+str(drive)+'"','-c','c:','-c','debugbox N3D20.EXE','-c','exit'];p=subprocess.Popen(args,cwd=str(work),env=env,startupinfo=startup,creationflags=0x10);conn=None;buffer=b'';transcript=[];nextid=0;success=False;error=None;result={}
def request(command):
 global nextid,buffer
 nextid+=1;key=str(nextid);conn.sendall(('REQ '+key+' '+command+'\n').encode('ascii'));lines=[]
 while True:
  while b'\n' not in buffer:
   part=conn.recv(65536)
   if not part:raise RuntimeError('debug control connection closed')
   buffer+=part
  line,buffer=buffer.split(b'\n',1);line=line.decode('utf-8',errors='replace').rstrip('\r');lines.append(line)
  if line=='END '+key:break
 transcript.append(dict(command=command,response=lines));return lines
def regs():
 lines=request('EXEC EV CS EIP DS ES SS SP AX BX CX DX');values=next((s.split() for s in reversed(lines) if re.fullmatch(r'[0-9A-Fa-f]+(?: [0-9A-Fa-f]+){9}',s)),None);assert values
 return dict(zip(('CS','IP','DS','ES','SS','SP','AX','BX','CX','DX'),map(lambda v:int(v,16),values)))
try:
 conn,address=server.accept();conn.settimeout(6);request('PING');time.sleep(1);before=regs();entryip,entrycs=struct.unpack_from('<HH',raw,0x14);load=before['DS']+16;assert before['CS']==load+entrycs and before['IP']==entryip
 help_lines=request('EXEC HELP');bpm=request('EXEC BPM 0000:00000024');listed=request('EXEC BPLIST');request('EXEC BPDEL *');after=regs();assert before==after
 help_text='\n'.join(help_lines);bpm_text='\n'.join(bpm);list_text='\n'.join(listed)
 result=dict(packed_entry=before,registers_unchanged=True,help_lists_BPM=bool(re.search(r'\bBPM\s+\[',help_text)),help_lists_LOG=bool(re.search(r'\bLOG\s+\[',help_text)),BPM_command_accepted='Set memory breakpoint' in bpm_text,BPM_listed=('BPMEM' in list_text or 'BPLM' in list_text),no_RUN_command=True,help_response_sha256=sha(help_text.encode()),BPM_response=bpm,breakpoint_list_response=listed);success=True
except Exception as e:error=repr(e)
finally:
 if conn:conn.close()
 server.close()
 if p.poll() is None:p.terminate()
 try:p.communicate(timeout=5)
 except subprocess.TimeoutExpired:p.kill();p.communicate()
 (out/'transcript.json').write_text(json.dumps(transcript,indent=2)+'\n');assert all(x['command'] not in ('EXEC RUN','BREAK') for x in transcript)
 result.update(success=success,error=error,exe_sha256=sha(exe.read_bytes()),game_sha256=sha(raw),game_source_unchanged=sha(game.read_bytes())==sha(raw),harness_sha256=sha(Path(__file__).read_bytes()),runtime_tests=0,new_deep_verified_bytes=0,scope='debugger capability probe paused at packed entry; no game instruction execution requested, not a gameplay runtime scenario')
 (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
