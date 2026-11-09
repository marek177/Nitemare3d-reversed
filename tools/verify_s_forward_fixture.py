from pathlib import Path
import json,base64,hashlib,struct
R=Path.cwd();D=R/'outputs/evidence/runtime/bsf_eof_s_20261107';a=json.loads((D/'forward_input_fixture.json').read_text());b=json.loads((D/'forward_fixture_finish.json').read_text());c=json.loads((D/'forward_exact_coordinates_after.json').read_text());raw={json.loads(p.read_text())['response']['id']:json.loads(p.read_text()) for p in D.glob('rpc_*.json')}
def check(x):
 if isinstance(x,dict):
  if 'jsonrpc' in x:
   assert raw[x['id']]['response']==x and raw[x['id']]['server_pid']==21868
   if 'data_base64' in x.get('result',{}):
    r=x['result'];data=base64.b64decode(r['data_base64']);assert len(data)==r['byte_count'] and hashlib.sha256(data).hexdigest()==r['sha256']
  for z in x.values():check(z)
 elif isinstance(x,list):
  for z in x:check(z)
for x in [a,b,c]:check(x)
def data(x):return base64.b64decode(x['result']['data_base64'])
assert data(a['before_flag'])==data(a['after_restore_flag'])==b'\0'
for k,want in [('set_input',b'\2'),('restore_input',b'\0')]:
 q=raw[a[k]['id']]['request']['params'];assert int(q['address']['segment'],16)==0x2f94 and int(q['address']['offset'],16)==0x3f50 and base64.b64decode(q['data_base64'])==want
assert int(b['after_registers']['result']['instruction_pointer'],16)==0x7f2 and b['operation_id'] is None
assert struct.unpack('<HH',data(c))==(1423,3593);ev=a['trace']['result']['events'];assert len(ev)==3000 and ev[36]['instruction']=='mov  cx,[4162] ; ds:[4162]=05A4' and ev[39]['instruction']=='mov  cx,[4164] ; ds:[4164]=0E24'
O=R/'outputs/forward_fixture_s_20261107';O.mkdir(exist_ok=True);(O/'validation.json').write_text(json.dumps({'status':'VERIFIED_RAW_RPC_INPUT_FIXTURE_AND_NATIVE_MOVEMENT_RETURN','input_bit':'DS3F50 mask02 set/restored','before_xy':[1444,3620],'after_xy':[1423,3593],'tile_before_after':[22,56],'return_PC':'06B0:07F2','trace_events':3000,'trace_capacity_reached':True,'scope':'Controlled inputbit fixture, no coordinate patch or nativeIRQ claim. Separate untraced continuation to actualreturn; full inner write/IRQ ledger open.'},indent=2));print('PASS controlled input, restore, native return and coordinate endpoints')
