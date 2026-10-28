from pathlib import Path
import json,struct,functools,operator,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 data=(root/'pass7/data'/('DOS'+v+'.bsf')).read_bytes();resource=next(r for r in json.loads((root/'pass7/evidence/bsf_resources.json').read_text()) if r['build']==v);tests=[('header',data[:54])]+[(f"mode{r['mode']}",data[r['file_offset']:r['file_offset']+r['length']]) for r in resource['blocks']]+[(f'length{n}',bytes((i*73+19)&255 for i in range(n))) for n in [0,1,51,52,53,54,255,256,1024]]
 key=bytes(p[q['actual_DS']*16-0x10000+q['key_offset']:q['actual_DS']*16-0x10000+q['key_offset']+52]);cs,ip=map(lambda x:int(x,16),q['decoder_entry'].split(':'))
 for label,source in tests:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));base=0x50200;u.mem_write(base-1,b'\xa5'+source+b'\x5a');ds=q['actual_DS']
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  u.mem_write(ds*16+0xe000,struct.pack('<HHHHH',0x600,0,0x200,0x5000,len(source)));u.emu_start(cs*16+ip,0x600,count=max(100,20*len(source)+100))
  expected=bytes(c^key[i%52] for i,c in enumerate(source));actual=bytes(u.mem_read(base,len(source)));xor=functools.reduce(operator.xor,source,0)
  assert actual==expected and (u.reg_read(UC_X86_REG_AX)&255)==xor and u.reg_read(UC_X86_REG_SP)==0xe004 and u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_IP)==0x600 and u.reg_read(UC_X86_REG_CS)==0
  assert bytes(u.mem_read(base-1,1))==b'\xa5' and bytes(u.mem_read(base+len(source),1))==b'\x5a'
  results.append(dict(build=v,case=label,length=len(source),returned_AL=xor,decoded_sha256=hashlib.sha256(actual).hexdigest(),passed=True))
(root/'pass7/evidence/decoder_emulation.json').write_text(json.dumps(dict(cases=len(results),hooks=False,stubs=False,scope='original complete in-place BSF XOR routine; real encoded header/blocks plus boundary lengths',results=results),indent=2));print(len(results),'decoder cases passed')
