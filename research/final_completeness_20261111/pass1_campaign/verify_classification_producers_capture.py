"""python verify_classification_producers_capture.py IMAGE RELOCS RUNTIME WORK EMULATOR OUT
Whole original native producers, MAP header identity, exact original-code replay.
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,relocs,runtime,work,emulator,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(emulator.resolve()));out.mkdir(exist_ok=True)
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();s=json.loads((runtime/'summary.json').read_text(encoding='utf-8'));assert s['success'] and s['source_files_unchanged'] and s['producer_calls']==2
b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';load=s['load_segment'];expected=bytearray(b)
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',expected,int(r['image_offset']),(int(r['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==expected
inputs=list(csv.DictReader((runtime/'inputs.csv').open()));assert len(inputs)==23
for x in inputs:assert sha(Path(x['source']).read_bytes())==sha(Path(x['copy']).read_bytes())==x['sha256']
map_input=next(x for x in inputs if Path(x['source']).name=='MAP.1');rawmap=Path(map_input['source']).read_bytes()
support=Path(__file__).with_name('dosbox_watch_support_newgame_v1.py');harness=Path(__file__).with_name('runtime_watch_classification_producers.py');assert sha(support.read_bytes())==s['support_sha256'] and sha(harness.read_bytes())==s['harness_sha256']
calls=json.loads((runtime/'producer_calls.json').read_text(encoding='utf-8'));assert len(calls)==2;rows=[];previous=None
def flags(which,n,seed):
 if which==0:return (seed&128)|(7 if 1<=n<=0x30 else 11 if 0x31<=n<=0x40 else 0)|(16 if 0x2e<=n<=0x2f else 0)|(64 if 0x47<=n<=0x48 else 0)
 return (seed&128)|(1 if 6<=n<=0x3d else 0)|(2 if 8<=n<=0x2d else 0)|(4 if 0x2f<=n<=0x3d else 0)|(8 if 8<=n<=0x25 else 0)|(32 if n==0x2a else 0)|(64 if n==4 else 0)
registers=dict(CS=UC_X86_REG_CS,IP=UC_X86_REG_IP,DS=UC_X86_REG_DS,SS=UC_X86_REG_SS,ES=UC_X86_REG_ES,SP=UC_X86_REG_SP,AX=UC_X86_REG_AX,BX=UC_X86_REG_BX,CX=UC_X86_REG_CX,DX=UC_X86_REG_DX,SI=UC_X86_REG_SI,DI=UC_X86_REG_DI,BP=UC_X86_REG_BP)
for n,c in enumerate(calls):
 p=c['prefix'];pre=c['pre_registers'];post=c['post_registers'];ds=pre['DS'];ip=(0x1b6,0x250)[n];dest=0xd00c+256*n;source=0xd30e+256*n
 assert c['stage']==('tile_flags_entry','occupancy_flags_entry')[n] and (pre['CS'],pre['IP'])==(load+0xf7,ip)
 assert pre['DS']==pre['SS']==post['DS']==post['SS']==load+0x2771 and post['SP']==pre['SP']+4
 assert c['pre_extra']==c['post_extra']
 before=(work/(p+'dgroup_before.bin')).read_bytes();after=(work/(p+'dgroup_after.bin')).read_bytes();frame=(work/(p+'frame_before.bin')).read_bytes();postframe=(work/(p+'frame_after.bin')).read_bytes()
 assert len(before)==len(after)==0xe030 and len(frame)==len(postframe)==12 and frame[8:]==postframe[8:]
 ret,retcs=struct.unpack_from('<HH',frame,8);assert (post['CS'],post['IP'])==(retcs,ret)==(load+0x277,(0xb8f,0xb94)[n])
 assert before[0xd30c:0xd50e]==rawmap[:514]
 if previous is not None:assert before==previous
 seed=frame[5];pred=bytearray(before);pred[dest:dest+256]=bytes(flags(n,value,seed) for value in before[source:source+256])
 clock_before=struct.unpack_from('<I',before,0x81e)[0];clock_after=struct.unpack_from('<I',after,0x81e)[0];clock_delta=(clock_after-clock_before)&0xffffffff
 assert clock_delta==(0,1)[n]
 if clock_delta:
  assert before[0x16f0]==1
  assert b[0xbcc0+0xf:0xbcc0+0x14]==bytes.fromhex('66ff061e08')
  struct.pack_into('<I',pred,0x81e,clock_after)
 assert bytes(pred)==after
 assert seed in (0,7) and not seed&128
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,bytes(expected));u.mem_write(ds*16,before);u.mem_write(pre['SS']*16+pre['SP']-8,frame)
 for name,value in dict(pre,**c['pre_extra']).items():u.reg_write(registers[name],value)
 u.reg_write(UC_X86_REG_EFLAGS,2);done=[];trace=[]
 def hook(emu,address,size,data):
  if address==retcs*16+ret:done.append(True);emu.emu_stop();return
  off=address-(load+0xf7)*16;assert ip<=off<(0x24f,0x2f2)[n];trace.append(off)
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((load+0xf7)*16+ip,0,count=30000);assert done
 replay=bytearray(u.mem_read(ds*16,len(after)));assert struct.unpack_from('<I',replay,0x81e)[0]==clock_before
 struct.pack_into('<I',replay,0x81e,clock_after);assert bytes(replay)==after
 replayframe=bytes(u.mem_read(pre['SS']*16+pre['SP']-8,12));assert replayframe[2:]==postframe[2:]
 for name,value in dict(post,**c['post_extra']).items():assert u.reg_read(registers[name])==value,(name,value,u.reg_read(registers[name]))
 rows.append(dict(stage=c['stage'],source_DS=source,destination_DS=dest,initial_local_BYTE=seed,retained_high_bit=seed&128,entries=256,changed_BYTES=sum(a!=z for a,z in zip(before,after)),cached_clock_delta=clock_delta,clock_writer_PC_not_captured=True,instruction_executions=len(trace),distinct_instruction_starts=len(set(trace)),destination_sha256=sha(after[dest:dest+256]),input_mapping_sha256=sha(before[source:source+256])))
 previous=after
(runtime/'verified_producer_context.json').write_text(json.dumps(dict(calls=rows,MAP1_header_SHA256=sha(rawmap[:514]),level_count_WORD=struct.unpack_from('<H',rawmap)[0],header_bytes=514,scope='header identity plus direct native producers; not an OS file-read trace'),indent=2)+'\n',encoding='utf-8')
tables=[]
for name,a,z,typ in [('MAP_header_level_count_WORD',0xd30c,0xd30e,'WORD_LE level count from MAP.1 file0..2'),('MAP_tile_type_mapping256',0xd30e,0xd40e,'BYTE256 tile-code to class/type map from MAP.1 file2..258'),('MAP_occupancy_type_mapping256',0xd40e,0xd50e,'BYTE256 occupancy-code to class/type map from MAP.1 file258..514')]:
 tables.append(dict(name=name,ds_start=a,ds_end_exclusive=z,image_start=0x27710+a,image_end_exclusive=0x27710+z,length=z-a,type=typ,status='PARTIAL',runtime_sha256=sha(previous[a:z]),outside_original_file_image=True,original_NONCODE_bytes_added=0))
with (out/'external_bss_tables.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(tables[0]));w.writeheader();w.writerows(tables)
files=[Path(x) for x in s['capture_files']]+[runtime/'summary.json',runtime/'producer_calls.json',runtime/'verified_producer_context.json',runtime/'inputs.csv',runtime/'runtime.conf',image,relocs,support,harness,Path(__file__),out/'external_bss_tables.csv']
proof=dict(verified=True,runtime_tests=1,new_deep_verified_bytes=0,summary_sha256=sha((runtime/'summary.json').read_bytes()),runtime_image_sha256=sha(expected),scope='two whole original00F7:01B6/0250 native producers,512outputs checked against MAP1header mappings and inherited localBYTE seeds0/7; DGROUP equals destination-only model plus observed cached-clock DWORD delta0/1; RTC original INC identified, native writerPC not captured; original producer replay matches registers/frame excluding2BYTE temporary space below savedSI; no global bit80-zero assumption/full gameplay/Win16 parity',files=[dict(path=str(x.resolve()),sha256=sha(x.read_bytes())) for x in dict.fromkeys(files)])
(runtime/'independent_verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(rows,indent=2))
