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
args=[str(exe),'-defaultconf','-conf',str(conf),'-nogui','-console','-fastlaunch','-log-con','-log-fileio','-time-limit','30','-c','mount c "'+str(drive)+'"','-c','c:','-c','autotype -w 15 -p 10 space space space','-c','debugbox N3D20.EXE','-c','exit']
env=dict(os.environ);env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software');startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0;ctypes.windll.kernel32.SetErrorMode(0x8003)
(out/'launch_arguments.json').write_text(json.dumps(args,indent=2)+'\n')
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
