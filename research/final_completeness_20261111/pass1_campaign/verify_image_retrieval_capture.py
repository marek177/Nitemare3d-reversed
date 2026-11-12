"""IMAGE RELOCS RUNTIME WORK OUT: independently check original0402 native readback."""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,relocs,runtime,work,out=map(Path,sys.argv[1:]);sha=lambda x:hashlib.sha256(x).hexdigest();out.mkdir(exist_ok=True)
s=json.loads((runtime/'summary.json').read_text(encoding='utf-8'));assert s['success'] and not s['error'];assert s['harness_sha256']=='605531fca5786875f8c0cac5b5e2b3a1d16d8aec0c5f3ae5b94e59aa11279fce'
root=runtime.parent;harness=root/'runtime_watch_image_retrieval.py';support=root/'dosbox_watch_support_newgame_v1.py'
assert sha(harness.read_bytes())==s['harness_sha256'];assert sha(support.read_bytes())==s['support_sha256']=='64675a5c918b22eb1d80e1d522efc1d459342a9ee04abf768a04b6a2e043fc89'
inputs=list(csv.DictReader((runtime/'inputs.csv').open(encoding='utf-8')))
assert len(inputs)==23
for r in inputs:
 for key in ('source','copy'):
  raw=Path(r[key]).read_bytes();assert len(raw)==int(r['bytes']) and sha(raw)==r['sha256']
canonical=image.read_bytes();assert sha(canonical)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
load=s['load_segment'];expected=bytearray(canonical)
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',expected,int(r['image_offset']),(int(r['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==expected
calls=json.loads((runtime/'image_retrievals.json').read_text());assert len(calls)==1;c=calls[0];prefix=c['prefix'];pre=c['pre_registers'];post=c['post_registers'];ds=load+0x2771
assert (pre['CS'],pre['IP'],pre['DS'],pre['SS'])==(load+0x768,0x402,ds,ds)
def read(name):return (work/(prefix+name+'.bin')).read_bytes()
frame=read('frame_before');retip,retcs,record=struct.unpack('<3H',frame);assert record==c['record_offset'];assert frame==read('frame_after')
rec=read('record_before');after=read('record_after');tag=struct.unpack_from('<I',rec,2)[0];assert tag>=0x80000000 and rec[6:]==bytes(4)
tick=struct.unpack('<I',read('tick_before'))[0];assert read('tick_before')==read('tick_after')
ptrs=read('slot_pointers');assert len(ptrs)==40;headers=[read('slot_%02d_before'%i) for i in range(10)];times=[struct.unpack_from('<I',v)[0] for v in headers]
eligible=[(t,i) for i,t in enumerate(times) if t<tick];selected=min(eligible)[1] if eligible else 0
off,seg=struct.unpack_from('<HH',ptrs,4*selected);far=((off+6)&65535)|(seg<<16)
length,handle,sourceoffset,desthandle,dest=struct.unpack('<IHIHI',read('xms_request'))
assert (length,handle,sourceoffset,desthandle,dest)==(8192,1,(-tag)&0xffffffff,0,far)
assert c['manager_return_registers']['CS']==load+0x768 and c['manager_return_registers']['IP']==0x815 and c['manager_return_registers']['AX']==1
assert c['xms_move_registers']['CS']==load+0x768 and c['xms_move_registers']['IP']==0x7fe
assert (post['CS'],post['IP'],post['DS'],post['SS'],post['SP'],post['DX'],post['AX'])==(retcs,retip,ds,ds,pre['SP']+4,seg,(off+6)&65535)
assert after[:6]==rec[:6] and struct.unpack_from('<I',after,6)[0]==far
stats=bytearray(read('stats_before'));owner=struct.unpack_from('<H',headers[selected],4)[0];assert owner==0 # No native eviction claim.
if not eligible:struct.pack_into('<I',stats,4,(struct.unpack_from('<I',stats,4)[0]+1)&0xffffffff)
assert read('stats_after')==stats
for i,h in enumerate(headers):
 assert read('slot_%02d_after'%i)==(struct.pack('<IH',tick,record) if i==selected else h)
pixels=read('destination_after_return');assert len(pixels)==8192 and pixels==read('destination_after_manager')
imgrow=next(r for r in inputs if Path(r['source']).name.upper()=='IMG.1');img=Path(imgrow['source']).read_bytes()
# Exact directory lookup, independent of the earlier raw-image catalog.
code=16;payload=struct.unpack_from('<I',img,4*code)[0];header=img[payload:payload+10];assert header[:2]==rec[:2]==bytes([128,64])
pixels_file=payload+10;assert pixels==img[pixels_file:pixels_file+8192]
assert pixels!=read('destination_before')
files={image.resolve(),relocs.resolve(),harness.resolve(),support.resolve(),Path(__file__).resolve()}
files.update(Path(p).resolve() for p in s['capture_files'])
files.update(p.resolve() for p in runtime.iterdir() if p.is_file() and p.name!='independent_verification.json')
proof=dict(status='PARTIAL',verified=True,runtime_tests=1,summary_sha256=sha((runtime/'summary.json').read_bytes()),runtime_image_sha256=sha(bytes(expected)),checks_passed=True,native_scenarios=1,new_deep_verified_bytes=0,load_segment=load,record_offset=record,tag_hex='%08X'%tag,XMS_source_offset=sourceoffset,selected_slot=selected,slot_FAR_hex='%04X:%04X'%(seg,off),destination_FAR_hex='%04X:%04X'%(seg,(off+6)&65535),manager_return_AX=1,IMG_episode=1,wall_code=code,group_payload=payload,pixels_file=pixels_file,pixel_bytes=8192,pixels_sha256=sha(pixels),source_files_unchanged=23,old_owner=owner,tick=tick,scope='Original0402 call and0350/07FE, direct manager AX1,8192B destination equals actual IMG1 wall16 pixels,ten slot headers and current record/stats/frame checked. No native zero-tag,eviction,positive-file path,fullDGROUP,heap-allocation,renderer or Win16 parity claim.',files=[dict(path=str(p),sha256=sha(p.read_bytes())) for p in sorted(files)],asset_sources=[dict(path=r['source'],sha256=r['sha256']) for r in inputs])
(out/'independent_verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in proof.items() if k not in ('files','asset_sources')},indent=2))
