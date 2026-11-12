"""python audit_remaining_noncode.py IMAGE MAP_CSV INVENTORY DECODER_DIR OUT
Candidate references retain unresolved DS/alias context and never promote status.
"""
import collections,csv,hashlib,json,sys
from pathlib import Path
image,mapping,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,Register,OpKind,MemorySizeExt,Mnemonic
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
allrows=list(csv.DictReader(mapping.open(encoding='utf-8-sig')));remaining=[r for r in allrows if r['status'] in ('CLASSIFIED ONLY','UNKNOWN')]
for r in allrows:
    a,e=int(r['start']),int(r['end_exclusive']);assert e-a==int(r['length']) and sha(b[a:e])==r['range_sha256']
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));relbytes={p for r in rel for p in (int(r['image_offset']),int(r['image_offset'])+1)}
refs=[];old=json.loads(inventory.read_text());fmt=Formatter(FormatterSyntax.INTEL)
def add(r,kind,start,width,asm):
    for row in remaining:
        a,e=int(row['start']),int(row['end_exclusive'])
        if start<e and start+max(1,width)>a:
            refs.append(dict(interval_start=a,interval_end_exclusive=e,kind=kind,reference_image=start,operand_width=width,cs=r['cs'],ip=r['ip'],instruction_image=r['image_offset'],bytes=r['bytes'],instruction=asm,scope='inventory only; default DS mapping conditional; aliases and natural reachability unresolved'))
for r in old:
    raw=bytes.fromhex(r['bytes']);p=r['image_offset'];assert p==r['cs']*16+r['ip'] and b[p:p+len(raw)]==raw
    i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw);asm=fmt.format(i)
    if i.op0_kind==OpKind.NEAR_BRANCH16:add(r,'DIRECT_CONTROL_TARGET',r['cs']*16+i.near_branch_target,1,asm)
    elif i.op0_kind==OpKind.FAR_BRANCH16:add(r,'DIRECT_CONTROL_TARGET',i.far_branch_selector*16+i.far_branch16,1,asm)
    if any(i.op_kind(n)==OpKind.MEMORY for n in range(i.op_count)):
        direct=i.memory_base==Register.NONE and i.memory_index==Register.NONE
        if i.memory_segment in (Register.DS,Register.CS):
            base=0x27710 if i.memory_segment==Register.DS else r['cs']*16
            if i.mnemonic==Mnemonic.LEA:kind='ADDRESS_FORMATION_CANDIDATE';width=0
            elif direct:kind='DS_DIRECT_CONDITIONAL' if i.memory_segment==Register.DS else 'CS_DIRECT_STATIC';width=MemorySizeExt.size(i.memory_size)
            else:kind='INDEXED_BASE_CANDIDATE';width=0
            if direct or i.memory_displacement!=0:add(r,kind,base+i.memory_displacement,width,asm)
    if i.mnemonic in (Mnemonic.MOV,Mnemonic.PUSH):
        if any(i.op_kind(n)==OpKind.IMMEDIATE16 for n in range(i.op_count)) and i.immediate16>=0x40:
            add(r,'IMMEDIATE_DS_CANDIDATE',0x27710+i.immediate16,0,asm)
ledger=[]
for r in remaining:
    a,e=int(r['start']),int(r['end_exclusive']);raw=b[a:e];related=[x for x in refs if x['interval_start']==a];k=collections.Counter(x['kind'] for x in related)
    zeros=not any(raw);ascii_candidate=bool(raw) and raw[-1]==0 and any(raw) and all(c in (0,9,10,13) or 32<=c<127 for c in raw)
    if k['DIRECT_CONTROL_TARGET']:step='decode each control target and reconstruct entry/CFG; do not promote from target alone'
    elif k['DS_DIRECT_CONDITIONAL'] or k['CS_DIRECT_STATIC']:step='trace exact operand widths, writers and segment context into a concrete data type'
    elif zeros:step='check segment/loader boundaries and all writers; zeros alone do not prove padding'
    elif ascii_candidate:step='trace actual string consumer/pointer table; NUL/ASCII observation alone is classification only'
    else:step='trace candidate constants/bases, other segment aliases and omitted code; no-reference result is not proof of non-use'
    ledger.append(dict(start=a,end_exclusive=e,length=e-a,status=r['status'],range_sha256=sha(raw),all_zero=zeros,ascii_nul_sequence_candidate=ascii_candidate,verified_relocation_bytes=sum(p in relbytes for p in range(a,e)),direct_control_targets=k['DIRECT_CONTROL_TARGET'],conditional_ds_direct=k['DS_DIRECT_CONDITIONAL'],static_cs_direct=k['CS_DIRECT_STATIC'],address_candidates=k['ADDRESS_FORMATION_CANDIDATE'],indexed_base_candidates=k['INDEXED_BASE_CANDIDATE'],immediate_candidates=k['IMMEDIATE_DS_CANDIDATE'],first_48_bytes_hex=raw[:48].hex(),ascii_preview=''.join(chr(c) if 32<=c<127 else '.' for c in raw[:96]),next_step=step))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('interval_ledger',ledger),('reference_candidates',refs)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/'interval_ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
counts=collections.Counter()
for r in ledger:counts[r['status']]+=r['length']
s=dict(image_sha256=sha(b),map_sha256=sha(mapping.read_bytes()),inventory_sha256=sha(inventory.read_bytes()),verified_inventory_starts=len(old),remaining_intervals=len(ledger),remaining_bytes=sum(counts.values()),status_bytes=dict(counts),reference_candidates=len(refs),candidate_kinds=dict(collections.Counter(r['kind'] for r in refs)),intervals_without_any_candidate=sum(not any(r[k] for k in ('direct_control_targets','conditional_ds_direct','static_cs_direct','address_candidates','indexed_base_candidates','immediate_candidates')) for r in ledger),all_zero_bytes=sum(r['length'] for r in ledger if r['all_zero']),status_changes=0,runtime_tests=0,new_deep_verified_bytes=0,scope='explicit static operand/control candidate inventory only; excludes dynamic memory targets, ES/SS mapping and code outside supplied inventory')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
