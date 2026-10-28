from pathlib import Path
import csv,json,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];vl=next(x for x in json.loads((root/'pass17/evidence/bsf_viewer.json').read_text())['locations'] if x['build']==v);call=vl['calls'][4];cs,site=[int(x,16) for x in call['address'].split(':')];entry=(site+3+struct.unpack('<h',bytes.fromhex(call['bytes'])[1:])[0])&65535;b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));body=[r for r in rows if r['address'].startswith(f'{cs:04x}:') and entry<=int(r['address'].split(':')[1],16)<entry+0x200];end=next(i for i,r in enumerate(body) if r['bytes']=='cb');body=body[:end+1];calls=[r for r in body if r['bytes'].startswith(('9a','e8'))];assert len(calls)==13,(v,len(calls));sites={cs*16+int(r['address'].split(':')[1],16):(i,r) for i,r in enumerate(calls)};locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',calls=calls,exe_sha256=hashlib.sha256(b).hexdigest()))
 samples=[('empty',b''),('letters',b'ABC'),('space',b'A B'),('tab',b'A\tB'),('tab0',b'\tB'),('crlf',b'A\r\nB'),('inline_hash',b'A#B'),('page_marker',b'#ABC'),('line_marker',b'A\n#B'),('empty_lines',b'\n\nB'),('high_byte',b'\xe9Z'),('18lines',b'A\n'*17+b'B'),('19lines',b'A\n'*18+b'B')]
 for (label,data),width in itertools.product(samples,[3,7]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));ds=q['actual_DS'];sp=0xe000;u.mem_write(0x50200,data+b'\0\0');u.mem_write(ds*16+sp,struct.pack('<6H',0x600,0,0x200,0x5000,2,9));state=dict(glyphs=[],flush=0,fatal=False,width_queries=0)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def hook(uc,a,n,_):
   if a not in sites:return
   index,r=sites[a];near=r['bytes'].startswith('e8');stack=ds*16+uc.reg_read(UC_X86_REG_SP)+(2 if near else 0)
   if index in [0,4]:uc.reg_write(UC_X86_REG_AX,0x5d)
   elif index==2:
    dst=struct.unpack('<H',uc.mem_read(stack,2))[0];uc.mem_write(ds*16+dst,b'H\0')
   elif index==6:state['fatal']=True;uc.emu_stop();return
   elif index in [7,8,9]:raise AssertionError('Unexpected format command path')
   elif index==10:
    x,y,off,seg,color,flags=struct.unpack('<6H',uc.mem_read(stack,12));char=uc.mem_read(seg*16+off,1)[0];assert uc.mem_read(seg*16+off+1,1)[0]==0 and color&255==0x5d and flags==0;state['glyphs'].append(dict(byte=char,x=x,y=y))
   elif index==11:state['width_queries']+=1;uc.reg_write(UC_X86_REG_AX,width)
   elif index==12:state['flush']+=1
   if near:uc.reg_write(UC_X86_REG_SP,uc.reg_read(UC_X86_REG_SP)+2)
   uc.reg_write(UC_X86_REG_IP,a-cs*16+(3 if near else 5))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+entry,0x600,count=30000)
  expected=[];x=12;y=7;col=0;at_start=True;fatal=False;queries=0
  for byte in data:
   if at_start:
    if byte==35:break
    if y>=205:fatal=True;break
    x=12;col=0;at_start=False
   if byte==10:y+=11;at_start=True;continue
   expected.append(dict(byte=byte,x=x,y=y))
   if byte==9:col+=4-col%4;x=6*(col+2)
   elif byte==32:x+=6;col+=1
   else:x+=width;col+=1;queries+=1
  assert state['glyphs']==expected and state['fatal']==fatal and state['width_queries']==queries,(v,label,width,state,expected)
  assert state['flush']==(0 if fatal else 1)
  if not fatal:assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4
  results.append(dict(build=v,case=label,width_return=width,**state,passed=True))
out=root/'pass18/evidence';out.mkdir(parents=True,exist_ok=True);(out/'text_layout.json').write_text(json.dumps(dict(cases=len(results),scope='Original page layout routine; UI/header/glyph renderer/width dependencies mocked. Percent command path excluded; fatal stops before callee. No framebuffer.',locations=locations,results=results),indent=2));print(len(results),'passed')
