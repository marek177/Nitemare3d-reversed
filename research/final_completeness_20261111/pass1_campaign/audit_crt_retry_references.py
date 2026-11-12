"""IMAGE INVENTORY CENTRAL_CSV DECODER OUT: finite decoded reference census, not global alias/nonuse proof."""
import csv,hashlib,json,sys
from pathlib import Path
image,inventory,central,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,InstructionInfoFactory,MemorySizeExt,Register,OpAccess,OpKind
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(exist_ok=True);rows={int(x['image_offset']):x for x in json.loads(inventory.read_text(encoding='utf-8'))};old_count=len(rows)
for x in csv.DictReader(central.open(encoding='utf-8')):
 p=int(x['image_offset'])
 if p in rows:assert rows[p]['bytes']==x['bytes']
 else:rows[p]=dict(cs=int(x['cs']),ip=int(x['ip']),image_offset=p,bytes=x['bytes'])
fields=[('far_malloc_retry',0x2332,0x2336),('large_allocation_retry',0x246a,0x246e),('shared_segment_marker',0x20f6,0x20f8),('segment_lower_bound',0x20f8,0x20fa)];factory=InstructionInfoFactory();fmt=Formatter(FormatterSyntax.INTEL);refs=[];constants=[];unresolved=0;used=0;writeaccess={OpAccess.WRITE,OpAccess.COND_WRITE,OpAccess.READ_WRITE,OpAccess.READ_COND_WRITE}
# Calibrate access classification and branch-vs-immediate distinction against actual decoded examples.
push=Decoder(16,bytes.fromhex('50')).decode();assert any(m.segment==Register.SS and m.access==OpAccess.WRITE for m in factory.info(push).used_memory())
branch=Decoder(16,bytes.fromhex('7507'),ip=0x2461).decode();assert branch.near_branch_target==0x246a and branch.op_kind(0)!=OpKind.IMMEDIATE16
store=Decoder(16,bytes.fromhex('a3f620')).decode();assert any(m.segment==Register.DS and m.displacement==0x20f6 and m.access in writeaccess for m in factory.info(store).used_memory())
for p,x in sorted(rows.items()):
 raw=bytes.fromhex(x['bytes']);assert b[p:p+len(raw)]==raw;i=Decoder(16,raw,ip=int(x['ip'])).decode();assert not i.is_invalid and i.len==len(raw)
 for m in factory.info(i).used_memory():
  used+=1;n=MemorySizeExt.size(m.memory_size)
  if m.segment!=Register.DS or m.base!=Register.NONE or m.index!=Register.NONE:unresolved+=1;continue
  for name,a,e in fields:
   if m.displacement<e and m.displacement+n>a:refs.append(dict(field=name,cs=x['cs'],ip=x['ip'],image_offset=p,bytes=raw.hex(),instruction=fmt.format(i),DS_offset=m.displacement,width=n,access_enum=m.access,contains_write=m.access in writeaccess,DS_context='fixed DS-relative candidate; actual DS must equal game DGROUP'))
 for op in range(i.op_count):
  if i.op_kind(op)==OpKind.IMMEDIATE16:
   for name,a,e in fields:
    if a<=i.immediate16<e:constants.append(dict(field=name,image_offset=p,instruction=fmt.format(i),immediate=i.immediate16,status='numeric/address-of candidate only; no pointer or write inference'))
def save(name,data,columns=None):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=columns or list(data[0]));w.writeheader();w.writerows(data)
save('fixed_DS_references',refs);save('immediate_candidates',constants,['field','image_offset','instruction','immediate','status'])
counts={name:dict(fixed_references=sum(x['field']==name for x in refs),fixed_write_references=sum(x['field']==name and x['contains_write'] for x in refs),immediate_candidates=sum(x['field']==name for x in constants)) for name,a,e in fields}
s=dict(historical_inventory_unique_starts=old_count,central_added_starts=len(rows)-old_count,decoded_starts=len(rows),used_memory_entries_including_implicit_stack=used,non_fixed_DS_entries_unresolved=unresolved,fields=counts,runtime_tests=0,new_deep_verified_bytes=0,status_changes=0,scope='Every retained unique instruction independently decoded/byte-matched. FixedDS operands and exactimmediate16candidates only; register aliases,bulkstores,mutablesegments,omittedcode,externalwrites unresolved. Zero directwriters doesnot establish nonuse or absenceofcallbacksetters. Branch targets are not address-of immediates.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,central,Path(__file__))]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
