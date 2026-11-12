"""python verify_class_descriptor_copy.py IMAGE RELOCS RUNTIME WORK EMULATOR OUT PRIOR_ORIENTATION_WORK
Original09C1..09D7 copy block; exact IMG1 provenance and original-code replay.
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,relocs,runtime,work,emulator,out,prior=map(Path,sys.argv[1:]);sys.path.insert(0,str(emulator.resolve()));out.mkdir(exist_ok=True)
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();s=json.loads((runtime/'summary.json').read_text(encoding='utf-8'));assert s['success'] and s['source_files_unchanged'] and s['class_copies']==1
b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';load=s['load_segment'];relocated=bytearray(b)
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',relocated,int(r['image_offset']),(int(r['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==relocated
inputs=list(csv.DictReader((runtime/'inputs.csv').open()));assert len(inputs)==23
for r in inputs:assert sha(Path(r['source']).read_bytes())==sha(Path(r['copy']).read_bytes())==r['sha256']
img=next(Path(r['source']) for r in inputs if Path(r['source']).name=='IMG.1');rawimg=img.read_bytes();support=Path(__file__).with_name('dosbox_watch_support_newgame_v1.py');harness=Path(__file__).with_name('runtime_watch_class_descriptor_copy.py');assert sha(support.read_bytes())==s['support_sha256'] and sha(harness.read_bytes())==s['harness_sha256']
c=json.loads((runtime/'class_copies.json').read_text(encoding='utf-8'))[0];p=c['prefix'];pre=c['pre_registers'];post=c['post_registers'];ext=c['pre_extra'];px=c['post_extra'];ds=pre['DS'];slot=c['slot_offset'];dest=c['destination_offset'];source=c['source_offset'];seg=load+0x21fd
assert (pre['CS'],pre['IP'])==(load+0x277,0x9c1) and (post['CS'],post['IP'])==(load+0x277,0x9d7) and pre['DS']==pre['SS']==post['DS']==post['SS']==load+0x2771
data={}
for name,length in [('world',0x573e),('dgroup',0xe030),('locals',0x18),('source_header',90)]:
 a=(work/(p+name+'_before.bin')).read_bytes();z=(work/(p+name+'_after.bin')).read_bytes();assert len(a)==len(z)==length and a==z,(name);data[name]=a
world,dg,locals_,header=(data[k] for k in ('world','dgroup','locals','source_header'));before=(work/(p+'destination_before.bin')).read_bytes();after=(work/(p+'destination_after.bin')).read_bytes();assert len(before)==len(after)==90 and after==header
assert slot==0x3d22+8*8 and struct.unpack_from('<H',locals_,0x16)[0]==slot and struct.unpack_from('<H',locals_,8)[0]==8
actor=struct.unpack_from('<H',locals_,4)[0];actorseg=struct.unpack_from('<H',locals_,0x10)[0];payload=struct.unpack_from('<I',locals_,0xa)[0];code=world[actor];assert (actor,actorseg,code,world[actor+4])==(0x236,seg,0x81,8)
count,word0,pointer,records=struct.unpack_from('<4H',dg,slot-4);assert (count,word0,pointer,records)==(12,0,dest,0xf186) and dest==0xf200
fileoff=0x800+90*(0x100+code);assert fileoff==0x8f5a and header==rawimg[fileoff:fileoff+90] and payload==struct.unpack_from('<I',rawimg,0x400+4*code)[0]==0x159b32
priorbank=(prior/'orientation_00_descriptor_before.bin').read_bytes();assert len(priorbank)==52 and header[:52]==priorbank
assert source==ext['BP']-0x74 and px['BP']==ext['BP'] and px['SI']==source+90 and px['DI']==dest+90 and post['SP']==pre['SP'] and post['CX']==0
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,bytes(relocated));u.mem_write(seg*16,world);u.mem_write(ds*16,dg);u.mem_write(ds*16+source,header);u.mem_write(ds*16+dest,before);u.mem_write(ds*16+ext['BP']-0x18,locals_)
regs=dict(CS=UC_X86_REG_CS,IP=UC_X86_REG_IP,DS=UC_X86_REG_DS,SS=UC_X86_REG_SS,ES=UC_X86_REG_ES,SP=UC_X86_REG_SP,AX=UC_X86_REG_AX,BX=UC_X86_REG_BX,CX=UC_X86_REG_CX,DX=UC_X86_REG_DX,SI=UC_X86_REG_SI,DI=UC_X86_REG_DI,BP=UC_X86_REG_BP)
for name,value in dict(pre,**ext).items():u.reg_write(regs[name],value)
u.reg_write(UC_X86_REG_EFLAGS,2);done=[];trace=[]
def hook(emu,address,size,data):
 if address==(load+0x277)*16+0x9d7:done.append(True);emu.emu_stop();return
 p=address-(load+0x277)*16;assert 0x9c1<=p<0x9d7;trace.append(p)
u.hook_add(UC_HOOK_CODE,hook);u.emu_start((load+0x277)*16+0x9c1,0,count=100);assert done
assert bytes(u.mem_read(ds*16+dest,90))==after and bytes(u.mem_read(seg*16,len(world)))==world and bytes(u.mem_read(ds*16,len(dg)))==dg
for name,value in dict(post,**px).items():assert u.reg_read(regs[name])==value,(name,value,u.reg_read(regs[name]))
context=dict(class_index=8,actor_offset=actor,actor_code=code,class_record_DS=slot-4,class_record_WORDs=[count,word0,pointer,records],IMG1_header_file_offset=fileoff,payload_file_offset=payload,source_SS_offset=source,destination_DS_offset=dest,copy_length=90,destination_changed_BYTEs=sum(a!=z for a,z in zip(before,after)),unchanged_world_bytes=len(world),unchanged_DGROUP_bytes=len(dg),prior52BYTEprefix_matches=True,replay_executions=len(trace),replay_distinct_starts=len(set(trace)),scope='original copy block only, not entire0686 loader or0584 file IO;90B native bank equals IMG1 descriptor and prior52B consumer snapshot')
(runtime/'verified_class_copy_context.json').write_text(json.dumps(context,indent=2)+'\n',encoding='utf-8')
fields=[dict(record='class8_record',offset=n*2,width=2,role=role,consumer='0277:096F..0989 producer;04C7:012A frame consumer;PARTIAL') for n,role in enumerate(('WORD image_count from descriptorBYTE2','WORD descriptor_header0','NEAR_DS90BYTEbank pointer,zero if absent','NEAR_DS image_count*10 decoded-record array pointer'))]
fields+= [dict(record='IMG90_descriptor',offset=0,width=2,role='WORD copied into class-record+2;meaning open',consumer='0277:0975..0978;PARTIAL'),dict(record='IMG90_descriptor',offset=2,width=1,role='BYTE image_count,alloc count*10',consumer='0277:0609..0617;PARTIAL'),dict(record='IMG90_descriptor',offset=3,width=1,role='BYTE nonzero gates90BYTEbank allocation/copy',consumer='0277:0997..09D6;PARTIAL')]
with (out/'consumer_field_roles.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(fields[0]));w.writeheader();w.writerows(fields)
with (out/'native_bank90_snapshot.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=['DS_start','length','IMG_file_offset','sha256','status','original_NONCODE_bytes_added']);w.writeheader();w.writerow(dict(DS_start=dest,length=90,IMG_file_offset=fileoff,sha256=sha(header),status='PARTIAL',original_NONCODE_bytes_added=0))
record_start=slot-4
bss=[dict(name='native_class8_four_WORD_record',ds_start=record_start,ds_end_exclusive=record_start+8,image_start=0x27710+record_start,image_end_exclusive=0x27710+record_start+8,length=8,type='WORD_count_WORD_header0_NEAR_DS90BYTEbank_NEAR_DS10BYTE_record_array',status='PARTIAL',runtime_sha256=sha(dg[record_start:record_start+8]),outside_original_file_image=True,original_NONCODE_bytes_added=0)]
with (out/'external_bss_tables.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(bss[0]));w.writeheader();w.writerows(bss)
files=[Path(x) for x in s['capture_files']]+[runtime/'summary.json',runtime/'class_copies.json',runtime/'verified_class_copy_context.json',runtime/'inputs.csv',runtime/'runtime.conf',image,relocs,support,harness,Path(__file__),prior/'orientation_00_descriptor_before.bin',out/'consumer_field_roles.csv',out/'native_bank90_snapshot.csv',out/'external_bss_tables.csv']
proof=dict(verified=True,runtime_tests=1,new_deep_verified_bytes=0,summary_sha256=sha((runtime/'summary.json').read_bytes()),runtime_image_sha256=sha(relocated),scope=context['scope'],files=[dict(path=str(x.resolve()),sha256=sha(x.read_bytes())) for x in dict.fromkeys(files)])
(runtime/'independent_verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(context,indent=2))
