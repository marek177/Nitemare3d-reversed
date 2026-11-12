"""IMAGE RELOCS RUNTIME WORK EMULATOR OUT: native XMS cache->scaled sprite/4 planes."""
import csv,hashlib,json,re,struct,sys
from pathlib import Path
image,relocs,runtime,work,emulator,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(emulator.resolve()))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INSN,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();out.mkdir(exist_ok=True);root=runtime.parent;s=json.loads((runtime/'summary.json').read_text());assert s['success'] and s['source_files_unchanged'];harness=root/'runtime_watch_object_cache_draw.py';support=root/'dosbox_watch_support_newgame_v1.py'
assert sha(harness.read_bytes())==s['harness_sha256']=='f4b7a9b43f5fa03960c3bb6abbb232d06eec23f4e8264e8071c706e229541b3c'
assert sha(support.read_bytes())==s['support_sha256']=='64675a5c918b22eb1d80e1d522efc1d459342a9ee04abf768a04b6a2e043fc89'
inputs=list(csv.DictReader((runtime/'inputs.csv').open(encoding='utf-8')));assert len(inputs)==23
for r in inputs:
 for key in ('source','copy'):
  raw=Path(r[key]).read_bytes();assert sha(raw)==r['sha256'] and len(raw)==int(r['bytes'])
b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';load=s['load_segment'];raw=bytearray(b)
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==raw
calls=json.loads((runtime/'object_cache_draw_calls.json').read_text());assert len(calls)==1;c=calls[0];prefix=c['prefix'];pre=c['pre_registers'];post=c['post_registers'];ds=load+0x2771;record=c['record_offset']
def read(name):return (work/(prefix+name+'.bin')).read_bytes()
frame=read('frame_before');retip,retcs,arg=struct.unpack('<3H',frame);assert arg==record and frame==read('frame_after');assert (pre['CS'],pre['IP'],pre['DS'],pre['SS'])==(load+0x768,0x4d8,ds,ds)
before=read('DGROUP_before');after=read('DGROUP_after');rec=read('record_before');reca=read('record_after');width,height=rec[:2];area=width*height;tag=struct.unpack_from('<I',rec,2)[0];assert area==600 and (width,height)==(30,20) and tag==0xfff61000
count=c['slot_count'];index=c['slot_index'];assert (count,index)==(62,0);assert struct.unpack_from('<H',before,0x3504)[0]==count and struct.unpack('<H',read('index_before'))[0]==index
probe_kib=struct.unpack_from('<H',before,0x3cb4)[0];assert probe_kib==257 and min(((probe_kib-70)*1024)//3074,128)==count
table=read('pointer_table_before');assert table==read('pointer_table_after') and len(table)==512
pointers=[struct.unpack_from('<HH',table,4*n) for n in range(128)];assert all(off or seg for off,seg in pointers[:count]) and all((off,seg)==(0,0) for off,seg in pointers[count:])
off,seg=pointers[index];dest=((off+2)&65535)|(seg<<16);assert read('slot_owner_before')==b'\0\0' and c['old_owner']==0 and read('slot_owner_after')==struct.pack('<H',record)
length,handle,offset,dh,df=struct.unpack('<IHIHI',read('xms_request'));assert (length,handle,offset,dh,df)==(1024,1,(-tag)&0xffffffff,0,dest)
pixels=read('destination_after_return');assert len(pixels)==1024 and pixels==read('destination_after_manager') and pixels!=read('destination_before')
assert c['manager_return_registers']['AX']==1 and c['manager_return_registers']['CS']==load+0x768 and c['manager_return_registers']['IP']==0x815
assert reca[:6]==rec[:6] and struct.unpack_from('<I',reca,6)[0]==dest and struct.unpack_from('<I',rec,6)[0]==0
expected=bytearray(before);struct.pack_into('<H',expected,0xc9c,1);assert after==expected and read('index_after')==b'\x01\0' and read('stats_before')==read('stats_after')==bytes(4)
assert c['pre_extra']==c['post_extra'];assert (post['CS'],post['IP'],post['DS'],post['SS'],post['SP'],post['AX'],post['DX'])==(retcs,retip,ds,ds,pre['SP']+4,(off+2)&65535,0)
imgpath=next(Path(r['source']) for r in inputs if Path(r['source']).name.upper()=='IMG.1');img=imgpath.read_bytes();code=0x25;payload=struct.unpack_from('<I',img,0x400+4*code)[0];assert payload==1348424 and img[payload:payload+2]==rec[:2];assert pixels[:area]==img[payload+10:payload+10+area]
# Replay original04D8+0350+07FE with captured XMS destination bytes/manager result fixture.
regs={'CS':UC_X86_REG_CS,'IP':UC_X86_REG_IP,'DS':UC_X86_REG_DS,'ES':UC_X86_REG_ES,'SS':UC_X86_REG_SS,'SP':UC_X86_REG_SP,'AX':UC_X86_REG_AX,'BX':UC_X86_REG_BX,'CX':UC_X86_REG_CX,'DX':UC_X86_REG_DX,'SI':UC_X86_REG_SI,'DI':UC_X86_REG_DI,'BP':UC_X86_REG_BP}
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,bytes(raw));u.mem_write(ds*16,read('draw_DS64_before'));u.mem_write(ds*16,before);u.mem_write(ds*16+record,rec);u.mem_write(ds*16+pre['SP'],frame);tableseg=struct.unpack('<H',read('table_segment'))[0];assert tableseg==load+0x1be7;u.mem_write(tableseg*16,table);u.mem_write(tableseg*16+0x200,b'\xa5'*16);u.mem_write(seg*16+off,read('slot_owner_before'));u.mem_write(seg*16+off+2,read('destination_before'))
for name,value in dict(pre,**c['pre_extra']).items():u.reg_write(regs[name],value)
u.reg_write(UC_X86_REG_EFLAGS,2);mgr=struct.unpack_from('<I',before,0x350e)[0];manager=(mgr>>16)*16+(mgr&65535);u.mem_write(manager,b'\xcb');cache_done=[];manager_seen=[];cache_trace=[]
def cache_hook(emu,address,size,data):
 if address==retcs*16+retip:cache_done.append(True);emu.emu_stop();return
 cache_trace.append(address-load*16)
 if address==manager:
  assert bytes(emu.mem_read(tableseg*16+0x200,16))==read('xms_request');manager_seen.append(True);emu.mem_write(seg*16+off+2,pixels);emu.reg_write(UC_X86_REG_AX,1);emu.reg_write(UC_X86_REG_BL,0)
