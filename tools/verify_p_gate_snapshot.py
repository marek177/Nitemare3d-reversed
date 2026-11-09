import json,base64,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'outputs/evidence/runtime/rng_episode3_p_20261107';O=R/'outputs/episode3_p_continuation_20261107';v=json.loads((D/'gate_endpoint_snapshot.json').read_text());raw={}
for p in D.glob('rpc_*.json'):
 x=json.loads(p.read_text());raw[x['response']['id']]=x
for x in v.values():assert raw[x['id']]['server_pid']==50760 and raw[x['id']]['response']==x
def data(x):
 a=x['result'];b=base64.b64decode(a['data_base64']);assert hashlib.sha256(b).hexdigest()==a['sha256'] and len(b)==a['byte_count'];return b
rawexe=Path('C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20-3/work/decoded/nite3d20/output.000.exe').read_bytes();assert hashlib.sha256(rawexe).hexdigest()=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';im=rawexe[int.from_bytes(rawexe[8:10],'little')*16:];start=0x83d*16+0x29ca;end=0x83d*16+0x2ad7;expected=bytearray(im[start:end]);relocs=[]
for i in range(int.from_bytes(rawexe[6:8],'little')):
 off,seg=struct.unpack_from('<HH',rawexe,int.from_bytes(rawexe[24:26],'little')+i*4);pos=seg*16+off
 if start<=pos<end:
  assert pos+2<=end;j=pos-start;struct.pack_into('<H',expected,j,(int.from_bytes(expected[j:j+2],'little')+0x822)&65535);relocs.append(j)
assert data(v['gate_code'])==expected
p=json.loads((D/'native_episode3_observation.json').read_text());g=p['gates'][0];assert g['DX_AX']==[0x2f93,0x363b]
header=data(v['header_buffer']);b=(Path(json.loads((D/'run_config.json').read_text())['game_dir'])/'NITE3D.BSF').read_bytes()
result={'status':'VERIFIED_LOADED_BYTES_MZ_RELOCATIONS_AND_ENDPOINT','code_bytes':len(expected),'relocation_offsets':relocs,'header_buffer_sha256':hashlib.sha256(header).hexdigest(),'endpoint_DS363B':header[3],'supplied_BSF_header_is_identical':header==b[:54],'prior_native_selector1_return':'2F93:363B','scope':'Endpoint code/table integrity and current header byte, not a native trace of header loading/decoding or all intervening writers.'};(O/'gate_endpoint_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
