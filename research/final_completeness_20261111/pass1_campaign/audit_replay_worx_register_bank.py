"""python audit_replay_worx_register_bank.py IMAGE INVENTORY DECODER EMULATOR OUT
Original bank copy/programmer/port writer/setter; explicit input resolver and IN values.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INSN
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);base=0x15bf0
def save(name,rs):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
defs=[('worx_bank_override_SB_record',0x3792,0x37c4),('worx_bank_program_voice',0x37d1,0x3896),('worx_port_callback_set',0x389a,0x38a7),('worx_port_write_delayed',0x38a7,0x38d2),('worx_bank_load_128x11',0x5973,0x5998)];functions=[];starts={};visited={}
for name,start,end in defs:
 todo=[start];dec={};edges=[]
 while todo:
  ip=todo.pop()
  if ip in dec:continue
  assert start<=ip<end;d=Decoder(16,b[base+ip:base+end],ip=ip);i=d.decode();assert not i.is_invalid;dec[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 rows=[]
 for ip,i in sorted(dec.items()):
  raw=b[base+ip:base+i.next_ip];assert old[base+ip]['bytes']==raw.hex();rows.append(dict(cs=0x15bf,ip=ip,image_offset=base+ip,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rows);save(name+'_cfg',edges);functions.append(dict(name=name,start=base+start,end_exclusive=base+end,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(x['bytes'])) for x in rows)));starts[name]=set(dec);visited[name]=set()
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];external_callback=0x70100
def run(kind,load,index=0,voice=0,callback=0,signature=0x4253,pattern=0,pointer=None,initial_if=0):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for r in rel:struct.pack_into('<H',runtime,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));cs=load+0x15bf;cb=cs*16;expected=bytearray(runtime[base:base+65536]);ss=0x9000;stack=0xf000;source_seg=0x6000;source_off=0x200
 target=dict(override=0x3792,program=0x37d1,writer=0x38a7,setter=0x389a,loader=0x5973)[kind];u.mem_write(ss*16+stack,struct.pack('<H',0x6000));u.mem_write(external_callback,b'\xcb')
 register_values={UC_X86_REG_AX:0x1234,UC_X86_REG_BX:0x2345,UC_X86_REG_CX:0x3456,UC_X86_REG_DX:0x4567,UC_X86_REG_SI:0x5678,UC_X86_REG_DI:source_off,UC_X86_REG_BP:0x6789}
 for q,v in register_values.items():u.reg_write(q,v)
 for q,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,cs),(UC_X86_REG_ES,source_seg),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,stack),(UC_X86_REG_EFLAGS,2+initial_if*0x200)]:u.reg_write(q,v)
 io=[];callbacks=[];done=[];expected_pairs=[];resolver=[]
 if kind in ('program','writer'):
  struct.pack_into('<HH',expected,0x3896,0x100,0x7000 if callback else 0);u.mem_write(cb+0x3896,bytes(expected[0x3896:0x389a]))
 if kind=='override':
  record=bytearray(0x24+11);struct.pack_into('<H',record,0,signature);record[0x24:]=bytes((index*17+j*29+load)&255 for j in range(11));u.mem_write(source_seg*16+source_off,bytes(record));u.reg_write(UC_X86_REG_BX,index);register_values[UC_X86_REG_BX]=index
  if signature==0x4253:expected[0x2513+11*index:0x2513+11*(index+1)]=record[0x24:]
 elif kind=='program':
  data=bytes(expected[0x2513+11*index:0x2513+11*(index+1)])
  if load==0x824:data=bytes((index*37+j*53)&255 for j in range(11));expected[0x2513+11*index:0x2513+11*(index+1)]=data;u.mem_write(cb+0x2513+11*index,data)
  u.reg_write(UC_X86_REG_BX,index|voice<<8);register_values[UC_X86_REG_BX]=index|voice<<8;op0,op1=expected[0x2b66+voice],expected[0x2b6f+voice]
  expected_pairs=[((reg+op)&255,data[j]) for j,(reg,op) in enumerate([(0x20,op0),(0x20,op1),(0x40,op0),(0x40,op1),(0x60,op0),(0x60,op1),(0x80,op0),(0x80,op1),(0xe0,op0),(0xe0,op1)])]+[(0xc0+voice,data[10])];expected[0x2bd0+voice]=data[3]
 elif kind=='writer':
  ax=index|(((index*73+17)&255)<<8);u.reg_write(UC_X86_REG_AX,ax);register_values[UC_X86_REG_AX]=ax;expected_pairs=[(ax&255,ax>>8)]
 elif kind=='setter':
  off,seg=pointer;u.reg_write(UC_X86_REG_BX,off);u.reg_write(UC_X86_REG_DX,seg);struct.pack_into('<HH',expected,0x3896,off,seg);register_values[UC_X86_REG_BX]=off;register_values[UC_X86_REG_DX]=seg
 else:
  raw=bytes((i*(1 if pattern==0 else 73)+pattern*29)&255 for i in range(4+128*16));u.mem_write(source_seg*16+source_off,raw)
  for n in range(128):expected[0x2513+11*n:0x2513+11*(n+1)]=raw[4+16*n:15+16*n]
 def outp(emu,port,size,value,data):io.append(('OUT',port,size,value))
 def inp(emu,port,size,data):io.append(('IN',port,size,None));return (len(io)*13+port)&255
 def hook(emu,address,size,data):
  if address==cb+0x6000:done.append(True);emu.emu_stop();return
  if address==external_callback:callbacks.append(emu.reg_read(UC_X86_REG_AX));return
  if kind=='loader' and address==cb+0x4630:
   resolver.append(True);sp=emu.reg_read(UC_X86_REG_SP);ret=struct.unpack('<H',bytes(emu.mem_read(ss*16+sp,2)))[0];emu.reg_write(UC_X86_REG_ES,source_seg);emu.reg_write(UC_X86_REG_DI,source_off);emu.reg_write(UC_X86_REG_SP,sp+2);emu.reg_write(UC_X86_REG_IP,ret);return
  ip=address-cb
  for name,points in starts.items():
   if ip in points:visited[name].add(ip);return
  raise AssertionError(('unexpected instruction',kind,hex(address)))
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INSN,outp,None,1,0,UC_X86_INS_OUT);u.hook_add(UC_HOOK_INSN,inp,None,1,0,UC_X86_INS_IN);u.emu_start(cb+target,0,count=30000)
 assert done and bytes(u.mem_read(cb,65536))==expected,(kind,index,voice,'memory')
 assert u.reg_read(UC_X86_REG_CS)==cs and u.reg_read(UC_X86_REG_DS)==cs and u.reg_read(UC_X86_REG_SS)==ss and u.reg_read(UC_X86_REG_SP)==stack+2 and u.reg_read(UC_X86_REG_BP)==0x6789
 expected_io=[]
 for reg,value in expected_pairs:expected_io += [('OUT',0x388,1,reg)]+[('IN',0x388,1,None)]*6+[('OUT',0x389,1,value)]+[('IN',0x389,1,None)]*70
 assert io==expected_io and callbacks==([reg|(value<<8) for reg,value in expected_pairs] if callback else [])
 if kind=='override':
  for q in (UC_X86_REG_BX,UC_X86_REG_CX,UC_X86_REG_SI,UC_X86_REG_DI):assert u.reg_read(q)==register_values[q]
  assert u.reg_read(UC_X86_REG_ES)==source_seg and (u.reg_read(UC_X86_REG_EFLAGS)&1)==(signature!=0x4253)
 elif kind in ('writer','program'):
  for q,v in register_values.items():assert u.reg_read(q)==v
 elif kind=='setter':assert u.reg_read(UC_X86_REG_EFLAGS)&0x200
 else:assert resolver==[True] and u.reg_read(UC_X86_REG_AX)==0 and u.reg_read(UC_X86_REG_BX)==128 and u.reg_read(UC_X86_REG_SI)==0x2513+1408
 cases.append(dict(kind=kind,load=load,index=index,voice=voice,callback=callback,signature=signature,pattern=pattern,port_pairs=len(expected_pairs),IN_reads=len(expected_pairs)*76,callback_calls=len(callbacks),status='PASS'))
for load in (0x1000,0x824):
 for index,signature in itertools.product(range(128),(0x4253,0x1234)):run('override',load,index=index,signature=signature)
 for index,voice,callback in itertools.product(range(128),range(9),(0,1)):run('program',load,index=index,voice=voice,callback=callback)
 for index,callback in itertools.product(range(256),(0,1)):run('writer',load,index=index,callback=callback)
 for pointer,initial_if in itertools.product(((0,0),(0x100,0),(0,0x7000),(0x100,0x7000)),(0,1)):run('setter',load,pointer=pointer,initial_if=initial_if)
 for pattern in range(3):run('loader',load,pattern=pattern)
save('cases',cases);save('instruction_execution_coverage',[dict(function=n,ip=ip,executed=ip in visited[n]) for n in starts for ip in sorted(starts[n])]);fields=[]
for name,a,z,typ in [('worx_register_bank128x11',base+0x2513,base+0x2a93,'128_records11BYTE_sound_register_parameters'),('worx_operator_offsets_2x9',base+0x2b66,base+0x2b78,'two_BYTE9_voice_operator_offset_maps'),('worx_voice_byte3_cache9',base+0x2bd0,base+0x2bd9,'mutable_BYTE9_programmed_bank_BYTE3_cache'),('worx_port_callback_FAR',base+0x3896,base+0x389a,'mutable_FAR16_pointer_segment0_disables_callback')]:fields.append(dict(name=name,start=a,end_exclusive=z,length=z-a,type=typ,status='PARTIAL',range_sha256=sha(b[a:z])))
save('data_fields',fields);save('bank_records',[dict(index=n,start=base+0x2513+11*n,end_exclusive=base+0x2513+11*(n+1),bytes=b[base+0x2513+11*n:base+0x2513+11*(n+1)].hex()) for n in range(128)])
candidate=0x1812d;assert b[candidate:candidate+4]==bytes.fromhex('00063201');offset=candidate-(base+0x2513);context=dict(candidate_image=candidate,table_start=base+0x2513,table_end_exclusive=base+0x2a93,record_index=offset//11,byte_in_record=offset%11,candidate_length=4,crosses_record_boundary=True,scope='proven bank storage and consumers; raw ADD[0132],AL parse is not a proved executable reference; alternate execution cannot be excluded solely by data role')
(out/'remaining_candidate_context.json').write_text(json.dumps(context,indent=2)+'\n',encoding='utf-8')
summary=dict(functions=functions,cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,typed_bytes=sum(x['length'] for x in fields),instruction_starts_executed=sum(len(x) for x in visited.values()),unexecuted_starts={n:sorted(starts[n]-visited[n]) for n in starts},scope='whole original5NEARfunctions,bankprogrammer uses original portwriter; controlled INvalues/callbackfixture; loader4630resolver substituted; DS=CS andDF0;128instruments9voices; no native playback/physicalhardware or invalidindex safety proof',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