u.hook_add(UC_HOOK_CODE,cache_hook);u.emu_start(pre['CS']*16+pre['IP'],0xfffff,count=3000);assert cache_done and len(manager_seen)==1
assert bytes(u.mem_read(ds*16,len(after)))==after and bytes(u.mem_read(ds*16+record,10))==reca and bytes(u.mem_read(tableseg*16,512))==table
for name,value in dict(post,**c['post_extra']).items():assert u.reg_read(regs[name])==value,('cache',name,u.reg_read(regs[name]),value)
# Native scaled-sprite entry and actual simple planar VGA configuration.
d=c['draw'];dp=d['pre_registers'];dz=d['post_registers'];q=d['queue_offset'];db=read('draw_DS64_before');da=read('draw_DS64_after');drawframe=read('draw_frame_before');drip,drcs,dq=struct.unpack('<3H',drawframe);assert dq==q and drawframe==read('draw_frame_after')
assert (dp['CS'],dp['IP'],dp['DS'],dp['SS'])==(load+0x156,0x5de,ds,ds);assert db[:0xe030]==da[:0xe030] and read('draw_queue_before')==read('draw_queue_after')==db[q:q+18]
slot=read('draw_queue_before');assert struct.unpack_from('<H',slot,6)[0]==record and read('draw_record')==reca and db[record:record+10]==reca
source=read('draw_source');assert source==pixels[:area];objectoff,objectseg=struct.unpack_from('<HH',slot,2);obj=read('draw_object_prefix6');assert obj[0]==code
def state(label):return json.loads((runtime/('draw_VGA_'+label+'.json')).read_text())
vb=state('before');va=state('after');gc='\n'.join(vb['GC']);mode='\n'.join(vb['MODE']);assert all(t in gc for t in ('enablesetreset=00h','data-rotate=00h','bitmask=ffh')) and 'wr-mode=0' in mode and 'chained=0' in mode
for label in ('before','after'):
 a=state(label);z=state(label+'_restored');assert all(a[k][1:-1]==z[k][1:-1] for k in a)
