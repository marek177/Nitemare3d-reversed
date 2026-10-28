from pathlib import Path
import struct,json,itertools,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;b=(root/'analysis/inputs/DOS18.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
for k in range(h[3]):
 off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
def s16(v):return ((v+32768)&65535)-32768
def model(diff,rng,kind,mode,special,difficulty):
 v=s16(s16(diff<<3)+rng%25)
 if kind in [12,29]:v>>=3
 elif kind==13:v>>=(1 if mode==1 else 3)
 elif kind in [14,17,20]:v>>=(1 if mode==2 else 3)
 elif kind in [15,16]:v>>=(8 if mode==1 else 1)
 elif kind in [18,19]:v>>=2
 elif kind in [21,25]:v=0
 elif kind==22:v=3 if special==3 else 0
 elif kind==23:v>>=(8 if mode==1 else 2)
 elif kind==24:v>>=(8 if mode==1 else 4 if mode==2 else 3)
 elif kind==26:v=(v>>1) if mode==1 else 0
 elif kind in [27,28]:v>>=1
 elif kind==30:v=0 if mode==1 else v>>3
 elif kind==31:v=0 if mode==1 else v>>2
 if difficulty==2:v>>=1
 elif difficulty==0:v=s16(v*2)
 return min(v,255)
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x10000,bytes(p));stopped=[];active_rng=[0]
base=0x183c*16
def hook(uc,a,n,d):
 if a==base+0x1e3:uc.reg_write(UC_X86_REG_AX,active_rng[0]);uc.reg_write(UC_X86_REG_IP,0x1e8)
 elif a==base+0x263:uc.reg_write(UC_X86_REG_IP,0x268)
 elif a==base+0x2e8:stopped.append(uc.reg_read(UC_X86_REG_AX));uc.emu_stop()
u.hook_add(UC_HOOK_CODE,hook);cases=0;negative=0;examples=[]
for kind,mode,diff,rng,difficulty,special in itertools.product([0,*range(12,32),255],[0,1,2],[-4096,-1,0,1,4095,4096],[0,24,32767],[0,1,2],[0,3]):
 stopped.clear();active_rng[0]=rng;u.mem_write(0x50000+0x100+0x18,struct.pack('<H',diff&65535));u.mem_write(0x50106,bytes([kind]));ds=0x376d*16
 for off,val,size in [(0x4550,0,2),(0x418d,mode,1),(0x6268,special,2),(0x417e,difficulty,2)]:u.mem_write(ds+off,val.to_bytes(size,'little'))
 u.mem_write(0x60000+0xff08,struct.pack('<HH',0x100,0x5000))
 for reg,val in [(UC_X86_REG_CS,0x183c),(UC_X86_REG_IP,0x1c6),(UC_X86_REG_DS,0x376d),(UC_X86_REG_SS,0x6000),(UC_X86_REG_SP,0xff00)]:u.reg_write(reg,val)
 u.emu_start(base+0x1c6,0,count=200);expected=model(diff,rng,kind,mode,special,difficulty)
 assert stopped==[expected&65535],(kind,mode,diff,rng,difficulty,special,stopped,expected)
 cases+=1
 if expected<0:
  negative+=1
  if len(examples)<5:examples.append(dict(type=kind,mode=mode,difference=diff,rng=rng,difficulty=difficulty,special=special,signed_AX=expected,AL=expected&255))
result=dict(build='V1.9 (input DOS18)',exe_sha256=hashlib.sha256(b).hexdigest(),entry='183c:01c6',cases=cases,passed=True,negative_return_cases=negative,negative_examples=examples,scope='RNG return AX injected; far side-effect call 183c:0263 skipped; whole-game reachability of negative inputs unknown')
(root/'pass3/evidence/damage_producer_emulation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
