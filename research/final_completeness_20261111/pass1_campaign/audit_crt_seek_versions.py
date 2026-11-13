"""VERSION_ROOT DECODER OUT: independently byte-matched seek/tail/error bodies; masked operands retained with bindings."""
import csv,hashlib,json,sys
from pathlib import Path
root,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,OpKind,Register
sha=lambda x:hashlib.sha256(x).hexdigest();out.mkdir(exist_ok=True);records=[];bindings=[];proofs=[];canonical={};needle=bytes.fromhex('558bec83ec048b5e063b1e');fmt=Formatter(FormatterSyntax.INTEL)
for version in ('20','10','11','12','15','17','18','19'):
 image=root/('N3D-'+version)/'unpacked_image.bin';inventory=image.parent/'instructions.json';b=image.read_bytes();old={x['image_offset']:x for x in json.loads(inventory.read_text(encoding='utf-8'))};hits=[i for i in range(len(b)) if b.startswith(needle,i)];assert len(hits)==1;p=hits[0];cs=old[p]['cs'];ip=old[p]['ip'];dec=Decoder(16,b[p:p+129],ip=ip);seek=list(dec);assert len(seek)==48;tailip=seek[-1].near_branch_target;tailp=cs*16+tailip;tail=list(Decoder(16,b[tailp:tailp+13],ip=tailip));assert len(tail)==7;errorip=tail[1].near_branch_target;errorp=cs*16+errorip;error=list(Decoder(16,b[errorp:errorp+45],ip=errorip));assert len(error)==21
 for name,start,items,length in [('crt_seek',p,seek,129),('crt_seek_shared_return',tailp,tail,13),('crt_dos_error_translate',errorp,error,45)]:
  masked=[];edges=[];offsets={i.ip:j for j,i in enumerate(items)}
  for j,i in enumerate(items):
   pos=cs*16+i.ip;raw=b[pos:pos+i.len];assert old[pos]['bytes']==raw.hex();patched=bytearray(raw);co=Decoder(16,raw,ip=i.ip);check=co.decode();constants=co.get_constant_offsets(check)
   if constants.displacement_size and i.memory_segment==Register.DS and any(i.op_kind(k)==OpKind.MEMORY for k in range(i.op_count)):
    a=constants.displacement_offset;n=constants.displacement_size;assert n;patched[a:a+n]=bytes(n);bindings.append(dict(version=version,function=name,instruction_index=j,physical_instruction=pos,operand='DS_displacement',ds_offset=i.memory_displacement,raw=raw.hex(),asm=fmt.format(i)))
   if name=='crt_dos_error_translate' and i.ip==errorip+32:
    a=constants.immediate_offset;n=constants.immediate_size;assert n==2;patched[a:a+n]=bytes(n);bindings.append(dict(version=version,function=name,instruction_index=j,physical_instruction=pos,operand='error_table_near_address',ds_offset=i.immediate16,raw=raw.hex(),asm=fmt.format(i)))
   if any(i.op_kind(k)==OpKind.NEAR_BRANCH16 for k in range(i.op_count)):
    target=i.near_branch_target;kind='local:'+str(offsets[target]) if target in offsets else ('shared_return' if target==tailip else 'error_translate' if target==errorip else 'UNRESOLVED');assert kind!='UNRESOLVED';edges.append((j,kind));a=constants.immediate_offset;n=constants.immediate_size;assert n;patched[a:a+n]=bytes(n)
   masked.append(patched.hex())
  norm=dict(bytes=masked,edges=edges);same=norm==canonical.get(name,norm)
  if version=='20':canonical[name]=norm
  assert same,(version,name);records.append(dict(version=version,function=name,start=start,end_exclusive=start+length,cs=cs,ip=items[0].ip,instructions=len(items),raw_sha256=sha(b[start:start+length]),masked_CFG_equal_DOS20=same))
 proofs.extend([dict(path=str(q.resolve()),sha256=sha(q.read_bytes())) for q in (image,inventory)])
def save(n,r):
 with (out/(n+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(r[0]));w.writeheader();w.writerows(r)
save('versions',records);save('masked_operand_bindings',bindings);s=dict(versions=8,body_comparisons=len(records),all_masked_CFG_equal=True,runtime_tests=0,separate_replay_cases=0,status_changes=0,new_deep_verified_bytes=0,scope='Original bytes+instruction shapes+branch edges; DS displacements including indexed flags and error-table immediate masked only with explicit bindings. No full runtime/library/Win16 parity.',files=proofs+[dict(path=str(Path(__file__).resolve()),sha256=sha(Path(__file__).read_bytes()))]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'}))
