from pathlib import Path
import json,struct,itertools,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
samples=[b'0',b'1',b'-1',b'+15',b'0x10',b'010',b'09',b'0Xf',b' 12x',b'',b'x',b'+',b'-',b'65535',b'65536',b'32768',b'-32769']
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];loc=next(x for x in json.loads((root/'pass19/evidence/bsf_commands.json').read_text())['locations'] if x['build']==v);entry,cs=struct.unpack_from('<HH',bytes.fromhex(loc['calls'][0]['bytes']),1);b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',exe_sha256=hashlib.sha256(b).hexdigest()))
 for fmt,data in itertools.product([b'%i',b'%d'],samples):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));ds=q['actual_DS'];sp=0xf800;u.mem_write(ds*16+0x9000,data+b'\0');u.mem_write(ds*16+0x9100,fmt+b'\0');u.mem_write(ds*16+0x9200,b'\x5a\xef\xbe\x5a');u.mem_write(ds*16+sp,struct.pack('<5H',0x600,0,0x9000,0x9100,0x9201))
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  try:u.emu_start(cs*16+entry,0x600,count=100000)
  except Exception:
   print(v,fmt,data,hex(u.reg_read(UC_X86_REG_CS)),hex(u.reg_read(UC_X86_REG_IP)),hex(u.reg_read(UC_X86_REG_SP)),hex(u.reg_read(UC_X86_REG_DS)));raise
  assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  mem=bytes(u.mem_read(ds*16+0x9200,4));assert mem[0]==mem[3]==0x5a;ax=u.reg_read(UC_X86_REG_AX);value=struct.unpack_from('<H',mem,1)[0]
  results.append(dict(build=v,format=fmt.decode(),input=data.decode(),returned_AX=ax,output_word=value,passed=True))
for fmt,data in itertools.product(['%i','%d'],[s.decode() for s in samples]):
 rows=[r for r in results if r['format']==fmt and r['input']==data];assert len({(r['returned_AX'],r['output_word']) for r in rows})==1
out=root/'pass20/evidence';out.mkdir(parents=True,exist_ok=True);(out/'original_scanf.json').write_text(json.dumps(dict(cases=len(results),scope='Complete original sscanf and CRT callees; no hooks/stubs. Controlled null-terminated near strings, one16-bit integer destination; cross-build equality and return/guards checked.',locations=locations,results=results),indent=2));print(len(results),'passed');print([(r['format'],r['input'],r['returned_AX'],r['output_word']) for r in results if r['build']=='10'])
