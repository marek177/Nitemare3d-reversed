from pathlib import Path
import csv,json,struct,re,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
def s16(x):return ((x+32768)&65535)-32768
values=sorted(set(range(0,329,8))|{1,7,15,199,255,319,321,32767,32768,65535})
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];split=next(x for x in json.loads((root/'pass25/evidence/blit_callers.json').read_text())['locations'] if x['build']==v and x['kind']=='split');boundary=int(split['boundary_global'],16);rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));writes=[(i,r) for i,r in enumerate(rows) if r['bytes']=='8916'+struct.pack('<H',boundary).hex()];assert len(writes)==1;i,writer=writes[0];starts=[j for j in range(max(0,i-40),i) if rows[j]['bytes']=='56' and rows[j+1]['bytes'].startswith('a1') and rows[j+2]['bytes']=='d1f8'];assert len(starts)==1;start=starts[0];body=[]
 for r in rows[start:]:
  body.append(r)
  if r['bytes']=='cb':break
 cs,entry=[int(x,16) for x in rows[start]['address'].split(':')];source=struct.unpack_from('<H',bytes.fromhex(rows[start+1]['bytes']),1)[0];halfword=struct.unpack_from('<H',bytes.fromhex(rows[start+3]['bytes']),1)[0];outputbase=halfword-2;calls=[r for r in body if r['bytes'].startswith('9a')];assert len(calls)==2;sites={cs*16+int(r['address'].split(':')[1],16) for r in calls};ds=q['actual_DS'];sp=0xe000
 def refs(address):return [dict(previous=rows[max(0,k-3):k],instruction=r,following=rows[k+1:k+3]) for k,r in enumerate(rows) if re.search(r'\b0x'+format(address,'x')+r'\b',r['disassembly'])]
 splitcalls=[dict(previous=rows[max(0,k-4):k],instruction=r) for k,r in enumerate(rows) if split['entry'] in r['targets'] and 'CALL' in r['flow']]
 locations.append(dict(build=v,setter_entry=f'{cs:04x}:{entry:04x}',source_width=hex(source),output_base=hex(outputbase),boundary=hex(boundary),instructions=body,boundary_direct_refs=refs(boundary),width_direct_refs=refs(source),split_direct_callers=splitcalls,exe_sha256=hashlib.sha256((root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes()).hexdigest()))
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 for width in values:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+source,struct.pack('<H',width));u.mem_write(ds*16+outputbase,b'\xa5'*18);u.mem_write(ds*16+sp,struct.pack('<HH',0x600,0));seen=[]
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def hook(uc,a,n,_):
   if a in sites:seen.append(hex(a));uc.reg_write(UC_X86_REG_IP,a-cs*16+5)
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+entry,0x600,count=1000);w=s16(width);hh=w>>1;left=(320-w)>>1;top=s16(left)>>1;bottom=s16(top+hh-1);center=s16(top+(hh>>1));expected=[width,hh,left,s16(left+w-1),top,bottom,s16(left+hh),center,s16(center<<4)];actual=list(struct.unpack('<9H',u.mem_read(ds*16+outputbase,18)));assert actual==[x&65535 for x in expected],(v,width,actual,expected);assert len(seen)==2 and u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,input_width=width,outputs=actual,boundary_signed=bottom,split_y4_available=s16(bottom-4+1),dependency_calls=seen,passed=True))
out=root/'pass26/evidence';(out/'viewport_boundary.json').write_text(json.dumps(dict(cases=len(results),scope='Original viewport arithmetic setter, two downstream callees mocked. Direct boundary/width refs and split callsite contexts from Ghidra export; no whole-game input reachability.',locations=locations,results=results),indent=2));print(len(results),'passed; widths',len(values))
