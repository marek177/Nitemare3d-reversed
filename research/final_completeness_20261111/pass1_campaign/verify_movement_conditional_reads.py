"""OUTPUTS DECODER: independently bind conditional collision and negative-angle NONCODE loads."""
import csv,json,hashlib,sys
from pathlib import Path
r,decoder=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()))
from iced_x86 import Decoder,Mnemonic,Register
sha=lambda b:hashlib.sha256(b).hexdigest();b=(r/'unpack/reproduced_image.bin').read_bytes();folder=r/'player_movement_collision_replay';w=list(csv.DictReader((folder/'conditional_NONCODE_loads.csv').open()));cases={x['case']:x for x in csv.DictReader((folder/'cases.csv').open())};mapping=list(csv.DictReader((r/'pass1_xms_move_request/noncode_intervals.csv').open()));out=r/'pass1_movement_conditional_refs';out.mkdir(exist_ok=True)
pcs={0x6387:(0x638a,Register.DI,0),0x6396:(0x6399,Register.SI,0),0x6421:(0x6425,Register.DI,1),0x6431:(0x6435,Register.SI,1)}
for x in w:
 c=cases[x['case']];cfg=json.loads(c['config']);q=int(x['target_image']);pc=int(x['instruction_image']);load=int(x['load']);start=int(x['original_load_start']);width=int(x['width']);v=int(x['loaded_value']);assert c['status']=='PASS' and x['natural_runtime']=='False' and load==int(c['load']);assert int(x['linear_address'])==load*16+start and start<=q<start+width
 m=next(z for z in mapping if int(z['start'])<=q<int(z['end_exclusive']));assert m['status']==x['status'];i=Decoder(16,b[pc:pc+16],ip=pc).decode();assert i.mnemonic==Mnemonic.MOV and i.next_ip==int(x['after_instruction_image'])
 if q==0x28ef7:
  assert cfg['body']=='heading' and cfg['angle']==-361 and start==0x28ef6 and width==2 and pc==0xcfc2;assert i.op0_register==Register.AX and i.memory_base==Register.SI and i.memory_displacement==0x17e8;assert ((-361+360)*2)&65535==65534;assert v==cfg['priority']+256*cfg['pad']
 else:
  assert q in (0x2770e,0x2770f) and cfg['body']=='resolve' and cfg['profile']=='tail' and (cfg['x'],cfg['y'],cfg['angle'],cfg['steps'])==(4068,4064,90,8);n,base,disp=pcs[pc];assert i.op0_register==Register.BL and i.memory_segment==Register.ES and i.memory_base==base and i.memory_displacement==disp and width==1 and start==q;assert q==(load+0x21fd)*16+(0x573e if q==0x2770e else 0x573f)-load*16
assert len(w)==80 and sum(int(x['target_image'])==0x28ef7 for x in w)==16
rows=[]
for q in sorted({int(x['target_image']) for x in w}):
 group=[x for x in w if int(x['target_image'])==q];rows.append(dict(start=q,end_exclusive=q+1,length=1,status=group[0]['status'],original_hex=b[q:q+1].hex(),witnesses=len(group),consumer_images=json.dumps(sorted({int(x['instruction_image']) for x in group})),loaded_values=json.dumps(sorted({int(x['loaded_value']) for x in group})),natural_runtime=False,new_typed_bytes=0,new_deep_verified_bytes=0))
with (out/'conditional_fields.csv').open('w',encoding='utf-8',newline='') as f:d=csv.DictWriter(f,fieldnames=list(rows[0]));d.writeheader();d.writerows(rows)
(out/'conditional_fields.json').write_text(json.dumps(rows,indent=2)+'\n');files=[r/'unpack/reproduced_image.bin',folder/'summary.json',folder/'cases.csv',folder/'conditional_NONCODE_loads.csv',r/'audit_replay_player_movement_collision.py',r/'pass1_xms_move_request/noncode_intervals.csv',Path(__file__)];s=dict(verified=True,witnesses=len(w),conditional_UNKNOWN_bytes=2,conditional_CLASSIFIED_ONLY_bytes=1,status_changes=0,new_typed_bytes=0,new_deep_verified_bytes=0,runtime_tests=0,scope='Original MOV bytes,case domain,addresses,loaded registers and unchanged ledger;controlled inputs,not naturalgameplay.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in files]);(out/'independent_verification.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'}))
