"""python audit_replay_intro_pcx.py IMAGE INVENTORY DECODER EMULATOR ASSET OUT
Original DOS2 PCX-like loader. CRT file operations, fatal handler and row renderer mocked.
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,asset_path,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest()
b=image.read_bytes();asset=asset_path.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
assert sha(asset)=='af574568089f1998ca50ceeba310ff068c728279ff470cd39f47a8919228b95a'
out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
functions=[]
for name,cs,start,end in [('intro_pcx_stream_load',0x277,0x1600,0x1765),('intro_optional_image',0xd29,0x79a,0x7c6)]:
 todo=[start];decoded={};rows=[];edges=[]
 while todo:
  ip=todo.pop()
  if ip in decoded:continue
  assert start<=ip<end
  i=Decoder(16,b[cs*16+ip:cs*16+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
   todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):
   todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 for ip,i in sorted(decoded.items()):
  pos=cs*16+ip;raw=b[pos:cs*16+i.next_ip];assert lookup[pos]['bytes']==raw.hex()
  rows.append(dict(cs=cs,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rows);save(name+'_cfg',edges)
 functions.append(dict(name=name,start=cs*16+start,end_exclusive=cs*16+end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows)))
assert b[0x27710+0x1c87:0x27710+0x1c87+12]==b'dstopen.img\0'

# Independent asset token parser: exactly the game's flat 64000 output bytes;
# neither palette nor PCX plane/stride assumptions are silently included.
def decode_flat(data):
 q=128;pixels=bytearray();tokens=[]
 while len(pixels)<64000:
  at=q;v=data[q];q+=1;count=1
  if v&192==192:count=v&63;v=data[q];q+=1
  before=len(pixels);pixels.extend(bytes([v])*count)
  tokens.append(dict(source_start=at,source_end_exclusive=q,output_start=before,output_end_exclusive=len(pixels),count=count,value=v,crosses_row=before//320!=(len(pixels)-1)//320 if count else False))
 assert len(pixels)==64000
 return bytes(pixels),q,tokens
pixels,asset_end,tokens=decode_flat(asset);save('real_asset_rle_tokens',tokens)
(out/'real_asset_pixels.bin').write_bytes(pixels)
def header(width,height,magic=10):
 h=bytearray(asset[:128]);h[0]=magic;struct.pack_into('<HHHH',h,4,0,0,width-1,height-1);return bytes(h)
def encode(data):
 result=bytearray();q=0
 while q<len(data):
  n=1
  while q+n<len(data) and n<63 and data[q+n]==data[q]:n+=1
  v=data[q]
  if n>1 or v>=192:result.extend((192+n,v))
  else:result.append(v)
  q+=n
 return bytes(result)
patterns=[('real_cd_asset',asset,pixels,'return',None),('missing_file',b'',b'','missing',None)]
blank=bytes([31])*64000;encoded=encode(blank)
for w,h in [(320,200),(17,200),(320,17),(17,17)]:
 patterns.append(('dimensions_%dx%d'%(w,h),header(w,h)+encoded,blank,'return' if w==320 or h==200 else 'fatal_dimensions',None))
patterns.extend([
 ('invalid_magic',header(320,200,11)+encoded,blank,'fatal_magic',None),
 ('ignored_encoding_planes_stride',header(320,200)[:2]+bytes([0,4])+header(320,200)[4:65]+bytes([3])+b'\x01\x00'+header(320,200)[68:]+encoded,blank,'return',None),
 ('zero_count_token',header(320,200)+b'\xc0\x55'+encoded,blank,'return',None),
 ('overshoot_final_row',header(320,200)+encode(blank[:-1])+b'\xff\x4d',blank[:-1]+b'\x4d','return',None),
 ('literal_low_values',header(320,200)+bytes(n%192 for n in range(64000)),bytes(n%192 for n in range(64000)),'return',None),
 ('read_return_zero_but_bytes_copied',header(320,200)+encoded,blank,'return',0),
 ('truncated_pixel_stream_eof',asset[:128],b'','bounded_eof_continuation',None),
])
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];row_results=[]
for load in (0,0x1000):
 for label,data,expected,want,read_result in patterns:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
  for r in rel:struct.pack_into('<H',runtime,int(r['image_offset']),(int(r['original_word'])+load)&65535)
  u.mem_write(load*16,bytes(runtime));cs=load+0x277;ds=load+0x2771;crt=(load+0x11ee)*16
  targets={crt+0x6e6:'open',crt+0x6fc:'read',crt+0x5fa:'close',(load+0xfba)*16+0xc:'fatal',(load+0x156)*16+0x7de:'row'}
  for addr in targets:u.mem_write(addr,b'\xcb')
  state=dict(position=0,reads=0,closed=False,fatal=None,rows=[],open=False,eof_reads=0)
  visited=set()
  def code(uc,address,size,user):
   if cs*16+0x1600<=address<cs*16+0x1765:visited.add(address-cs*16)
   if address not in targets:return
   op=targets[address];ss=uc.reg_read(UC_X86_REG_SS);sp=uc.reg_read(UC_X86_REG_SP)
   def args(n):return struct.unpack('<'+'H'*n,bytes(uc.mem_read(ss*16+sp+4,n*2)))
   if op=='open':
    filename,mode=args(2);assert filename==0x1c87 and mode==0x64b;assert bytes(uc.mem_read(ds*16+mode,3))==b'rb\0'
    state['open']=label!='missing_file';uc.reg_write(UC_X86_REG_AX,0x7000 if state['open'] else 0)
   elif op=='read':
    dest,size,count,stream=args(4);assert stream==0x7000 and count==1 and size in (128,1)
    chunk=data[state['position']:state['position']+size];state['position']+=len(chunk);state['reads']+=1
    if chunk:uc.mem_write(ds*16+dest,chunk)
    else:state['eof_reads']+=1
    uc.reg_write(UC_X86_REG_AX,read_result if read_result is not None else int(len(chunk)==size))
    if state['eof_reads']>20 and want=='bounded_eof_continuation':uc.emu_stop()
   elif op=='row':
    a=args(10);assert a[1]==ds and a[2]==0 and a[3]==len(state['rows']) and a[4:]==(320,1,320,1,0,65535),a
    row=bytes(uc.mem_read(a[1]*16+a[0],320));state['rows'].append(row)
   elif op=='close':assert args(1)==(0x7000,);state['closed']=True;uc.reg_write(UC_X86_REG_AX,0)
   elif op=='fatal':state['fatal']=args(1)[0];uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,code)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
  # Zeroed scratch makes truncated-input experiment reproducible, not natural-stack proof.
  u.mem_write(ds*16+0xed00,bytes(0x300));u.mem_write(ds*16+0xf000,struct.pack('<HHH',0x6000,cs,0x1c87))
  u.emu_start(cs*16+0x1600,cs*16+0x6000,count=3000000)
  returned=u.reg_read(UC_X86_REG_CS)==cs and u.reg_read(UC_X86_REG_IP)==0x6000
  if want=='return':
   assert returned and len(state['rows'])==200 and b''.join(state['rows'])==expected and state['closed'] and u.reg_read(UC_X86_REG_AX)&255==1,(label,state['fatal'],len(state['rows']))
  elif want=='missing':assert returned and not state['rows'] and not state['closed'] and u.reg_read(UC_X86_REG_AX)&255==0
  elif want.startswith('fatal_'):assert not returned and state['fatal']==(0x64e if want=='fatal_magic' else 0x663)
  else:assert not returned and state['eof_reads']==21 and state['fatal'] is None
  if returned:
   for reg,val in [(UC_X86_REG_SP,0xf004),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_DS,ds)]:assert u.reg_read(reg)==val
  cases.append(dict(load=load,case=label,expected_outcome=want,returned=returned,reads=state['reads'],consumed=state['position'],eof_reads=state['eof_reads'],rows=len(state['rows']),fatal_message_offset=state['fatal'],pixels_sha256=sha(b''.join(state['rows'])),native_instruction_starts_visited=len(visited),passed=True))
  if label=='real_cd_asset' and load==0:
   row_results=[dict(row=n,pixels_sha256=sha(row)) for n,row in enumerate(state['rows'])]
save('cases',cases);save('real_asset_rows',row_results)
summary=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),asset_path=str(asset_path.resolve()),asset_sha256=sha(asset),asset_bytes=len(asset),asset_decoded_bytes=len(pixels),asset_stream_end=asset_end,asset_trailing_bytes=len(asset)-asset_end,asset_pixels_sha256=sha(pixels),asset_tokens=len(tokens),asset_cross_row_tokens=sum(t['crosses_row'] for t in tokens),functions=functions,cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='original bounded DOS2 loader instructions; file APIs/fatal and row renderer mocked; real CD asset plus synthetic input cases at two loads; truncated input uses zeroed synthetic stack, no natural DOS or VGA/runtime parity',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,asset_path,Path(__file__))])
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
