import json,base64,struct,hashlib,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'outputs/evidence/runtime/rng_level5_n_20261106';O=R/'outputs/wall_sort_20261106';v=json.loads((D/'post_init_actor_domain.json').read_text());rpc={r['response']['id']:r for p in D.glob('rpc_*.json') for r in [json.loads(p.read_text())]}
def data(x):return base64.b64decode(x['result']['data_base64'],validate=True)
def check(x):
 if isinstance(x,dict):
  if 'jsonrpc' in x and 'id' in x:
   r=rpc[x['id']];assert r['response']==x and r['server_pid']==23808
   if r['request']['method']=='memory.read':assert len(data(x))==r['request']['params']['length']==x['result']['byte_count'] and hashlib.sha256(data(x)).hexdigest()==x['result']['sha256']
  for y in x.values():check(y)
 elif isinstance(x,list):
  for y in x:check(y)
def addr(x,s,o,n):
 q=rpc[x['id']]['request']['params'];assert int(q['address']['segment'],16)==s and int(q['address']['offset'],16)==o and q['length']==n
check(v);r=v['registers']['result'];assert (int(r['segments']['cs'],16),int(r['instruction_pointer'],16))==(0xed3,0x2e0);reads=v['reads'];addr(reads['count'],0x2f94,0x6276,2);n=struct.unpack('<h',data(reads['count']))[0];assert 0<=n<=100 and len(v['rows'])==n;addr(reads['actors'],0x2a20,0x264e,n*26);actors=data(reads['actors']);addr(reads['object_segment'],0x2f94,0x2562,2);objseg=struct.unpack('<H',data(reads['object_segment']))[0];addr(reads['player_tiles'],0x2f94,0x415e,4);px,py=struct.unpack('<hh',data(reads['player_tiles']));types=collections.Counter();modes=collections.Counter();states=collections.Counter()
for i,row in enumerate(v['rows']):
 b=actors[i*26:(i+1)*26];index=struct.unpack_from('<H',b,8)[0];o=(6+28*index)&65535;addr(row['object_read'],objseg,o,28);ob=data(row['object_read']);x,y=struct.unpack_from('<hh',ob,16);assert (row['slot'],row['object_index'],row['mode'],row['state'],row['direction'],row['type'])==(i,index,b[10],b[11],b[17],ob[6]);assert row['object_xy']==[x,y] and row['tile_delta_to_player']==[px-(x>>6),py-(y>>6)] and row['within_helper_axis8']==(abs(px-(x>>6))<=8 and abs(py-(y>>6))<=8);types[ob[6]]+=1;modes[b[10]]+=1;states[b[11]]+=1
addr(reads['config'],0x2f94,0x4144,16);loaded=data(reads['config']);disk=(R/'work/runtime/game_rng_level5_n_20261106/CONFIG.SAV').read_bytes();differences=[i for i,(a,b) in enumerate(zip(loaded,disk)) if a!=b];assert len(loaded)==len(disk)==16;assert differences==[8,12,13,15] and all(loaded[i]==0 and disk[i]==1 for i in differences)
summary={'status':'VERIFIED_RUNTIME_ENDPOINT_RAW_RPC_CORRELATED','checkpoint':'06B0:02E0','actors':n,'type_histogram':dict(types),'mode_histogram':dict(modes),'state_histogram':dict(states),'mode3_count':modes[3],'selector9_10_count':types[9]+types[10],'selector17_20_count':sum(types[i] for i in range(17,21)),'selector27_31_count':sum(types[i] for i in range(27,32)),'config_difference_offsets':differences,'loaded_Omnificent':0,'disk_Omnificent':1,'scope':'Initial actor endpoint only. Counts do not prove all constructors, future spawns/transforms/callbacks or unreachable RNG sites. Offsets8/12/13/15 differ1-to0; only15 is interpreted here from prior Omnificent provenance. No new config writer trace is claimed.'};(O/'post_init_actor_validation.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary))