assert vb['GC'][1:-1]==va['GC'][1:-1]
initial_planes=[read('draw_before_plane%d'%p) for p in range(4)];native_planes=[read('draw_after_plane%d'%p) for p in range(4)];assert all(len(p)==65536 for p in initial_planes+native_planes)
page=struct.unpack_from('<H',db,0x12e)[0];x,x2,y,y2,depth=struct.unpack_from('<5h',slot,8);L,R,T,B=struct.unpack_from('<4h',db,0x4548);assert page==0xa400 and (x,x2,y,y2)==(82,96,86,95) and L<=x<x2<R and T<=y<=y2<=B
rows=y2-y+1;columns=x2-x+2;step=(height<<16)//rows;bypass=bool(obj[5]&0x10);expected_stores=[];expected_ports=[(0x3c4,1,2)];mask=((0x11<<(x&3))|(0x11>>(8-(x&3))))&255
for col in range(columns):
 expected_ports.append((0x3c5,1,mask));sx=(col*step)>>16;assert sx<width
 depthvalue=struct.unpack_from('<H',db,0x47e4+2*(x+col))[0]
 if bypass or depthvalue<=(depth&65535):
  for row in range(rows):
   sy=(row*step)>>16;pixel=source[sx*height+sy]
   if pixel!=31:expected_stores.append((page*16+(y+row)*80+(x+col)//4,1,pixel,mask&15))
 if (((col+1)*step)>>16)>=width:break
 if col+1==columns:
  expected_ports.append((0x3c5,1,((mask<<1)|(mask>>7))&255));break
 mask=((mask<<1)|(mask>>7))&255
observed_stores=[];observed_ports=[];planes=[bytearray(p) for p in initial_planes];mathematical_planes=[bytearray(p) for p in initial_planes];seq={'index':2,'mask':int(re.search(r'map_mask=([0-9a-f]+)h','\n'.join(vb['SEQ'])).group(1),16)};draw_done=[];draw_trace=[]
v=Uc(UC_ARCH_X86,UC_MODE_16);v.mem_map(0,0x100000);v.mem_write(load*16,bytes(raw));v.mem_write(ds*16,db);v.mem_write(seg*16+off+2,pixels);v.mem_write(objectseg*16+objectoff,obj);v.mem_write(0xa0000,initial_planes[0])
for name,value in dict(dp,**d['pre_extra']).items():v.reg_write(regs[name],value)
v.reg_write(UC_X86_REG_EFLAGS,2)
def draw_hook(emu,address,size,data):
 if address==drcs*16+drip:draw_done.append(True);emu.emu_stop();return
 draw_trace.append(address-load*16);assert emu.reg_read(UC_X86_REG_CS)==load+0x156
def port(emu,number,size,value,data):
 observed_ports.append((number,size,value));assert size==1
 if number==0x3c4:seq['index']=value
 else:assert number==0x3c5 and seq['index']==2;seq['mask']=value&15
def store(emu,access,address,size,value,data):
 if 0xa0000<=address<0xb0000:
  assert size==1;observed_stores.append((address,size,value,seq['mask']))
  for p in range(4):
   if seq['mask']&(1<<p):planes[p][address-0xa0000]=value
v.hook_add(UC_HOOK_CODE,draw_hook);v.hook_add(UC_HOOK_INSN,port,None,1,0,UC_X86_INS_OUT);v.hook_add(UC_HOOK_MEM_WRITE,store);v.emu_start(dp['CS']*16+dp['IP'],0xfffff,count=200000);assert draw_done
assert observed_stores==expected_stores and observed_ports==expected_ports
for address,size,value,maskbits in expected_stores:
 for p in range(4):
  if maskbits&(1<<p):mathematical_planes[p][address-0xa0000]=value
assert planes==mathematical_planes==native_planes
for name,value in dict(dz,**d['post_extra']).items():assert v.reg_read(regs[name])==value,('draw',name,v.reg_read(regs[name]),value)
assert bytes(v.mem_read(ds*16,0xe030))==da[:0xe030] and bytes(v.mem_read(ds*16+dp['SP'],6))==drawframe
finalmask=int(re.search(r'map_mask=([0-9a-f]+)h','\n'.join(va['SEQ'])).group(1),16);assert finalmask==seq['mask'] and 'index=02h' in '\n'.join(va['SEQ'])
store_rows=[dict(order=i,address=a,size=z,value=value,plane_mask=m) for i,(a,z,value,m) in enumerate(observed_stores)]
with (out/'verified_sprite_stores.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(store_rows[0]));w.writeheader();w.writerows(store_rows)
(out/'verified_sprite_ports.json').write_text(json.dumps(observed_ports,indent=2)+'\n',encoding='utf-8')
files={image.resolve(),relocs.resolve(),harness.resolve(),support.resolve(),Path(__file__).resolve()};files.update(Path(p).resolve() for p in s['capture_files']);files.update(p.resolve() for p in runtime.iterdir() if p.is_file() and p.name!='independent_verification.json')
proof=dict(verified=True,runtime_tests=1,status='PARTIAL',summary_sha256=sha((runtime/'summary.json').read_bytes()),runtime_image_sha256=sha(bytes(raw)),slot_count=count,probe_KiB=probe_kib,slot_index=index,record_offset=record,width=width,height=height,pixel_bytes=area,XMS_transfer_bytes=length,XMS_source_offset=offset,manager_AX=1,cache_destination_hex='%04X:%04X'%(seg,(off+2)&65535),cache_return_DX=post['DX'],pointer_table_bytes=512,active_pointer_prefix_bytes=count*4,cache_DGROUP_changed_offsets=[0xc9c],source_IMG1_object_code=code,IMG1_payload=payload,IMG1_pixels_file=payload+10,pixel_sha256=sha(source),cache_replay_instruction_events=len(cache_trace),cache_original_instruction_events=sum(p!=manager-load*16 for p in cache_trace),cache_external_manager_RETF_events=len(manager_seen),draw_original_replay_instructions=len(draw_trace),draw_unique_starts=len(set(draw_trace)),target_rectangle=[x,x2,y,y2],clip_rectangle=[L,R,T,B],source_step16_16=step,CPU_pixel_stores=len(observed_stores),replay_OUT_events=len(observed_ports),native_plane_changed_bytes=[sum(x!=y for x,y in zip(a,z)) for a,z in zip(initial_planes,native_planes)],native_plane_bytes_compared=4*65536,planes_sha256=sha(b''.join(native_planes)),independent_mathematical_store_model_matches=True,new_deep_verified_bytes=0,scope='One whole original04D8 XMS cache fill->first0156:05DE scaled sprite,actual600B source equals IMG1object25h (same600B exists other episodes),1024B nativeXMS readback/AX1.62of128FAR vector entries nonnull,cyclicindex0to1,no native eviction. Whole draw matches original replay plus independent unclipped/depth/transparency math and all4*65536B nativeVGA planes under captured simple write-mode0/maskFF/no-setreset. All captured cache/draw registers,frames andDGROUP agree; no complete frame/presentation/full clipping/Win16/lifecycle parity. Native OUT sequence not directly trapped; replay/mathematical sequence and nativefinal mask match.',files=[dict(path=str(p),sha256=sha(p.read_bytes())) for p in sorted(files)],asset_sources=[dict(path=r['source'],sha256=r['sha256']) for r in inputs])
(out/'independent_verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in proof.items() if k not in ('files','asset_sources')},indent=2))
