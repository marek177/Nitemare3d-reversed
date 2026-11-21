"""Exhaustive synthetic16-bit domain test of original0000:01E0 predicate."""
import argparse,sys,hashlib,json,struct
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('unpacked_exe',type=Path);ap.add_argument('--unicorn-path',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
if args.unicorn_path:sys.path.insert(0,str(args.unicorn_path))
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
raw=args.unpacked_exe.read_bytes();source=hashlib.sha256(raw).hexdigest();assert source=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';image=raw[int.from_bytes(raw[8:10],'little')*16:];code=image[0x1e0:0x1fc]
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x1e0,code);SS=0x2771;OBJ=0x5000;STOP=0x60000;writes=[]
def stop(mu,address,size,user):
 if address==STOP:mu.emu_stop()
def write(mu,access,address,size,value,user):writes.append((address,size,value))
u.hook_add(UC_HOOK_CODE,stop);u.hook_add(UC_HOOK_MEM_WRITE,write);digest=hashlib.sha256();accepted=[]
for state in range(65536):
 initial_flags=0x202|(0x400 if state&1 else 0)
 for reg,val in [(UC_X86_REG_AX,0xa5ff),(UC_X86_REG_BX,0x1111),(UC_X86_REG_CX,0x2222),(UC_X86_REG_DX,0x3333),(UC_X86_REG_SI,0x4444),(UC_X86_REG_DI,0x5555),(UC_X86_REG_BP,0x6666),(UC_X86_REG_CS,0),(UC_X86_REG_DS,SS),(UC_X86_REG_SS,SS),(UC_X86_REG_ES,SS),(UC_X86_REG_SP,0x8000),(UC_X86_REG_EFLAGS,initial_flags)]:u.reg_write(reg,val)
 u.mem_write(SS*16+0x8000,struct.pack('<HHHH',0,0x6000,0x100,OBJ));u.mem_write(OBJ*16+0x108,struct.pack('<H',state));writes.clear();u.emu_start(0x1e0,0xfffff,count=40)
 ax=u.reg_read(UC_X86_REG_AX);flags=u.reg_read(UC_X86_REG_EFLAGS);want=int(state in (0,4));assert ax==0xa500+want
 assert u.reg_read(UC_X86_REG_CS)==0x6000 and u.reg_read(UC_X86_REG_IP)==0 and u.reg_read(UC_X86_REG_SP)==0x8004
 for reg,val in [(UC_X86_REG_BX,0x100),(UC_X86_REG_ES,OBJ),(UC_X86_REG_CX,state),(UC_X86_REG_DX,0x3333),(UC_X86_REG_SI,0x4444),(UC_X86_REG_DI,0x5555),(UC_X86_REG_BP,0x6666),(UC_X86_REG_DS,SS),(UC_X86_REG_SS,SS)]:assert u.reg_read(reg)==val
 assert flags&0x8c5==0x44 and flags&0x600==initial_flags&0x600
 assert writes==[(SS*16+0x7ffe,2,0x6666)]
 digest.update(struct.pack('<HHH',state,ax,flags&0xec5))
 if want:accepted.append(state)
v={'status':'SYNTHETIC_CPU_ONLY','source_sha256':source,'predicate':'0000:01E0','code_span_sha256':hashlib.sha256(code).hexdigest(),'cases':65536,'accepted_states':accepted,'returned_AL':'1 iff word+8 in{0,4}; otherwise0','AH_preserved_fixture':'A5','clobbers_verified':['BX=argument.offset','ES=argument.segment','CX=record.word+8','AL'],'preserved_verified':['DX','SI','DI','BP','DS','SS','AH fixture','IF','DF both values'],'flags_on_all_local_returns':'CF0 PF1 ZF1 SF0 OF0; AF excluded','stack':'FAR RETF consumes4 bytes; caller retains4-byte argument; one BP push write only','case_digest_sha256':digest.hexdigest(),'unicorn':unicorn.__version__,'scope':'Original predicate instructions only, valid FAR object and stack, no IRQs, no arbitrary alternate entry; not native game execution or all caller ABI proof'}
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v))
