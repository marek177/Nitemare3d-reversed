import json,base64,struct,hashlib,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'outputs/evidence/runtime/rng_level1_o_20261107';O=R/'outputs/target_maps_20261107';v=json.loads((D/'level1_actor_domain.json').read_text());identity=json.loads((D/'startup_identity.json').read_text());B=identity['loadbase'];pid=identity['server_pid'];DS=B+0x2771;A=B+0x21fd;rpc={r['response']['id']:r for p in D.glob('rpc_*.json') for r in [json.loads(p.read_text())]}
def data(x):return base64.b64decode(x['result']['data_base64'],validate=True)
def check(x):
 if isinstance(x,dict):
  if 'jsonrpc' in x and 'id' in x:
   r=rpc[x['id']];assert r['response']==x and r['server_pid']==pid
   if r['request']['method']=='memory.read':assert len(data(x))==r['request']['params']['length']==x['result']['byte_count'] and hashlib.sha256(data(x)).hexdigest()==x['result']['sha256']
  for y in x.values():check(y)
 elif isinstance(x,list):
  for y in x:check(y)
def addr(x,s,o,n):
 q=rpc[x['id']]['request']['params'];assert int(q['address']['segment'],16)==s and int(q['address']['offset'],16)==o and q['length']==n
check(v);r=v['registers']['result'];assert (int(r['segments']['cs'],16)-B,int(r['instruction_pointer'],16))==(0x6b0,0x2e0);reads=v['reads'];addr(reads['count'],DS,0x6276,2);n=struct.unpack('<h',data(reads['count']))[0];assert n==33 and len(v['rows'])==n;addr(reads['actors'],A,0x264e,n*26);actors=data(reads['actors']);addr(reads['object_segment'],DS,0x2562,2);objseg=struct.unpack('<H',data(reads['object_segment']))[0];addr(reads['player_tiles'],DS,0x415e,4);px,py=struct.unpack('<hh',data(reads['player_tiles']));assert(px,py)==(22,56);types=collections.Counter();modes=collections.Counter();near=[];m=(R/'work/runtime/game_rng_level1_o_20261107/MAP.1').read_bytes();assert hashlib.sha256(m).hexdigest()=='0f36888ef9df05004c77f920d810780e2023853b7ab6575dc6d910a871ae59f0'
for i,row in enumerate(v['rows']):
 b=actors[i*26:(i+1)*26];index=struct.unpack_from('<H',b,8)[0];o=(6+28*index)&65535;addr(row['object_read'],objseg,o,28);ob=data(row['object_read']);x,y=struct.unpack_from('<hh',ob,16);tx,ty=x>>6,y>>6;assert (row['slot'],row['object_index'],row['mode'],row['state'],row['direction'],row['type'])==(i,index,b[10],b[11],b[17],ob[6]);assert row['object_xy']==[x,y] and row['tile_delta_to_player']==[px-tx,py-ty] and row['within_helper_axis8']==(abs(px-tx)<=8 and abs(py-ty)<=8);tile=ty*64+tx;oid=m[514+2*tile+1];assert ob[6]==m[258+oid];to,ts=struct.unpack_from('<HH',ob,12);assert (to,ts)==(0x373e+2*tile,A);types[ob[6]]+=1;modes[b[10]]+=1
 if ob[6] in (9,10) and row['within_helper_axis8']:near.append({'slot':i,'type':ob[6],'mode':b[10],'state':b[11],'direction':b[17],'tile':[tx,ty],'delta':[px-tx,py-ty]})
summary={'status':'VERIFIED_RUNTIME_ENDPOINT_RAW_RPC_AND_MAP_JOIN','server_pid':pid,'loadbase':f'{B:04X}','actors':n,'player_tile':[px,py],'type_histogram':dict(types),'mode_histogram':dict(modes),'selector9_10_actor_count':types[9]+types[10],'axis8_selector9_10_candidates':near,'all33_actor_types_positions_and_even_wall_pointers_join_originalMAP1_level0':True,'scope':'Initial endpoint under documented input fixtures. No all-constructor trace, native perception/ray/attack/path acceptance, future spawn closure or RNG target invocation is claimed.'};(O/'actor_domain_validation.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary))
