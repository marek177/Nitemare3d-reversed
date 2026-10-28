from pathlib import Path
import json,struct,csv
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;out=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 cs,entry=map(lambda x:int(x,16),q['loader_entry'].split(':'));base=cs*16;ins=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));section=[r for r in ins if r['address'].startswith(f'{cs:04x}:') and entry<=int(r['address'].split(':')[1],16)<entry+0x98];fc=[r for r in section if r['bytes'].startswith('9a') and len(r['bytes'])==10];assert len(fc)==8
 kinds={base+int(r['address'].split(':')[1],16):k for r,k in zip(fc,['open','open_error','alloc','alloc_error','seek','read','close','decoder'])};ds=q['actual_DS'];key=bytes(p[ds*16-0x10000+q['key_offset']:ds*16-0x10000+q['key_offset']+52]);nameoff=bytes(p).find(b'nite3d.bsf\0')-(ds*16-0x10000);data=(root/'pass7/data'/('DOS'+v+'.bsf')).read_bytes();res=next(r for r in json.loads((root/'pass7/evidence/bsf_resources.json').read_text()) if r['build']==v)
 raw=bytes.fromhex(fc[4]['bytes']);seek_ip,seek_cs=struct.unpack_from('<HH',raw,1);sb=[r for r in ins if r['address'].startswith(f'{seek_cs:04x}:') and seek_ip<=int(r['address'].split(':')[1],16)<seek_ip+0x82];maxaddr=struct.unpack_from('<H',bytes.fromhex(next(r for r in sb if r['bytes'].startswith('3b1e'))['bytes']),2)[0];guardaddr=struct.unpack_from('<H',bytes.fromhex(next(r for r in sb if r['bytes'].startswith('833e'))['bytes']),2)[0]
 tests=[(f"mode{r['mode']}",r['file_offset'],r['length'],None,None) for r in res['blocks']]+[('empty',0,0,None,None),('key_boundary',0,52,None,None),('short_zero',0,54,0,None),('short_53',0,54,53,None),('read_error',0,54,0,'read'),('seek_error',54,54,None,'seek'),('open_error',0,54,None,'open'),('alloc_error',0,54,None,'alloc')]
 for label,offset,length,short,error in tests:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(0x501ff,b'\x5a'+b'\xa5'*(length+1)+b'\x5a');u.mem_write(ds*16+0xe000,struct.pack('<HHHIH',0x600,0,nameoff,offset,length));trace=[];stopped=[];state=dict(position=0,seek_calls=[])
  u.mem_write(ds*16+maxaddr,struct.pack('<H',20));u.mem_write(ds*16+guardaddr,bytes(2));u.mem_write(ds*16+maxaddr+5,b'\xa7')
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  def hook(uc,a,n,_):
   if a not in kinds:return
   kind=kinds[a];sp=uc.reg_read(UC_X86_REG_SP);stack=ds*16+sp
   if kind=='decoder':trace.append(kind);return
   if kind.endswith('_error'):stopped.append(kind);uc.emu_stop();return
   if kind=='open':
    filename,flags=struct.unpack('<HH',uc.mem_read(stack,4));assert filename==nameoff and flags==0x8000;uc.reg_write(UC_X86_REG_AX,0xffff if error=='open' else 3)
   elif kind=='alloc':
    requested=struct.unpack('<H',uc.mem_read(stack,2))[0];assert requested==length+1;uc.reg_write(UC_X86_REG_AX,0 if error=='alloc' else 0x200);uc.reg_write(UC_X86_REG_DX,0 if error=='alloc' else 0x5000)
   elif kind=='seek':
    handle,lo,hi,origin=struct.unpack('<4H',uc.mem_read(stack,8));assert handle==3 and (hi<<16)|lo==offset and origin==0;trace.append(kind);return # Execute original seek
   elif kind=='read':
    handle,off,seg,count=struct.unpack('<4H',uc.mem_read(stack,8));assert (handle,off,seg,count)==(3,0x200,0x5000,length);nread=length if short is None else short
    if nread:uc.mem_write(0x50200,data[state['position']:state['position']+nread])
    uc.reg_write(UC_X86_REG_AX,0xffff if error=='read' else nread)
   elif kind=='close':assert struct.unpack('<H',uc.mem_read(stack,2))[0]==3
   trace.append(kind);uc.reg_write(UC_X86_REG_IP,a-base+5)
  def intr(uc,n,_):
   assert n==0x21 and uc.reg_read(UC_X86_REG_AX)==0x4200 and uc.reg_read(UC_X86_REG_BX)==3
   target=(uc.reg_read(UC_X86_REG_CX)<<16)|uc.reg_read(UC_X86_REG_DX);assert target==offset;state['seek_calls'].append(dict(target=target,error=error=='seek'))
   if error=='seek':uc.reg_write(UC_X86_REG_AX,5);uc.reg_write(UC_X86_REG_EFLAGS,uc.reg_read(UC_X86_REG_EFLAGS)|1)
   else:state['position']=target;uc.reg_write(UC_X86_REG_AX,target&65535);uc.reg_write(UC_X86_REG_DX,target>>16);uc.reg_write(UC_X86_REG_EFLAGS,uc.reg_read(UC_X86_REG_EFLAGS)&~1)
  u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_CODE,hook);u.emu_start(base+entry,0x600,count=max(1000,20*length+1000))
  if error in ['open','alloc']:assert stopped==[error+'_error']
  else:
   nread=length if short is None else short;source=data[state['position']:state['position']+nread]+b'\xa5'*(length-nread);expected=bytes(c^key[i%52] for i,c in enumerate(source));assert bytes(u.mem_read(0x50200,length+1))==expected+b'\0';assert u.reg_read(UC_X86_REG_AX)==0x200 and u.reg_read(UC_X86_REG_DX)==0x5000 and u.reg_read(UC_X86_REG_SP)==0xe004 and u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_IP)==0x600
   assert bytes(u.mem_read(0x501ff,1))==b'\x5a' and bytes(u.mem_read(0x50200+length+1,1))==b'\x5a' and trace==['open','alloc','seek','read','close','decoder']
  out.append(dict(build=v,case=label,offset=offset,length=length,short_read=short,error=error,seek_state=state,trace=trace,passed=True))
(root/'pass13/evidence/loader_seek_emulation.json').write_text(json.dumps(dict(cases=len(out),scope='original complete resource-loader instructions with mocked open/malloc/read/close; original lseek executes through mocked DOS INT21 seek and error dependency stops; original decoder executes',results=out),indent=2));print(len(out),'loader integration cases passed')
