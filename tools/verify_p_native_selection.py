"""Read-only validation of P selection against saved raw RPC receipts."""
import json,base64,hashlib,struct,sys
from pathlib import Path
def verify(d):
 d=Path(d);s=json.loads((d/'native_episode3_observation.json').read_text());raw={}
 for p in d.glob('rpc_*.json'):
  x=json.loads(p.read_text());assert x['server_pid']==50760;raw[x['response']['id']]=x
 def data(x):
  assert raw[x['id']]['response']==x
  a=x['result'];b=base64.b64decode(a['data_base64']);assert len(b)==a['byte_count'] and hashlib.sha256(b).hexdigest()==a['sha256'];return b
 assert s['phase']=='header' and s['selected_episode']==3
 assert [p['returned_AX'] for p in s['probes']]==[65535,65535,0]
 names=[]
 for p in s['probes']:
  names.append(data(p['filename']).split(b'\0')[0].decode('ascii'))
  assert struct.unpack('<HH',data(p['arguments']))[1]==4
 assert names==['map.1','map.2','map.3'],names
 assert data(s['cache_before']['source'])==data(s['cache_after']['destination'])
 assert data(s['cache_before']['source'])[8]==1
 a=bytearray(data(s['clear_before']['config']));assert a[15]==1;a[15]=0;assert a==data(s['clear_after']['config'])
 assert struct.unpack_from('<3H',data(s['loader_arguments']['stack']))==(0x154b,0,3)
 assert struct.unpack('<HH',data(s['header']['episode_level']))==(3,0)
 assert len(data(s['header']['map_header']))==514
 assert len(s['bp_cleanup_after']['result']['breakpoints'])==9
 spec=json.loads((d/'run_config.json').read_text());game=Path(spec['game_dir'])
 for row in json.loads((d/'input_manifest.json').read_text()):
  b=(game/row['name']).read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
 assert not (game/'MAP.1').exists() and not (game/'MAP.2').exists()
 writes=[x['request']['params'] for x in raw.values() if x['request']['method']=='memory.write']
 for x in writes:
  assert int(x['address']['segment'],16)==0x40
  off=int(x['address']['offset'],16);assert off==0x1c or 0x1e<=off<=0x3c
  assert len(base64.b64decode(x['data_base64']))==2
 return {'status':'VERIFIED_RAW_RPC_SELECTION_CACHE_HEADER','filenames':names,'access_AX':[65535,65535,0],'episode':3,'level_index':0,'cached_option8':1,'API_memory_writes':len(writes),'all_API_writes_are_BIOS_queue_words':True,'scope':'Native original selection under documented file/config inputs; transition of option8 from input0 to cached1 not localized. No function-boundary or remake parity closure.'}
if __name__=='__main__':print(json.dumps(verify(sys.argv[1]),indent=2))

