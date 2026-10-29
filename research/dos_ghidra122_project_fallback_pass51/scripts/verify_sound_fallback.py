from pathlib import Path
import csv,json,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for m in json.loads((root/'pass47/evidence/dispatch.json').read_text())['locations']:
 v=m['build'];ds=next(q['actual_DS'] for q in json.loads((root/'pass7/evidence/specs.json').read_text()) if q['build']==v);call=[r for r in m['instructions'] if r['bytes'].startswith(('9a','e8'))][5];cs=int(call['address'].split(':')[0],16);ip=int(call['address'].split(':')[1],16);entry=(ip+3+int.from_bytes(bytes.fromhex(call['bytes'])[1:],'little',signed=True))&65535
 rows=list(csv.DictReader((root/f'pass7/audit/DOS{v}/instructions.tsv').open(),delimiter='\t'));idx=next(i for i,r in enumerate(rows) if r['address']==f'{cs:04x}:{entry:04x}');body=[]
 for r in rows[idx:]:
  body.append(r)
  if r['bytes']=='cb':break
 modern=any(r['bytes'].startswith('81bf') for r in body)
 table=int(m['resource_table'],16);limit=15000 if modern else None
 calls=[r for r in body if r['bytes'].startswith('9a')];roles=['transfer'] if modern else ['release','allocate','fatal','transfer'];sites={cs*16+int(r['address'].split(':')[1],16):role for r,role in zip(calls,roles)}
 seg=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('ba')))[1:],'little') if modern else 0x6000
 pointer=None if modern else int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('66833e')))[3:5],'little')
 b=(root/f'analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+k*4);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',model='fixed' if modern else 'allocated',limit=limit,buffer=f'{seg:04x}:0000' if modern else None,pointer_global=pointer,instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 for length,offset,old,allocated in itertools.product([0,8192,8193,14999,15000,15001,32768,65535],[0,123,-123,-2147483648],([0] if modern else [0,1]),([1] if modern else [0,1])):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xd000;ident=66;trace=[];u.mem_write(ds*16+sp,struct.pack('<3H',0x600,0,ident));u.mem_write(ds*16+table+ident*6,struct.pack('<Hi',length,offset))
  if not modern:u.mem_write(ds*16+pointer,struct.pack('<HH',0x100 if old else 0,0x6000 if old else 0))
  def hook(uc,addr,n,_):
   if addr not in sites:return
   role=sites[addr];st=uc.reg_read(UC_X86_REG_SP);nargs={'transfer':5,'release':2,'allocate':1,'fatal':2}[role];args=list(struct.unpack('<'+str(nargs)+'H',uc.mem_read(ds*16+st,nargs*2)));trace.append([role,args])
   if role=='fatal':uc.emu_stop();return
   uc.reg_write(UC_X86_REG_AX,0x200 if role=='allocate' and allocated else 0 if role=='allocate' else 0xffff);uc.reg_write(UC_X86_REG_DX,0x6000 if role=='allocate' and allocated else 0 if role=='allocate' else 0xffff);uc.reg_write(UC_X86_REG_IP,addr-cs*16+5)
  u.hook_add(UC_HOOK_CODE,hook)
  for r,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(r,val)
  u.emu_start(cs*16+entry,0x600,count=500)
  expected=[]
  if modern:
   if length<=limit:expected=[['transfer',[0,seg,offset&65535,(offset>>16)&65535,length]]]
  else:
   if old:expected.append(['release',[0x100,0x6000]])
   expected.append(['allocate',[length]])
   if allocated:expected.append(['transfer',[0x200,0x6000,offset&65535,(offset>>16)&65535,length]])
   else:
    assert trace[-1][0]=='fatal';expected.append(trace[-1])
  assert trace==expected,(v,trace,expected)
  ret=[u.reg_read(UC_X86_REG_AX),u.reg_read(UC_X86_REG_DX)]
  if modern or allocated:
   assert ret==([0,seg] if modern else [0x200,0x6000]);assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4
  results.append(dict(build=v,length=length,offset=offset,old_pointer_present=old,allocation_succeeds=allocated,trace=trace,returned=ret if modern or allocated else None,fatal=not modern and not allocated,passed=True))
(root/'pass51/evidence/fallback.json').write_text(json.dumps(dict(cases=len(results),scope='Original fallback; release/allocation/fatal/data-transfer boundaries mocked, synthetic resource records; no asset reads or audio output',locations=locations,results=results),indent=2));print(len(results),'passed')
