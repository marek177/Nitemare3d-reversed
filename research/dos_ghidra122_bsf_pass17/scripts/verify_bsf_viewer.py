from pathlib import Path
import json,csv,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];catalog=next(x for x in json.loads((root/'pass15/evidence/bsf_callers.json').read_text()) if x['build']==v);cs,entry=[int(x,16) for x in catalog['dynamic_caller_entry'].split(':')];b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));body=[r for r in rows if r['address'].startswith(f'{cs:04x}:') and entry<=int(r['address'].split(':')[1],16)<entry+0x1e4];end=next(i for i,r in enumerate(body) if r['bytes']=='cb');body=body[:end+1];calls=[r for r in body if r['bytes'].startswith(('9a','e8'))];free_entry=next(x for x in json.loads((root/'pass15/evidence/mode4_owner.json').read_text())['locations'] if x['build']==v)['free'];free_off,free_seg=[int(x,16) for x in free_entry.split(':')][::-1];free_bytes='9a'+struct.pack('<HH',free_off,free_seg).hex();free_index=next(i for i,r in enumerate(calls) if r['bytes']==free_bytes);sites={cs*16+int(r['address'].split(':')[1],16):(i,r) for i,r in enumerate(calls)}
 # Calls in order: initial setup, dispatch, UI setup/color, page renderer, UI setup/color, key,
 # optional print-dialog/format dependencies, page renderer, cleanup query/message, free, final setup.
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',calls=calls,exe_sha256=hashlib.sha256(b).hexdigest()))
 samples=[('empty',b''),('one',b'A'),('pages',b'A#B#C'),('leading',b'#A'),('repeated',b'A##B'),('trailing',b'A#B#'),('mode3',(root/'pass7/data'/('DOS'+v+'_mode3.bin')).read_bytes()),('mode5',(root/'pass7/data'/('DOS'+v+'_mode5.bin')).read_bytes())]
 for (label,data),mode,keys in itertools.product(samples,[3,5],[[27],[80,27],[80,80,27],[80,72,27],[72,27]]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));ds=q['actual_DS'];sp=0xe000;off=0x200;seg=0x5000;u.mem_write(0x501fe,b'\x80\xa5'+data+b'\0');u.mem_write(ds*16+sp,struct.pack('<4H',0x600,0,16,mode));state=dict(key_index=0,pages=[],free_calls=0,dispatch_modes=[])
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def hook(uc,a,n,_):
   if a not in sites:return
   index,r=sites[a];near=r['bytes'].startswith('e8');stack=ds*16+uc.reg_read(UC_X86_REG_SP)+(2 if near else 0)
   if index==1:
    actual=struct.unpack('<H',uc.mem_read(stack,2))[0];assert actual==mode;state['dispatch_modes'].append(actual);uc.reg_write(UC_X86_REG_AX,off);uc.reg_write(UC_X86_REG_DX,seg)
   elif index in [4,12]:
    po,ps,page,total=struct.unpack('<4H',uc.mem_read(stack,8));assert ps==seg;state['pages'].append(dict(offset=po,page=page,total=total))
   elif index==7:
    assert state['key_index']<len(keys);uc.reg_write(UC_X86_REG_AX,keys[state['key_index']]);state['key_index']+=1
   elif index==free_index:
    assert struct.unpack('<HH',uc.mem_read(stack,4))==(off,seg);state['free_calls']+=1;return
   else:uc.reg_write(UC_X86_REG_AX,0)
   if near:uc.reg_write(UC_X86_REG_SP,uc.reg_read(UC_X86_REG_SP)+2)
   uc.reg_write(UC_X86_REG_IP,a-cs*16+(3 if near else 5))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+entry,0x600,count=max(30000,30*len(data)))
  total=1+data.count(b'#');page=1;pos=0;expected=[dict(offset=off,page=1,total=total)]
  for key in keys:
   old=(page,pos)
   if key==80:
    marker=data.find(b'#',pos+1)
    if marker>=0:pos=marker+1;page+=1
   elif key==72 and pos!=0:
    pos=max(0,pos-2)
    while pos>0 and data[pos]!=35:pos-=1
    if pos>0:pos+=1
    page-=1
   if (page,pos)!=old:expected.append(dict(offset=off+pos,page=page,total=total))
  assert state['pages']==expected,(v,label,mode,keys,state['pages'],expected);assert state['key_index']==len(keys) and state['free_calls']==1 and state['dispatch_modes']==[mode]
  assert bytes(u.mem_read(0x501fe,2))==b'\x81\xa5' and u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,case=label,mode=mode,keys=keys,source_sha256=hashlib.sha256(data).hexdigest(),source_length=len(data),**state,passed=True))
out=root/'pass17/evidence';out.mkdir(parents=True,exist_ok=True);(out/'bsf_viewer.json').write_text(json.dumps(dict(cases=len(results),scope='Original full generic BSF viewer, page scanning/navigation and far free; dispatch return, key input, renderer/UI/print dependencies mocked. No actual DOS or framebuffer.',locations=locations,results=results),indent=2));print(len(results),'passed')
