from pathlib import Path
import json,struct,hashlib,csv
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass80/evidence';results=[]
for l in json.load(open(r/'pass79/evidence/locations.json')):
 v=l['build'];ds=next(x['actual_DS'] for x in json.load(open(r/'baseline58/pass7/evidence/specs.json')) if x['build']==v)
 b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 for sp in [0xe000,0xd000]:
  for prefix in ['', 'C:\\N3D\\','C:\\N3D','./data/','data path/']:
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+l['prefix'],prefix.encode()+b'\0');u.mem_write(ds*16+sp,struct.pack('<HH',0,0x600));cs,ip=[int(x,16) for x in l['config_loader'].split(':')]
   for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
   state={'open_before':None,'interrupts':[],'writes':[]};ptr=[None]
   def readstr(seg,off):return bytes(u.mem_read(seg*16+off,200)).split(b'\0')[0].decode('latin1')
   def code(u,a,size,_):
    if a==int(l['open_call'].split(':')[0],16)*16+int(l['open_call'].split(':')[1],16):
     ptr[0]=struct.unpack('<H',u.mem_read(ds*16+u.reg_read(UC_X86_REG_SP),2))[0];state['open_before']=readstr(ds,ptr[0])
   def write(u,access,a,size,val,_):
    if ptr[0] is not None and a<ds*16+ptr[0]+len(prefix+'config.sav')+1 and a+size>ds*16+ptr[0]:state['writes'].append({'cs':u.reg_read(UC_X86_REG_CS),'ip':u.reg_read(UC_X86_REG_IP),'address':a,'size':size,'value':val})
   def intr(u,n,_):
    state['interrupts'].append({'number':n,'ax':u.reg_read(UC_X86_REG_AX),'ds':u.reg_read(UC_X86_REG_DS),'dx':u.reg_read(UC_X86_REG_DX),'path':readstr(u.reg_read(UC_X86_REG_DS),u.reg_read(UC_X86_REG_DX))});u.emu_stop()
   u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_INTR,intr);u.emu_start(cs*16+ip,0,count=100000)
   assert state['open_before']==prefix+'config.sav';assert len(state['interrupts'])==1;it=state['interrupts'][0];assert it['number']==33 and it['ax']==0x3d00 and it['path']==prefix+'config.sav';assert not state['writes']
   results.append(dict(build=v,exe_sha256=hashlib.sha256(b).hexdigest(),sp=sp,prefix=prefix,pointer=ptr[0],**state,passed=True))
(o/'native_open_tests.json').write_text(json.dumps({'passed':len(results),'cases':results,'boundary':'Original config loader, path helper and CRT open execute unchanged; stop at first DOS INT21 before OS executes. DS=SS DF=0; no mocked calls.'},indent=2)+'\n');print(len(results),'passed')
