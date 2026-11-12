"""IMAGE INVENTORY DECODER EMULATOR SND OUT: whole SND reader, explicit CRT open/seek/far-read responses."""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,snd,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
b=image.read_bytes();asset=snd.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297' and sha(asset)=='f3434984d315531602d32285cb8ff55990bba786f5fb37f53710e88379388614';out.mkdir(exist_ok=True);old={x['image_offset']:x for x in json.loads(inventory.read_text(encoding='utf-8'))};fmt=Formatter(FormatterSyntax.INTEL);todo=[0x8a];d={};edges=[]
while todo:
 ip=todo.pop()
 if ip in d:continue
 assert 0x8a<=ip<0xeb;i=Decoder(16,b[0x2770+ip:0x285b],ip=ip).decode();assert not i.is_invalid;d[ip]=i
 if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
 if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
rows=[]
for ip,i in sorted(d.items()):
 p=0x2770+ip;raw=b[p:0x2770+i.next_ip];assert old[p]['bytes']==raw.hex();rows.append(dict(cs=0x277,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
def save(name,data):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
save('music_snd_reader',rows);save('music_snd_reader_cfg',edges);rel=list(csv.DictReader((image.parent/'relocations.csv').open()));configs=[];cases=[];events=[];visited=set()
for cached in (0,5,0xffff):
 for offset,count in ((0,192),(960,3204),(4164,20290),(0,0)):
  for seek_error in (False,True):
   for delta in (0,-1,1):
    if not count and delta<0:continue
    configs.append(dict(cached=cached,open_result=5,offset=offset,count=count,seek_error=seek_error,read_delta=delta,repeats=1))
for opened in (0,0xffff):configs.append(dict(cached=0,open_result=opened,offset=0,count=192,seek_error=False,read_delta=0,repeats=2 if opened==0 else 1))
configs.append(dict(cached=0,open_result=5,offset=0,count=192,seek_error=False,read_delta=0,repeats=2))
for load,split,c in itertools.product((0x824,0x1000),(False,True),configs):
 raw=bytearray(b)
 for x in rel:struct.pack_into('<H',raw,int(x['image_offset']),(int(x['original_word'])+load)&65535)
 ds=load+0x2771;ss=0x4800 if split else ds;base=ds*16;stack=0xf000;sl,sh=ss*16+stack-64,ss*16+stack+16;ram=bytearray(b'\xa5'*0x200000);ram[load*16:load*16+len(raw)]=raw;struct.pack_into('<H',ram,base+0x1ac,c['cached']);dest=0x60200;count=c['count'];frame=struct.pack('<4HIH',0x200,0x4e00,0x200,0x6000,c['offset'],count);ram[ss*16+stack:ss*16+stack+14]=frame;expected=bytearray(ram)
 targets={(load+0x11ee)*16+0x1c72:'open',(load+0x11ee)*16+0x1bd6:'seek',(load+0xfba)*16+0x9e:'read'}
 for p in targets:ram[p]=expected[p]=0xcb
 fatal=(load+0xfba)*16+0xc;want_calls=[];want_writes=[];handle=c['cached'];fatal_kind=None
 for repeat in range(c['repeats']):
  if not handle:
   want_calls.append(('open',(0x1ae,0x8000)));handle=c['open_result'];struct.pack_into('<H',expected,base+0x1ac,handle);want_writes.append((base+0x1ac,2,handle))
   if handle==0xffff:want_calls.append(('fatal',(0x1be,0x1b6)));fatal_kind='open';break
  want_calls.extend([('seek',(handle,c['offset']&65535,c['offset']>>16,0)),('read',(handle,0x200,0x6000,count))]);transferred=max(0,min(count,count+c['read_delta']));expected[dest:dest+transferred]=asset[c['offset']:c['offset']+transferred]
  if c['read_delta']:
   want_calls.append(('fatal',(0x1dc,0x1d4)));fatal_kind='read_count';break
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));calls=[];writes=[];stops=[]
 def code(e,a,n,data):
  if a==0x4e200:stops.append('return');e.emu_stop();return
  if a in targets or a==fatal:
   name='fatal' if a==fatal else targets[a];sp=e.reg_read(UC_X86_REG_SP);nwords={'open':2,'seek':4,'read':4,'fatal':2}[name];args=struct.unpack('<'+'H'*nwords,bytes(e.mem_read(ss*16+sp+4,nwords*2)));calls.append((name,args));assert calls[-1]==want_calls[len(calls)-1]
   if name=='fatal':stops.append('fatal');e.emu_stop();return
   if name=='open':assert bytes(e.mem_read(base+0x1ae,8))==b'snd.dat\0';e.reg_write(UC_X86_REG_AX,c['open_result'])
   elif name=='seek':e.reg_write(UC_X86_REG_AX,0xffff if c['seek_error'] else c['offset']&65535);e.reg_write(UC_X86_REG_DX,0xffff if c['seek_error'] else c['offset']>>16)
   else:
    transferred=max(0,min(count,count+c['read_delta']))
    if transferred:e.mem_write(dest,asset[c['offset']:c['offset']+transferred])
    e.reg_write(UC_X86_REG_AX,(count+c['read_delta'])&65535)
   return
  p=a-load*16;assert p in {x['image_offset'] for x in rows};visited.add(p)
 def write(e,access,a,n,value,data):
  if not(sl<=a and a+n<=sh):writes.append((a,n,value&((1<<(n*8))-1)))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 for repeat in range(c['repeats']):
  u.mem_write(ss*16+stack,frame)
  for reg,value in [(UC_X86_REG_CS,load+0x277),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,stack),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,value)
  u.emu_start((load+0x277)*16+0x8a,0x1fffff,count=200);assert stops
  if stops[-1]=='fatal':break
  assert u.reg_read(UC_X86_REG_SP)==stack+4 and u.reg_read(UC_X86_REG_BP)==0x1234 and bytes(u.mem_read(ss*16+stack,14))==frame
 assert calls==want_calls and writes==want_writes;actual=bytes(u.mem_read(0,len(ram)));assert actual[:sl]==expected[:sl] and actual[sh:]==expected[sh:]
 cid=len(cases)
 for j,(name,args) in enumerate(calls):events.append(dict(case=cid,index=j,callee=name,args=json.dumps(args)))
 cases.append(dict(case=cid,load=load,split_SS_DS=split,config=json.dumps(c),stop=stops[-1],fatal_kind=fatal_kind,open_calls=sum(name=='open' for name,args in calls),original_nonstack_stores=len(writes),whole_RAM_bytes_checked=len(ram)-(sh-sl),status='PASS'))
save('cases',cases);save('dependency_events',events);save('instruction_execution_coverage',[dict(image_offset=x['image_offset'],executed=x['image_offset'] in visited) for x in rows])
s=dict(functions=[dict(name='music_snd_reader',start=0x27fa,end_exclusive=0x285b,instructions=len(rows),instruction_bytes=97)],cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,unexecuted_starts=sorted({x['image_offset'] for x in rows}-visited),scope='Whole originalSNDreader only CRTopen/seek/farreadresponsesfixtures; fatalpathsstopatentry. Cached0/5/FFFF,open0/5/FFFF,repeatedzero-handle reopen,seekfailureignored,short/long/zero-countread checks,DS/SSsplit,two loads. Exactoriginalglobalstores/full2MiBRAMexcept80controlstackB;hostfixturedatawritesnotoriginalreaderstores. No realDOSfailuresemantics.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,image.parent/'relocations.csv',snd,Path(__file__))]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
