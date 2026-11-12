"""IMAGE INVENTORY DECODER EMULATOR OUT: original gameclock/ftime, only INT21 fixtures."""
import csv,datetime,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(exist_ok=True);old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
functions=[];starts={};visited={}
for name,lo,hi in [('crt_ftime_timeb10',0x2aea,0x2bf3),('crt_DOS_date5',0x3a0a,0x3a23),('crt_DOS_time4',0x3a24,0x3a3d)]:
 todo=[lo];dec={};edges=[]
 while todo:
  ip=todo.pop()
  if ip in dec:continue
  assert lo<=ip<hi;i=Decoder(16,b[0x11ee0+ip:0x11ee0+hi],ip=ip).decode();assert not i.is_invalid;dec[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 rr=[]
 for ip,i in sorted(dec.items()):
  p=0x11ee0+ip;raw=b[p:0x11ee0+i.next_ip];assert old[p]['bytes']==raw.hex();rr.append(dict(cs=0x11ee,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rr);save(name+'_cfg',edges);functions.append(dict(name=name,start=0x11ee0+lo,end_exclusive=0x11ee0+hi,instructions=len(rr),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rr)));starts[name]=set(r['image_offset'] for r in rr);visited[name]=set()
model=Path(__file__).with_name('audit_replay_crt_calendar.py');source=model.read_text(encoding='utf-8');exec(source[source.index('common=list'):source.index('rel=list')],globals())
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));runtime={};cases=[]
for load in (0x824,0x1000):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 runtime[load]=bytes(raw)
tzs=[('cold_absent',0,[],28800,1,None,None),('cold_empty',0,[b'TZ='],28800,1,None,None),('cold_plus3',0,[b'TZ=ABC3DEF'],10800,68,b'ABC',b'DEF'),('cold_minus5',0,[b'TZ=XYZ-5GHI'],-18000,71,b'XYZ',b'GHI'),('cold_zero',0,[b'TZ=ABC0'],0,0,b'ABC',b''),('warm_plus61',1,[b'TZ=IGN9RED'],61,1,None,None),('warm_minus61',1,[b'TZ=IGN9RED'],-61,1,None,None),('warm_noDST',1,[],0,0,None,None)]
dates=[((2024,6,1),(2024,6,1),(5,6,7,8)),((2026,11,12),(2026,11,12),(17,9,37,12)),((2026,5,31),(2026,6,1),(0,0,4,99)),((2026,6,1),(2026,6,1),(0,1,0,0)),((2024,2,29),(2024,2,29),(23,59,59,99)),((1987,4,5),(1987,4,5),(1,59,59,1)),((1987,4,5),(1987,4,5),(2,0,0,50)),((1986,10,26),(1986,10,26),(0,30,0,75)),((2100,2,28),(2100,2,28),(12,34,56,78))]
def run(load,mode,tz,date):
 label,cache,env,zone,enabled,std,dayname=tz;date1,date2,time=date;h,m,sec,centi=time;redate=(h==0 and m==0);year,month,day=date2 if redate else date1;y=year-1980
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,runtime[load]);ds=load+0x2771;dg=bytearray(b[0x27710:])+bytearray(0xe030-(len(b)-0x27710));dg[0x3cc7]=1;dg[0x3ccf]=int(mode=='sample');struct.pack_into('<I',dg,0x81e,0x87654321);struct.pack_into('<H',dg,0x3ca8,cache)
 if cache:struct.pack_into('<iH',dg,0x24a6,zone,enabled)
 vector=0x9000;cursor=0x9040;struct.pack_into('<H',dg,0x2142,vector)
 for index,text in enumerate(env):struct.pack_into('<H',dg,vector+2*index,cursor);dg[cursor:cursor+len(text)+1]=text+b'\0';cursor+=len(text)+1
 struct.pack_into('<H',dg,vector+2*len(env),0);u.mem_write(ds*16,bytes(dg));frame=struct.pack('<HH',0x100,0x5000);u.mem_write(ds*16+0xf000,frame)
 for reg,val in [(UC_X86_REG_CS,load+0xbde),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 done=[];dates_seen=[];times_seen=[];tb={};executed=set()
 def code(emu,address,size,data):
  p=address-load*16;executed.add(p)
  for name,ss in starts.items():
   if p in ss:visited[name].add(p)
  if address==0x50100:done.append(True);emu.emu_stop();return
  if p==0x11ee0+0x2aea:
   sp=emu.reg_read(UC_X86_REG_SP);retip,retcs,ptr=struct.unpack('<3H',bytes(emu.mem_read(ds*16+sp,6)));tb.update(ptr=ptr,before=bytes(emu.mem_read(ds*16+ptr,14)))
 def interrupt(emu,number,data):
  assert number==0x21;ah=emu.reg_read(UC_X86_REG_AH)
  if ah==0x2a:
   d=date1 if not dates_seen else date2;dates_seen.append(d);yy,mm,dd=d;weekday=(datetime.date(yy,mm,dd).weekday()+1)%7;emu.reg_write(UC_X86_REG_AX,0x2a00|weekday);emu.reg_write(UC_X86_REG_CX,yy);emu.reg_write(UC_X86_REG_DX,mm<<8|dd)
  elif ah==0x2c:
   times_seen.append(time);emu.reg_write(UC_X86_REG_AX,0x2c00);emu.reg_write(UC_X86_REG_CX,h<<8|m);emu.reg_write(UC_X86_REG_DX,sec<<8|centi)
  else:raise AssertionError(hex(ah))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,interrupt);u.emu_start((load+0xbde)*16+(0x18 if mode=='sample' else 0x94),0xfffff,count=20000);assert done
 prior=common[month-1]+int(y&3==0 and month>2);yday=day+prior;is_dst=dst(year-1900,month-1,yday,h) if enabled else 0;epoch=((((365*y+((y+3)>>2)+day+prior+3652)*24+h)*60+m)*60+sec+zone-3600*is_dst)&0xffffffff;millis=centi*10;zone_minutes=(abs(zone)//60)*(-1 if zone<0 else 1)
 expected_tb=struct.pack('<IHhH',epoch,millis,s16(zone_minutes),is_dst)+tb['before'][10:];assert bytes(u.mem_read(ds*16+tb['ptr'],14))==expected_tb
 result=(epoch*1000+millis)&0xffffffff;assert u.reg_read(UC_X86_REG_AX)|(u.reg_read(UC_X86_REG_DX)<<16)==result
 expected=bytearray(dg)
 if not cache:
  struct.pack_into('<H',expected,0x3ca8,1);struct.pack_into('<iH',expected,0x24a6,zone,enabled)
  if std is not None:expected[0x24ac:0x24af]=std
  if dayname==b'':expected[0x24b0]=0
  elif dayname is not None:expected[0x24b0:0x24b3]=dayname
 if mode=='cached':struct.pack_into('<I',expected,0x81e,result)
 assert bytes(u.mem_read(ds*16,len(dg)))==expected,(label,date,mode)
 assert dates_seen==([date1,date2] if redate else [date1]) and times_seen==[time]
 for reg,val in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xf004),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)]:assert u.reg_read(reg)==val
 assert bytes(u.mem_read(ds*16+0xf000,4))==frame
 cases.append(dict(load=load,mode=mode,TZ_fixture=label,date1=str(date1),date2=str(date2),time=str(time),date_calls=len(dates_seen),time_calls=len(times_seen),timezone_seconds=zone,timezone_minutes=zone_minutes,DST_flag=is_dst,epoch_hex='%08X'%epoch,milliseconds=millis,clock_result_hex='%08X'%result,ftime_record_hex=expected_tb.hex(),status='PASS'))
for params in itertools.product((0x824,0x1000),('sample','cached'),tzs,dates):run(*params)
save('cases',cases);save('instruction_execution_coverage',[dict(function=n,image_offset=p,executed=p in visited[n]) for n in starts for p in sorted(starts[n])])
s=dict(functions=functions,cases=len(cases),failures=0,executed_instruction_starts=sum(map(len,visited.values())),unexecuted_starts={n:sorted(starts[n]-visited[n]) for n in starts},runtime_tests=0,new_deep_verified_bytes=0,scope='Original game sample/cached,ftime,date/time wrappers,timezone parser/getenv/string/number/compiler helpers/calendar/DST execute. Only INT21 date/time responses are fixtures. All57392B DGROUP,10B output plus4 untouched tailB,frames/registers and OS call counts checked. No real OS/native/calendar-law/Win16 parity by this matrix.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,image.parent/'relocations.csv',model,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
