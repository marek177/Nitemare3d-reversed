"""python audit_replay_menu_save_gate.py IMAGE INVENTORY DECODER EMULATOR OUT
Native menu selector and USER.SAV metadata reader, dependencies explicitly mocked.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
functions=[]
for name,cs,start,end in [('main_menu_descriptor_select',0xd29,0x252e,0x260a),('save_slot_metadata_read',0x277,0xd3e,0xe1c)]:
 todo=[start];decoded={};rows=[];edges=[]
 while todo:
  ip=todo.pop()
  if ip in decoded:continue
  assert start<=ip<end;i=Decoder(16,b[cs*16+ip:cs*16+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 for ip,i in sorted(decoded.items()):
  pos=cs*16+ip;raw=b[pos:cs*16+i.next_ip];assert lookup[pos]['bytes']==raw.hex();rows.append(dict(cs=cs,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rows);save(name+'_cfg',edges);functions.append(dict(name=name,start=cs*16+start,end_exclusive=cs*16+end,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows)))
prefix=[]
for r in old:
 if r['cs']==0xd29 and 0x1946<=r['ip']<0x19e4:
  raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;prefix.append(r)
save('menu_draw_focus_prefix_not_whole_function',prefix)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
def make(load,cs0):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for r in rel:struct.pack_into('<H',runtime,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));ds=load+0x2771;cs=load+cs0
 for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 return u,cs,ds
for load,flag,mode,slot,metadata in itertools.product((0,0x1000),(0,1,0x100,0x101,0xffff),(0,3,0xffff),(-1,0,1,32767),(0xffff,0x0201,0x0202,0x0301,0x8001)):
 u,cs,ds=make(load,0xd29);table_seg=load+0x20b9;u.mem_write(ds*16+0x256a,struct.pack('<H',table_seg));u.mem_write(ds*16+0x3cd4,struct.pack('<H',mode));u.mem_write(ds*16+0x626a,struct.pack('<HH',2,1))
 expected=bytearray(u.mem_read(table_seg*16+0xe10,414))
 for start in (0xe8e,0xf1e):
  q=start
  while expected[q-0xe10]:u.mem_write(table_seg*16+q+4,b'\xa5');expected[q-0xe10+4]=int(expected[q-0xe10]==8);q+=18
 calls=[];probe=(load+0x277)*16+0xd3e;followup=(load+0x277)*16+0x1176
 for address in (probe,followup):u.mem_write(address,b'\xcb')
 def hook(uc,address,size,user):
  sp=uc.reg_read(UC_X86_REG_SP)
  if address==probe:
   arg_slot,filename,buf_off,buf_seg=struct.unpack('<4H',bytes(uc.mem_read(ds*16+sp+4,8)));assert (arg_slot,filename,buf_seg)==(slot&65535,0x1fe4,ds);uc.mem_write(buf_seg*16+buf_off,b'TEST'+bytes(37));uc.reg_write(UC_X86_REG_AX,metadata);calls.append('probe')
  elif address==followup:assert struct.unpack('<HH',bytes(uc.mem_read(ds*16+sp+4,4)))==(slot&65535,0x1fed);calls.append('followup')
 u.hook_add(UC_HOOK_CODE,hook);u.mem_write(ds*16+0xf000,struct.pack('<4H',0x100,0x5000,flag,slot&65535));u.emu_start(cs*16+0x252e,0x50100,count=3000)
 should_probe=mode==3 and slot>=0;success=should_probe and metadata<0x8000 and metadata&255==1 and metadata>>8==2
 expected_offset=0xf1e if success else 0xe8e if flag&255 and mode!=3 else 0xe10
 assert (u.reg_read(UC_X86_REG_AX),u.reg_read(UC_X86_REG_DX))==(expected_offset,table_seg) and bytes(u.mem_read(table_seg*16+0xe10,414))==expected
 assert calls==(['probe','followup'] if success else ['probe'] if should_probe else [])
 assert u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SP)==0xf004 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x2345 and u.reg_read(UC_X86_REG_DI)==0x3456
 cases.append(dict(kind='menu_selector',load=load,flag=flag,mode=mode,slot=slot,metadata=metadata,result_offset=expected_offset,probe=should_probe,followup_called=success,passed=True))
save('cases',cases)

paths=[Path(r'L:\nite3d\dos\nite3d-A\USER.SAV'),Path(r'L:\nite3d\dos\N3D-Dos\USER.SAV'),Path(r'L:\nite3d\dos\n3dfull\USER.SAV'),Path(r'L:\nite3d\win\n3w-5\user.sav'),Path(r'L:\nite3d\win\100MEDIA\n3w\user.sav')];assets=[];patterns=[]
for path in paths:
 raw=path.read_bytes();declared=struct.unpack_from('<I',raw)[0];assets.append(dict(path=str(path),sha256=sha(raw),bytes=len(raw),declared_first_record_bytes=declared,whole_declared_records=len(raw)//declared if declared else None,remainder=len(raw)%declared if declared else None,status='PARTIAL',scope='folder label not version binding; full payload not decoded'))
 patterns.append((path.name+'_'+path.parent.name,raw,0,True,None))
header=lambda episode,level,length=54758:struct.pack('<I',length)+b'A'*41+struct.pack('<HH',episode,level)
for episode,level in ((1,0),(1,1),(2,3),(2,0x8000),(0xffff,0x101)):
 patterns.append(('synthetic_%d_%d'%(episode,level),header(episode,level),0,True,None))
patterns.extend([('wrong_length',header(1,1,54756),0,True,None),('valid_header_null_description',header(2,3),0,False,None),('read_returns_zero',header(1,1),0,True,0),('negative_slot',header(1,1),-1,True,None),('truncated',header(1,1)[:4],0,True,None)])
metadata_cases=[]
for load,pattern,registered,open_handle in itertools.product((0,0x1000),patterns,(0,1),(0xffff,0,7)):
 label,data,slot,desc,read_result=pattern;u,cs,ds=make(load,0x277);crt=(load+0x11ee)*16;targets={cs*16+0xc20:'path',crt+0x1c72:'open',crt+0x1bd6:'seek',crt+0x1e14:'near_read',(load+0xfba)*16+0x9e:'far_read',crt+0x1bb6:'close',(load+0x83d)*16+0x29ca:'registered'}
 for addr in targets:u.mem_write(addr,b'\xcb')
 state=dict(position=0,reads=[],near_index=0,closed=False,registered_called=False)
 u.mem_write(ds*16+0xefd0,bytes(48));u.mem_write(0x70100,bytes(41))
 def hook(uc,address,size,user):
  if address not in targets:return
  op=targets[address];sp=uc.reg_read(UC_X86_REG_SP)
  def args(n):return struct.unpack('<'+'H'*n,bytes(uc.mem_read(ds*16+sp+4,n*2)))
  if op=='path':assert args(1)==(0x1fe4,);uc.reg_write(UC_X86_REG_AX,0x1fe4)
  elif op=='open':assert args(2)==(0x1fe4,0x8000);uc.reg_write(UC_X86_REG_AX,open_handle)
  elif op=='seek':
   handle,lo,hi,origin=args(4);assert handle==7;offset=lo|(hi<<16);offset=offset-(1<<32) if offset&(1<<31) else offset
   if origin==0:assert offset==slot*54758;state['position']=offset
   else:assert origin==1 and offset==41;state['position']+=offset
   uc.reg_write(UC_X86_REG_AX,state['position']&65535);uc.reg_write(UC_X86_REG_DX,(state['position']>>16)&65535)
  elif op in ('near_read','far_read'):
   if op=='near_read':
    handle,dest,count=args(3);seg=ds;n=state['near_index'];assert n<3 and count==(4,2,2)[n] and dest==(uc.reg_read(UC_X86_REG_BP)+(-10,-6,-4)[n])&65535;state['near_index']+=1
   else:
    handle,dest,seg,count=args(4);assert desc and (dest,seg,count)==(0x100,0x7000,41)
   assert handle==7;pos=state['position'];chunk=data[pos:pos+count] if 0<=pos<len(data) else b''
   if chunk:uc.mem_write(seg*16+dest,chunk)
   state['position']+=len(chunk);state['reads'].append((pos,count,len(chunk)));uc.reg_write(UC_X86_REG_AX,read_result if read_result is not None else len(chunk))
  elif op=='close':assert args(1)==(7,);state['closed']=True
  elif op=='registered':assert args(1)==(1,);state['registered_called']=True;uc.reg_write(UC_X86_REG_AX,registered);uc.reg_write(UC_X86_REG_DX,0)
 u.hook_add(UC_HOOK_CODE,hook);u.mem_write(ds*16+0xf000,struct.pack('<6H',0x100,0x5000,slot&65535,0x1fe4,0x100 if desc else 0,0x7000 if desc else 0));u.emu_start(cs*16+0xd3e,0x50100,count=1000)
 raw_header=data[:49] if slot==0 else b'';record_length=int.from_bytes(raw_header[:4].ljust(4,b'\0'),'little');episode=int.from_bytes(raw_header[45:47].ljust(2,b'\0'),'little');level=int.from_bytes(raw_header[47:49].ljust(2,b'\xff'),'little') if len(raw_header)<49 else int.from_bytes(raw_header[47:49],'little')
 # Locals record_length/episode are zeroed by the fixture, result WORD startsFFFF.
 if len(raw_header)<49:level=65535
 episode_signed=episode-65536 if episode&32768 else episode
 valid=open_handle==7 and record_length==54758 and (registered or episode_signed<=1)
 expected=(level|((episode&255)<<8)) if valid else 65535
 assert u.reg_read(UC_X86_REG_AX)==expected and state['closed']==(open_handle==7),(label,registered,open_handle,u.reg_read(UC_X86_REG_AX),expected,state)
 assert state['registered_called']==(open_handle==7 and record_length==54758)
 if open_handle==7:
  assert state['near_index']==3
  desc_start=slot*54758+4;desc_bytes=data[desc_start:desc_start+41] if desc and 0<=desc_start<len(data) else b''
  assert bytes(u.mem_read(0x70100,41))==desc_bytes+bytes(41-len(desc_bytes))
 metadata_cases.append(dict(load=load,pattern=label,registered=registered,open_handle=open_handle,description=desc,slot=slot,AX=expected,reads=len(state['reads']),closed=state['closed'],passed=True))
save('metadata_cases',metadata_cases);save('save_candidates',assets)
layout=[dict(start=0,end_exclusive=4,length=4,type='DWORD_record_size_must_equal_D5E6',status='PARTIAL'),dict(start=4,end_exclusive=45,length=41,type='BYTE41_optional_description_no_terminator_written',status='PARTIAL'),dict(start=45,end_exclusive=47,length=2,type='WORD_episode_signed_for_unregistered_check',status='PARTIAL'),dict(start=47,end_exclusive=49,length=2,type='WORD_level_ORed_with_low_episode_BYTE_shift8',status='PARTIAL'),dict(start=49,end_exclusive=54758,length=54709,type='payload_not_analyzed_by_this_reader',status='UNKNOWN')]
save('dos20_slot_intervals',layout);(out/'dos20_slot_intervals.json').write_text(json.dumps(layout,indent=2)+'\n')
records=[]
for asset in assets:
 raw=Path(asset['path']).read_bytes();stride=asset['declared_first_record_bytes'];assert stride and len(raw)%stride==0
 for n in range(len(raw)//stride):
  start=n*stride;assert struct.unpack_from('<I',raw,start)[0]==stride
  records.append(dict(source=asset['path'],file_sha256=asset['sha256'],index=n,start=start,end_exclusive=start+stride,length=stride,type='declared_size_stride_candidate_not_full_payload_schema',status='CLASSIFIED ONLY',range_sha256=sha(raw[start:start+stride])))
save('candidate_record_intervals',records);(out/'candidate_record_intervals.json').write_text(json.dumps(records,indent=2)+'\n')
summary=dict(functions=functions,cases=len(cases)+len(metadata_cases),selector_cases=len(cases),metadata_cases=len(metadata_cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,save_candidate_files=len(assets),scope='whole menu selector with metadata/followup dependencies mocked; whole save header reader with modeled CRT/path/registered query and actual candidate file bytes plus synthetic headers; no natural save creation/restore/load or full payload behavior; malformed/truncated cases use initialized synthetic local scratch',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in [image,inventory,Path(__file__)]+paths])
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
