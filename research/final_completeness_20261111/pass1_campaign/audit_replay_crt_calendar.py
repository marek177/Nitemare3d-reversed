"""IMAGE INVENTORY DECODER EMULATOR OUT. Original calendar/DST+mul/remainder."""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(exist_ok=True);old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
defs=[('crt_DST_style_predicate',0x2d00,0x2dbf),('crt_calendar_to_epoch32',0x2dc0,0x2eb3),('compiler_mul32_low',0x3ad8,0x3b0a),('compiler_signed_remainder32',0x3b0a,0x3baa)];functions=[];starts={};visited={}
for name,lo,hi in defs:
 todo=[lo];dec={};edges=[]
 while todo:
  ip=todo.pop()
  if ip in dec:continue
  assert lo<=ip<hi;i=Decoder(16,b[0x11ee0+ip:0x11ee0+hi],ip=ip).decode();assert not i.is_invalid;dec[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 rr=[]
 for ip,i in sorted(dec.items()):
  pos=0x11ee0+ip;raw=b[pos:0x11ee0+i.next_ip];assert old[pos]['bytes']==raw.hex();rr.append(dict(cs=0x11ee,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rr);save(name+'_cfg',edges);functions.append(dict(name=name,start=0x11ee0+lo,end_exclusive=0x11ee0+hi,instructions=len(rr),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rr)));starts[name]=set(r['image_offset'] for r in rr);visited[name]=set()
common=list(struct.unpack('<13h',b[0x29b98:0x29bb2]));assert common==[-1,30,58,89,119,150,180,211,242,272,303,333,364]
def s16(x):return (x+32768)%65536-32768
def s32(x):return (x+2147483648)%4294967296-2147483648
def rem(a,d):return a-((abs(a)//abs(d))*(-1 if (a<0)!=(d<0) else 1))*d
def dst(year,month,yday,hour):
 if year<67 or month<3 or month>9:return 0
 if 3<month<9:return 1
 base=(common[month]+7) if year>86 and month==3 else common[month+1]
 if year&3==0:base+=1
 n=s16(365*s16(year-70)+(s16(year-1)>>2)+base)-13
 boundary=s16(base-rem(n,7))
 if month==3:return int(boundary<yday or (boundary==yday and hour>=2))
 return int(yday<boundary or (yday==boundary and hour<1))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));runtime={}
for load in (0x824,0x1000):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 runtime[load]=bytes(raw)
cases=[]
def run(load,year,month,day,hour,timezone,dst_enabled):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,runtime[load]);ds=load+0x2771
 dg=bytearray(b[0x27710:])+bytearray([0x66]*(0xe030-(len(b)-0x27710)));struct.pack_into('<IH',dg,0x24a6,timezone&0xffffffff,dst_enabled);u.mem_write(ds*16,bytes(dg));minute,second=37,58
 frame=struct.pack('<8H',0x100,0x5000,year&65535,month,day,hour,minute,second);u.mem_write(ds*16+0xf000,frame)
 for reg,val in [(UC_X86_REG_CS,load+0x11ee),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 done=[];refresh=[];table_reads=[]
 def hook(emu,address,size,data):
  pos=address-load*16
  for name,ss in starts.items():
   if pos in ss:visited[name].add(pos)
  if address==0x50100:done.append(True);emu.emu_stop();return
  if pos==0x11ee0+0x2dd0:table_reads.append((emu.reg_read(UC_X86_REG_BX)+0x2486)&65535)
  if pos==0x11ee0+0x2bf4:
   refresh.append(True);sp=emu.reg_read(UC_X86_REG_SP);ip,cs=struct.unpack('<HH',bytes(emu.mem_read(ds*16+sp,4)));emu.reg_write(UC_X86_REG_SP,sp+4);emu.reg_write(UC_X86_REG_CS,cs);emu.reg_write(UC_X86_REG_IP,ip)
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((load+0x11ee)*16+0x2dc0,0xfffff,count=3000);assert done and len(refresh)==1
 yday=common[month-1]+day+int(year&3==0 and month>2)
 expected=((((365*year+((year+3)>>2)+day+common[month-1]+int(year&3==0 and month>2)+3652)*24+hour)*60+minute)*60+second+timezone-3600*(dst(s16(year+80),month-1,yday,hour) if dst_enabled else 0))&0xffffffff
 actual=u.reg_read(UC_X86_REG_AX)|(u.reg_read(UC_X86_REG_DX)<<16);assert actual==expected,(year,month,day,hour,timezone,dst_enabled,actual,expected)
 assert bytes(u.mem_read(ds*16,len(dg)))==dg and table_reads==[0x2486+2*month]
 for reg,val in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xf004),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)]:assert u.reg_read(reg)==val
 assert bytes(u.mem_read(ds*16+0xf000,16))==frame
 cases.append(dict(load=load,year_since1980=year,month=month,day=day,hour=hour,minute=minute,second=second,timezone_seconds=timezone,DST_enable=dst_enabled,yday=yday,expected_epoch_hex='%08X'%expected,table_read_DS='%04X'%table_reads[0],status='PASS'))
