from pathlib import Path
import csv,json,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for m in json.loads((root/'pass50/evidence/cache.json').read_text())['locations']:
 v=m['build'];ds=next(q['actual_DS'] for q in json.loads((root/'pass7/evidence/specs.json').read_text()) if q['build']==v);call=next(r for r in m['instructions'] if r['bytes'].startswith('e8'));cs=int(call['address'].split(':')[0],16);ip=int(call['address'].split(':')[1],16);entry=(ip+3+int.from_bytes(bytes.fromhex(call['bytes'])[1:],'little',signed=True))&65535;rows=list(csv.DictReader((root/f'pass7/audit/DOS{v}/instructions.tsv').open(),delimiter='\t'))
 def body_at(e):
  i=next(i for i,r in enumerate(rows) if r['address']==f'{cs:04x}:{e:04x}');b=[]
  for r in rows[i:]:
   b.append(r)
   if r['bytes']=='cb':return b
 body=body_at(entry);nc=next(r for r in body if r['bytes'].startswith('e8'));ni=int(nc['address'].split(':')[1],16);ne=(ni+3+int.from_bytes(bytes.fromhex(nc['bytes'])[1:],'little',signed=True))&65535;wrapper=body_at(ne);push=next(r for r in reversed(body[:body.index(nc)]) if r['bytes'].startswith(('68','6a')));descriptor_offset=int.from_bytes(bytes.fromhex(push['bytes'])[1:],'little');driver=next(r for r in wrapper if r['bytes'].startswith('26ff1e'));da=cs*16+int(driver['address'].split(':')[1],16);fatal=next(r for r in body if r['bytes'].startswith('9a'));fa=cs*16+int(fatal['address'].split(':')[1],16);scratch=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('8e06')))[2:4],'little');handle=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('a1')))[1:3],'little')
 b=(root/f'analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+k*4);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',wrapper_entry=f'{cs:04x}:{ne:04x}',descriptor_offset=hex(descriptor_offset),scratch_segment_global=hex(scratch),source_handle_global=hex(handle),instructions=body,wrapper_instructions=wrapper,sha256=hashlib.sha256(b).hexdigest()))
 for length,offset,(axret,blret) in itertools.product([0,1,1023,1024,1025,8191,8192,65535],[0,123,65536,4294967295],[(1,0),(1,255),(65535,128),(0,0),(0,127),(0,128),(0,255)]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xd000;u.mem_write(ds*16+sp,struct.pack('<7H',0x600,0,0x200,0x6000,offset&65535,offset>>16,length));u.mem_write(ds*16+scratch,struct.pack('<H',0x5000));u.mem_write(ds*16+handle,struct.pack('<H',0x1234));trace=[];stopped=[False]
  def hook(uc,a,n,_):
   if a==da:
    ptr=uc.reg_read(UC_X86_REG_DS)*16+uc.reg_read(UC_X86_REG_SI);descriptor=bytes(uc.mem_read(ptr,16));fields=list(struct.unpack('<IHIHI',descriptor));trace.append(dict(AH=uc.reg_read(UC_X86_REG_AH),DS=uc.reg_read(UC_X86_REG_DS),SI=uc.reg_read(UC_X86_REG_SI),fields=fields,hex=descriptor.hex()));uc.reg_write(UC_X86_REG_AX,axret);uc.reg_write(UC_X86_REG_BL,blret);uc.reg_write(UC_X86_REG_IP,a-cs*16+5)
   elif a==fa:stopped[0]=True;uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook)
  for r,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp),(UC_X86_REG_SI,0x7777)]:u.reg_write(r,val)
  u.emu_start(cs*16+entry,0x600,count=1000);assert len(trace)==1;assert trace[0]['AH']==11 and trace[0]['DS']==0x5000 and trace[0]['SI']==descriptor_offset, (v,trace);assert trace[0]['fields']==[((length+1023)//1024)*1024,0x1234,offset,0,0x60000200]
  expected_dx=(blret<<8) if axret==0 else 0;expected_fatal=axret==0 and blret>=128;assert stopped[0]==expected_fatal;assert u.reg_read(UC_X86_REG_DX)==expected_dx;assert u.reg_read(UC_X86_REG_AX)==axret;assert u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SI)==0x7777
  if not stopped[0]:assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4
  results.append(dict(build=v,length=length,source_offset=offset,driver_AX=axret,driver_BL=blret,descriptor=trace[0],returned_DX=expected_dx,fatal=stopped[0],within_cache_length_contract=length<=8192,passed=True))
(root/'pass56/evidence/xms.json').write_text(json.dumps(dict(cases=len(results),scope='Original rounded-transfer helper and original XMS wrapper; indirect XMS driver call mocked, fatal handler stopped at entry. Synthetic scratch segment and handle; no actual XMS data copying.',locations=locations,results=results),indent=2));print(len(results),'passed')
