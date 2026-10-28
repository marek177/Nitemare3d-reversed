from pathlib import Path
import csv,json,struct,itertools,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];ev=json.loads((root/'pass19/evidence/bsf_commands.json').read_text());loc=next(x for x in ev['locations'] if x['build']==v);rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'))
 targets={}
 for cmd in ['o','p']:
  r=next(x for x in ev['results'] if x['build']==v and x['command']==cmd and x['injected_value']==0 and x['injected_conversion_count']==1);physical=int(r['effects'][0]['site'],16);call=next(x for x in loc['calls'] if int(x['address'].split(':')[0],16)*16+int(x['address'].split(':')[1],16)==physical);ip,cs=struct.unpack_from('<HH',bytes.fromhex(call['bytes']),1);targets[cmd]=(cs,ip)
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 def section(cs,ip,n):return [r for r in rows if r['address'].startswith(f'{cs:04x}:') and ip<=int(r['address'].split(':')[1],16)<ip+n]
 cs,entry=targets['o'];body=section(cs,entry,0xf4);fc=[r for r in body if r['bytes'].startswith(('9a','e8'))];assert len(fc)==12,(v,len(fc));kinds=['open','fatal','seek','read4','fatal','fatal','seek','read10','fatal','seek_relative','final_reader','close'];sites={cs*16+int(r['address'].split(':')[1],16):(kind,r['bytes'].startswith('e8')) for r,kind in zip(fc,kinds)}
 pcs,pentry=targets['p'];pb=section(pcs,pentry,0x1c);mapcall=next(r for r in pb if r['bytes'].startswith('9a'));mip,mcs=struct.unpack_from('<HH',bytes.fromhex(mapcall['bytes']),1);mb=section(mcs,mip,0x36);table=struct.unpack_from('<H',bytes.fromhex(next(r for r in mb if r['bytes'].startswith('8a87'))['bytes']),2)[0];fatal=next(r for r in mb if r['bytes'].startswith('9a'));mapfatal=mcs*16+int(fatal['address'].split(':')[1],16);forward=next(r for r in pb if r['bytes'].startswith('e8'));forwardsite=pcs*16+int(forward['address'].split(':')[1],16)
 locations.append(dict(build=v,object_loader=f'{cs:04x}:{entry:04x}',picture_wrapper=f'{pcs:04x}:{pentry:04x}',class_lookup=f'{mcs:04x}:{mip:04x}',class_table=hex(table),loader_calls=fc,exe_sha256=hashlib.sha256(b).hexdigest()));ds=q['actual_DS'];sp=0xe000
 for index,frame in itertools.product([0,1,255,65535,0x4000],[-1,0,1,2]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+sp,struct.pack('<5H',0x600,0,index,frame&65535,0x9000));state=dict(seeks=[],headers=0,final_reader=[],close=0)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def hook(uc,a,n,_):
   if a not in sites:return
   kind,near=sites[a];stack=ds*16+uc.reg_read(UC_X86_REG_SP)+(2 if near else 0)
   if kind=='fatal':raise AssertionError((v,index,frame,'unexpected fatal'))
   if kind=='open':filename,flags=struct.unpack('<2H',uc.mem_read(stack,4));assert flags==0x8000;uc.reg_write(UC_X86_REG_AX,3)
   elif kind in ['seek','seek_relative']:
    handle,lo,hi,origin=struct.unpack('<4H',uc.mem_read(stack,8));assert handle==3;state['seeks'].append(dict(offset=hi*65536+lo,origin=origin))
   elif kind in ['read4','read10']:
    handle,dst,count=struct.unpack('<3H',uc.mem_read(stack,6));assert handle==3 and count==(4 if kind=='read4' else 10)
    uc.mem_write(ds*16+dst,struct.pack('<I',0x12345678) if kind=='read4' else b'\x02\x03'+bytes(8));uc.reg_write(UC_X86_REG_AX,count)
    if kind=='read10':state['headers']+=1
   elif kind=='final_reader':state['final_reader'].append(list(struct.unpack('<2H',uc.mem_read(stack,4))))
   elif kind=='close':assert struct.unpack('<H',uc.mem_read(stack,2))[0]==3;state['close']+=1
   if near:uc.reg_write(UC_X86_REG_SP,uc.reg_read(UC_X86_REG_SP)+2)
   uc.reg_write(UC_X86_REG_IP,a-cs*16+(3 if near else 5))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+entry,0x600,count=10000)
  n=max(0,frame);assert state['seeks']==[dict(offset=((index+256)*4)&65535,origin=0),dict(offset=0x12345678,origin=0)]+[dict(offset=6,origin=1)]*n;assert state['headers']==n and state['final_reader']==[[3,0x9000]] and state['close']==1
  assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4
  results.append(dict(build=v,kind='object_loader',index=index,frame=frame,**state,passed=True))
 for frame,match in itertools.product([0,1,31,65535],[None,0,7,255]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+table,bytes(256))
  if match is not None:u.mem_write(ds*16+table+match,b'\x3e')
  u.mem_write(ds*16+sp,struct.pack('<4H',0x600,0,frame,0x9000));state=dict(forwarded=[],fatal=False)
  for reg,val in [(UC_X86_REG_CS,pcs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def hookp(uc,a,n,_):
   if a==mapfatal:state['fatal']=True;uc.emu_stop()
   elif a==forwardsite:
    callsp=uc.reg_read(UC_X86_REG_SP);args=struct.unpack('<3H',uc.mem_read(ds*16+callsp+2,6));state['forwarded'].append(list(args));uc.reg_write(UC_X86_REG_SP,callsp+2);uc.reg_write(UC_X86_REG_IP,a-pcs*16+3)
  u.hook_add(UC_HOOK_CODE,hookp);u.emu_start(pcs*16+pentry,0x600,count=10000);assert state['fatal']==(match is None) and state['forwarded']==([] if match is None else [[match,frame,0x9000]])
  if match is not None:assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4
  results.append(dict(build=v,kind='picture_wrapper',frame=frame,class_match=match,**state,passed=True))
out=root/'pass21/evidence';out.mkdir(parents=True,exist_ok=True);(out/'graphic_producers.json').write_text(json.dumps(dict(cases=len(results),scope='Original object-loader selection/skip wrapper and picture class lookup; file I/O/final record reader mocked for object cases, loader target mocked for picture cases. No real assets/graphics.',locations=locations,results=results),indent=2));print(len(results),'passed')
