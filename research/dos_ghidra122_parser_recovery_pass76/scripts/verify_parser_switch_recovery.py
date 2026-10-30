from pathlib import Path
import json,struct,csv
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass76/evidence';spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));loc=json.load(open(r/'pass75/evidence/parser_locations.json'));results=[];summary=[]
for l in loc:
 v=l['build'];cs,ip=[int(x,16) for x in l['entry'].split(':')];rows=next(x['instructions'] for x in json.load(open(r/'pass75/evidence/parser_instructions.json')) if x['build']==v);jump=next(x for x in rows if x['bytes'].startswith('2effa7'));j=rows.index(jump);first=int.from_bytes(bytes.fromhex([x for x in rows[:j] if x['bytes'].startswith('2d')][-1]['bytes'])[1:3],'little');bound=int.from_bytes(bytes.fromhex([x for x in rows[:j] if x['bytes'].startswith('3d')][-1]['bytes'])[1:3],'little');table=int.from_bytes(bytes.fromhex(jump['bytes'])[3:5],'little');b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:]);targets=struct.unpack_from('<'+'H'*(bound+1),p,(cs-4096)*16+table);sw=(o/f'DOS{v}.switch.tsv').read_text().splitlines();assert sw[0]==jump['address'];assert sw[1:]==[f'{cs:04x}:{t:04x}' for t in dict.fromkeys(targets)]
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 for ins in rows:
  ss,ii=[int(x,16) for x in ins['address'].split(':')];raw=bytes.fromhex(ins['bytes']);z=(ss-4096)*16+ii;assert bytes(p[z:z+len(raw)])==raw,(v,ins['address'])
 ds=next(x['actual_DS'] for x in spec if x['build']==v);calls={cs*16+int(x['address'].split(':')[1],16):x['bytes'] for x in rows if x['bytes'].startswith(('e8','9a'))};targetaddrs={cs*16+t for t in targets}
 for index,target in enumerate(targets):
  c=chr(first+index);u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+0x5000,struct.pack('<2H',0x5100,0x5120));u.mem_write(ds*16+0x5100,b'n3d\0');u.mem_write(ds*16+0x5120,('-'+c).encode()+b'\0');u.mem_write(ds*16+0xe000,struct.pack('<4H',0,0x600,2,0x5000));state=dict(got=None,dispatch=False)
  def hook(u,a,size,_):
   if a==cs*16+int(jump['address'].split(':')[1],16):state['dispatch']=True
   if state['dispatch'] and a in targetaddrs:state['got']=a;u.emu_stop();return
   code=calls.get(a)
   if code:
    u.reg_write(UC_X86_REG_AX,0)
    if code.startswith('e8'):u.reg_write(UC_X86_REG_SP,u.reg_read(UC_X86_REG_SP)+2)
    u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+(3 if code.startswith('e8') else 5))
  u.hook_add(UC_HOOK_CODE,hook)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  u.emu_start(cs*16+ip,0,count=10000);assert state['got']==cs*16+target,(v,c,state,target);results.append(dict(build=v,option=c,target=f'{cs:04x}:{target:04x}',passed=True))
 lines=(o/f'DOS{v}.exe.rebuild.tsv').read_text().splitlines();matches=[x.split('\t') for x in lines if x.startswith('instruction\t')];assert all(x[4]=='true' for x in matches);assert any('decompile=true' in x for x in lines);summary.append(dict(build=v,matched=len(matches),mismatch=0,decompile=True,cases=len(targets)));print(v,len(targets),'dispatches passed')
(o/'switch_recovery_tests.json').write_text(json.dumps(dict(summary=summary,cases=results,passed=len(results),boundary='startup helper calls mocked; original parser dispatch executes; stop at selected branch entry'),indent=2)+'\n')
