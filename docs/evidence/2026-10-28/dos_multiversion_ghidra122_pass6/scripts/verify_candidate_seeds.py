from pathlib import Path
import struct,json,re,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];calls=0
for q in json.loads((root/'pass6/evidence/specs.json').read_text()):
 v=q['build']
 if not q['candidates']:continue
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:]);raw=bytes(p);relocs=[]
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;relocs.append(i);struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 origins=json.loads((root/'pass6/evidence'/('DOS'+v)/'original_near_specs.json').read_text())
 for candidate in q['candidates']:
  cs,ip=map(lambda x:int(x,16),candidate.split(':'));physical=cs*16+ip;known=[]
  for r in origins:
   if candidate not in r['previous']:continue
   s,o=map(lambda x:int(x,16),r['source'].split(':'));pos=s*16+o-0x10000;code=bytes(p[pos:pos+3]);assert code.hex()==r['bytes'] and code[0]==0xe8
   want=(o+3+int.from_bytes(code[1:],'little',signed=True))&65535;assert r['target']==f'{s:04x}:{want:04x}' and physical-(s*16+want)==65536
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.reg_write(UC_X86_REG_CS,s);u.reg_write(UC_X86_REG_SS,0x5000);u.reg_write(UC_X86_REG_SP,0xff00);u.emu_start(s*16+o,0,count=1)
   assert u.reg_read(UC_X86_REG_CS)==s and u.reg_read(UC_X86_REG_IP)==want and u.reg_read(UC_X86_REG_SP)==0xfefe;assert struct.unpack('<H',u.mem_read(0x50000+0xfefe,2))[0]==o+3
   known.append(r);calls+=1
  assert known
  static=[]
  for i in relocs:
   if i<2:continue
   ptr_off=struct.unpack_from('<H',raw,i-2)[0];ptr_seg=struct.unpack_from('<H',p,i)[0]
   if ptr_seg*16+ptr_off==physical:static.append(dict(image_offset=hex(i-2),segment=hex(ptr_seg),offset=hex(ptr_off)))
  pat=struct.pack('<HH',ip,(cs-0x1000)&65535);matches=[];start=0
  while True:
   k=raw.find(pat,start)
   if k<0:break
   matches.append(hex(k));start=k+1
  j=physical-0x10000;prefix=raw[j:j+64];run=0
  for c in raw[j:]:
   if c:break
   run+=1
  results.append(dict(build=v,candidate=candidate,known_invalid_call_seeds=known,relocation_backed_far_pointer_hits=static,canonical_raw_far_pattern_hits=matches,first64_bytes=prefix.hex(),zero_run_bytes=run,status='documented near-call seed rejected; candidate retained; dynamic reachability unresolved'))
(root/'pass6/evidence/candidate_seed_audit.json').write_text(json.dumps(dict(candidates=len(results),original_CALL_instruction_tests=calls,results=results),indent=2));print(len(results),'candidate seeds audited;',calls,'original CALL instruction tests');print([(r['build'],r['candidate'],len(r['relocation_backed_far_pointer_hits']),r['zero_run_bytes']) for r in results])
