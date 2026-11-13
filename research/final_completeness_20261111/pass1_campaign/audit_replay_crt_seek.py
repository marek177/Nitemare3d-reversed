"""IMAGE INVENTORY DECODER EMULATOR OUT: original CRT seek + shared return/error bodies; DOS42 responses explicitly modeled."""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,OpKind
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old={x['image_offset']:x for x in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);functions=[];allowed=set();allrows=[]
def save(n,rows):
 with (out/(n+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for name,a,e in [('crt_seek',0x1bd6,0x1c57),('crt_seek_shared_return',0x5b7,0x5c4),('crt_dos_error_translate',0x5ca,0x5f7)]:
 rows=[]
 for i in Decoder(16,b[0x11ee0+a:0x11ee0+e],ip=a):
  p=0x11ee0+i.ip;raw=b[p:0x11ee0+i.next_ip];assert not i.is_invalid and old[p]['bytes']==raw.hex();allowed.add(p);rows.append(dict(cs=0x11ee,ip=i.ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rows);allrows+=rows;functions.append(dict(name=name,start=0x11ee0+a,end_exclusive=0x11ee0+e,instructions=len(rows),instruction_bytes=e-a))
edges=[]
for row in allrows:
 i=Decoder(16,bytes.fromhex(row['bytes']),ip=row['ip']).decode()
 if any(i.op_kind(k)==OpKind.NEAR_BRANCH16 for k in range(i.op_count)):edges.append(dict(source=row['image_offset'],target=0x11ee0+i.near_branch_target,kind='call' if i.flow_control==FlowControl.CALL else 'branch'))
 if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):edges.append(dict(source=row['image_offset'],target=0x11ee0+i.next_ip,kind='fallthrough_or_call_return'))
save('CFG_edges',edges)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));table=b[0x29870:0x29884];cases=[];events=[];visited=set();configs=[]
for enabled,offset,whence in itertools.product((0,1),(0,960,4164,0x7fffffff,0x80000000,0xfffffff6,0xffffffff),(0,1,2,3,0x100,0xffff)):
 configs.append(dict(enabled=enabled,offset=offset,whence=whence,handle=5,limit=20,current=10,length=100,failstage=0,error=5,major=3))
for current,length,failstage,error,major in itertools.product((0,0x7fffffff,0x80000000),(0,100),(0,1,2,3),(5,0x1234),(2,3)):
 configs.append(dict(enabled=1,offset=0xfffffff6,whence=2,handle=5,limit=20,current=current,length=length,failstage=failstage,error=error,major=major))
for handle,limit in ((0,0),(20,20),(0xffff,20),(0,20)):
 configs.append(dict(enabled=1,offset=0,whence=0,handle=handle,limit=limit,current=0,length=0,failstage=0,error=5,major=3))
for error,major in itertools.product((19,20,32,33,34,255),(2,3)):
 configs.append(dict(enabled=0,offset=0,whence=0,handle=5,limit=20,current=0,length=0,failstage=1,error=error,major=major))
for flag in (0,2,0xfd):
 configs.append(dict(enabled=0,offset=4164,whence=0,handle=5,limit=20,current=0,length=0,failstage=0,error=5,major=3,flag=flag))
