from pathlib import Path
import csv,json,struct,zipfile,re,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_MEM_WRITE,UC_HOOK_INSN
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;out=root/'pass22/evidence';out.mkdir(parents=True,exist_ok=True);(root/'pass22/data').mkdir(parents=True,exist_ok=True);results=[];blits=[];sources=[]
z=zipfile.ZipFile(root/'inputs/all-nite3d.zip') if (root/'inputs/all-nite3d.zip').exists() else None
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];bs=next(x for x in json.loads((root/'pass7/evidence/bsf_resources.json').read_text()) if x['build']==v);name=bs['source'].rsplit('/',1)[0]+'/IMG.1';asset=z.read(name) if z else (root/'pass22/data'/('DOS'+v+'_IMG.1')).read_bytes();(root/'pass22/data'/('DOS'+v+'_IMG.1')).write_bytes(asset);sources.append(dict(build=v,zip_source=name,size=len(asset),sha256=hashlib.sha256(asset).hexdigest()));indices=sorted(set(int(x) for x in re.findall(rb'%o(\d+)%',(root/'pass7/data'/('DOS'+v+'_mode3.bin')).read_bytes())))
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 producer=next(x for x in json.loads((root/'pass21/evidence/graphic_producers.json').read_text())['locations'] if x['build']==v);record=next(x for x in json.loads((root/'pass21/evidence/graphic_record.json').read_text())['locations'] if x['build']==v);parser=next(x for x in json.loads((root/'pass19/evidence/bsf_commands.json').read_text())['locations'] if x['build']==v);heap=next(x for x in json.loads((root/'pass14/evidence/far_allocator.json').read_text())['locations'] if x['build']==v)
 def phys(s):a,b=[int(x,16) for x in s.split(':')];return a*16+b
 def target(r):off,seg=struct.unpack_from('<HH',bytes.fromhex(r['bytes']),1);return seg,off
 hooks={}
 for r,kind in zip(producer['loader_calls'],['open','fatal','seek','read_near','fatal','fatal','seek','read_near','fatal','seek','original_record','close']):
  if kind!='original_record':hooks[phys(r['address'])]=kind
 for r,kind in zip(record['calls'],['read_near','fatal','tell','original_alloc','fatal','read_far','fatal']):
  if kind!='original_alloc':hooks[phys(r['address'])]=kind
 cs,entry=[int(x,16) for x in parser['entry'].split(':')];ds=q['actual_DS'];sp=0xf800
 # Layout passes record byte0 as outer column count and byte1 as inner row/column stride.
 layout=next(x for x in json.loads((root/'pass18/evidence/text_layout.json').read_text())['locations'] if x['build']==v);blit_cs,blit_ip=target(layout['calls'][8]);rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));screen=struct.unpack_from('<H',bytes.fromhex(next(r for r in rows if r['address'].startswith(f'{blit_cs:04x}:') and blit_ip<=int(r['address'].split(':')[1],16)<blit_ip+0x20 and r['bytes'].startswith('a1'))['bytes']),1)[0]
 for index in indices:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));command=('%o'+str(index)+'%').encode();u.mem_write(0x40200,command+b'\0'*16);u.mem_write(ds*16+0x9000,b'\x5a');u.mem_write(ds*16+0x9010,b'\xa5'*10);u.mem_write(ds*16+0x9020,bytes(2));u.mem_write(ds*16+sp,struct.pack('<7H',0x600,0,0x200,0x4000,0x9000,0x9010,0x9020));u.mem_write(ds*16+int(heap['failure_handler_address'],16),bytes(24));u.mem_write(ds*16+int(heap['minimum_segment_address'],16)-2,bytes(4));state=dict(position=0,trace=[],dos_allocations=0)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def hook(uc,a,n,_):
   if a not in hooks:return
   kind=hooks[a];stack=ds*16+uc.reg_read(UC_X86_REG_SP);state['trace'].append(kind)
   if kind=='fatal':raise AssertionError((v,index,state))
   if kind=='open':uc.reg_write(UC_X86_REG_AX,3);state['position']=0
   elif kind=='seek':
    handle,lo,hi,origin=struct.unpack('<4H',uc.mem_read(stack,8));assert handle==3;offset=(hi<<16)|lo;offset=offset if offset<0x80000000 else offset-0x100000000;state['position']=([0,state['position'],len(asset)][origin])+offset;uc.reg_write(UC_X86_REG_AX,state['position']&65535);uc.reg_write(UC_X86_REG_DX,state['position']>>16)
   elif kind=='tell':uc.reg_write(UC_X86_REG_AX,state['position']&65535);uc.reg_write(UC_X86_REG_DX,state['position']>>16)
   elif kind in ['read_near','read_far']:
    if kind=='read_near':handle,off,count=struct.unpack('<3H',uc.mem_read(stack,6));seg=ds
    else:handle,off,seg,count=struct.unpack('<4H',uc.mem_read(stack,8))
    assert handle==3;chunk=asset[state['position']:state['position']+count];uc.mem_write(seg*16+off,chunk);state['position']+=len(chunk);uc.reg_write(UC_X86_REG_AX,len(chunk))
   elif kind=='close':assert struct.unpack('<H',uc.mem_read(stack,2))[0]==3
   # All intercepted I/O callsites are original far calls.
   uc.reg_write(UC_X86_REG_IP,(a-uc.reg_read(UC_X86_REG_CS)*16)+5)
  def intr(uc,n,_):
   assert n==0x21 and uc.reg_read(UC_X86_REG_AH)==0x48;state['dos_allocations']+=1;assert state['dos_allocations']==1;uc.reg_write(UC_X86_REG_AX,0x6000);uc.reg_write(UC_X86_REG_EFLAGS,uc.reg_read(UC_X86_REG_EFLAGS)&~1)
  hcode=u.hook_add(UC_HOOK_CODE,hook);hi=u.hook_add(UC_HOOK_INTR,intr);u.emu_start(cs*16+entry,0x600,count=100000)
  offset=struct.unpack_from('<I',asset,1024+index*4)[0];w,h=asset[offset:offset+2];payload=asset[offset+10:offset+10+w*h];rec=bytes(u.mem_read(ds*16+0x9010,10));assert rec==bytes([w,h])+struct.pack('<II',offset+10,0x60000016),(v,index,rec.hex());assert bytes(u.mem_read(0x60016,w*h))==payload;assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4
  results.append(dict(build=v,index=index,record_offset=offset,width=w,height=h,pixel_bytes=w*h,pixel_sha256=hashlib.sha256(payload).hexdigest(),record_hex=rec.hex(),trace=state['trace'],passed=True));u.hook_del(hcode);u.hook_del(hi)
  for transparent in [65535,31]:
   x=index%4;y=7;u.mem_write(ds*16+screen,struct.pack('<H',0x7000));u.mem_write(ds*16+sp,struct.pack('<12H',0x600,0,0x16,0x6000,x,y,w,h,w,h,0,transparent));render=dict(mask=0,writes=[])
   for reg,val in [(UC_X86_REG_CS,blit_cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
   def port(uc,port,size,value,_):
    assert size==1 and port in [0x3c4,0x3c5]
    if port==0x3c4:assert value==2
    else:render['mask']=value&15
   def write(uc,access,a,size,value,_):
    if 0x70000<=a<0x80000:assert size==1;render['writes'].append((render['mask'],a-0x70000,value))
   hp=u.hook_add(UC_HOOK_INSN,port,None,1,0,UC_X86_INS_OUT);hm=u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(blit_cs*16+blit_ip,0x600,count=max(5000,20*w*h));expected=[(1<<((x+col)%4),(y+row)*80+(x+col)//4,payload[col*h+row]) for col in range(w) for row in range(h) if transparent==65535 or payload[col*h+row]!=transparent];assert render['writes']==expected,(v,index,transparent,len(render['writes']),len(expected));assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds;u.hook_del(hp);u.hook_del(hm)
   blits.append(dict(build=v,index=index,x=x,y=y,width=w,height=h,transparent=transparent,writes=len(expected),write_trace_sha256=hashlib.sha256(json.dumps(expected).encode()).hexdigest(),passed=True))
(out/'real_graphics.json').write_text(json.dumps(dict(load_cases=len(results),blit_cases=len(blits),scope='Original command parser/sscanf/object loader/record reader/far allocator with real IMG.1 bytes, simulated file I/O and DOS allocation; original blitter with OUT/memory-write observation and planar write oracle, not full VGA/DAC.',sources=sources,loads=results,blits=blits),indent=2));print(len(results),'loads and',len(blits),'blits passed')
