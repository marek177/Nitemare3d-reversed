from pathlib import Path
import csv,json,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 files=[f for f in (root/'pass7/audit'/('DOS'+v)).glob('*_stock.c') if 'BsfDispatchMode(4)' in f.read_text()];assert len(files)==1
 cs,entry=[int(x,16) for x in files[0].name.split('_')[:2]];rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));body=[r for r in rows if r['address'].startswith(f'{cs:04x}:') and entry<=int(r['address'].split(':')[1],16)<entry+0x59];fc=[r for r in body if r['bytes'].startswith('9a')];assert len(fc)==3;sites={cs*16+int(r['address'].split(':')[1],16):k for r,k in zip(fc,['dispatch','print','free'])}
 free_ip,free_cs=struct.unpack_from('<HH',bytes.fromhex(fc[2]['bytes']),1);locations.append(dict(build=v,caller=f'{cs:04x}:{entry:04x}',free=f'{free_cs:04x}:{free_ip:04x}',instructions=body,exe_sha256=hashlib.sha256(b).hexdigest()))
 samples=[('empty',b''),('single',b'A'),('two',b'AB'),('three',b'ABC'),('embedded_nul',b'A\0B'),('high_byte',b'\xe9Z'),('crlf',b'A\r\n'),('real_mode4',(root/'pass7/data'/('DOS'+v+'_mode4.bin')).read_bytes())]
 for (label,data),segment,off in itertools.product(samples,[0,0x5000],[0x200,0xfffc]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));ds=q['actual_DS'];sp=0xe000;u.mem_write(ds*16+sp,struct.pack('<HH',0x600,0))
  for i,value in enumerate(data+b'\0'):u.mem_write(segment*16+((off+i)&65535),bytes([value]))
  header=segment*16+((off-2)&65535);u.mem_write(header,b'\x80\xa5');printed=[];freecalls=[];modes=[]
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def hook(uc,a,n,_):
   if a not in sites:return
   kind=sites[a];stack=ds*16+uc.reg_read(UC_X86_REG_SP)
   if kind=='dispatch':
    mode=struct.unpack('<H',uc.mem_read(stack,2))[0];assert mode==4;modes.append(mode);uc.reg_write(UC_X86_REG_AX,off);uc.reg_write(UC_X86_REG_DX,segment)
   elif kind=='print':
    fmt,arg=struct.unpack('<HH',uc.mem_read(stack,4));assert bytes(uc.mem_read(ds*16+fmt,3))==b'%c\0';printed.append(arg)
   else:
    actual=struct.unpack('<HH',uc.mem_read(stack,4));assert actual==(off,segment);freecalls.append(actual);return # Run original far free.
   uc.reg_write(UC_X86_REG_IP,a-cs*16+5)
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+entry,0x600,count=max(2000,40*len(data)))
  logical=data.split(b'\0')[0];expected=logical[:-1];signed=[x if x<128 else x|0xff00 for x in expected];assert printed==signed,(v,label,segment,off,len(printed),len(expected));assert len(modes)==len(freecalls)==1
  assert bytes(u.mem_read(header,2))==(b'\x81\xa5' if segment else b'\x80\xa5');assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4
  results.append(dict(build=v,case=label,segment=hex(segment),offset=hex(off),source_sha256=hashlib.sha256(data).hexdigest(),source_length=len(data),first_nul_length=len(logical),printed_length=len(printed),printed_sha256=hashlib.sha256(bytes(x&255 for x in printed)).hexdigest(),original_free_calls=len(freecalls),header_after=bytes(u.mem_read(header,2)).hex(),passed=True))
out=root/'pass15/evidence';out.mkdir(parents=True,exist_ok=True);(out/'mode4_owner.json').write_text(json.dumps(dict(cases=len(results),scope='Original mode4 caller and far free. Dispatch pointer and formatted character output mocked; no actual DOS console or loader execution.',locations=locations,results=results),indent=2));print(len(results),'passed')
