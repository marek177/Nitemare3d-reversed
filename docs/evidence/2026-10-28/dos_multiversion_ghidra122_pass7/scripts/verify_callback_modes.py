from pathlib import Path
import json,struct,csv,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 cs,entry=map(lambda x:int(x,16),q['callback_entry'].split(':'));base=cs*16;mode1=int(q['mode_targets'][1].split(':')[1],16);ins=list(csv.DictReader((root/'pass6/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));section=[r for r in ins if r['address'].startswith(f'{cs:04x}:') and entry<=int(r['address'].split(':')[1],16)<mode1];farcalls=[r for r in section if r['bytes'].startswith('9a') and len(r['bytes'])==10];assert len(farcalls)==6
 far_types={base+int(r['address'].split(':')[1],16):k for r,k in zip(farcalls,['open','open_error','read','close','decoder','checksum_error'])};near_validators={base+int(r['address'].split(':')[1],16) for r in section if r['bytes'].startswith('e8') and len(r['bytes'])==6};assert len(near_validators)==2
 data=(root/'pass7/data'/('DOS'+v+'.bsf')).read_bytes();res=next(r for r in json.loads((root/'pass7/evidence/bsf_resources.json').read_text()) if r['build']==v);header=bytes.fromhex(res['header_hex']);decoder_key=bytes(p[q['actual_DS']*16-0x10000+q['key_offset']:q['actual_DS']*16-0x10000+q['key_offset']+52]);loader_cs,loader_ip=map(lambda x:int(x,16),q['loader_entry'].split(':'))
 # Shared resource loader call is the last far CALL in the callback body.
 all_calls=[r for r in ins if r['address'].startswith(f'{cs:04x}:') and entry<=int(r['address'].split(':')[1],16)<entry+0x110 and r['bytes'].startswith('9a') and len(r['bytes'])==10];loader_site=base+int(all_calls[-1]['address'].split(':')[1],16)
 def run(mode,ds,seed,flag=None,return_pair=None,error=None):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));ss=q['actual_DS'];sp=0xe000;u.mem_write(ss*16+sp,struct.pack('<HHH',0x600,0,mode));u.mem_write(ss*16+sp-6,struct.pack('<HH',*seed));u.mem_write(ds*16+q['header_base'],header)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  raw=bytearray(data[:54]);flag=q['mode1_flag'] and header[3] if flag is None else flag;delta=header[3]^flag;raw[3]^=delta;raw[0]^=delta
  if error=='checksum':raw[0]^=1
  trace=[];stopped=[]
  def hook(uc,a,n,_):
   callsp=uc.reg_read(UC_X86_REG_SP);stack=ss*16+callsp
   if a in far_types:
    kind=far_types[a]
    if kind=='decoder':trace.append(dict(kind='original_decoder'));return
    if kind.endswith('_error'):stopped.append(kind);uc.emu_stop();return
    if kind=='open':uc.reg_write(UC_X86_REG_AX,0 if error=='open' else 0x123)
    elif kind=='read':
     dst,count,size,stream=struct.unpack('<4H',uc.mem_read(stack,8));assert dst==q['header_base'] and count==54 and size==1 and stream==0x123;uc.mem_write(ds*16+dst,bytes(raw));uc.reg_write(UC_X86_REG_AX,1)
    trace.append(dict(kind=kind));uc.reg_write(UC_X86_REG_IP,(a-base)+5)
   elif a in near_validators:
    filename,lo,hi,value=struct.unpack('<4H',uc.mem_read(stack+2,8));name=bytes(uc.mem_read(ds*16+filename,24)).split(b'\0')[0].decode('ascii');trace.append(dict(kind='file_checksum_validator_stub',filename=name,range=(hi<<16)|lo,expected_byte=value&255));uc.reg_write(UC_X86_REG_SP,callsp+2);uc.reg_write(UC_X86_REG_IP,(a-base)+3)
   elif a==loader_site:
    filename,lo,hi,length=struct.unpack('<4H',uc.mem_read(stack,8));name=bytes(uc.mem_read(ds*16+filename,24)).split(b'\0')[0];block=next(r for r in res['blocks'] if r['mode']==mode);assert name==b'nite3d.bsf' and ((hi<<16)|lo)==block['file_offset'] and length==block['length'];trace.append(dict(kind='resource_loader_stub',offset=(hi<<16)|lo,length=length));uc.reg_write(UC_X86_REG_AX,return_pair[0]);uc.reg_write(UC_X86_REG_DX,return_pair[1]);uc.reg_write(UC_X86_REG_IP,(a-base)+5)
  hooked=mode in [0,3,4,5]
  if hooked:u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start(base+entry,0x600,count=20000);ax=u.reg_read(UC_X86_REG_AX);dx=u.reg_read(UC_X86_REG_DX)
  if error:assert stopped==[error+'_error']
  else:
   assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_IP)==0x600 and u.reg_read(UC_X86_REG_SP)==sp+4
   if mode==2:expected=(q['header_base']+4,ds)
   elif mode in [3,4,5]:expected=return_pair
   else:expected=seed
   assert (ax,dx)==expected,(v,mode,seed,(ax,dx),expected)
   if mode==0:
    actual=bytes(u.mem_read(ds*16+q['header_base'],54));assert actual==bytes(c^decoder_key[i%52] for i,c in enumerate(raw));validators=[x['filename'] for x in trace if x['kind']=='file_checksum_validator_stub'];assert validators==(['n3d.exe','map.1'] if flag==0 else ['n3d.exe']); observed=[(x['filename'],x['range'],x['expected_byte']) for x in trace if x['kind']=='file_checksum_validator_stub']; expected_checks=[('n3d.exe',0,header[1])]+([('map.1',0,header[2])] if flag==0 else []); assert observed==expected_checks
  results.append(dict(build=v,mode=mode,DS=hex(ds),seed=list(seed),flag=flag,returned_AX=hex(ax) if not error else None,returned_DX=hex(dx) if not error else None,error_branch=error,hooks=hooked,trace=trace,passed=True))
 for ds in [0,q['actual_DS'],0x5000,0xffff]:
  for flag in [0,1]:run(2,ds,(0x1357,0x2468),flag=flag)
 for mode,seed in itertools.product([6,65535],[(0,0),(0x1234,0xabcd),(65535,65535),(1,2)]):run(mode,q['actual_DS'],seed)
 for mode,pair in itertools.product([3,4,5],[(0,0),(0x7000,0x5000),(65535,65535)]):run(mode,q['actual_DS'],(0x1357,0x2468),return_pair=pair)
 for flag,seed in itertools.product([0,1],[(0x1357,0x2468),(0xbeef,0xabcd)]):run(0,q['actual_DS'],seed,flag=flag)
 for error in ['open','checksum']:run(0,q['actual_DS'],(0x1357,0x2468),flag=0,error=error)
(root/'pass7/evidence/callback_mode_emulation.json').write_text(json.dumps(dict(cases=len(results),scope='original dispatch/control flow with injected header/CRT I/O/loader/file-validator dependencies where stated; mode2 and invalid-mode cases have no hooks',results=results),indent=2));print(len(results),'callback cases passed;',sum(not r['hooks'] for r in results),'without hooks')