for load,year,month,hour,timezone,enabled in itertools.product((0x824,0x1000),(-14,-13,0,6,7,20,44,46,120),range(1,13),(0,1,2,23),(-18000,0,3600),(0,1)):
 length=([31,29 if year&3==0 else 28,31,30,31,30,31,31,30,31,30,31])[month-1]
 days={1,length}
 if month in (4,10):
  for day in range(2,length):
   yday=common[month-1]+day+int(year&3==0 and month>2)
   if dst(year+80,month-1,yday,0)!=dst(year+80,month-1,yday,23):days.update((day-1,day,day+1))
 for day in sorted(days):run(load,year,month,day,hour,timezone,enabled)
helper_cases=[]
def helper(load,operation,a,d):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,runtime[load]);ds=load+0x2771;frame=struct.pack('<HHII',0x100,0x5000,a&0xffffffff,d&0xffffffff);u.mem_write(ds*16+0xf000,frame)
 for reg,val in [(UC_X86_REG_CS,load+0x11ee),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_BX,0x4567),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 done=[]
 def hook(emu,address,size,data):
  if address==0x50100:done.append(True);emu.emu_stop();return
  pos=address-load*16
  for name,ss in starts.items():
   if pos in ss:visited[name].add(pos)
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((load+0x11ee)*16+(0x3ad8 if operation=='multiply' else 0x3b0a),0xfffff,count=3000);assert done
 expected=(a*d if operation=='multiply' else rem(s32(a),s32(d)))&0xffffffff;actual=u.reg_read(UC_X86_REG_AX)|(u.reg_read(UC_X86_REG_DX)<<16);assert actual==expected,(operation,hex(a),hex(d),hex(actual),hex(expected))
 for reg,val in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf00c),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_BX,0x4567)]:assert u.reg_read(reg)==val
 expected_frame=frame if operation=='multiply' else struct.pack('<HHII',0x100,0x5000,abs(s32(a))&0xffffffff,abs(s32(d))&0xffffffff)
 assert bytes(u.mem_read(ds*16+0xf000,12))==expected_frame
 helper_cases.append(dict(load=load,operation=operation,a_hex='%08X'%a,b_hex='%08X'%d,result_hex='%08X'%expected,status='PASS'))
values=(0,1,2,7,0x7fff,0x8000,0xffff,0x10000,0x10001,0x7fffffff,0x80000000,0x80000001,0xffff0000,0xfffffffe,0xffffffff)
for load,operation,a,d in itertools.product((0x824,0x1000),('multiply','remainder'),values,values):
 if operation=='remainder' and d==0:continue
 helper(load,operation,a,d)
save('cases',cases);save('helper_cases',helper_cases);save('instruction_execution_coverage',[dict(function=n,image_offset=p,executed=p in visited[n]) for n in starts for p in sorted(starts[n])])
s=dict(functions=[f for f in functions if f['name']!='compiler_mul32_low'],reused_functions=[f for f in functions if f['name']=='compiler_mul32_low'],cases=len(cases)+len(helper_cases),calendar_cases=len(cases),helper_cases=len(helper_cases),failures=0,executed_instruction_starts=sum(map(len,visited.values())),unexecuted_starts={n:sorted(starts[n]-visited[n]) for n in starts},runtime_tests=0,new_deep_verified_bytes=0,scope='Whole original converter and DST predicate plus original mul32/remainder32; timezone refresh only external fixture preserving preseeded fields. Valid month1..12; year edges1966/1967/2100 synthetic. Separate signed arithmetic helper matrix excludes zero divisors. FullDGROUP/frame/register/lookup targets compared for calendar cases. No native or Win16 parity by replay alone.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,image.parent/'relocations.csv',Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
