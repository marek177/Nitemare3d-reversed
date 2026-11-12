"""python audit_unknown_alignment.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

from iced_x86 import Register,OpKind,MemorySizeExt
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));types=list(csv.DictReader((out.parent/'campaign_catalog/current_pass1_data_types.csv').open()));spans=[(0x1bda2,0x1bdb0),(0x1d0ec,0x1d0f0),(0x20b88,0x20b90),(0x2770e,0x27710)];layout=[];segment_refs=[];refs=[]
for a,e in spans:
 before=[x for x in types if int(x['end_exclusive'])<=a];after=[x for x in types if int(x['start'])>=e];left=max(before,key=lambda x:int(x['end_exclusive'])) if before else None;right=min(after,key=lambda x:int(x['start'])) if after else None
 assert b[a:e]==bytes(e-a) and e==((a+15)//16)*16
 witnesses=[x for x in rel if int(x['original_word'])==e//16]
 for x in witnesses:segment_refs.append(dict(interval_start=a,next_segment=e//16,relocation_image_offset=int(x['image_offset']),original_word=int(x['original_word']),evidence='relocated segment base only; not a reference to the gap'))
 layout.append(dict(start=a,end_exclusive=e,length=e-a,bytes_hex=b[a:e].hex(),range_sha256=sha(b[a:e]),status='UNKNOWN',candidate='zero fill to next paragraph base; alignment-padding hypothesis only',next_paragraph_segment=e//16,segment_relocation_witnesses=len(witnesses),preceding_typed_name=left['name'] if left else '',preceding_typed_end=left['end_exclusive'] if left else '',following_typed_name=right['name'] if right else '',following_typed_start=right['start'] if right else '',semantic_padding_proven=False))
#Exact-CS absolute memory addressing can be resolved without DS/ES inference.
#Default/DS/ES/SS/FS/GS and indexed references remain unclosed; do not treat
#absence below as a whole-program no-access proof.
absolute_cs=0;indexed_or_context_dependent=0
for r in old:
 raw=bytes.fromhex(r['bytes']);pos=r['image_offset'];assert b[pos:pos+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert i.len==len(raw)
 if not any(i.op_kind(k)==OpKind.MEMORY for k in range(i.op_count)):continue
 if i.memory_segment==Register.CS and i.memory_base==Register.NONE and i.memory_index==Register.NONE:
  absolute_cs+=1;target=r['cs']*16+i.memory_displacement;size=MemorySizeExt.size(i.memory_size);assert size>0 and i.memory_displacement+size<=65536
  #Resolve complete scalar access width; indexed or context-dependent operands remain open.
  for a,e in spans:
   if target<e and a<target+size:refs.append(dict(instruction_image_offset=pos,cs=r['cs'],ip=r['ip'],bytes=raw.hex(),target=target,memory_size_bytes=size,scope='exact CS absolute byte-range intersection'))
 else:indexed_or_context_dependent+=1
save('remaining_unknown_geometry',layout);save('next_segment_relocation_witnesses',segment_refs)
with (out/'exact_cs_absolute_range_matches.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['instruction_image_offset','cs','ip','bytes','target','memory_size_bytes','scope']);w.writeheader();w.writerows(refs)
s=dict(intervals=4,unknown_bytes=28,all_zero=True,all_end_at_next_paragraph=True,instructions_scanned=len(old),absolute_cs_memory_instructions=absolute_cs,context_or_index_dependent_memory_instructions=indexed_or_context_dependent,exact_cs_absolute_range_matches=len(refs),map_status_changed=False,new_deep_verified_bytes=0,runtime_tests=0,scope='structural hypothesis only; complete provided instruction inventory bytes checked, but inventory is not complete executable reachability and only CS absolute byte-range accesses resolved; aliases, dynamic segments, indexed accesses, drivers and callbacks unclosed',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
