from pathlib import Path
import csv,json,struct,itertools,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];loc=next(x for x in json.loads((root/'pass21/evidence/graphic_producers.json').read_text())['locations'] if x['build']==v);near=next(r for r in loc['loader_calls'] if r['bytes'].startswith('e8'));cs,ip=[int(x,16) for x in near['address'].split(':')];entry=(ip+3+struct.unpack('<h',bytes.fromhex(near['bytes'])[1:])[0])&65535;b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));body=[r for r in rows if r['address'].startswith(f'{cs:04x}:') and entry<=int(r['address'].split(':')[1],16)<entry+0xa0];body=body[:next(i for i,r in enumerate(body) if r['bytes']=='cb')+1];fc=[r for r in body if r['bytes'].startswith('9a')];assert len(fc)==7;sites={cs*16+int(r['address'].split(':')[1],16):kind for r,kind in zip(fc,['header','header_error','tell','alloc','alloc_error','pixels','pixels_error'])};locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',calls=fc,exe_sha256=hashlib.sha256(b).hexdigest()));ds=q['actual_DS'];sp=0xe000
 for width,height,error in itertools.product([0,1,2,255],[0,1,3,255],[None,'header','alloc','pixels']):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+0x8fff,b'\x5a'+b'\xa5'*10+b'\x5a');u.mem_write(ds*16+sp,struct.pack('<4H',0x600,0,3,0x9000));state=dict(trace=[],fatal=None);nbytes=width*height
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def hook(uc,a,n,_):
   if a not in sites:return
   kind=sites[a];state['trace'].append(kind);stack=ds*16+uc.reg_read(UC_X86_REG_SP)
   if kind.endswith('_error'):state['fatal']=kind;uc.emu_stop();return
   if kind=='header':
    assert struct.unpack('<3H',uc.mem_read(stack,6))==(3,0x9000,10);uc.mem_write(ds*16+0x9000,bytes([width,height])+b'\xa5'*8);uc.reg_write(UC_X86_REG_AX,9 if error=='header' else 10)
   elif kind=='tell':assert struct.unpack('<H',uc.mem_read(stack,2))[0]==3;uc.reg_write(UC_X86_REG_AX,0x5678);uc.reg_write(UC_X86_REG_DX,0x1234)
   elif kind=='alloc':assert struct.unpack('<H',uc.mem_read(stack,2))[0]==nbytes;uc.reg_write(UC_X86_REG_AX,0 if error=='alloc' else 0x200);uc.reg_write(UC_X86_REG_DX,0 if error=='alloc' else 0x5000)
   elif kind=='pixels':
    assert struct.unpack('<4H',uc.mem_read(stack,8))==(3,0x200,0x5000,nbytes);uc.reg_write(UC_X86_REG_AX,((nbytes-1)&65535) if error=='pixels' else nbytes)
   uc.reg_write(UC_X86_REG_IP,a-cs*16+5)
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+entry,0x600,count=10000);assert state['fatal']==(error+'_error' if error else None),(v,width,height,error,state)
  actual=bytes(u.mem_read(ds*16+0x9000,10));assert actual[:2]==bytes([width,height]);assert u.mem_read(ds*16+0x8fff,1)[0]==u.mem_read(ds*16+0x900a,1)[0]==0x5a
  if error!='header':assert actual[2:6]==struct.pack('<I',0x12345678)
  if error not in ['header','alloc']:assert actual[6:10]==struct.pack('<I',0x50000200)
  if not error:assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4
  results.append(dict(build=v,width=width,height=height,pixel_bytes=nbytes,injected_error=error,record_hex=actual.hex(),**state,passed=True))
out=root/'pass21/evidence';(out/'graphic_record.json').write_text(json.dumps(dict(cases=len(results),scope='Original10-byte graphic-record reader with mocked header read,tell,far allocation,pixel read; fatal stopped. No actual asset or pixel decoding.',locations=locations,results=results),indent=2));print(len(results),'passed')
