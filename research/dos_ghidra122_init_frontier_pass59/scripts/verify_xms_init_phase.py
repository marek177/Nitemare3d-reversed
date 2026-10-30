from pathlib import Path
import csv,json,struct,itertools,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;base=root/'baseline58';results=[];locations=[]
for src in json.loads((base/'evidence/store.json').read_text())['locations']:
 v=src['build'];cs=int(src['entry'].split(':')[0],16);rows=[r for r in csv.DictReader((base/f'pass7/audit/DOS{v}/instructions.tsv').open(),delimiter='\t') if r['address'].startswith(f'{cs:04x}:')];cap=int(src['capacity_global'],16);used=int(src['used_global'],16);j=next(i for i,r in enumerate(rows) if r['bytes']=='a3'+struct.pack('<H',cap).hex());si=max(i for i in range(j) if rows[i]['bytes'].startswith('803e'));pi=max(i for i in range(si) if rows[i]['bytes'].startswith('c8'));body=[]
 for r in rows[si:]:
  if body and r['bytes'].startswith('803e'):break
  body.append(r)
 entry=int(body[0]['address'].split(':')[1],16);flag=int.from_bytes(bytes.fromhex(body[0]['bytes'])[2:4],'little');history=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('a2')))[1:3],'little');calls=[r for r in body if r['bytes'].startswith(('e8','9a'))];roles=['detect','query','allocate','lock','free','warn'];assert len(calls)==6;sites={cs*16+int(r['address'].split(':')[1],16):(role,r) for role,r in zip(roles,calls)};local=int.from_bytes(bytes.fromhex(rows[pi]['bytes'])[1:3],'little');saved=[]
 for r in rows[pi+1:]:
  if r['bytes'] in ['56','57']:saved.append(r['bytes'])
  else:break
 ds=next(q['actual_DS'] for q in json.loads((base/'pass7/evidence/specs.json').read_text()) if q['build']==v);b=(base/f'analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+k*4);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 handle=cap-2;rawcap=int.from_bytes(bytes.fromhex(rows[j+1]['bytes'])[1:3],'little');locations.append(dict(build=v,function_entry=rows[pi]['address'],phase_entry=f'{cs:04x}:{entry:04x}',capacity=hex(cap),raw_reported_capacity=hex(rawcap),used=hex(used),handle=hex(handle),enable=hex(flag),history=hex(history),instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 for enabled,detected,reported,allocfail,lockfail in itertools.product([0,1],[0,1],[0,63,64,2047,2048,2049,32767,32768,65535],[0,1],[0,1]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));bp=0xc000;sp=bp-local-len(saved)*2;u.mem_write(ds*16+bp,struct.pack('<4H',0xface,0x600,0,0));trace=[]
  for a,val,fmt in [(cap,0x7777,'H'),(rawcap,0x6666,'H'),(used,55,'H'),(handle,0x5555,'H'),(flag,enabled,'B'),(history,9,'B')]:u.mem_write(ds*16+a,struct.pack('<'+fmt,val))
  def hook(uc,a,n,_):
   if a not in sites:return
   role,r=sites[a];st=uc.reg_read(UC_X86_REG_SP);near=r['bytes'].startswith('e8');extra=2 if near else 0;nargs=1 if role in ['allocate','lock','free','warn'] else 0;args=list(struct.unpack('<'+str(nargs)+'H',uc.mem_read(ds*16+st+extra,nargs*2))) if nargs else [];trace.append([role,args])
   ax=detected if role=='detect' else reported if role=='query' else 0x1234 if role=='allocate' else 0;dx=0x8000 if (role=='allocate' and allocfail) or (role=='lock' and lockfail) else 0
   uc.reg_write(UC_X86_REG_AX,ax);uc.reg_write(UC_X86_REG_DX,dx)
   if near:uc.reg_write(UC_X86_REG_SP,st+2)
   uc.reg_write(UC_X86_REG_IP,a-cs*16+(3 if near else 5))
  u.hook_add(UC_HOOK_CODE,hook)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_BP,bp),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  u.emu_start(cs*16+entry,0x600,count=1000);signed=reported if reported<32768 else reported-65536;bounded=min(signed,2048)&65535;eligible=enabled and detected and min(signed,2048)>=64;success=bool(eligible and not allocfail and not lockfail);rolesgot=[x[0] for x in trace];expected=[]
  if enabled:
   expected=['detect']
   if detected:
    expected+=['query']
    if eligible:
     expected+=['allocate']
     if not allocfail:
      expected+=['lock']
      if lockfail:expected+=['free','warn']
  assert rolesgot==expected,(v,enabled,detected,reported,allocfail,lockfail,trace,expected)
  if eligible:assert next(t[1] for t in trace if t[0]=='allocate')==[bounded]
  for role in ['lock','free']:
   if role in rolesgot:assert next(t[1] for t in trace if t[0]==role)==[0x1234]
  def word(a):return struct.unpack('<H',u.mem_read(ds*16+a,2))[0]
  assert word(cap)==(bounded if enabled and detected else 0x7777);assert word(rawcap)==(reported if enabled and detected else 0x6666);assert word(used)==(0 if enabled and detected else 55);assert word(handle)==(0x1234 if eligible and not allocfail else 0x5555)
  assert u.mem_read(ds*16+flag,1)[0]==success and u.mem_read(ds*16+history,1)[0]==success;assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==bp+6 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,enabled=enabled,detected=detected,reported_KiB=reported,allocate_failure=allocfail,lock_failure=lockfail,success=success,capacity_after=word(cap),used_after=word(used),trace=trace,passed=True))
(root/'pass59/evidence/init.json').write_text(json.dumps(dict(cases=len(results),scope='Original post-heap initialization phase only, starting at XMS enable check with synthetic established stack frame. Detect/query/allocate/lock/free/message calls mocked. No actual XMS manager or full startup.',locations=locations,results=results),indent=2));print(len(results),'passed')
