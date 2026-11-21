import json,base64,struct,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'outputs/evidence/runtime/rng_level1_o_20261107';O=R/'outputs/target_maps_20261107';identity=json.loads((D/'startup_identity.json').read_text());B=identity['loadbase'];pid=identity['server_pid'];DS=B+0x2771;rows=[json.loads(p.read_text()) for p in D.glob('rpc_*.json')];raw={r['response']['id']:r for r in rows};log=(R/'work/runtime/rng_o_context_after180.log').read_bytes();lines=[json.loads(s) for s in log.decode('utf-8-sig').splitlines() if s.strip()];assert len(lines)==9
mid={'status':lines[0],'registers':lines[1],'reads':dict(zip(('RTC','RNG','world','mode','flags'),lines[2:7])),'breakpoints':lines[7],'words':lines[8],'provenance':'Reconstructed from preserved complete context log','source_log_sha256':hashlib.sha256(log).hexdigest()};(O/'context_after180_reconstructed.json').write_text(json.dumps(mid,indent=2),encoding='utf-8');end=json.loads((D/'current_context.json').read_text());sentry=json.loads((D/'rng_search_sentinel.json').read_text());arm=json.loads((D/'search_boundary_arm.json').read_text());level=json.loads((R/'work/runtime/rng_o_boundary_level.log').read_text());ctl=json.loads((R/'work/runtime/rng_o_target_control.json').read_text());expected={x['site'] for x in json.loads((R/'outputs/wall_sort_20261106/remaining_RNG_targets.json').read_text())['records']}
def data(x):return base64.b64decode(x['result']['data_base64'],validate=True)
def check(x):
 if isinstance(x,dict):
  if 'jsonrpc' in x and 'id' in x:
   r=raw[x['id']];assert r['response']==x and r['server_pid']==pid
   if r['request']['method']=='memory.read':assert len(data(x))==r['request']['params']['length']==x['result']['byte_count'] and hashlib.sha256(data(x)).hexdigest()==x['result']['sha256']
  for y in x.values():check(y)
 elif isinstance(x,list):
  for y in x:check(y)
for x in (mid,end,sentry,arm,level):check(x)
def addr(x,s,o,n):
 q=raw[x['id']]['request']['params'];assert int(q['address']['segment'],16)==s and int(q['address']['offset'],16)==o and q['length']==n
for c in (mid,end):
 for key,o,n in [('RTC',0x81e,4),('RNG',0x24b8,4),('world',0x4540,34),('mode',0x3cd4,4),('flags',0x3f50,2)]:addr(c['reads'][key],DS,o,n)
assert ctl['phase']=='sentinel' and ctl['operation_id'] is None and ctl['pending'] is None and ctl['observations']==0 and not list(D.glob('target_observation_*.json'));assert mid['status']['result']['state']==end['status']['result']['state']=='stopped'
for c in (mid,end):
 bps=c['breakpoints']['result']['breakpoints'];actual={f"{int(x['address']['segment'],16)-B:04X}:{int(x['address']['offset'],16):04X}" for x in bps};assert actual==expected and len(bps)==9 and all(x['enabled'] for x in bps)
assert int.from_bytes(data(mid['reads']['world'])[:4],'little')==mid['words']['world'][0]==244 and int.from_bytes(data(end['reads']['world'])[:4],'little')==281
assert sentry['pc']=='0D29:26F4';r=sentry['snapshot']['registers'];assert (int(r['segments']['cs'],16)-B,int(r['instruction_pointer'],16))==(0xd29,0x26f4);assert struct.unpack_from('<3H',data(sentry['snapshot']['reads']['stack']))==(B+0xd29,10,1) and int.from_bytes(data(sentry['snapshot']['reads']['counter']),'little')==281
addr(sentry['snapshot']['reads']['stack'],int(r['segments']['ss'],16),int(r['general']['esp'],16)&65535,32);addr(sentry['snapshot']['reads']['counter'],DS,0x4540,4)
assert struct.unpack('<HH',data(level))==(1,0);q=raw[level['id']]['request']['params'];assert int(q['address']['segment'],16)==DS and int(q['address']['offset'],16)==0x626a and q['length']==4
assert any(x['request']['method']=='execution.wait' and x['response'].get('result',{}).get('stop_reason',{}).get('breakpoint_id')==arm['result']['breakpoint_id'] for x in rows)
actors=json.loads((D/'level1_actor_after180.json').read_text());check(actors);addr(actors['reads']['count'],DS,0x6276,2);n=struct.unpack('<h',data(actors['reads']['count']))[0];assert n==len(actors['rows'])==33;addr(actors['reads']['actors'],B+0x21fd,0x264e,n*26);addr(actors['reads']['player_tiles'],DS,0x415e,4);addr(actors['reads']['object_segment'],DS,0x2562,2);objseg=int.from_bytes(data(actors['reads']['object_segment']),'little');a=base64.b64decode(actors['reads']['actors']['result']['data_base64']);pt=struct.unpack('<hh',data(actors['reads']['player_tiles']));assert pt==(20,51);gates=[]
for row in actors['rows']:
 if row['type'] not in (9,10) or not row['within_helper_axis8']:continue
 i=row['slot'];b=a[i*26:(i+1)*26];index=struct.unpack_from('<H',b,8)[0];addr(row['object_read'],objseg,(6+28*index)&65535,28);ob=data(row['object_read']);x,y=struct.unpack_from('<hh',ob,16);dx,dy=pt[0]-(x>>6),pt[1]-(y>>6);direction=b[17];assert row['type']==ob[6] and row['mode']==b[10] and row['state']==b[11] and row['direction']==direction and row['tile_delta_to_player']==[dx,dy];cone=sum(1<<d for d in {(direction-1)&7,direction,(direction+1)&7});mask=(0x66 if abs(dx)>=abs(dy) else 0x99)&(0x3c if dy>=0 else 0xc3)&(0x0f if dx>=0 else 0xf0);gates.append({'slot':i,'type':ob[6],'state':b[11],'direction':direction,'delta':[dx,dy],'modeled_facing_passes':bool(cone&mask)})
summary={'status':'VERIFIED_RUNTIME_BOUNDED_SEARCH_AND_SENTINEL','server_pid':pid,'loadbase':f'{B:04X}','initial_counter':2,'first_requested_budget_seconds':180,'first_endpoint_counter':244,'second_requested_budget_seconds':300,'second_completed_full_budget':False,'sentinel_counter':281,'sentinel':'0D29:26F4','next_native_loader_arguments':{'episode':1,'level_index':10},'current_loaded_episode_level':[1,0],'target_hits':0,'active_target_count':9,'RNG_endpoint':int.from_bytes(data(end['reads']['RNG']),'little'),'near_selector_actors_at_first_endpoint':gates,'scope':'Second interval stopped at native next-loader boundary, not at its full300-second budget. First interval has endpoint evidence but no complete map-writer trace. Facing is an inference from previously tested helper model, not witnessed native helper returns. Reload cause/EOF/death/whole domain remainsUNKNOWN; no zero-global-RNG claim.'};(O/'search_validation.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary))
