"""Whole-image fixed-CS access atlas; candidates are not semantic verification.
Usage: python build_dos_cs_reference_atlas.py IMAGE INVENTORY DECODER_DIR CAMPAIGN_CSV OVERLAYS_CSV OUT_DIR
"""
import collections,csv,hashlib,json,sys
from pathlib import Path
image,inventory,dep,campaign,overlays,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,InstructionInfoFactory,MemorySizeExt,Register,OpAccess
b=image.read_bytes();sha=hashlib.sha256(b).hexdigest();assert sha=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
inv=inventory.read_bytes();assert hashlib.sha256(inv).hexdigest()=='a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a'
rows=json.loads(inv);factory=InstructionInfoFactory();fmt=Formatter(FormatterSyntax.INTEL);hist=set();refs=[];bybyte=collections.defaultdict(set);stats=collections.Counter()
mutable_displacement_owners={int(r['owner_instruction_image']) for r in csv.DictReader(overlays.open(encoding='utf-8-sig')) if r['encoded_role']=='displacement'}
for r in rows:
    a=r['image_offset'];raw=bytes.fromhex(r['bytes']);assert a==r['cs']*16+r['ip'] and b[a:a+len(raw)]==raw
    ins=Decoder(16,raw,ip=r['ip']).decode();assert not ins.is_invalid and ins.len==len(raw)
    hist.update(range(a,a+len(raw)))
    for mem in factory.info(ins).used_memory():
        if mem.segment!=Register.CS:continue
        stats['CS_operands']+=1
        width=MemorySizeExt.size(mem.memory_size)
        if mem.base!=Register.NONE or mem.index!=Register.NONE:stats['indexed_CS_operands']+=1;continue
        stats['fixed_CS_operands']+=1
        target=r['cs']*16+mem.displacement;end=target+width
        safe=width>0 and mem.displacement+width<=65536 and 0<=target<end<=len(b)
        patched=a in mutable_displacement_owners
        reason='runtime_patched_displacement_requires_state' if patched else 'bounded_image_range' if safe else 'unknown_width_or_segment_limit_or_outside_image'
        refid=len(refs)
        refs.append(dict(reference_id=refid,image_offset=a,cs=r['cs'],ip=r['ip'],bytes=raw.hex(),instruction=fmt.format(ins),cs_offset=mem.displacement,target_start=target,target_end_exclusive=end,width=width,access_enum=mem.access,bounded=safe,included_in_candidate_map=safe and not patched,bounds_result=reason,status='CLASSIFIED ONLY',scope='conditional on historical CS context and execution; not a semantic type proof'))
        if safe and not patched:
            for pos in range(target,end):bybyte[pos].add(refid)
campaign_status={}
for r in csv.DictReader(campaign.open(encoding='utf-8-sig')):
    for pos in range(int(r['start']),int(r['end_exclusive'])):campaign_status[pos]=(r['primary_type'],r['status'])
assert len(campaign_status)==len(b)
def key(pos):
    if pos not in bybyte:return ('NO_FIXED_CS_REFERENCE','UNKNOWN',False,(),campaign_status[pos])
    code=pos in hist
    return ('REFERENCED_HISTORICAL_CODE_BYTE' if code else 'REFERENCED_NONCODE_CANDIDATE','CLASSIFIED ONLY',code,tuple(sorted(bybyte[pos])),campaign_status[pos])
intervals=[];start=0;prior=key(0)
for pos in range(1,len(b)+1):
    current=key(pos) if pos<len(b) else None
    if current!=prior:
        intervals.append(dict(start=start,end_exclusive=pos,length=pos-start,reference_class=prior[0],status=prior[1],historical_code_overlap=prior[2],reference_ids=';'.join(map(str,prior[3])),campaign_primary_type=prior[4][0],campaign_status=prior[4][1],range_sha256=hashlib.sha256(b[start:pos]).hexdigest(),pass320_membership='UNKNOWN'))
        start=pos;prior=current
assert sum(r['length'] for r in intervals)==len(b)
out.mkdir(parents=True,exist_ok=True)
for name,rs in [('references.csv',refs),('byte_intervals.csv',intervals)]:
    with (out/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
(out/'byte_intervals.json').write_text(json.dumps(intervals,indent=2)+'\n',encoding='utf-8')
priority=[]
for r in intervals:
    if r['reference_class']=='REFERENCED_NONCODE_CANDIDATE' and r['campaign_primary_type']=='UNKNOWN_CONTENT':
        priority.append(dict(start=r['start'],end_exclusive=r['end_exclusive'],length=r['length'],fixed_reference_count=len(r['reference_ids'].split(';')),reference_ids=r['reference_ids'],status='CLASSIFIED ONLY',pass320_membership='UNKNOWN'))
priority.sort(key=lambda r:(-r['fixed_reference_count'],r['start']))
with (out/'candidate_priority.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(priority[0]));w.writeheader();w.writerows(priority)
candidate={p for p in bybyte if p not in hist};outside={p for p in candidate if campaign_status[p][0]=='UNKNOWN_CONTENT'}
result=dict(image_sha256=sha,inventory_sha256=hashlib.sha256(inv).hexdigest(),validated_instruction_starts=len(rows),historical_instruction_union_bytes=len(hist),operand_counts=dict(stats),reference_rows=len(refs),bounded_reference_rows=sum(r['bounded'] for r in refs),unique_fixed_referenced_bytes=len(bybyte),historical_code_referenced_bytes=len(set(bybyte)&hist),referenced_noncode_candidate_bytes=len(candidate),candidate_bytes_outside_current_local_evidence=len(outside),partition_intervals=len(intervals),partition_bytes=sum(r['length'] for r in intervals),candidate_access_width_counts=dict(collections.Counter(r['width'] for r in refs if r['bounded'])),original_pass320_ledger_imported=False,original_noncode_intersection_known=False,central_semantic_partition_changed=False,reachability_proven=False,new_deep_verified_bytes=0,runtime_tests=0)
result['known_runtime_patched_references_excluded']=sum(not r['included_in_candidate_map'] and r['bounds_result']=='runtime_patched_displacement_requires_state' for r in refs)
result['overlay_inventory_sha256']=hashlib.sha256(overlays.read_bytes()).hexdigest()
result['campaign_partition_sha256']=hashlib.sha256(campaign.read_bytes()).hexdigest()
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
