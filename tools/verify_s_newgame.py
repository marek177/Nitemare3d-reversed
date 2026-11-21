from pathlib import Path
import json,base64,hashlib
D=Path('outputs/evidence/runtime/bsf_eof_s_20261107');v=json.loads((D/'newgame_loader_seek_control.json').read_text());r=json.loads((D/'newgame_load_return_control.json').read_text());a=json.loads((D/'s_newgame_loaded.json').read_text());raw={json.loads(p.read_text())['response']['id']:json.loads(p.read_text()) for p in D.glob('rpc_*.json')}
for x in [v['registers'],v['stack'],r['registers'],*a['reads'].values()]:
 assert raw[x['id']]['response']==x and raw[x['id']]['server_pid']==21868
 if 'data_base64' in x['result']:assert hashlib.sha256(base64.b64decode(x['result']['data_base64'])).hexdigest()==x['result']['sha256']
import struct
f=struct.unpack('<8H',base64.b64decode(v['stack']['result']['data_base64']));assert f[:4]==(0x281a,0x154c,0,1);assert int(r['registers']['result']['instruction_pointer'],16)==0x281a;assert base64.b64decode(a['reads']['config']['result']['data_base64'])[15]==1
O=Path('outputs/natural_newgame_s_20261107');O.mkdir(exist_ok=True);(O/'validation.json').write_text(json.dumps({'status':'VERIFIED_RAW_RPC_NATIVE_NEWGAME_LOADER_AND_ENDPOINT','pid':21868,'episode':1,'level_index':0,'actual_loader_return':'0D29:281A','actor_histogram':a['type_histogram'],'Omnificent':1,'scope':'BIOS queue menu fixtures; no native hardware input parity. This endpoint does not prove native constructors/all writes or accepted perception.'},indent=2));print('PASS native loader input/return and config endpoint')
