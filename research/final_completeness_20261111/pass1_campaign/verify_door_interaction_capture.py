"""python verify_door_interaction_capture.py IMAGE RELOCS RUNTIME WORK DECODER EMULATOR
Checks whole native call against exact side effects and independently reruns original code.
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,relocs,runtime,work,decoder,emulator=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();s=json.loads((runtime/'summary.json').read_text(encoding='utf-8'));assert s['success'] and s['source_files_unchanged'] and s['interaction_calls']==1
b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';load=s['load_segment'];expected=bytearray(b)
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',expected,int(r['image_offset']),(int(r['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==expected
inputs=list(csv.DictReader((runtime/'inputs.csv').open()));assert len(inputs)==23
for x in inputs:assert sha(Path(x['source']).read_bytes())==sha(Path(x['copy']).read_bytes())==x['sha256']
support=Path(__file__).with_name('dosbox_watch_support_newgame_v1.py');harness=Path(__file__).with_name('runtime_watch_door_interaction.py');assert sha(support.read_bytes())==s['support_sha256'] and sha(harness.read_bytes())==s['harness_sha256']
calls=json.loads((runtime/'interaction_calls.json').read_text(encoding='utf-8'));assert len(calls)==1;c=calls[0];p=c['prefix'];pre=c['pre_registers'];post=c['post_registers'];ds=pre['DS'];seg=c['door_segment'];door=c['door_offset']
assert (pre['CS'],pre['IP'])==(load,0x598) and pre['DS']==pre['SS']==post['DS']==post['SS']==load+0x2771 and seg==load+0x21fd
frame=(work/(p+'frame_before.bin')).read_bytes();assert len(frame)==10 and frame==(work/(p+'frame_after.bin')).read_bytes();ret,retcs,q,qs,cmd=struct.unpack('<5H',frame);assert (q,qs,cmd)==(door,seg,c['command_word'])
assert (post['CS'],post['IP'])==(retcs,ret) and (retcs,ret)==(load+0x4c7,0x3f9) and post['SP']==pre['SP']+4 and c['pre_extra']==c['post_extra']
world=(work/(p+'world_before.bin')).read_bytes();after=(work/(p+'world_after.bin')).read_bytes();dg=(work/(p+'dgroup_before.bin')).read_bytes();dg_after=(work/(p+'dgroup_after.bin')).read_bytes()
assert len(world)==len(after)==0x573e and len(dg)==len(dg_after)==0xe030 and dg==dg_after and dg[0x430e]==0
desc,desc2,cell,cellseg,state=struct.unpack_from('<5H',world,door);assert door==0x30f4 and cell==0x4d54 and cellseg==seg and state==1 and dg[desc+6]==0x40 and world[door+16]==0
step=128 if dg[desc+7]==2 else 2;pred=bytearray(world);struct.pack_into('<H',pred,door+8,2);changes=[];lookupkeys=[]
for neighbor in ((cell+step)&65535,(cell-step)&65535):
 tile=world[neighbor];flags=dg[0xd00c+tile]
 if flags&8:
  found=[i for i in range(struct.unpack_from('<H',world)[0]) if struct.unpack_from('<HH',world,0x3076+18*i+4)==(neighbor,seg)];assert len(found)==1
  n=found[0];off=0x3076+18*n;old=struct.unpack_from('<H',world,off+8)[0];struct.pack_into('<H',pred,off+8,2);changes.append(dict(index=n,offset=off,old_state=old,new_state=2));lookupkeys.append(neighbor)
assert bytes(pred)==after and changes==[dict(index=6,offset=0x30e2,old_state=1,new_state=2)]
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,bytes(expected));u.mem_write(seg*16,world);u.mem_write(ds*16,dg);u.mem_write(pre['SS']*16+pre['SP'],frame)
registers=dict(CS=UC_X86_REG_CS,IP=UC_X86_REG_IP,DS=UC_X86_REG_DS,SS=UC_X86_REG_SS,ES=UC_X86_REG_ES,SP=UC_X86_REG_SP,AX=UC_X86_REG_AX,BX=UC_X86_REG_BX,CX=UC_X86_REG_CX,DX=UC_X86_REG_DX,SI=UC_X86_REG_SI,DI=UC_X86_REG_DI,BP=UC_X86_REG_BP)
for name,value in dict(pre,**c['pre_extra']).items():u.reg_write(registers[name],value)
u.reg_write(UC_X86_REG_EFLAGS,2);done=[];visited=[]
def hook(emu,address,size,data):
 if address==retcs*16+ret:done.append(True);emu.emu_stop();return
 assert load*16<=address<load*16+0x704,'unexpected external callee: native sample has no sound call'
 visited.append(address-load*16)
u.hook_add(UC_HOOK_CODE,hook);u.emu_start(load*16+0x598,0,count=5000);assert done
assert bytes(u.mem_read(seg*16,len(world)))==after and bytes(u.mem_read(ds*16,len(dg)))==dg_after
for name,value in dict(post,**c['post_extra']).items():assert u.reg_read(registers[name])==value,(name,value,u.reg_read(registers[name]))
context=dict(door_index=7,door_offset=door,old_state=1,new_state=2,command_word=cmd,descriptor=desc,kind=dg[desc+6],orientation=dg[desc+7],neighbor_changes=changes,world_BYTE_deltas=[dict(offset=i,old=a,new=z) for i,(a,z) in enumerate(zip(world,after)) if a!=z],dgroup_bytes_unchanged=len(dg),lookup_cell_keys=lookupkeys,original_code_replay_instruction_count=len(visited),original_code_replay_distinct_starts=len(set(visited)),sound_calls=0)
(runtime/'verified_interaction_context.json').write_text(json.dumps(context,indent=2)+'\n',encoding='utf-8')
files=[Path(x) for x in s['capture_files']]+[runtime/'summary.json',runtime/'interaction_calls.json',runtime/'verified_interaction_context.json',runtime/'inputs.csv',runtime/'runtime.conf',image,relocs,support,harness,Path(__file__)]
proof=dict(verified=True,runtime_tests=1,new_deep_verified_bytes=0,summary_sha256=sha((runtime/'summary.json').read_bytes()),runtime_image_sha256=sha(expected),scope='whole original0000:0598 native GUARD caller04C7:03F9; source door7 and neighbor6 states1to2, exact2BYTE world delta and57392B DGROUP unchanged; original instructions independently replayed with native inputs, no stub executed; other modes/sound/native state3 path unverified',files=[dict(path=str(x.resolve()),sha256=sha(x.read_bytes())) for x in dict.fromkeys(files)])
(runtime/'independent_verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(context,indent=2))
