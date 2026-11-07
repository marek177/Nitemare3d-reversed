"""Isolated CPU checks of private original helper bytes on an empty grid."""
import argparse,sys,hashlib,json,struct
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('unpacked_exe',type=Path);ap.add_argument('--unicorn-path',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
if args.unicorn_path:sys.path.insert(0,str(args.unicorn_path))
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
raw=args.unpacked_exe.read_bytes();assert hashlib.sha256(raw).hexdigest()=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';image=raw[int.from_bytes(raw[8:10],'little')*16:]
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);CS=0x4c7;SS=0x2771;ACT=0x5000;OBJ=0x5100;MAP=0x21fd;STOP=0x60000
for s,lo,hi in [(CS,0x6d2,0x7d2),(0xaea,0xcc0,0xe22)]:u.mem_write(s*16+lo,image[s*16+lo:s*16+hi])
u.mem_write(SS*16+0x2568,struct.pack('<H',MAP))
def stop(mu,address,size,user):
    if address==STOP:mu.emu_stop()
u.hook_add(UC_HOOK_CODE,stop)
def expected(dx,dy,direction,skip):
    if abs(dx)>8 or abs(dy)>8:return 0
    if not skip:
        cone=sum(1<<d for d in {(direction-1)&7,direction,(direction+1)&7})
        mask=(0x66 if abs(dx)>=abs(dy) else 0x99)&(0x3c if dy>=0 else 0xc3)&(0x0f if dx>=0 else 0xf0)
        if not cone&mask:return 0
    return int(dx!=0 or dy!=0)
def run(dx,dy,direction,skip):
    for reg,val in [(UC_X86_REG_AX,0),(UC_X86_REG_BX,0),(UC_X86_REG_CX,0),(UC_X86_REG_DX,0),(UC_X86_REG_SI,0x1234),(UC_X86_REG_DI,0x5678),(UC_X86_REG_BP,0x7788),(UC_X86_REG_CS,CS),(UC_X86_REG_DS,SS),(UC_X86_REG_SS,SS),(UC_X86_REG_ES,SS),(UC_X86_REG_SP,0x8000),(UC_X86_REG_EFLAGS,0x202)]:u.reg_write(reg,val)
    u.mem_write(ACT*16+0x111,bytes([direction]));u.mem_write(OBJ*16+0x110,struct.pack('<hh',32*64+32,32*64+32));u.mem_write(SS*16+0x415e,struct.pack('<hh',32+dx,32+dy))
    frame=struct.pack('<10H',0,0x6000,0x100,ACT,0x100,OBJ,0,skip,0,0);u.mem_write(SS*16+0x8000,frame)
    u.emu_start(CS*16+0x6d2,0,count=3000)
    assert u.reg_read(UC_X86_REG_CS)==0x6000 and u.reg_read(UC_X86_REG_IP)==0 and u.reg_read(UC_X86_REG_SP)==0x8004
    assert u.reg_read(UC_X86_REG_SI)==0x1234 and u.reg_read(UC_X86_REG_DI)==0x5678 and u.reg_read(UC_X86_REG_BP)==0x7788 and u.reg_read(UC_X86_REG_DS)==SS
    return u.reg_read(UC_X86_REG_AX)&255
cases=0
for dx in range(-9,10):
    for dy in range(-9,10):
        for direction in range(8):
            got=run(dx,dy,direction,0);want=expected(dx,dy,direction,0);assert got==want,(dx,dy,direction,got,want);cases+=1
        got=run(dx,dy,0,1);want=expected(dx,dy,0,1);assert got==want,(dx,dy,'skip',got,want);cases+=1
v={'status':'SYNTHETIC_CPU_ONLY','source_sha256':hashlib.sha256(raw).hexdigest(),'unicorn':unicorn.__version__,'cases':cases,'empty_grid_range_direction_and_nonzero_target_verified':True,'SI_DI_BP_DS_and_FAR_stack_checked':True,'scope':'Original helper06D2 and gridCC0 instruction bytes; empty wall/object flag tables, valid map coordinates, no IRQs; external door callbacks and nonempty-grid domains are not tested; not original-game runtime coverage'}
args.output.write_text(json.dumps(v,indent=2));print(json.dumps(v))
