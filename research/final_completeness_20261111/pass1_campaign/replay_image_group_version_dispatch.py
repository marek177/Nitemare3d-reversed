"""python replay_image_group_version_dispatch.py EMULATOR COMPARISON_DIR
Original resource wrapper; compare version-specific decoder call ABIs with recording stubs.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
emulator,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(emulator.resolve()))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');comparisons=list(csv.DictReader((out/'function_comparisons.csv').open()));rows=[];inputs=[]
for label in ('10','11','12','15','17','18','19','20'):
 p=root/('N3D-'+label)/'unpacked_image.bin';b=p.read_bytes();ipath=p.with_name('instructions.json');inv=json.loads(ipath.read_text(encoding='utf-8'));r=next(x for x in comparisons if x['version']==label);cs,ip=int(r['cs']),int(r['ip']);owner='%04X:%04X'%(cs,ip);owned=sorted((x for x in inv if owner in x['owners']),key=lambda x:x['image_offset']);far=[struct.unpack_from('<HH',bytes.fromhex(x['bytes']),1) for x in owned if x['bytes'].startswith('9a')];assert len(far)==7 and far[0]==far[1]==far[5] and far[2]==far[6]
 near=[int(x['operands'],16) for x in owned if x['mnemonic']=='call'];assert len(near)==(2 if label=='10' else 1)
 targets={far[0][1]*16+far[0][0]:'error',far[2][1]*16+far[2][0]:'seek',far[3][1]*16+far[3][0]:'read',far[4][1]*16+far[4][0]:'allocate'};targets.update({cs*16+q:'decode' for q in near})
 for wall,count,code in itertools.product((0,1),(0,1,3),(0,129,255)):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,b);ds=0x7000;buffer=0x7000;allocated=0x9000;handle=7;payload=0x12345678;header=bytearray(90);header[2]=count;header[3]=1;dg=bytearray(0xe030);expected=bytearray(dg);expected[buffer:buffer+90]=header
  for n in range(count):expected[allocated+10*n:allocated+10*(n+1)]=bytes((code+n+j+wall)&255 for j in range(10))
  u.mem_write(ds*16,bytes(dg));u.mem_write(ds*16+0xf000,struct.pack('<9H',0x100,0x5000,handle,payload&65535,payload>>16,code,8,buffer,wall))
  for q,value in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(q,value)
  calls=[];decoder_args=[];done=[]
  def hook(emu,address,size,data):
   if address==0x50100:done.append(True);emu.emu_stop();return
   if address not in targets:return
   name=targets[address];assert name!='error';sp=emu.reg_read(UC_X86_REG_SP)
   def get(n):return struct.unpack('<'+'H'*n,bytes(emu.mem_read(ds*16+sp+4,2*n)))
   calls.append(name)
   if name=='seek':
    seek=0x800+90*(code+(0 if wall else 256)) if calls.count('seek')==1 else payload;assert get(4)==(handle,seek&65535,seek>>16,0);emu.reg_write(UC_X86_REG_AX,seek&65535);emu.reg_write(UC_X86_REG_DX,seek>>16)
   elif name=='read':assert get(3)==(handle,buffer,90);emu.mem_write(ds*16+buffer,bytes(header));emu.reg_write(UC_X86_REG_AX,90)
   elif name=='allocate':assert get(1)==(10*count,);emu.reg_write(UC_X86_REG_AX,allocated)
   else:
    n=len(decoder_args);want=(handle,allocated+10*n,code,n) if wall and label=='10' else (handle,allocated+10*n) if label=='10' else (handle,allocated+10*n,code,n,wall|((0x56 if n==0 else 0)<<8));assert get(len(want))==want
    selected=near[0] if wall else near[-1];assert address==cs*16+selected;decoder_args.append(want);emu.mem_write(ds*16+allocated+10*n,bytes((code+n+j+wall)&255 for j in range(10)));emu.reg_write(UC_X86_REG_AX,0xd2e3)
   ret,rcs=struct.unpack('<HH',bytes(emu.mem_read(ds*16+sp,4)));emu.reg_write(UC_X86_REG_SP,sp+4);emu.reg_write(UC_X86_REG_CS,rcs);emu.reg_write(UC_X86_REG_IP,ret)
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+ip,0xfffff,count=1000);assert done and len(decoder_args)==count and calls==['seek','read','allocate','seek']+['decode']*count
  assert bytes(u.mem_read(ds*16,len(dg)))==expected and u.reg_read(UC_X86_REG_AX)==allocated and u.reg_read(UC_X86_REG_SP)==0xf004
  rows.append(dict(version=label,wall=wall,count=count,code=code,decoder_target_IP=(near[0] if wall else near[-1]),decoder_argument_WORDs=(4 if wall else 2) if label=='10' else 5,status='PASS'))
 inputs.extend(dict(path=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest()) for q in (p,ipath))
with (out/'decoder_dispatch_cases.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(cases=len(rows),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='whole original wrapper load0 with controlled IO/allocation/decoder results; DOS10 uses separate4WORDwall/2WORDobject decoders, later5WORDunified decoder; caller ABI/loop verified, no decoder output equivalence/native/Win16 parity',files=inputs+[dict(path=str(q.resolve()),sha256=hashlib.sha256(q.read_bytes()).hexdigest()) for q in (Path(__file__),out/'function_comparisons.csv')])
(out/'decoder_dispatch_summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
