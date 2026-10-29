from pathlib import Path
import csv,json,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for m in json.loads((root/'pass51/evidence/fallback.json').read_text())['locations']:
 v=m['build'];ds=next(q['actual_DS'] for q in json.loads((root/'pass7/evidence/specs.json').read_text()) if q['build']==v);call=[r for r in m['instructions'] if r['bytes'].startswith('9a')][-1];raw=bytes.fromhex(call['bytes']);cs=int.from_bytes(raw[3:],'little');entry=int.from_bytes(raw[1:3],'little');rows=list(csv.DictReader((root/f'pass7/audit/DOS{v}/instructions.tsv').open(),delimiter='\t'));idx=next(i for i,r in enumerate(rows) if r['address']==f'{cs:04x}:{entry:04x}');body=[]
 for r in rows[idx:]:
  body.append(r)
  if r['bytes']=='cb':break
 handle=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('833e')))[2:4],'little');calls=[r for r in body if r['bytes'].startswith('9a')];assert len(calls)==5;roles=['open','fatal_open','seek','read','fatal_read'];sites={cs*16+int(r['address'].split(':')[1],16):role for r,role in zip(calls,roles) if role!='read'}
 fatalargs={}
 for role,r in zip(roles,calls):
  if role.startswith('fatal'):
   j=body.index(r);fatalargs[role]=[int.from_bytes(bytes.fromhex(body[j-k]['bytes'])[1:],'little') for k in [1,2]]
 readraw=bytes.fromhex(calls[3]['bytes']);rcs=int.from_bytes(readraw[3:],'little');rip=int.from_bytes(readraw[1:3],'little');ri=next(i for i,r in enumerate(rows) if r['address']==f'{rcs:04x}:{rip:04x}');readbody=[]
 for r in rows[ri:]:
  readbody.append(r)
  if r['bytes']=='cb':break
 b=(root/f'analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+k*4);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 filename=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('68') and r['bytes']!='680080'))[1:],'little');start=ds*16+filename;name=bytes(p[start-0x10000:start-0x10000+64]).split(b'\0')[0].decode('ascii',errors='replace')
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',read_entry=f'{rcs:04x}:{rip:04x}',handle_global=hex(handle),filename=name,filename_offset=hex(filename),instructions=body,read_instructions=readbody,sha256=hashlib.sha256(b).hexdigest()))
 for (cached,opened),length,offset,readmode,seekfail in itertools.product([(0,0),(0,5),(0,65535),(7,5),(65535,5)],[0,1,8192,65535],[0,123,-123],['full','short','error'],[0,1]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+handle,struct.pack('<H',cached));trace=[];fatal=[None];sp=0xd000;desired=length if readmode=='full' else max(length-1,0) if readmode=='short' else 65535
  def hook(uc,a,n,_):
   if a not in sites:return
   role=sites[a];st=uc.reg_read(UC_X86_REG_SP);nargs=4 if role=='seek' else 2;args=list(struct.unpack('<'+str(nargs)+'H',uc.mem_read(ds*16+st,nargs*2)));trace.append([role,args])
   if role.startswith('fatal'):fatal[0]=role;uc.emu_stop();return
   if role=='open':uc.reg_write(UC_X86_REG_AX,opened)
   else:uc.reg_write(UC_X86_REG_AX,65535 if seekfail else offset&65535);uc.reg_write(UC_X86_REG_DX,65535 if seekfail else (offset>>16)&65535)
   uc.reg_write(UC_X86_REG_IP,a-cs*16+5)
  def interrupt(uc,n,_):
   assert n==0x21 and uc.reg_read(UC_X86_REG_AH)==0x3f
   trace.append(['dos_read',[uc.reg_read(UC_X86_REG_BX),uc.reg_read(UC_X86_REG_DS),uc.reg_read(UC_X86_REG_DX),uc.reg_read(UC_X86_REG_CX)]])
   uc.reg_write(UC_X86_REG_AX,5 if readmode=='error' else desired);flags=uc.reg_read(UC_X86_REG_EFLAGS);uc.reg_write(UC_X86_REG_EFLAGS,(flags|1) if readmode=='error' else (flags&~1))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,interrupt)
  repetitions=0
  for rep in range(2):
   repetitions+=1;u.mem_write(ds*16+sp,struct.pack('<7H',0x600,0,0x200,0x6000,offset&65535,(offset>>16)&65535,length))
   for r,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(r,val)
   u.emu_start(cs*16+entry,0x600,count=1000)
   if fatal[0]:break
   assert u.reg_read(UC_X86_REG_AX)==length
   assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  expected=[];active=cached
  for rep in range(repetitions):
   if active==0:
    expected.append(['open',[filename,0x8000]]);active=opened
    if active==65535:expected.append(['fatal_open',fatalargs['fatal_open']]);break
   expected.append(['seek',[active,offset&65535,(offset>>16)&65535,0]]);expected.append(['dos_read',[active,0x6000,0x200,length]])
   if desired!=length:expected.append(['fatal_read',fatalargs['fatal_read']]);break
  assert trace==expected,(v,cached,opened,length,offset,readmode,seekfail,trace,expected)
  assert struct.unpack('<H',u.mem_read(ds*16+handle,2))[0]==active
  results.append(dict(build=v,cached_handle=cached,open_return=opened,length=length,offset=offset,read_mode=readmode,seek_failure=seekfail,repetitions=repetitions,fatal=fatal[0],trace=trace,passed=True))
(root/'pass55/evidence/transfer.json').write_text(json.dumps(dict(cases=len(results),locations=locations,scope='Original lazy-open/seek/read checking and original INT21 far-read wrapper. CRT open,seek,fatal and DOS read boundary mocked. No real file bytes copied.',results=results),indent=2));print(len(results),'passed')
