"""IMAGE RELOCS RUNTIME WORK DECODER EMULATOR OUT: original no-stub native replay."""
import csv,datetime,hashlib,json,struct,sys
from pathlib import Path
image,relocs,runtime,work,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda x:hashlib.sha256(x).hexdigest();s=json.loads((runtime/'summary.json').read_text());assert s['success'] and s['source_files_unchanged'];out.mkdir(exist_ok=True)
root=runtime.parent;harness=root/'runtime_watch_calendar.py';support=root/'dosbox_watch_support_newgame_v1.py'
assert sha(harness.read_bytes())==s['harness_sha256']=='2193bc410cd765468c70e45dfa811940be9de55f20da49f9171b456beac445b4'
assert sha(support.read_bytes())==s['support_sha256']=='64675a5c918b22eb1d80e1d522efc1d459342a9ee04abf768a04b6a2e043fc89'
inputs=list(csv.DictReader((runtime/'inputs.csv').open(encoding='utf-8')));assert len(inputs)==23
for r in inputs:
 for k in ('source','copy'):
  data=Path(r[k]).read_bytes();assert sha(data)==r['sha256'] and len(data)==int(r['bytes'])
b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';load=s['load_segment'];relocated=bytearray(b)
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',relocated,int(r['image_offset']),(int(r['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==relocated
calls=json.loads((runtime/'calendar_calls.json').read_text());assert len(calls)==1;c=calls[0];prefix=c['prefix'];pre=c['pre_registers'];post=c['post_registers'];ds=load+0x2771
def read(name):return (work/(prefix+name+'.bin')).read_bytes()
frame=read('frame_before');assert read('frame_after')==frame;retip,retcs,year,month,day,hour,minute,second=struct.unpack('<8H',frame)
assert [year,month,day,hour,minute,second]==[c[k] for k in ('year_since1980','month','day','hour','minute','second')]
assert (pre['CS'],pre['IP'],pre['DS'],pre['SS'])==(load+0x11ee,0x2dc0,ds,ds)
before=read('dgroup_before');tzready=read('dgroup_timezone_ready');after=read('dgroup_after');assert before==tzready==after and len(before)==0xe030
timezone,enabled=struct.unpack_from('<iH',before,0x24a6);assert struct.unpack_from('<H',before,0x3ca8)[0]!=0
assert month==11 and year==46 and day==12 # Native scope: DST-style predicate exits for zero-based month10.
expected=(int((datetime.datetime(year+1980,month,day,hour,minute,second)-datetime.datetime(1970,1,1)).total_seconds())+timezone)&0xffffffff
assert (post['DX']<<16|post['AX'])==expected
assert (post['CS'],post['IP'],post['DS'],post['SS'],post['SP'])==(retcs,retip,ds,ds,pre['SP']+4)
assert c['pre_extra']==c['post_extra']
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,bytes(relocated));u.mem_write(ds*16,before);u.mem_write(ds*16+pre['SP']-128,b'\xa7'*128);u.mem_write(ds*16+pre['SP'],frame)
registers={'CS':UC_X86_REG_CS,'IP':UC_X86_REG_IP,'DS':UC_X86_REG_DS,'ES':UC_X86_REG_ES,'SS':UC_X86_REG_SS,'SP':UC_X86_REG_SP,'AX':UC_X86_REG_AX,'BX':UC_X86_REG_BX,'CX':UC_X86_REG_CX,'DX':UC_X86_REG_DX,'SI':UC_X86_REG_SI,'DI':UC_X86_REG_DI,'BP':UC_X86_REG_BP}
for name,value in dict(pre,**c['pre_extra']).items():u.reg_write(registers[name],value)
u.reg_write(UC_X86_REG_EFLAGS,2);executed=[];done=[];lookups=[]
def hook(emu,address,size,data):
 if address==retcs*16+retip:done.append(True);emu.emu_stop();return
 pos=address-load*16;executed.append(pos)
 assert emu.reg_read(UC_X86_REG_CS)==load+0x11ee
 assert 0x14be0<=pos<0x14c9f or 0x14ca0<=pos<0x14d93 or 0x159b8<=pos<0x159ea or 0x14ad4<=pos<0x14ae6,(hex(pos))
 if pos==0x14cb0:lookups.append((emu.reg_read(UC_X86_REG_BX)+0x2486)&65535)
u.hook_add(UC_HOOK_CODE,hook);u.emu_start(pre['CS']*16+pre['IP'],0xfffff,count=3000);assert done
assert bytes(u.mem_read(ds*16,len(before)))==after and bytes(u.mem_read(ds*16+pre['SP'],16))==frame
for name,value in dict(post,**c['post_extra']).items():assert u.reg_read(registers[name])==value,(name,u.reg_read(registers[name]),value)
assert lookups==[0x249c] # month11: common-table index10, not the preceding leap table.
files={image.resolve(),relocs.resolve(),harness.resolve(),support.resolve(),Path(__file__).resolve()}
files.update(Path(p).resolve() for p in s['capture_files']);files.update(p.resolve() for p in runtime.iterdir() if p.is_file() and p.name!='independent_verification.json')
proof=dict(verified=True,runtime_tests=1,status='PARTIAL',summary_sha256=sha((runtime/'summary.json').read_bytes()),runtime_image_sha256=sha(bytes(relocated)),year_since1980=year,month=month,day=day,hour=hour,minute=minute,second=second,timezone_seconds_added=timezone,DST_enable=enabled,DST_subtracted_seconds=0,return_DXAX_hex='%08X'%expected,whole_DGROUP_bytes_compared=len(before),DGROUP_changed_bytes=0,original_no_stub_replay_instructions=len(executed),unique_original_starts=len(set(executed)),lookup_DS_offsets=lookups,new_deep_verified_bytes=0,scope='Whole native2DC0 entry-to-return,month11/common249C lookup; cached original2BF4 returns without external calls; full57392B DGROUP unchanged,all captured registers/frame match original no-stub replay. Date arithmetic model also checked. No native DST transition,TZ parsing,leap-table consumer,all-year or Win16 parity.',files=[dict(path=str(p),sha256=sha(p.read_bytes())) for p in sorted(files)],asset_sources=[dict(path=r['source'],sha256=r['sha256']) for r in inputs])
(out/'independent_verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in proof.items() if k not in ('files','asset_sources')},indent=2))