# Fixtures preserve registers except AX/DX/CF; each call's request is independently predicted.
for load,split,df,c in itertools.product((0x824,0x1000),(False,True),(0,1),configs):
 raw=bytearray(b)
 for x in rel:struct.pack_into('<H',raw,int(x['image_offset']),(int(x['original_word'])+load)&65535)
 ds=load+0x2771;ss=0x6000 if split else ds;base=ds*16;sp=0xf000;sl,sh=ss*16+sp-64,ss*16+sp+20;ram=bytearray(b'\xa5'*0x200000);ram[load*16:load*16+len(raw)]=raw
 struct.pack_into('<H',ram,base+0x2128,c['limit']);struct.pack_into('<H',ram,base+0x2330,c['enabled']);ram[base+0x2121]=c['major'];struct.pack_into('<H',ram,base+0x2118,0xaabb);ram[base+0x2126]=0xcc
 if c['handle']<c['limit']:ram[base+0x212a+c['handle']]=c.get('flag',0xff)
 frame=struct.pack('<3HIH',0x200,0x4e00,c['handle'],c['offset'],c['whence']);ram[ss*16+sp:ss*16+sp+12]=frame;expected=bytearray(ram);want=[];stores=[];errno=None
 def dos(sub,off,result):
  failure=c['failstage']==len(want)+1;ax=c['error'] if failure else result&65535;dx=result>>16;want.append((0x4200|(sub&255),c['handle'],(off>>16)&65535,off&65535,failure,ax,dx));return failure,ax,dx
 def err(value):
  global errno
  al,ah=value&255,value>>8;v=ah if ah else table[5 if c['major']>=3 and al in (32,33) else min(al,19)];errno=v if v<128 else v-256;expected[base+0x2126]=al;struct.pack_into('<H',expected,base+0x2118,errno&65535);stores.extend([(base+0x2126,1,al),(base+0x2118,2,errno&65535)]);return 0xffff,0xffff
 error=None
 if c['handle']>=c['limit']:error=0x900
 elif c['enabled'] and c['offset']&0x80000000:
  if c['whence']==0:error=0x1600
  else:
   cf,ax,dx=dos(1,0,c['current'])
   if cf:error=ax
   elif not(c['whence']&2):
    if (((dx<<16)|ax)+c['offset'])&0x80000000:error=0x1600
   else:
    saved=(dx<<16)|ax;cf,ax,dx=dos(2,0,c['length']) # this CF is intentionally ignored by original body
    if (((dx<<16)|ax)+c['offset'])&0x80000000:
     dos(0,saved,saved);error=0x1600
 if error is None:
  cf,ax,dx=dos(c['whence'],c['offset'],0x12345678)
  if cf:error=ax
  else:
   p=base+0x212a+c['handle'];expected[p]&=0xfd;stores.append((p,1,expected[p]))
 if error is not None:ax,dx=err(error)
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));seen=[];writes=[];stopped=[]
 def code(e,a,n,data):
  if a==0x4e200:stopped.append(True);e.emu_stop();return
  p=a-load*16;assert p in allowed,hex(p);visited.add(p)
 def intr(e,no,data):
  assert no==0x21 and len(seen)<len(want);w=want[len(seen)];actual=tuple(e.reg_read(x) for x in (UC_X86_REG_AX,UC_X86_REG_BX,UC_X86_REG_CX,UC_X86_REG_DX));assert actual==w[:4],(c,actual,w);seen.append(w);e.reg_write(UC_X86_REG_AX,w[5]);e.reg_write(UC_X86_REG_DX,w[6]);e.reg_write(UC_X86_REG_EFLAGS,(e.reg_read(UC_X86_REG_EFLAGS)&~1)|int(w[4]))
 def write(e,access,a,n,v,data):
  if not(sl<=a and a+n<=sh):writes.append((a,n,v&((1<<(8*n))-1)))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_MEM_WRITE,write)
 for reg,value in ((UC_X86_REG_CS,load+0x11ee),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_ES,0x4567),(UC_X86_REG_EFLAGS,2|(df<<10))):u.reg_write(reg,value)
 u.emu_start((load+0x11ee)*16+0x1bd6,0x1fffff,count=300);assert stopped and seen==want and writes==stores,(c,seen,want,writes,stores)
 assert u.reg_read(UC_X86_REG_AX)==ax and u.reg_read(UC_X86_REG_DX)==dx,(c,ax,dx)
 for reg,value in ((UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp+4),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_ES,0x4567)):assert u.reg_read(reg)==value
 expected_cf=int(error is not None and error>>8==0 and (error&255)<19)
 assert (u.reg_read(UC_X86_REG_EFLAGS)>>10)&1==df and (u.reg_read(UC_X86_REG_EFLAGS)&1)==expected_cf,(c,error,u.reg_read(UC_X86_REG_EFLAGS),expected_cf)
 actual=bytes(u.mem_read(0,len(ram)));assert actual[:sl]==expected[:sl] and actual[sh:]==expected[sh:];assert actual[ss*16+sp:ss*16+sp+12]==frame
 cid=len(cases)
 for j,w in enumerate(seen):events.append(dict(case=cid,index=j,AX=w[0],BX=w[1],CX=w[2],DX=w[3],CF_response=w[4],AX_response=w[5],DX_response=w[6]))
 cases.append(dict(case=cid,load=load,split_SS_DS=split,DF=df,config=json.dumps(c),DOS_calls=len(seen),error=error,errno=errno,return_AX=ax,return_DX=dx,nonstack_stores=len(writes),status='PASS'))
save('cases',cases);save('DOS_events',events);save('execution_coverage',[dict(image_offset=x['image_offset'],executed=x['image_offset'] in visited) for x in allrows]);s=dict(functions=functions,cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,unexecuted_starts=sorted(allowed-visited),scope='Original seek,shared FAR return and errno translation; only DOS42 response fixtures. Full2MiB outside84 control-stack bytes and exact original nonstack writes/frame preserved. Fixture DOS semantics not proven; no new native scenario.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,image.parent/'relocations.csv',Path(__file__))]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
