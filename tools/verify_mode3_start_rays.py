"""Original helper on original level6 cells and captured episode1 trait tables."""
import json,base64,struct,hashlib,sys
from pathlib import Path
sys.path.insert(0,'C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20/work/deps')
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
R=Path(__file__).resolve().parents[1];O=R/'outputs/mode3_start_20261106';D=R/'outputs/evidence/runtime/rng_level5_n_20261106';raw=Path('C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20-3/work/decoded/nite3d20/output.000.exe').read_bytes();H=lambda b:hashlib.sha256(b).hexdigest();assert H(raw)=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';im=raw[int.from_bytes(raw[8:10],'little')*16:];cap=json.loads((D/'wall_object_traits_capture.json').read_text());traits=base64.b64decode(cap['traits']['result']['data_base64']);assert len(traits)==512 and H(traits)==cap['traits']['result']['sha256'];assert base64.b64decode(cap['episode_level']['result']['data_base64'])==struct.pack('<HH',1,10)
rpc={v['response']['id']:v for p in D.glob('rpc_*.json') for v in [json.loads(p.read_text())]}
for x in cap.values():assert rpc[x['id']]['response']==x and rpc[x['id']]['server_pid']==23808
q=rpc[cap['traits']['id']]['request']['params'];assert q['length']==512 and int(q['address']['segment'],16)==0x2f94 and int(q['address']['offset'],16)==0xd00c
map1=(R/'work/runtime/game_rng_targets_i_20261031/MAP.1').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);SS=0x2771;ACT=0x5000;OBJ=0x5100;MAP=0x21fd;CS=0x4c7
for s,a,b in [(CS,0x6d2,0x7d2),(0xaea,0xcc0,0xe22)]:u.mem_write(s*16+a,im[s*16+a:s*16+b])
u.mem_write(SS*16+0xd00c,traits);u.mem_write(SS*16+0x2568,struct.pack('<H',MAP));state={};visited=[]
def hook(mu,a,size,data):
 if a==0x60000:state['return']=True;mu.emu_stop()
 if a==0:state['door_lookup_unmodeled']=True;mu.emu_stop()
 if a==0xaea*16+0xd95:visited.append((mu.reg_read(UC_X86_REG_SI),mu.reg_read(UC_X86_REG_DI)))
u.hook_add(UC_HOOK_CODE,hook);results=[]
for c in json.loads((O/'mode3_start_candidates.json').read_text())['pre_ray_candidates']:
 state.clear();visited.clear();ep=c['episode'];assert ep==1;level=c['display_level']-1;u.mem_write(MAP*16+0x373e,map1[514+8192*level:514+8192*(level+1)]);x,y=c['tile'];px,py=c['selected_start_gate']['start']['tile'];u.mem_write(ACT*16+0x111,bytes([c['direction_from_asset_encoding']]));u.mem_write(OBJ*16+0x110,struct.pack('<hh',x*64+32,y*64+32));u.mem_write(SS*16+0x415e,struct.pack('<hh',px,py));u.mem_write(SS*16+0x8000,struct.pack('<10H',0,0x6000,0x100,ACT,0x100,OBJ,0,0,0,0))
 for reg,val in [(UC_X86_REG_AX,0),(UC_X86_REG_BX,0),(UC_X86_REG_CX,0),(UC_X86_REG_DX,0),(UC_X86_REG_SI,0x1234),(UC_X86_REG_DI,0x5678),(UC_X86_REG_BP,0x7788),(UC_X86_REG_CS,CS),(UC_X86_REG_DS,SS),(UC_X86_REG_SS,SS),(UC_X86_REG_ES,SS),(UC_X86_REG_SP,0x8000),(UC_X86_REG_EFLAGS,0x202)]:u.reg_write(reg,val)
 u.emu_start(CS*16+0x6d2,0xfffff,count=3000);r={'episode':ep,'display_level':level+1,'tile':c['tile'],'start':[px,py],'visited_cells':list(visited),**state}
 if state.get('return'):assert (u.reg_read(UC_X86_REG_CS),u.reg_read(UC_X86_REG_IP),u.reg_read(UC_X86_REG_SP))==(0x6000,0,0x8004);r['AL']=u.reg_read(UC_X86_REG_AX)&255
 else:assert state.get('door_lookup_unmodeled')
 results.append(r)
v={'status':'SYNTHETIC_ORIGINAL_CPU_WITH_CAPTURED_TABLES','source_sha256':H(raw),'MAP1_sha256':H(map1),'traits_sha256':H(traits),'traits_source':'Original N episode1 levelIndex10, read-only512-byte table capture; reuse across level6 is a fixture, not traced loader equivalence','cases':results,'scope':'Original helper06D2 and gridCC0, original level6 cells with captured episode1 traits. Stop before any unmodeled door lookup. No native successfulC37 or native level6 load claim.'};(O/'start_ray_cpu_validation.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v))

