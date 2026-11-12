"""python audit_vga_blit_versions.py IMAGE VERSION_ROOT DECODER OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,versions,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,FlowControl
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();reference=b[0x1d3e:0x1dec];assert len(reference)==174
def norm(code):
 result=bytearray(code);assert result[7]==result[16]==0xa1
 result[8:10]=b'\0\0';result[17:19]=b'\0\0';return bytes(result)
def cfg(code):
 result=[]
 for i in Decoder(16,code,ip=0):
  assert not i.is_invalid
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):result.append((i.ip,i.near_branch_target,'branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):result.append((i.ip,i.next_ip,'fallthrough'))
 return result
anchor=bytes.fromhex('bac403b002ee4280e103b011d2c0ee8ad8c57606');assert reference.find(anchor)==45
rows=[];inputs=[];reference_cfg=cfg(reference)
for version in ('10','11','12','15','17','18','19','20'):
 p=versions/('N3D-'+version)/'unpacked_image.bin';inventory=p.with_name('instructions.json');data=p.read_bytes();old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};hits=[];q=0
 while True:
  q=data.find(anchor,q)
  if q<0:break
  start=q-45
  if start>=0 and norm(data[start:start+174])==norm(reference):hits.append(start)
  q+=1
 assert len(hits)==1,(version,hits);start=hits[0];code=data[start:start+174];assert cfg(code)==reference_cfg
 count=0
 for i in Decoder(16,code,ip=0):
  record=lookup[start+i.ip];assert record['bytes']==code[i.ip:i.next_ip].hex();count+=1
 assert count==78
 first,second=struct.unpack_from('<H',code,8)[0],struct.unpack_from('<H',code,17)[0]
 assert (first,second)==((0x12c,0x12a) if version in ('10','11','12') else (0x12e,0x12c))
 diffs=[n for n,(a,z) in enumerate(zip(reference,code)) if a!=z];assert set(diffs)<={8,9,17,18}
 record=lookup[start];rows.append(dict(version=version,image_sha256=sha(data),start=start,end_exclusive=start+174,cs=record['cs'],ip=record['ip'],code_sha256=sha(code),normalized_sha256=sha(norm(code)),byte_exact_to_DOS20=code==reference,changed_byte_offsets=','.join(map(str,diffs)),page_zero_ds_word=first,page_nonzero_ds_word=second,instructions=78,relative_cfg_edges=len(reference_cfg),status='PARTIAL',scope='byte or two-operand-normalized native code/CFG identity; page producer and runtime binding not cross-version verified'))
 inputs.extend(dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (p,inventory))
out.mkdir(parents=True,exist_ok=True)
with (out/'versions.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
result=dict(labels=8,unique_images=len({r['image_sha256'] for r in rows}),byte_exact_labels=sum(r['byte_exact_to_DOS20'] for r in rows),normalized_matches=8,normalized_operands=['MOV AX,[DS:page_zero] at byte8:10','MOV AX,[DS:page_nonzero] at byte17:19'],instructions_per_function=78,relative_cfg_edges=len(reference_cfg),files=inputs,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
