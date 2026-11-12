"""python replay_door_state4_versions.py EMULATOR COMPARISON_DIR
Original unrelocated DOS images at load0, controlled DS=SS7000, no sound path.
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
emulator,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(emulator.resolve()))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');rows=[];files=[]
for label in ('10','11','12','15','17','18','19','20'):
 folder=root/('N3D-'+label);p=folder/'unpacked_image.bin';b=p.read_bytes();inv=json.loads((folder/'instructions.json').read_text(encoding='utf-8'));owned=[x for x in inv if '0000:0598' in x['owners']]
 tests=[bytes.fromhex(x['bytes']) for x in owned if x['bytes'].startswith('f687') and x['bytes'].endswith('08')];assert len(tests)==2;flagbase=struct.unpack_from('<H',tests[0],2)[0];seg=struct.unpack_from('<H',b,5)[0];assert b[4]==0xb8
 assert b[0x59e:0x5a0]==bytes.fromhex('803e');gateoff=struct.unpack_from('<H',b,0x5a0)[0]
 for gate in (0,1):
  for orientation in (0,2):
   for state in (1,4):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,b);ds=0x7000;world=bytearray(0x573e);dg=bytearray(0xe030);struct.pack_into('<H',world,0,3);step=128 if orientation==2 else 2
    for n,cell in enumerate((0x5000,0x5000+step,0x5000-step)):
     q=0x3076+18*n;desc=0x7100+32*n;struct.pack_into('<HHHHH',world,q,desc,desc+0x80,cell,seg,state if n==0 else 0x1234+n);world[cell]=0x71;dg[desc+6]=0x40;dg[desc+7]=orientation
    dg[gateoff]=gate;dg[flagbase+0x71]=8;pred=bytearray(world)
    if not gate and (state!=4 or label in ('10','11','12')):
     new=2 if state==1 else 4
     for n in range(3):struct.pack_into('<H',pred,0x3076+18*n+8,new)
    u.mem_write(seg*16,bytes(world));u.mem_write(ds*16,bytes(dg));u.mem_write(ds*16+0xf000,struct.pack('<5H',0x100,0x5000,0x3076,seg,0xe300))
    for reg,value in [(UC_X86_REG_CS,0),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,value)
    done=[]
    def hook(emu,address,size,data):
     if address==0x50100:done.append(True);emu.emu_stop();return
     assert address<0x704,'unexpected external callee'
    u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x598,0xfffff,count=5000);assert done
    assert bytes(u.mem_read(seg*16,len(world)))==pred and bytes(u.mem_read(ds*16,len(dg)))==dg
    assert u.reg_read(UC_X86_REG_SP)==0xf004 and u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SS)==ds
    rows.append(dict(version=label,load=0,DS=ds,gate=gate,orientation=orientation,source_state=state,neighbor_state_after=struct.unpack_from('<H',pred,0x3088+8)[0],state4_early_exit_present=label not in ('10','11','12'),status='PASS'))
 files.extend(dict(path=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest()) for q in (p,folder/'instructions.json'))
with (out/'state4_cross_version_cases.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary=dict(cases=len(rows),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='controlled original load0 DOS images; arbitrary DS=SS7000 with version-specific gate/tileflag bindings and original lookup mapsegment; state4 neighbor propagation exists10/11/12, earlyexit15/17/18/19/20; normal initialization/natural calls/Win16 not proved',files=files+[dict(path=str(Path(__file__).resolve()),sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())])
(out/'state4_cross_version_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
