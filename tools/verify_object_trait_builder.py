"""Original object-trait builder, all input classes and initial local byte values."""
import sys,json,struct,hashlib,base64
from pathlib import Path
sys.path.insert(0,'C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20/work/deps')
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
R=Path(__file__).resolve().parents[1];O=R/'outputs/native_trait_20261106';raw=Path('C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20-3/work/decoded/nite3d20/output.000.exe').read_bytes();H=lambda b:hashlib.sha256(b).hexdigest();assert H(raw)=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';im=raw[int.from_bytes(raw[8:10],'little')*16:]
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);CS=0xf7;DS=0x2771;u.mem_write(CS*16+0x250,im[CS*16+0x250:CS*16+0x2f2]);u.mem_write(DS*16+0xd40e,bytes(range(256)));u.hook_add(UC_HOOK_CODE,lambda mu,a,s,d:mu.emu_stop() if a==0x60000 else None)
def model(c,initial):return (initial&128)|(1 if 6<=c<=0x3d else 0)|(2 if 8<=c<=0x2d else 0)|(4 if 0x2f<=c<=0x3d else 0)|(8 if 8<=c<=0x25 else 0)|(32 if c==0x2a else 0)|(64 if c==4 else 0)
for initial in range(256):
 u.mem_write(DS*16+0xd10c,b'\xa5'*256);u.mem_write(DS*16+0x8000,struct.pack('<HH',0,0x6000));u.mem_write(DS*16+0x7ffd,bytes([initial]))
 for reg,val in [(UC_X86_REG_AX,0xaaaa),(UC_X86_REG_BX,0xbbbb),(UC_X86_REG_CX,0xcccc),(UC_X86_REG_DX,0xdddd),(UC_X86_REG_SI,0x1234),(UC_X86_REG_DI,0x5678),(UC_X86_REG_BP,0x7788),(UC_X86_REG_CS,CS),(UC_X86_REG_DS,DS),(UC_X86_REG_SS,DS),(UC_X86_REG_ES,DS),(UC_X86_REG_SP,0x8000),(UC_X86_REG_EFLAGS,0x602)]:u.reg_write(reg,val)
 u.emu_start(CS*16+0x250,0xfffff,count=20000)
 assert (u.reg_read(UC_X86_REG_CS),u.reg_read(UC_X86_REG_IP),u.reg_read(UC_X86_REG_SP))==(0x6000,0,0x8004)
 for reg,val in [(UC_X86_REG_SI,0x1234),(UC_X86_REG_DI,0x5678),(UC_X86_REG_BP,0x7788),(UC_X86_REG_DS,DS),(UC_X86_REG_BX,0xbbbb),(UC_X86_REG_CX,0xcccc)]:assert u.reg_read(reg)==val
 assert bytes(u.mem_read(DS*16+0xd10c,256))==bytes(model(c,initial) for c in range(256)),initial
 assert u.reg_read(UC_X86_REG_AX)==0xaa00|model(255,initial) and u.reg_read(UC_X86_REG_DX)==255
 assert u.reg_read(UC_X86_REG_EFLAGS)&0x8d5==0x44 and u.reg_read(UC_X86_REG_EFLAGS)&0x400
cap=json.loads((R/'outputs/evidence/runtime/rng_level5_n_20261106/wall_object_traits_capture.json').read_text());native=base64.b64decode(cap['traits']['result']['data_base64'])[256:512];m=(R/'work/runtime/game_rng_targets_i_20261031/MAP.1').read_bytes();assert all((x&127)==model(c,0) for x,c in zip(native,m[258:514]));high={x&128 for x in native};assert len(high)==1
v={'status':'SYNTHETIC_ORIGINAL_CPU_AND_RUNTIME_TABLE_VALUE_JOIN','source_sha256':H(raw),'function':'00F7:0250','CPU_invocations':256,'class_initial_byte_pairs':65536,'all256_destination_bytes_checked_per_invocation':True,'preserved_SI_DI_BP_DS_BX_CX_and_FAR_stack_checked':True,'class_mapping':{'bit0':'6<=class<=3Dh','bit1':'8<=class<=2Dh','bit2':'2Fh<=class<=3Dh','bit3':'8<=class<=25h','bit4':'cleared','bit5':'class2Ah','bit6':'class4','bit7':'preserved from uninitialized local byteSS:[entrySP-3]; same for all256 outputs'},'native_episode1_table_low7_matches_original_header':True,'native_bit7_value':next(iter(high)),'scope':'Canonical entry, separate nonaliasing source/destination/stack fixture. This isolated CPU test does not trace native entry/exit; separate native evidence exists; global alternate entries, aliases, bit7 downstream consumers and IRQ effects remain open. Native table-value join does not prove native builder invocation.'};(O/'object_trait_builder_validation.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v))

