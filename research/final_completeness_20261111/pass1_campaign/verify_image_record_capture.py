"""python verify_image_record_capture.py IMAGE RELOCS RUNTIME WORK OUT
Native image metadata/rawpixel/XMSrequest/cache-tag stages; no XMS readback claim.
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,relocs,runtime,work,out=map(Path,sys.argv[1:]);out.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest();s=json.loads((runtime/'summary.json').read_text(encoding='utf-8'));assert s['success'] and s['source_files_unchanged'] and s['image_records']==1
b=image.read_bytes();load=s['load_segment'];relocated=bytearray(b);assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',relocated,int(r['image_offset']),(int(r['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==relocated
inputs=list(csv.DictReader((runtime/'inputs.csv').open()));assert len(inputs)==23
for r in inputs:assert sha(Path(r['source']).read_bytes())==sha(Path(r['copy']).read_bytes())==r['sha256']
img=next(Path(r['source']) for r in inputs if Path(r['source']).name=='IMG.1');rawimg=img.read_bytes();support=Path(__file__).with_name('dosbox_watch_support_newgame_v1.py');harness=Path(__file__).with_name('runtime_watch_image_record.py');assert sha(support.read_bytes())==s['support_sha256'] and sha(harness.read_bytes())==s['harness_sha256']
c=json.loads((runtime/'image_records.json').read_text(encoding='utf-8'))[0];p=c['prefix'];pre=c['pre_registers'];post=c['post_registers'];ds=pre['DS'];frame=(work/(p+'frame_before.bin')).read_bytes();assert len(frame)==14 and frame==(work/(p+'frame_after.bin')).read_bytes();ret,retcs,handle,record,code,index,wall=struct.unpack('<7H',frame)
assert (handle,record,code,index,wall)==(c['handle'],c['record_offset'],c['code_WORD'],c['image_index'],c['wall_WORD'])
assert (pre['CS'],pre['IP'])==(load+0x277,0x45c) and (post['CS'],post['IP'])==(retcs,ret)==(load+0x277,0x66d) and pre['DS']==pre['SS']==post['DS']==post['SS']==load+0x2771 and post['SP']==pre['SP']+4 and c['pre_extra']==c['post_extra']
assert (code,index,wall&255)==(1,0,1)
def read(stage,kind):return (work/(p+stage+'_'+kind+'.bin')).read_bytes()
stages=('entry','raw_loaded','xms_move','append_return','caller_return');recs={x:read(x,'record') for x in stages};stats={x:read(x,'stats') for x in stages};states={x:struct.unpack('<3H',read(x,'cache_state')) for x in stages}
assert all(len(recs[x])==10 and len(stats[x])==0x12 and read(x,'flag')==b'\1' for x in stages)
payload=struct.unpack_from('<I',rawimg,4*(code&255))[0];raw=recs['raw_loaded'];width,height=raw[:2];area=width*height;pixel_pos=payload+10;assert (width,height,area,payload)==(128,64,8192,0xbc00)
assert raw[:2]==rawimg[payload:payload+2] and struct.unpack_from('<I',raw,2)[0]==pixel_pos and recs['xms_move']==recs['append_return']==raw
pixels=(work/(p+'pixels_raw.bin')).read_bytes();moved=(work/(p+'xms_source.bin')).read_bytes();assert len(pixels)==area and pixels==moved==rawimg[pixel_pos:pixel_pos+area]
request=(work/(p+'xms_request.bin')).read_bytes();length,src_handle,source,dst_handle,destination=struct.unpack('<IHIHI',request);assert (length,src_handle,source,dst_handle,destination)==(8192,0,struct.unpack_from('<I',raw,6)[0],1,0)
assert struct.unpack('<H',(work/(p+'request_segment.bin')).read_bytes())[0]==load+0x1be7
assert states['entry']==states['raw_loaded']==states['xms_move']==(1,2048,0) and states['append_return']==states['caller_return']==(1,2048,8)
ar=c['append_return_registers'];assert (ar['CS'],ar['IP'],ar['AX'],ar['DX'])==(load+0x768,0x3e4,0,0)
assert recs['caller_return']==bytes([128,64])+b'\0'*8
assert stats['entry']==stats['raw_loaded']==stats['xms_move']==stats['append_return']==b'\0'*0x12;expected=bytearray(stats['entry']);struct.pack_into('<H',expected,0xe010-0xe00c,1);assert stats['caller_return']==expected
prior=Path(__file__).parent/'dosbox_xms_request_runtime/independent_verification.json';old=json.loads(prior.read_text(encoding='utf-8'));assert old['verified'] and old['xms_fields']==dict(length=length,source_handle=src_handle,source_far=source,destination_handle=dst_handle,destination_offset=destination) and old['native_return']==dict(AX=1,DX=0)
for r in old['files']:assert sha(Path(r['path']).read_bytes())==r['sha256']
context=dict(code_WORD=code,image_index=index,wall_WORD=wall,record_DS=record,width=width,height=height,IMG_payload_offset=payload,IMG_pixels_offset=pixel_pos,pixels_bytes=area,pixels_sha256=sha(pixels),raw_source_far=source,XMS_request=dict(length=length,source_handle=src_handle,source_far=source,destination_handle=dst_handle,destination_offset=destination),used_KiB_before=0,used_KiB_after=8,final_position_tag=0,final_pixels_pointer=0,cached_wall_counter_delta=1,prior_identical_request_native_return=old['native_return'],scope='current045C whole call with raw pixels identical IMG1 and XMS source,request emitted/tag0/counter/free-pointer-clear; current managerreturnAX not trapped,prior separate same-request wrapper-returnAX1 verified; no XMSreadback/wholeheap/VGA parity')
(runtime/'verified_image_record_context.json').write_text(json.dumps(context,indent=2)+'\n',encoding='utf-8')
fields=[dict(record='image_record10',offset=o,width=n,role=t,consumer='0277:03CA/045C and0768:03CE;PARTIAL') for o,n,t in [(0,1,'width BYTE'),(1,1,'height BYTE'),(2,4,'DWORD file pixel offset or negated XMS byte offset,including zero'),(6,4,'temporary FAR16 rawpixel pointer;free then zero')]]
with (out/'consumer_field_roles.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(fields[0]));w.writeheader();w.writerows(fields)
tables=[]
for off,name in [(0xe00e,'wall_uncached_count'),(0xe010,'wall_cached_count'),(0xe01a,'object_uncached_count'),(0xe01c,'object_cached_count')]:
 value=stats['caller_return'][off-0xe00c:off-0xe00c+2];tables.append(dict(name=name,ds_start=off,ds_end_exclusive=off+2,image_start=0x27710+off,image_end_exclusive=0x27710+off+2,length=2,type='mutable_WORD counter increment modulo65536 by045C branch; only cachedwall native increment captured',status='PARTIAL',runtime_sha256=sha(value),outside_original_file_image=True,original_NONCODE_bytes_added=0))
with (out/'external_bss_tables.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(tables[0]));w.writeheader();w.writerows(tables)
files=[Path(x) for x in s['capture_files']]+[runtime/'summary.json',runtime/'image_records.json',runtime/'verified_image_record_context.json',runtime/'inputs.csv',runtime/'runtime.conf',image,relocs,support,harness,Path(__file__),prior,out/'consumer_field_roles.csv',out/'external_bss_tables.csv']
proof=dict(verified=True,runtime_tests=1,new_deep_verified_bytes=0,summary_sha256=sha((runtime/'summary.json').read_bytes()),runtime_image_sha256=sha(relocated),scope=context['scope'],files=[dict(path=str(q.resolve()),sha256=sha(q.read_bytes())) for q in dict.fromkeys(files)])
(runtime/'independent_verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(context,indent=2))
