"""python audit_replay_episode_probe.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
rows=[];p=0xf926
for i in Decoder(16,b[0xf926:0xf971],ip=0x2696):
 assert not i.is_invalid and lookup[p]['bytes']==b[p:p+i.len].hex();rows.append(dict(cs=0xd29,ip=i.ip,image_offset=p,bytes=b[p:p+i.len].hex(),instruction=fmt.format(i)));p+=i.len
assert p==0xf971 and rows[-1]['bytes']=='cb'
def save(name,rs):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
save('episode_available_probe',rows);assert b[0x29710:0x2971a]==b'map.\0%s%d\0';rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];events=[]
for load,mask,registered in itertools.product((0,0x1000),range(64),(0,1)):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for r in rel:struct.pack_into('<H',runtime,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));ds=load+0x2771;cs=load+0xd29;formatter=(load+0x11ee)*16+0x278c;access=(load+0x11ee)*16+0x3990;bsf=(load+0x83d)*16+0x29ca
 for address in (formatter,access,bsf):u.mem_write(address,b'\xcb')
 observed=[];cursor={'episode':None,'buffer':None}
 def hook(uc,address,size,user):
  if address not in (formatter,access,bsf):return
  ss=uc.reg_read(UC_X86_REG_SS);sp=uc.reg_read(UC_X86_REG_SP);read=lambda n:struct.unpack('<'+'H'*n,bytes(uc.mem_read(ss*16+sp+4,n*2)))
  if address==formatter:
   dest,fmtarg,prefix,n=read(4);assert (fmtarg,prefix)==(0x2005,0x2000) and 1<=n<=6;assert ss==ds
   uc.mem_write(ds*16+dest,('map.%d'%n).encode()+b'\0');cursor.update(episode=n,buffer=dest);observed.append(('format',n));uc.reg_write(UC_X86_REG_AX,5)
  elif address==access:
   name,mode=read(2);assert name==cursor['buffer'] and mode==4;n=cursor['episode'];assert bytes(uc.mem_read(ds*16+name,6))==('map.%d'%n).encode()+b'\0'
   observed.append(('access',n));uc.reg_write(UC_X86_REG_AX,0 if mask&(1<<(n-1)) else 0xffff)
  else:
   assert read(1)==(1,);observed.append(('bsf_registered',cursor['episode']));uc.reg_write(UC_X86_REG_AX,0x363b if registered else 0);uc.reg_write(UC_X86_REG_DX,ds if registered else 0)
 u.hook_add(UC_HOOK_CODE,hook)
 for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 u.mem_write(ds*16+0xff00,struct.pack('<HH',0x6000,cs));u.emu_start(cs*16+0x2696,cs*16+0x6000,count=500)
 wanted=7;expected=[]
 for n in range(1,7):
  expected.extend([('format',n),('access',n)])
  if not mask&(1<<(n-1)):continue
  expected.append(('bsf_registered',n))
  if registered or n==1:wanted=n;break
 assert observed==expected and u.reg_read(UC_X86_REG_AX)==wanted
 for reg,val in [(UC_X86_REG_DS,ds),(UC_X86_REG_SP,0xff04),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345)]:assert u.reg_read(reg)==val
 case=len(cases);cases.append(dict(case=case,load=load,accessible_episode_mask=mask,registered=registered,result=wanted,access_calls=sum(k=='access' for k,n in observed),passed=True));events.extend(dict(case=case,order=j,callee=k,episode=n) for j,(k,n) in enumerate(observed))
save('cases',cases);save('callee_events',events)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=[dict(name='episode_available_probe',start=0xf926,end_exclusive=0xf971,instruction_bytes=75,instructions=len(rows))],cases=len(cases),failures=0,cases_sha256=sha((out/'cases.csv').read_bytes()),runtime_tests=0,new_deep_verified_bytes=0,scope='original episode1..6 selector control; formatter,access,BSFmode1 mocked; DS=SS caller precondition; result7 means scan exhausted, not a validated playable episode')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
