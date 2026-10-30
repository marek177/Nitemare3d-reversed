from pathlib import Path
import json,struct,csv,itertools,hashlib
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass92/evidence';out=[];locations=[];s16=lambda n:(n+32768)%65536-32768
for v in ['10','11','12','15','17','18']:
 ds=next(x['actual_DS'] for x in json.load(open(r/'baseline58/pass7/evidence/specs.json')) if x['build']==v);cs=int(next(x['entry'] for x in json.load(open(o/'sensitivity_locations.json')) if x['build']==v).split(':')[0],16);rows=[x for x in csv.DictReader(open(r/f'baseline58/pass7/audit/DOS{v}/instructions.tsv'),delimiter='\t') if x['address'].split(':')[0]==f'{cs:04x}'];k=next(i for i,x in enumerate(rows) if x['bytes']=='2420' and rows[i+2]['bytes'].startswith('8b36'));start=k-1;end=next(i for i in range(k,len(rows)) if rows[i]['bytes']=='bf0100')+1;block=rows[start:end];ip=int(block[0]['address'].split(':')[1],16);stop=int(rows[end]['address'].split(':')[1],16);flag=int.from_bytes(bytes.fromhex(block[0]['bytes'])[1:3],'little');gx=int.from_bytes(bytes.fromhex(rows[k+2]['bytes'])[2:4],'little');gy=next(int.from_bytes(bytes.fromhex(x['bytes'])[2:4],'little') for x in block if x['bytes'].startswith('8b3e'));locations.append(dict(build=v,entry=f'{cs:04x}:{ip:04x}',stop=f'{cs:04x}:{stop:04x}',flags=flag,si_global=gx,di_global=gy,instructions=block))
 b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();locations[-1]['exe_sha256']=hashlib.sha256(b).hexdigest();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 for mask,x,y in itertools.product([0,32,64,96],[-32768,-1,0,1,100,16384,32767],[-32768,-1,0,1,100,16384,32767]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+flag,bytes([mask]));u.mem_write(ds*16+gx,struct.pack('<h',x));u.mem_write(ds*16+gy,struct.pack('<h',y));state={'done':False}
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  def hook(u,a,size,_):
   if a==cs*16+stop:state['done']=True;u.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+ip,0,count=100);expected=[1,1] if mask&64 else [s16(z*(2 if mask&32 else 1)) for z in [x,y]];actual=[s16(u.reg_read(reg)) for reg in [UC_X86_REG_SI,UC_X86_REG_DI]];assert state['done'] and actual==expected;assert u.reg_read(UC_X86_REG_SP)==0xe000
  out.append(dict(build=v,flags=mask,si_source=x,di_source=y,si=actual[0],di=actual[1],passed=True))
 print(v,'196 passed')
(o/'limit_tests.json').write_text(json.dumps(dict(locations=locations,passed=len(out),cases=out,boundary='Original input collector sub-block only, no calls or mocks; synthetic globals/flags, stop before movement dispatch.'),indent=2)+'\n')
