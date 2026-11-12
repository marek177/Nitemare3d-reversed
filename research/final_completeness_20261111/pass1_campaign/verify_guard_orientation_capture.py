"""python verify_guard_orientation_capture.py IMAGE RELOCS RUNTIME WORK EMULATOR OUT
Whole original012A with originalC0A, including captured near-DS heap frame bank.
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,relocs,runtime,work,emulator,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(emulator.resolve()));out.mkdir(exist_ok=True)
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();s=json.loads((runtime/'summary.json').read_text(encoding='utf-8'));assert s['success'] and s['source_files_unchanged'] and s['orientation_calls']==1
b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';load=s['load_segment'];relocated=bytearray(b)
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',relocated,int(r['image_offset']),(int(r['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==relocated
inputs=list(csv.DictReader((runtime/'inputs.csv').open()));assert len(inputs)==23
for r in inputs:assert sha(Path(r['source']).read_bytes())==sha(Path(r['copy']).read_bytes())==r['sha256']
support=Path(__file__).with_name('dosbox_watch_support_newgame_v1.py');harness=Path(__file__).with_name('runtime_watch_guard_orientation_v2.py');assert sha(support.read_bytes())==s['support_sha256'] and sha(harness.read_bytes())==s['harness_sha256']
c=json.loads((runtime/'orientation_calls.json').read_text(encoding='utf-8'))[0];p=c['prefix'];pre=c['pre_registers'];post=c['post_registers'];ds=pre['DS'];seg=c['guard_segment'];g=c['guard_offset'];a=c['actor_offset'];force=c['force_word']
frame=(work/(p+'frame_before.bin')).read_bytes();assert len(frame)==14 and frame==(work/(p+'frame_after.bin')).read_bytes();ret,retcs,gg,gs,aa,aseg,ff=struct.unpack('<7H',frame)
assert (gg,gs,aa,aseg,ff)==(g,seg,a,seg,force) and seg==load+0x21fd and (pre['CS'],pre['IP'])==(load+0x4c7,0x12a)
assert (post['CS'],post['IP'])==(retcs,ret) and pre['DS']==pre['SS']==post['DS']==post['SS']==load+0x2771 and post['SP']==pre['SP']+4 and c['pre_extra']==c['post_extra']
world=(work/(p+'world_before.bin')).read_bytes();after=(work/(p+'world_after.bin')).read_bytes();dg=(work/(p+'dgroup_before.bin')).read_bytes();dgafter=(work/(p+'dgroup_after.bin')).read_bytes();bank=(work/(p+'descriptor_before.bin')).read_bytes();bankafter=(work/(p+'descriptor_after.bin')).read_bytes()
assert len(world)==len(after)==0x573e and len(dg)==len(dgafter)==0xe030 and dg==dgafter and len(bank)==len(bankafter)==0x34 and bank==bankafter
actor_class=world[a+4];descriptor=struct.unpack_from('<H',dg,0x3d22+8*actor_class)[0];assert descriptor==c['descriptor_offset']==0xf200 and descriptor>=len(dg)
signed=lambda v:(v&65535) if (v&65535)<32768 else (v&65535)-65536
x,y=struct.unpack_from('<HH',world,a+16);px,py=struct.unpack_from('<HH',dg,0x4162);dx,dy=signed(px-x),signed(py-y);ax,ay=abs(dx)&65535,abs(dy)&65535;flag=world[g+15]
if flag:
 view=(2 if dx>0 else 6) if ((2*ay)&65535)<ax else (4 if dy>0 else 0) if ((2*ax)&65535)<ay else ((3 if dy>0 else 1) if dx>0 else (5 if dy>0 else 7))
else:view=((7 if ay>ax else 6) if dy<0 else (4 if ay>ax else 5)) if dx<0 else ((0 if ay>ax else 1) if dy<0 else (2 if ay<=ax else 3))
heading=world[g+17];relative=((4 if flag else 3)+heading-view)&7;mode=world[g+11];strategy=world[g+10];row=1 if mode in (8,16,17) else 2 if mode==6 and strategy!=2 else 0;bank_offset=4+16*row+2*relative;selected=struct.unpack_from('<H',bank,bank_offset)[0];pred=bytearray(world)
if world[g+18]!=relative or force&255:pred[g+18]=relative;struct.pack_into('<H',pred,g,selected);pred[a+3]=selected&255
assert bytes(pred)==after
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,bytes(relocated));u.mem_write(seg*16,world);u.mem_write(ds*16,dg);u.mem_write(ds*16+descriptor,bank);u.mem_write(ds*16+pre['SP'],frame)
regs=dict(CS=UC_X86_REG_CS,IP=UC_X86_REG_IP,DS=UC_X86_REG_DS,SS=UC_X86_REG_SS,ES=UC_X86_REG_ES,SP=UC_X86_REG_SP,AX=UC_X86_REG_AX,BX=UC_X86_REG_BX,CX=UC_X86_REG_CX,DX=UC_X86_REG_DX,SI=UC_X86_REG_SI,DI=UC_X86_REG_DI,BP=UC_X86_REG_BP)
for name,value in dict(pre,**c['pre_extra']).items():u.reg_write(regs[name],value)
u.reg_write(UC_X86_REG_EFLAGS,2);done=[];trace=[]
def hook(emu,address,size,data):
 if address==retcs*16+ret:done.append(True);emu.emu_stop();return
 p=address-load*16;assert 0x4d9a<=p<0x4e87 or 0xbaaA<=p<0xbb60,(hex(p));trace.append(p)
u.hook_add(UC_HOOK_CODE,hook);u.emu_start((load+0x4c7)*16+0x12a,0,count=1000);assert done
assert bytes(u.mem_read(seg*16,len(world)))==after and bytes(u.mem_read(ds*16,len(dg)))==dgafter and bytes(u.mem_read(ds*16+descriptor,len(bank)))==bankafter
for name,value in dict(post,**c['post_extra']).items():assert u.reg_read(regs[name])==value,(name,value,u.reg_read(regs[name]))
context=dict(guard_offset=g,guard_slot=(g-0x264e)//26,actor_offset=a,actor_slot=(a-6)//28,actor_class=actor_class,force_WORD=force,mode=mode,strategy=strategy,view_flag_BYTE=flag,heading=heading,actor_coordinates=[x,y],player_coordinates=[px,py],signed_delta=[dx,dy],view_octant=view,relative_octant=relative,frame_bank_DS=descriptor,selected_bank_offset=bank_offset,selected_WORD=selected,world_BYTE_deltas=[dict(offset=i,old=v,new=z) for i,(v,z) in enumerate(zip(world,after)) if v!=z],dgroup_bytes_unchanged=len(dg),bank_snapshot_bytes=len(bank),replay_executions=len(trace),replay_distinct_starts=len(set(trace)),scope='whole original012A+C0A, captured nearDS heap bank; all world/DGROUP/bank/final registers match, no stubs; native sample initialized mode7 GUARD0, not all modes')
(runtime/'verified_orientation_context.json').write_text(json.dumps(context,indent=2)+'\n',encoding='utf-8')
heap=[dict(name='native_guard_frame_bank_snapshot',DS_start=descriptor,DS_end_exclusive=descriptor+len(bank),physical_start=ds*16+descriptor,length=len(bank),status='PARTIAL',type='52BYTE minimum consumer window:4headerBYTES plus3x8WORD rows; producer/full allocation extent unclosed',sha256=sha(bank),original_NONCODE_bytes_added=0)]
with (out/'near_heap_regions.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(heap[0]));w.writeheader();w.writerows(heap)
files=[Path(x) for x in s['capture_files']]+[runtime/'summary.json',runtime/'orientation_calls.json',runtime/'verified_orientation_context.json',runtime/'inputs.csv',runtime/'runtime.conf',image,relocs,support,harness,Path(__file__),out/'near_heap_regions.csv']
proof=dict(verified=True,runtime_tests=1,new_deep_verified_bytes=0,summary_sha256=sha((runtime/'summary.json').read_bytes()),runtime_image_sha256=sha(relocated),scope=context['scope'],files=[dict(path=str(x.resolve()),sha256=sha(x.read_bytes())) for x in dict.fromkeys(files)])
(runtime/'independent_verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(context,indent=2))
