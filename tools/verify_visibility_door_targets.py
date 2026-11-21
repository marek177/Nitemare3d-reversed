"""Resolve relocated segment-zero direct calls and test bounded wall states."""
import runpy,sys,json,struct,hashlib,argparse
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('unpacked_exe',type=Path);ap.add_argument('--unicorn-path',type=Path);ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--helper',type=Path,default=Path(__file__).with_name('verify_actor_visibility_cpu.py'));args=ap.parse_args()
O=args.output_dir;O.mkdir(parents=True,exist_ok=True)
sys.argv=['verify_actor_visibility_cpu.py',str(args.unpacked_exe),'--output',str(O/'empty_grid_revalidation.json')]
if args.unicorn_path:sys.argv+=['--unicorn-path',str(args.unicorn_path)]
d=runpy.run_path(str(args.helper));u=d['u'];image=d['image'];raw=d['raw'];run=d['run'];SS=d['SS'];MAP=d['MAP']
class InteriorZeroAddressCPU:
 # Unicorn's previous until=0 would stop before the legitimate target0000:0000.
 # Preserve the existing explicit FAR-return hook; choose an unused end address.
 def __getattr__(self,name):return getattr(u,name)
 def emu_start(self,begin,until,**kw):return u.emu_start(begin,0xfffff,**kw)
run.__globals__['u']=InteriorZeroAddressCPU()
n,=struct.unpack_from('<H',raw,6);ro,=struct.unpack_from('<H',raw,24);rel=[struct.unpack_from('<HH',raw,ro+4*i) for i in range(n)];linear={s*16+o for o,s in rel};calls=[]
for pc,target in [(0xdce,0),(0xdd8,0x1e0)]:
 off=0xaea*16+pc;code=image[off:off+5];assert code==b'\x9a'+struct.pack('<HH',target,0);assert off+3 in linear
 calls.append({'site':f'0AEA:{pc:04X}','direct_target':f'0000:{target:04X}','segment_word_relocation_linear':off+3,'runtime_target_rule':f'(MZ_loadbase+0000):{target:04X}','indirect':False})
for lo,hi in [(0,0x52),(0x1e0,0x1fc)]:u.mem_write(lo,image[lo:hi])
# A wall at (33,32), strictly between start(32,32) and end(34,32).
tile=0x373e+2*(32*64+33);u.mem_write(MAP*16+tile,b'\x01');u.mem_write(MAP*16,struct.pack('<H',1));u.mem_write(MAP*16+0x3076+4,struct.pack('<HH',tile,MAP))
rows=[]
for trait in (0,2,6,10,14):
 for state in (0,1,2,3,4,5,0xffff):
  u.mem_write(SS*16+0xd00d,bytes([trait]));u.mem_write(MAP*16+0x3076+8,struct.pack('<H',state));got=run(2,0,0,1)
  want=0 if trait&2 and (trait&4 or trait&8 and state not in (0,4)) else 1
  assert got==want,(trait,state,got,want);rows.append({'wall_traits':trait,'record_state':state,'AL':got})
out={'status':'VERIFIED_STATIC_RELOCATION_AND_SYNTHETIC_CPU_ONLY','source_sha256':hashlib.sha256(raw).hexdigest(),'relocation_entries':n,'resolved_calls':calls,'lookup_contract':'0000:0000 searches up to signed count DS(21FD):0000 records at3076 stride18 for FAR tile pointer at+4/+6; returns matching record DX:AX. Missing-record branch calls0FBA:000C with42h; not executed in this fixture.','predicate_contract':'0000:01E0 returns AL1 exactly for record word+8 equal0 or4, otherwiseAL0.','cases':rows,'case_count':len(rows),'preserved_registers_and_FAR_stack_checked':True,'scope':'One interior tile, one matching lookup record, skip-direction flag. Original helper, grid, lookup and predicate bytes execute in Unicorn. No native-game target invocation, absent-record behavior, all door lifecycle or global code-write closure is claimed.','correction':'The segment-zero call operands are direct MZ-relocated calls, not unresolved indirect callbacks or absent targets.'}
(O/'visibility_direct_targets.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({'calls':calls,'cases':len(rows),'status':out['status']}))
