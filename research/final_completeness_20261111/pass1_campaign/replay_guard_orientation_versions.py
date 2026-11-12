"""python replay_guard_orientation_versions.py EMULATOR COMPARISON_DIR
Original load0 frame updater/view helper, controlled DS=SS9000 and valid synthetic descriptor.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
emulator,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(emulator.resolve()))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');cmp=list(csv.DictReader((out/'function_comparisons.csv').open()));cases=[];files=[]
for label in ('10','11','12','15','17','18','19','20'):
 p=root/('N3D-'+label)/'unpacked_image.bin';b=p.read_bytes();ipath=p.with_name('instructions.json');inv=json.loads(ipath.read_text(encoding='utf-8'));r=next(x for x in cmp if x['version']==label and x['function']=='guard_relative_frame_update');cs,ip=int(r['cs']),int(r['ip']);owner='%04X:%04X'%(cs,ip);code=[x for x in inv if owner in x['owners']]
 globals_=[struct.unpack_from('<H',bytes.fromhex(x['bytes']),2)[0] for x in code if x['bytes'].startswith('8b9f')];assert globals_ and len(set(globals_))==1;classbase=globals_[0]
 h=next(x for x in cmp if x['version']==label and x['function']=='actor_to_player_view_octant');howner='%04X:%04X'%(int(h['cs']),int(h['ip']));hc=[x for x in inv if howner in x['owners']];player0=next(struct.unpack_from('<H',bytes.fromhex(x['bytes']),1)[0] for x in hc if x['bytes'].startswith('a1'));player1=next(struct.unpack_from('<H',bytes.fromhex(x['bytes']),2)[0] for x in hc if x['bytes'].startswith('8b0e'))
 for flag,mode,strategy,force,equal in itertools.product((0,1),(6,8),(0,2),(0,1),(0,1)):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,b);ds=0x9000;seg=0x7000;g=0x264e;a=6;world=bytearray(0x573e);dg=bytearray(0xe030);world[g+10]=strategy;world[g+11]=mode;world[g+15]=flag;world[g+17]=2;struct.pack_into('<HH',world,a+16,1000,2000);struct.pack_into('<H',dg,player0,1100);struct.pack_into('<H',dg,player1,2200);struct.pack_into('<H',dg,classbase,0x7000);relative=3 if flag else 2;world[g+18]=relative if equal else relative^7
  for row in range(3):
   for col in range(8):struct.pack_into('<H',dg,0x7000+4+16*row+2*col,0x1000+row*0x111+col*17)
  pred=bytearray(world);row=1 if mode==8 else 2 if label=='10' or strategy!=2 else 0;selected=0x1000+row*0x111+relative*17
  if not equal or force:pred[g+18]=relative;struct.pack_into('<H',pred,g,selected);pred[a+3]=selected&255
  u.mem_write(seg*16,bytes(world));u.mem_write(ds*16,bytes(dg));u.mem_write(ds*16+0xf000,struct.pack('<7H',0x100,0x5000,g,seg,a,seg,force))
  for q,value in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(q,value)
  done=[]
  def hook(emu,address,size,data):
   if address==0x50100:done.append(True);emu.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+ip,0xfffff,count=1000);assert done
  assert bytes(u.mem_read(seg*16,len(world)))==pred and bytes(u.mem_read(ds*16,len(dg)))==dg,(label,flag,mode,strategy,force,equal)
  assert u.reg_read(UC_X86_REG_SP)==0xf004 and u.reg_read(UC_X86_REG_DS)==u.reg_read(UC_X86_REG_SS)==ds
  cases.append(dict(version=label,view_flag=flag,mode=mode,strategy=strategy,force=force,previous_relative_equal=equal,selected_row=row,selection_executed=not equal or bool(force),result_frame_WORD=struct.unpack_from('<H',pred,g)[0],status='PASS'))
 files.extend(dict(path=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest()) for q in (p,ipath))
with (out/'version_replay_cases.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(cases[0]));w.writeheader();w.writerows(cases)
s=dict(cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='original load0 frame+view functions, DS=SS9000 valid synthetic descriptor; DOS10mode6alwaysrow24h, laterstrategy2row04h; gates/force/equality/mode8controls; no natural old-version/Win16 parity',files=files+[dict(path=str(q.resolve()),sha256=hashlib.sha256(q.read_bytes()).hexdigest()) for q in (Path(__file__),out/'function_comparisons.csv')])
(out/'version_replay_summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
