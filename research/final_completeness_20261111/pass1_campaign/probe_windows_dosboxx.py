"""python probe_windows_dosboxx.py EXE OUT WORKDIR"""
import ctypes,hashlib,json,os,subprocess,sys,time
from pathlib import Path
exe,out,work=map(lambda x:Path(x).resolve(),sys.argv[1:]);out.mkdir(parents=True,exist_ok=True);work.mkdir(parents=True,exist_ok=True);drive=work/'drive_c';drive.mkdir(exist_ok=True)
log=out/'dosbox.log';conf=out/'smoke.conf';conf.write_text('[sdl]\nfullscreen=false\noutput=surface\nwaitonerror=false\n[log]\nlogfile='+str(log)+'\n[dosbox]\nmachine=svga_s3\nmemsize=16\n[cpu]\ncore=normal\ncycles=fixed 10000\n[mixer]\nnosound=true\n[dos]\nautomount=false\nautomountall=false\n',encoding='ascii')
args=[str(exe),'-defaultconf','-conf',str(conf),'-nogui','-noconsole','-fastlaunch','-log-con','-time-limit','8','-c','mount c "'+str(drive)+'"','-c','c:','-c','echo N3D_RUNTIME_SMOKE_OK>SMOKE.TXT','-c','exit']
env=dict(os.environ);env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software')
startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0;ctypes.windll.kernel32.SetErrorMode(0x8003)
t=time.monotonic();p=subprocess.Popen(args,cwd=str(work),env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,startupinfo=startup,creationflags=0x08000000);timed_out=False
try:stdout,stderr=p.communicate(timeout=18)
except subprocess.TimeoutExpired:timed_out=True;p.kill();stdout,stderr=p.communicate()
(out/'stdout.txt').write_bytes(stdout);(out/'stderr.txt').write_bytes(stderr)
marker=drive/'SMOKE.TXT';s=dict(exe=str(exe),exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),args=args,environment_overrides={k:env[k] for k in ['SDL_VIDEODRIVER','SDL_AUDIODRIVER','SDL_RENDER_DRIVER']},returncode=p.returncode,timed_out=timed_out,elapsed_seconds=time.monotonic()-t,marker_exists=marker.exists(),marker_text=marker.read_text(errors='replace') if marker.exists() else '',game_runtime_tests=0,scope='DOSBox-X host/command smoke only; original game not launched')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
