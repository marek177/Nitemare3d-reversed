"""Exhaustive printable+NUL pattern census, bounded literal-CS xrefs.
Usage: python build_ascii_candidate_atlas.py DECODER_DIR IMAGE INVENTORY OUT_DIR
Patterns are not proven strings; overlaps with historical instruction bytes stay visible.
"""
import bisect
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

def writecsv(path,rows,fields):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def main():
    dep,ipath,hpath,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep))
    from iced_x86 import Decoder,Register,OpKind,Formatter,FormatterSyntax
    image=ipath.read_bytes();ih=hashlib.sha256(image).hexdigest()
    if ih!='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297':raise ValueError('image mismatch')
    inventory=json.loads(hpath.read_text());covered=set();valid=[];conflicts=[];fmt=Formatter(FormatterSyntax.INTEL)
    for row in inventory:
        a=row['image_offset'];code=bytes.fromhex(row['bytes']);ins=Decoder(16,code,ip=row['ip']).decode()
        reason=''
        if image[a:a+len(code)]!=code:reason='byte_mismatch'
        elif a!=16*row['cs']+row['ip']:reason='segment_mapping_mismatch'
        elif ins.is_invalid or ins.len!=len(code):reason='decoder_boundary_conflict'
        if reason:conflicts.append(dict(image_offset=a,bytes=code.hex(),reason=reason));continue
        covered.update(range(a,a+len(code)));valid.append((row,ins))
    candidates=[]
    for match in re.finditer(rb'[\x20-\x7e]{4,}\x00',image):
        a,b=match.span()
        candidates.append(dict(id='ASCII%04d'%len(candidates),start=a,end_exclusive=b,length=b-a,text=match.group()[:-1].decode('ascii'),range_sha256=hashlib.sha256(image[a:b]).hexdigest(),historical_instruction_overlap_bytes=sum(p in covered for p in range(a,b)),status='CLASSIFIED_ONLY',interpretation='printable_ASCII_plus_NUL_pattern_not_proven_string',pass320_membership='UNKNOWN'))
    starts=[r['start'] for r in candidates];xrefs=[]
    for row,ins in valid:
        if not any(ins.op_kind(n)==OpKind.MEMORY for n in range(ins.op_count)):continue
        if ins.memory_segment!=Register.CS or ins.memory_base!=Register.NONE or ins.memory_index!=Register.NONE:continue
        target=row['cs']*16+ins.memory_displacement
        index=bisect.bisect_right(starts,target)-1
        if index>=0 and target<candidates[index]['end_exclusive']:
            xrefs.append(dict(candidate_id=candidates[index]['id'],instruction_image_offset=row['image_offset'],bytes=row['bytes'],instruction=fmt.format(ins),target_image_offset=target,offset_in_candidate=target-starts[index],scope='fixed_CS_memory_access_only; not proof of string consumption'))
    out.mkdir(parents=True,exist_ok=True)
    writecsv(out/'ascii_candidates.csv',candidates,list(candidates[0]))
    writecsv(out/'fixed_cs_references.csv',xrefs,['candidate_id','instruction_image_offset','bytes','instruction','target_image_offset','offset_in_candidate','scope'])
    writecsv(out/'decoder_conflicts.csv',conflicts,['image_offset','bytes','reason'])
    result=dict(image_sha256=ih,inventory_sha256=hashlib.sha256(hpath.read_bytes()).hexdigest(),historical_instruction_records=len(inventory),byte_and_boundary_valid_records=len(valid),decoder_conflicts=len(conflicts),historical_instruction_byte_union=len(covered),pattern_rule='maximal printable ASCII 0x20..0x7E run of >=4 bytes immediately followed by NUL; includes terminator',candidate_count=len(candidates),candidate_bytes=sum(r['length'] for r in candidates),candidates_without_historical_instruction_overlap=sum(r['historical_instruction_overlap_bytes']==0 for r in candidates),fixed_cs_reference_count=len(xrefs),new_deep_verified_bytes=0,semantic_promotions=0,original_pass320_ledger_imported=False,runtime_tests=0,scope='pattern census and bounded xref extraction only; no proof that historical inventory is complete or all candidate bytes are data')
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
