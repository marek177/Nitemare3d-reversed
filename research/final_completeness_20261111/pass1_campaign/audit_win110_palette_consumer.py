"""python audit_win110_palette_consumer.py EXE ASM FIXUPS DECODER EMULATOR GAME_PAL OUT"""
import csv,hashlib,itertools,json,re,struct,sys
from pathlib import Path
exe,asm,fixups,dep,emu,assetpath,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INSN
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=exe.read_bytes();asset=assetpath.read_bytes();assert sha(b)=='12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481';assert sha(asset)=='b6b71824a73a74c79e0f3ae12c9a423f2ae500ca956fe156f1f0d4d2307d24fc';out.mkdir(parents=True,exist_ok=True)
ne=struct.unpack_from('<I',b,60)[0];word=lambda p:struct.unpack_from('<H',b,p)[0];segments={}
for seg in range(1,word(ne+28)+1):
 sector,size,flags,alloc=struct.unpack_from('<4H',b,ne+word(ne+34)+(seg-1)*8)
 if sector:a=sector<<word(ne+50);segments[seg]=(a,b[a:a+(size or 65536)])
assert word(ne+14)==10 and segments[10][1][0xeae:0xeb7]==b'game.pal\0'
rx=re.compile(r'^([0-9A-Fa-f]{4}):([0-9A-Fa-f]{4})\s+((?:[0-9A-Fa-f]{2}\s+)+)');inventory={}
for line in asm.read_text(encoding='utf-8-sig').splitlines():
 m=rx.match(line)
 if m:inventory[(int(m[1],16),int(m[2],16))]=bytes.fromhex(m[3])
fmt=Formatter(FormatterSyntax.INTEL);far={(int(r['segment']),int(r['instruction_offset'])):r for r in csv.DictReader((fixups/'far_candidates.csv').open())};sites={(int(r['segment']),int(r['source_offset'])):r for r in csv.DictReader((fixups/'expanded_sites.csv').open())};rows=[];functions=[];edges=[]
for name,start,end in [('win_palette_load_tail',0x4904,0x4989),('win_palette_dispatch',0x3af4,0x3b15),('win_palette_vga_upload',0x3acc,0x3af4),('win_palette_gdi',0x31aa,0x335f)]:
 todo=[start];decoded={}
 while todo:
  ip=todo.pop()
  if ip in decoded:continue
  assert start<=ip<end;i=Decoder(16,segments[3][1][ip:end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
 local=[]
 for ip,i in sorted(decoded.items()):
  raw=segments[3][1][ip:i.next_ip];assert inventory[(3,ip)]==raw;row=dict(function=name,segment=3,offset=ip,file_offset=segments[3][0]+ip,bytes=raw.hex(),instruction=fmt.format(i));rows.append(row);local.append(row)
  if raw[0]==0x9a:
   f=far[(3,ip)];assert bytes.fromhex(f['raw_instruction'])==raw
   site=sites[(3,int(f['fixup_source_offset']))];assert site['target']==f['target'] and site['source_type']==f['source_type']
   assert int(f['fixup_source_offset'])==ip+(3 if f['source_type']=='2' else 1)
   edges.append(dict(caller=ip,target=f['target'],target_segment=f['effective_internal_segment'],target_offset=f['effective_internal_offset'],fixup_source_offset=f['fixup_source_offset'],source_type=f['source_type'],scope='NE fixup-backed static target; runtime selector unresolved'))
 functions.append(dict(name=name,segment=3,start=start,end_exclusive=end,instructions=len(local),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in local),status='PARTIAL',scope='bounded static CFG; replay scopes separate'))
def save(name,rs):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
save('instructions',rows);save('functions',functions);save('call_edges',edges);cases=[];lp_rows=[]
patterns=[('actual',asset[-768:]),('ramp',bytes(range(256))*3),('allFF',b'\xff'*768),('all00',b'\0'*768)]
# Every rewritten call is backed by an expanded NE edge; these are synthetic selectors.
def prepare(layout,phase):
 cs=0x3000+layout*0x100;ds=0x5000+layout*0x100;u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(cs*16,segments[3][1]);u.mem_write(ds*16,segments[10][1]);stubs={};nextstub=0
 native={0x3af4,0x3acc} if phase=='loader' else set()
 for e in edges:
  ip=e['caller'];seg=e['target_segment'];off=e['target_offset'];internal=(int(seg),int(off)) if seg and off else None
  if phase=='loader' and internal and internal[0]==3 and internal[1] in native:
   u.mem_write(cs*16+ip+1,struct.pack('<HH',internal[1],cs));continue
  key=e['target'];key=('%d:%04X'%internal) if internal else key
  if key not in stubs:
   nextstub+=0x10;stubs[key]=(0x8000,nextstub)
   cleanup={'USER:#66':2,'GDI:#373':4,'GDI:#375':10,'GDI:#360':4}.get(key,0)
   u.mem_write(0x80000+nextstub,b'\xca'+struct.pack('<H',cleanup) if cleanup else b'\xcb')
  segstub,offstub=stubs[key];u.mem_write(cs*16+ip+1,struct.pack('<HH',offstub,segstub))
 return u,cs,ds,{seg*16+off:key for key,(seg,off) in stubs.items()}
for layout,(pattern,raw),backend in itertools.product((0,1),patterns,(0,1)):
 u,cs,ds,stubs=prepare(layout,'loader');u.mem_write(ds*16+0x46b0,bytes([backend]));state={'reads':0,'gdi_calls':0};ports=[];trace=[]
 def hook(uc,address,size,user):
  if address not in stubs:return
  key=stubs[address];sp=uc.reg_read(UC_X86_REG_SP);args=lambda n:struct.unpack('<'+'H'*n,bytes(uc.mem_read(ds*16+sp+4,n*2)));trace.append(key)
  if key=='2:54D4':assert args(2)==(0xeae,0x8000);uc.reg_write(UC_X86_REG_AX,7)
  elif key=='2:53E8':assert args(4)==(7,0xfd00,0xffff,2);uc.reg_write(UC_X86_REG_AX,len(asset)-768);uc.reg_write(UC_X86_REG_DX,0)
  elif key=='2:5798':
   handle,dest,count=args(3);n=state['reads'];assert (handle,dest,count)==(7,0x5b7e+n,1) and n<768;uc.mem_write(ds*16+dest,raw[n:n+1]);state['reads']+=1;uc.reg_write(UC_X86_REG_AX,1)
  elif key=='3:31AA':assert args(2)==(0x5b7e,0);assert bytes(uc.mem_read(ds*16+0x5b7e,768))==raw;state['gdi_calls']+=1
  elif key=='3:2AAC':assert args(1)==(0,)
  elif key=='2:53B0':assert args(1)==(7,)
  else:raise AssertionError(('unexpected loader callee',key))
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INSN,lambda uc,port,size,value,user:ports.append((port,size,value)),None,1,0,UC_X86_INS_OUT)
 for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 u.mem_write(ds*16+0xff00,struct.pack('<HH',0xf800,cs));u.emu_start(cs*16+0x4904,cs*16+0xf800,count=40000)
 assert bytes(u.mem_read(ds*16+0x5b7e,768))==raw and state['reads']==768
 assert ports==([(0x3c8,1,0)]+[(0x3c9,1,n>>2) for n in raw] if backend else []) and state['gdi_calls']==(0 if backend else 1)
 for reg,val in [(UC_X86_REG_DS,ds),(UC_X86_REG_SP,0xff04),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)]:assert u.reg_read(reg)==val
 cases.append(dict(phase='loader_dispatch',layout=layout,pattern=pattern,backend=backend,reserved_flag='',calls=len(trace),port_writes=len(ports),passed=True))
