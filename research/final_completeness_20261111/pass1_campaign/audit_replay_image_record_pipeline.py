"""python audit_replay_image_record_pipeline.py IMAGE INVENTORY DECODER EMULATOR OUT
Original03CA+045C+0768:03CE and original XMSappend/wrapper; external DOS/heap/XMS fixtures.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rs):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
defs=[('image_record_raw_pixels_load',0x277,0x3ca,0x45c),('image_record_index_or_cache',0x277,0x45c,0x584),('image_record_tag_XMS_offset',0x768,0x3ce,0x402)];functions=[];starts={};visited={}
for name,cs,start,end in defs:
 todo=[start];dec={};edges=[]
 while todo:
  ip=todo.pop()
  if ip in dec:continue
  assert start<=ip<end;i=Decoder(16,b[cs*16+ip:cs*16+end],ip=ip).decode();assert not i.is_invalid;dec[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 rows=[]
 for ip,i in sorted(dec.items()):
  pos=cs*16+ip;raw=b[pos:cs*16+i.next_ip];assert old[pos]['bytes']==raw.hex();rows.append(dict(cs=cs,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rows);save(name+'_cfg',edges);functions.append(dict(name=name,start=cs*16+start,end_exclusive=cs*16+end,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows)));starts[name]=set(cs*16+q for q in dec);visited[name]=set()
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));runtimes={};cases=[]
for load in (0x824,0x1000):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 runtimes[load]=bytes(raw)
def run(load,cache,width,height,wall,used,limit,ok=1,error=0,fault=''):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,runtimes[load]);ds=load+0x2771;record=0x7000;handle=7;file_start=0x1a100;pixel_pos=file_start+10;area=width*height;src_off,src_seg=0x1000,0x6000;far=src_off|src_seg<<16;manager=0x80100;request_seg=load+0x1be7;request_ptr=request_seg*16+0x200
 dg=bytearray([0x66]*0xe030);dg[0x3cce]=cache;struct.pack_into('<HHH',dg,0x3506,1,limit,used);struct.pack_into('<HH',dg,0x350e,0x100,0x8000);struct.pack_into('<H',dg,0x2560,request_seg)
 for off in (0xe00e,0xe010,0xe01a,0xe01c):struct.pack_into('<H',dg,off,65535)
 header=bytes([width,height])+bytes(range(0xa0,0xa8));pixels=bytes((j*37+width+height)&255 for j in range(area));expected=bytearray(dg);er=bytearray(dg[record:record+10]);frees=[];calls=[];state=dict(cursor=file_start,manager=0,diagnostic=False);done=[];cached=False;expected_error='';chunks=(area+1023)//1024;accepted=((used+chunks)&65535)<=limit;offset=(used if used<32768 else used-65536)*1024&0xffffffff
 if fault=='header_short':er[:9]=header[:9];expected_error='header_short'
 else:
  er[:]=header;struct.pack_into('<I',er,2,pixel_pos)
  if cache:
   struct.pack_into('<I',er,6,0 if fault=='allocation' else far)
   if fault=='allocation':expected_error='allocation'
   elif fault=='pixels_short':expected_error='pixels_short'
   elif accepted and not ok and error>=128:expected_error='XMS_fatal'
   else:
    cached=accepted and (offset>>31)==0
    if accepted:struct.pack_into('<H',expected,0x350a,(used+chunks)&65535)
    if cached:struct.pack_into('<I',er,2,(-offset)&0xffffffff)
    stat=(0xe010 if wall else 0xe01c) if cached else (0xe00e if wall else 0xe01a);struct.pack_into('<H',expected,stat,0);struct.pack_into('<I',er,6,0)
  else:
   struct.pack_into('<I',er,6,0);stat=0xe00e if wall else 0xe01a;struct.pack_into('<H',expected,stat,0)
  if not expected_error:
   if wall and height!=64:expected_error='height'
   elif wall and width not in (64,128):expected_error='width'
   elif not wall and (area if area<32768 else area-65536)>0xc00:expected_error='area_signed'
 expected[record:record+10]=er;u.mem_write(ds*16,bytes(dg));u.mem_write(request_ptr,b'\x5a'*16);u.mem_write(src_seg*16+src_off,b'\xaa'*65536);u.mem_write(manager,b'\xcb')
 frame=struct.pack('<7H',0x100,0x5000,handle,record,0xab81,5,wall|0x3900);u.mem_write(ds*16+0xf000,frame)
 for q,value in [(UC_X86_REG_CS,load+0x277),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(q,value)
 targets={(load+0x11ee)*16+0x1e14:'header_read',(load+0x11ee)*16+0x2898:'tell',(load+0x11ee)*16+0x2065:'far_allocate',(load+0xfba)*16+0x9e:'far_read',(load+0x11ee)*16+0x1bd6:'seek',(load+0x11ee)*16+0x2052:'far_free',(load+0xfba)*16+0xc:'diagnostic',manager:'manager'}
 def hook(emu,address,size,data):
  if address==0x50100:done.append(True);emu.emu_stop();return
  p=address-load*16
  for name,points in starts.items():
   if p in points:visited[name].add(p);break
  if address not in targets:return
  name=targets[address];sp=emu.reg_read(UC_X86_REG_SP)
  def get(n):return struct.unpack('<'+'H'*n,bytes(emu.mem_read(ds*16+sp+4,n*2)))
  if name=='diagnostic':
   wanted={'header_short':(0x2d7 if cache else 0x333,0x628c),'allocation':(0x2fa,0x2ed),'pixels_short':(0x31d,0x628c),'XMS_fatal':(0xc6a,0,error<<8),'height':(0x350,0x349,height,0xab81,6),'width':(0x380,0x37a,width,0xab81,6),'area_signed':(0x3aa,area,0xc00,0xab81,6)}[expected_error]
   assert get(len(wanted))==wanted,(expected_error,get(len(wanted)),wanted);state['diagnostic']=True;emu.emu_stop();return
  calls.append(name)
  if name=='manager':
   assert cache and accepted and emu.reg_read(UC_X86_REG_AH)==0xb and emu.reg_read(UC_X86_REG_DS)==request_seg and emu.reg_read(UC_X86_REG_SI)==0x200
   expected_req=struct.pack('<IHIHI',chunks*1024,0,far,1,offset);assert bytes(emu.mem_read(request_ptr,16))==expected_req;state['manager']+=1;emu.reg_write(UC_X86_REG_AX,ok);emu.reg_write(UC_X86_REG_BL,error);return
  if name=='header_read':
   assert get(3)==(handle,record,10);n=9 if fault=='header_short' else 10;emu.mem_write(ds*16+record,header[:n]);state['cursor']+=n;emu.reg_write(UC_X86_REG_AX,n)
  elif name=='tell':assert get(1)==(handle,);emu.reg_write(UC_X86_REG_AX,state['cursor']&65535);emu.reg_write(UC_X86_REG_DX,state['cursor']>>16)
  elif name=='far_allocate':assert get(1)==(area,);emu.reg_write(UC_X86_REG_AX,0 if fault=='allocation' else src_off);emu.reg_write(UC_X86_REG_DX,0 if fault=='allocation' else src_seg)
  elif name=='far_read':
   assert get(4)==(handle,src_off,src_seg,area);n=max(0,area-1) if fault=='pixels_short' else area
   if n:emu.mem_write(src_seg*16+src_off,pixels[:n])
   state['cursor']+=n;emu.reg_write(UC_X86_REG_AX,n)
  elif name=='seek':
   signed_area=area if area<32768 else area-65536;assert get(4)==(handle,area,65535 if signed_area<0 else 0,1);state['cursor']=(state['cursor']+signed_area)&0xffffffff;emu.reg_write(UC_X86_REG_AX,state['cursor']&65535);emu.reg_write(UC_X86_REG_DX,state['cursor']>>16)
  else:assert get(2)==(src_off,src_seg);frees.append(True)
  ret,rcs=struct.unpack('<HH',bytes(emu.mem_read(ds*16+sp,4)));emu.reg_write(UC_X86_REG_SP,sp+4);emu.reg_write(UC_X86_REG_CS,rcs);emu.reg_write(UC_X86_REG_IP,ret)
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((load+0x277)*16+0x45c,0xfffff,count=3000)
 assert bool(state['diagnostic'])==bool(expected_error) and bool(done)==(not expected_error),(cache,width,height,wall,fault,expected_error,calls)
 assert bytes(u.mem_read(ds*16,len(dg)))==expected,(load,cache,width,height,wall,used,limit,ok,error,fault,expected_error)
 assert len(frees)==int(bool(cache) and fault not in ('header_short','allocation','pixels_short') and expected_error!='XMS_fatal')
 assert state['manager']==int(bool(cache) and accepted and fault not in ('header_short','allocation','pixels_short'))
 if not expected_error:
  assert u.reg_read(UC_X86_REG_DS)==u.reg_read(UC_X86_REG_SS)==ds and u.reg_read(UC_X86_REG_SP)==0xf004 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x2345 and u.reg_read(UC_X86_REG_DI)==0x3456 and bytes(u.mem_read(ds*16+0xf000,14))==frame
 cases.append(dict(load=load,cache_BYTE=cache,width=width,height=height,wall_BYTE=wall,area_unsigned=area,used_KiB=used,limit_KiB=limit,manager_AX=ok,manager_BL=error,fault=fault,diagnostic=expected_error,cached_marker=cached,final_file_cursor=state['cursor'],final_record_hex=bytes(er).hex(),status='PASS'))
sizes=((0,0),(64,64),(128,64),(39,34),(48,64),(49,64),(65,64),(64,63),(255,255),(128,255))
for load,cache,(width,height),wall,(used,limit,ok,error) in itertools.product((0x824,0x1000),(0,1),sizes,(0,1,255),((1,100,1,0),(1,1,1,0),(0,100,1,0),(32768,65535,1,0),(1,100,0,0x7f),(1,100,0,0x80))):run(load,cache,width,height,wall,used,limit,ok,error)
for load,cache in itertools.product((0x824,0x1000),(0,1)):run(load,cache,64,64,1,1,100,fault='header_short')
for load,fault in itertools.product((0x824,0x1000),('allocation','pixels_short')):run(load,1,64,64,1,1,100,fault=fault)
save('cases',cases);save('instruction_execution_coverage',[dict(function=n,image_offset=p,executed=p in visited[n]) for n in starts for p in sorted(starts[n])])
s=dict(functions=functions,cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,executed_instruction_starts=sum(len(v) for v in visited.values()),unexecuted_starts={n:sorted(starts[n]-visited[n]) for n in starts},scope='whole original3newfunctions plus originalXMSappend/wrapper; external DOS/heap/XMSmanager fixtures; fullDGROUP/counters/records/requests checked; diagnostics stop atentry; unsignedpixel area but signedskip/sizecheck preserved; managerAX0 BL<80 still permits append bookkeeping; no native fullpixel/render/XMS implementation parity',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,image.parent/'relocations.csv',Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
