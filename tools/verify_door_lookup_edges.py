"""Synthetic lookup boundary cases; stop before external missing-key callee."""
import argparse,sys,json,hashlib,struct
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('unpacked_exe',type=Path);ap.add_argument('--unicorn-path',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
if args.unicorn_path:sys.path.insert(0,str(args.unicorn_path))
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
raw=args.unpacked_exe.read_bytes();assert hashlib.sha256(raw).hexdigest()=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';image=raw[int.from_bytes(raw[8:10],'little')*16:]
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,image[:0x52]);SS=0x2771;A=0x21fd;STOP=0x60000;ERROR=0xfba*16+0xc;stops=[]
def hook(mu,address,size,user):
 if address in (STOP,ERROR):stops.append(address);mu.emu_stop()
u.hook_add(UC_HOOK_CODE,hook)
cases=[('count_zero',0,[],None),('negative_one',-1,[],None),('negative_min',-32768,[],None),('one_missing',1,[(1,2)],None),('one_found',1,[(0x1234,0x4567)],0),('second_found',2,[(1,2),(0x1234,0x4567)],1),('first_of_two',2,[(0x1234,0x4567),(0x1234,0x4567)],0),('same_physical_alias',1,[(0x1244,0x4566)],None)]
rows=[]
for name,count,keys,found in cases:
 for reg,val in [(UC_X86_REG_AX,0xa5a5),(UC_X86_REG_BX,0x1111),(UC_X86_REG_CX,0x2222),(UC_X86_REG_DX,0x3333),(UC_X86_REG_SI,0x4444),(UC_X86_REG_DI,0xabcd),(UC_X86_REG_BP,0x5555),(UC_X86_REG_CS,0),(UC_X86_REG_DS,0x4000),(UC_X86_REG_SS,SS),(UC_X86_REG_ES,0x3333),(UC_X86_REG_SP,0x8000),(UC_X86_REG_EFLAGS,0x202)]:u.reg_write(reg,val)
 u.mem_write(SS*16+0x8000,struct.pack('<HHHH',0,0x6000,0x1234,0x4567));u.mem_write(A*16,struct.pack('<h',count));u.mem_write(A*16+0x3076,bytes(36))
 for i,(off,seg) in enumerate(keys):u.mem_write(A*16+0x3076+18*i+4,struct.pack('<HH',off,seg))
 stops.clear();u.emu_start(0,0xfffff,count=1000);assert len(stops)==1;assert u.reg_read(UC_X86_REG_DS)==SS and u.reg_read(UC_X86_REG_ES)==A and u.reg_read(UC_X86_REG_SI)==0x4444
 if found is not None:
  want=0x3076+18*found;assert stops[0]==STOP;assert u.reg_read(UC_X86_REG_AX)==want and u.reg_read(UC_X86_REG_DX)==A and u.reg_read(UC_X86_REG_BX)==want and u.reg_read(UC_X86_REG_CX)==found
  assert u.reg_read(UC_X86_REG_DI)==0xabcd and u.reg_read(UC_X86_REG_BP)==0x5555 and u.reg_read(UC_X86_REG_SP)==0x8004
 else:
  assert stops[0]==ERROR and u.reg_read(UC_X86_REG_SP)==0x7ff6;assert bytes(u.mem_read(SS*16+0x7ff6,6))==struct.pack('<HHH',0x4c,0,0x42)
  assert u.reg_read(UC_X86_REG_CX)==max(0,count)
 if name=='same_physical_alias':assert 0x4567*16+0x1234==0x4566*16+0x1244
 rows.append({'name':name,'signed_count':count,'found_record_index':found,'outcome':'returned_FAR_record' if found is not None else 'entered_external_callee_0FBA000C_without_executing_it','DS_equals_SS':True})
v={'evidence_status':'VERIFIED_STATIC','test_kind':'SYNTHETIC_CPU_ONLY','source_sha256':hashlib.sha256(raw).hexdigest(),'function':'0000:0000','cases':rows,'case_count':len(rows),'exact_FAR_representation_comparison_confirmed':True,'error_stack_argument':'near offset0042; return0000:004C','scope':'Stable counts0/negative/1/2, valid stack and tiny array. No error-callee instructions executed, no count mutation, large-count offset wrap, IRQ or native-game invocation proof.','unicorn':unicorn.__version__}
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v))