for layout,reserved in itertools.product((0,1),(0,1,255)):
 u,cs,ds,stubs=prepare(layout,'gdi_prefix');raw=asset[-768:];u.mem_write(ds*16+0x5b7e,raw);u.mem_write(ds*16+0x46af,bytes([reserved]));state={'captured':None};trace=[]
 system=bytes(v for n in range(256) for v in (n,n^0x55,255-n,0x80));nreserved=10 if reserved else 0;expected=bytearray(system)
 for n in range(256):expected[n*4+3]=0
 for n in range(nreserved,256-nreserved):expected[n*4:n*4+4]=raw[n*3:n*3+3]+b'\1'
 def hook(uc,address,size,user):
  if address not in stubs:return
  key=stubs[address];sp=uc.reg_read(UC_X86_REG_SP);args=lambda n:struct.unpack('<'+'H'*n,bytes(uc.mem_read(ds*16+sp+4,n*2)));trace.append(key)
  if key=='USER:#66':uc.reg_write(UC_X86_REG_AX,0x2222)
  elif key=='GDI:#373':assert args(2)==(1,0x2222)
  elif key=='GDI:#375':
   off,seg,count,start,hdc=args(5);assert (seg,count,start,hdc)==(ds,256,0,0x2222);uc.mem_write(seg*16+off,system);uc.reg_write(UC_X86_REG_AX,256)
  elif key=='3:2CC6':pass
  elif key=='GDI:#360':
   off,seg=args(2);assert seg==ds;lp=bytes(uc.mem_read(seg*16+off,1028));assert lp==bytes.fromhex('00030001')+expected;state['captured']=lp;uc.emu_stop()
  else:raise AssertionError(('unexpected GDI prefix callee',key))
 u.hook_add(UC_HOOK_CODE,hook)
 for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 u.mem_write(ds*16+0xff00,struct.pack('<4H',0xf800,cs,0x5b7e,0));u.emu_start(cs*16+0x31aa,cs*16+0xf800,count=10000);assert state['captured'] is not None
 cases.append(dict(phase='gdi_prefix',layout=layout,pattern='actual',backend=0,reserved_flag=reserved,calls=len(trace),port_writes=0,passed=True));lp_rows.append(dict(layout=layout,reserved_flag=reserved,preserved_first_last=nreserved,palette_sha256=sha(state['captured']),scope='stop at GDI ordinal360 before API body; system entries and earlier APIs mocked'))
save('cases',cases);save('logical_palette_prefix',lp_rows)
s=dict(exe_sha256=sha(b),asm_sha256=sha(asm.read_bytes()),asset_sha256=sha(asset),far_candidates_sha256=sha((fixups/'far_candidates.csv').read_bytes()),functions=len(functions),instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),relocation_backed_calls=len(edges),cases=len(cases),loader_cases=16,gdi_prefix_cases=6,failures=0,cases_sha256=sha((out/'cases.csv').read_bytes()),runtime_tests=0,new_deep_verified_bytes=0,runtime_DS_closed=False,scope='Win110 bounded static code and synthetic-selector instruction replay; file/API dependencies mocked; GDI only prefix through creation call; no actual Win16 runtime or full palette parity')
s['source_inputs']=[dict(path=str(path.resolve()),sha256=sha(path.read_bytes())) for path in (exe,asm,assetpath,fixups/'far_candidates.csv',fixups/'expanded_sites.csv')]
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='source_inputs'},indent=2))
