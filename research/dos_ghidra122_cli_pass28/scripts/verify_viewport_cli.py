from pathlib import Path
import csv,json,struct,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
meta=json.loads((root/'pass26/evidence/viewport_boundary.json').read_text())['locations']
inputs=[('',None),('x',None),('304',304),('311',311),('0',0),('7',7),('8',8),('320',320),('328',328),('-1',65535),('-8',65528),('32768',32768),('65535',65535),('65536',0),('65537',1),('  +319junk',319),('0x130',0),('0304',304)]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];m=next(x for x in meta if x['build']==v);ds=q['actual_DS'];source=int(m['source_width'],16);rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));marker='8026'+struct.pack('<H',source).hex()+'f8';i=next(i for i,r in enumerate(rows) if r['bytes']==marker);body=rows[i-8:i+5];assert body[0]['bytes']=='68'+struct.pack('<H',source).hex();cs,entry=[int(x,16) for x in body[0]['address'].split(':')];stop=cs*16+int(rows[i+3]['address'].split(':')[1],16)+3
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 fmt=int.from_bytes(bytes.fromhex(body[1]['bytes'])[1:],'little');fmtbytes=bytes(p[(ds-0x1000)*16+fmt:]).split(b'\0')[0];assert fmtbytes==b'%d',fmtbytes
 settercs=int(m['setter_entry'].split(':')[0],16);deps={settercs*16+int(r['address'].split(':')[1],16) for r in m['instructions'] if r['bytes'].startswith('9a')}
 # Identify option jump-table entry from raw relocated CS words, not Ghidra data decoding.
 tables=[]
 for r in rows:
  rb=bytes.fromhex(r['bytes'])
  if r['address'].startswith(f'{cs:04x}:') and rb[:3]==bytes.fromhex('2effa7'):
   tab=int.from_bytes(rb[3:5],'little');vals=struct.unpack_from('<24H',p,(cs-0x1000)*16+tab)
   if entry in vals:tables.append(dict(address=f'{cs:04x}:{tab:04x}',option=chr(97+vals.index(entry)),targets=list(vals)))
 assert len(tables)==1
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',width=hex(source),format=fmtbytes.decode(),dispatch_table=tables[0],instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 for text,parsed in inputs:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xf800;initial=311;u.mem_write(ds*16+source,struct.pack('<H',initial));u.mem_write(ds*16+0x602,struct.pack('<H',0x700));u.mem_write(ds*16+0x700,text.encode()+b'\0');seen=[];done=[];scanret=[]
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp),(UC_X86_REG_DI,0x600),(UC_X86_REG_SI,0)]:u.reg_write(reg,val)
  afterscan=cs*16+int(rows[i-1]['address'].split(':')[1],16)
  def hook(uc,a,n,_):
   if a==afterscan:scanret.append(uc.reg_read(UC_X86_REG_AX))
   if a==stop:done.append(True);uc.emu_stop()
   if a in deps:seen.append(a);uc.reg_write(UC_X86_REG_IP,a-settercs*16+5)
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+entry,0,count=100000)
  actual=struct.unpack('<H',u.mem_read(ds*16+source,2))[0];expected=(initial if parsed is None else parsed)&0xfff8
  assert done and actual==expected and len(seen)==2,(v,text,actual,expected,done,seen)
  assert scanret==([65535] if text=='' else [0] if parsed is None else [1]),(text,scanret)
  assert u.reg_read(UC_X86_REG_SP)==sp and u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SI)==1
  results.append(dict(build=v,input=text,initial_width=initial,scanf_return=scanret[0],result_width=actual,dependency_calls=len(seen),passed=True))
(root/'pass28/evidence/cli.json').write_text(json.dumps(dict(cases=len(results),scope='Original CLI conversion fragment, original sscanf and original viewport setter. Two downstream setter calls mocked. Stop after setter argument cleanup; full argv dispatcher not executed.',locations=locations,results=results),indent=2));print(len(results),'passed')
