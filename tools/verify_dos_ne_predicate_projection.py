"""Differential original-byte CPU test under an explicit record-field projection."""
import argparse,sys,json,hashlib,struct
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('dos_exe',type=Path);ap.add_argument('ne_exe',type=Path);ap.add_argument('--mapping',type=Path,required=True);ap.add_argument('--binary-id',default='historical_11');ap.add_argument('--unicorn-path',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
if a.unicorn_path:sys.path.insert(0,str(a.unicorn_path))
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
d=a.dos_exe.read_bytes();assert hashlib.sha256(d).hexdigest()=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';rec=next(x for x in json.loads(a.mapping.read_text())['records'] if x['binary_id']==a.binary_id);n=a.ne_exe.read_bytes();assert hashlib.sha256(n).hexdigest()==rec['source_sha256'];dc=d[int.from_bytes(d[8:10],'little')*16+0x1e0:][:28];nc=n[rec['predicate_file_offset']:][:28];assert hashlib.sha256(nc).hexdigest()==rec['predicate_body_sha256'];projected=bytearray(dc);projected[9]=12;assert nc==projected
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x1000,dc);u.mem_write(0x2000,nc);SS=0x2771
def stop(mu,address,size,user):
 if address==0x60000:mu.emu_stop()
u.hook_add(UC_HOOK_CODE,stop);digest=hashlib.sha256()
def run(entry,obj,field,state,initial_flags):
 for r,v in [(UC_X86_REG_AX,0xa5ff),(UC_X86_REG_BX,0x1111),(UC_X86_REG_CX,0x2222),(UC_X86_REG_DX,0x3333),(UC_X86_REG_SI,0x4444),(UC_X86_REG_DI,0x5555),(UC_X86_REG_BP,0x6666),(UC_X86_REG_CS,0),(UC_X86_REG_DS,SS),(UC_X86_REG_SS,SS),(UC_X86_REG_ES,SS),(UC_X86_REG_SP,0x8000),(UC_X86_REG_EFLAGS,initial_flags)]:u.reg_write(r,v)
 u.mem_write(SS*16+0x8000,struct.pack('<HHHH',0,0x6000,0x100,obj));u.mem_write(obj*16+0x100+field,struct.pack('<H',state));u.emu_start(entry,0xfffff,count=40)
 assert u.reg_read(UC_X86_REG_CS)==0x6000 and u.reg_read(UC_X86_REG_IP)==0 and u.reg_read(UC_X86_REG_SP)==0x8004
 assert u.reg_read(UC_X86_REG_ES)==obj and u.reg_read(UC_X86_REG_BX)==0x100
 for r,v in [(UC_X86_REG_DX,0x3333),(UC_X86_REG_SI,0x4444),(UC_X86_REG_DI,0x5555),(UC_X86_REG_BP,0x6666),(UC_X86_REG_DS,SS),(UC_X86_REG_SS,SS)]:assert u.reg_read(r)==v
 return u.reg_read(UC_X86_REG_AX),u.reg_read(UC_X86_REG_CX),u.reg_read(UC_X86_REG_EFLAGS)&0xec5
for state in range(65536):
 flags=0x202|(0x400 if state&1 else 0);x=run(0x1000,0x5000,8,state,flags);y=run(0x2000,0x5100,12,state,flags);assert x==y and x[0]==0xa500+int(state in (0,4)) and x[1]==state and x[2]&0x8c5==0x44;digest.update(struct.pack('<4H',state,*x))
# Equal raw fields without the projection can yield different outputs.
u.mem_write(0x5100*16+0x108,struct.pack('<H',0));unprojected=run(0x2000,0x5100,12,1,0x202);dos_same=run(0x1000,0x5000,8,0,0x202);assert unprojected[0]&255==0 and dos_same[0]&255==1
v={'evidence_status':'VERIFIED_DIFFERENTIAL','test_kind':'SYNTHETIC_ORIGINAL_BYTE_CPU_ONLY','DOS_sha256':hashlib.sha256(d).hexdigest(),'NE_sha256':hashlib.sha256(n).hexdigest(),'NE_binary_id':a.binary_id,'paired_cases':65536,'projection':'DOS record.word+8 equals NE record.word+12; ES normalized to each argument segment','AX_CX_defined_FLAGS_and_FAR_return_match':True,'preserved_registers_checked':True,'AH_fixture':'A5','IF_DF_fixtures':'IF1, DF alternating by state','case_digest_sha256':digest.hexdigest(),'unprojected_layout_counterexample':{'NE_word8':0,'NE_word12':1,'NE_AL':0},'unicorn':unicorn.__version__,'scope':'Two isolated original predicate bodies in a valid real-mode CPU fixture; not a running Win16/NE loader, protected-mode selector/IRQ behavior, whole-record isomorphism or whole-game/remake parity'}
a.output.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v))
