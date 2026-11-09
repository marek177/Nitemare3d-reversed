"""Read-only explicit-address census; deliberately not alias closure."""
import json, hashlib, argparse, sys
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parent/'decoder'))
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
from capstone.x86 import X86_OP_MEM, X86_OP_IMM
from iced_x86 import Decoder

ROOT=Path(__file__).resolve().parents[1]
args=argparse.ArgumentParser(description=__doc__)
args.add_argument('unpacked_exe',type=Path);args.add_argument('functions_json',type=Path);args.add_argument('output_dir',type=Path)
args=args.parse_args();b=args.unpacked_exe.read_bytes();header=int.from_bytes(b[8:10],'little')*16
assert b[:2]==b'MZ' and 28<=header<=len(b)
image=b[header:];md=Cs(CS_ARCH_X86,CS_MODE_16);md.detail=True
OUT=args.output_dir
OUT.mkdir(exist_ok=True)
assert hashlib.sha256(b).hexdigest()=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3'
functions=json.loads(args.functions_json.read_text())
members={}
for f in functions:
    for old in f['instructions']:
        members.setdefault((f['segment'],old['offset']),set()).add(f['start'])
rows=[]; pointer=[]; counts=Counter(); failed=[]; edges=[]; intervals=[]
targets={(0x11ee,0x31e6):'seed_setter',(0x11ee,0x31f8):'RNG_core',(0xfba,0x1a0):'RNG_wrapper',(0xfba,0x1a6):'seed1_wrapper'}
for (seg,off), owners in sorted(members.items()):
    raw=image[seg*16+off:seg*16+off+15]
    ins=next(md.disasm(raw,off,count=1),None)
    if ins is None:
        failed.append(f'{seg:04X}:{off:04X}');continue
    independent=next(iter(Decoder(16,raw,ip=off)))
    assert not independent.is_invalid and independent.len==ins.size and independent.ip==ins.address
    counts['decoded_unique_segment_offset']+=1
    intervals.append((seg*16+off,seg*16+off+ins.size,f'{seg:04X}:{off:04X}'))
    if ins.mnemonic in ('lcall','ljmp') and len(ins.operands)==2 and all(x.type==X86_OP_IMM for x in ins.operands):
        target=tuple(x.imm&0xffff for x in ins.operands)
        if target in targets:
            edges.append({'pc':f'{seg:04X}:{off:04X}','target':f'{target[0]:04X}:{target[1]:04X}','role':targets[target],'kind':ins.mnemonic,'candidate_owners':[f'{seg:04X}:{x:04X}' for x in sorted(owners)]})
    for n,op in enumerate(ins.operands):
        base={'pc':f'{seg:04X}:{off:04X}','instruction':ins.mnemonic+' '+ins.op_str,'bytes':ins.bytes.hex(),'operand':n,'candidate_owners':[f'{seg:04X}:{x:04X}' for x in sorted(owners)]}
        if op.type==X86_OP_MEM:
            indexed=bool(op.mem.base or op.mem.index)
            counts['indexed_memory_operands' if indexed else 'absolute_memory_operands']+=1
            if indexed and op.access&2: counts['indexed_explicit_write_operands']+=1
            # Inclusive byte overlap, including accesses starting before the state.
            if not indexed and any(((op.mem.disp+k)&0xffff) in range(0x24b8,0x24bc) for k in range(op.size)):
                rows.append(dict(base,width=op.size,segment=ins.reg_name(op.mem.segment) or 'ds',read=bool(op.access&1),write=bool(op.access&2),access_unknown=op.access==0))
            if indexed and (op.mem.disp&0xffff) in range(0x24b8,0x24bc):
                pointer.append(dict(base,kind='indexed_state_displacement',width=op.size))
        elif op.type==X86_OP_IMM and (op.imm&0xffff) in range(0x24b8,0x24bc):
            pointer.append(dict(base,kind='immediate_state_offset_candidate'))
encoded=[]
for (seg,off),role in targets.items():
    pattern=off.to_bytes(2,'little')+seg.to_bytes(2,'little');pos=0
    while True:
        pos=image.find(pattern,pos)
        if pos<0:break
        encoded.append({'image_offset':pos,'target':f'{seg:04X}:{off:04X}','role':role,'overlapping_inherited_instructions':[pc for lo,hi,pc in intervals if lo<pos+4 and pos<hi],'status':'ENCODED_BYTES_ONLY; execution and relocation not implied'})
        pos+=1
for occurrence in encoded:
    matches=[e for e in edges if e['target']==occurrence['target'] and int(e['pc'][:4],16)*16+int(e['pc'][5:],16)+1==occurrence['image_offset']]
    occurrence['exact_direct_far_operand_matches']=[e['pc'] for e in matches]
result={'binary_sha256':hashlib.sha256(b).hexdigest(),'analysis_membership_sha256':hashlib.sha256(args.functions_json.read_bytes()).hexdigest(),'scope':'All unique segment:offset members inherited from nite3d20/functions.json, decoded as 16-bit x86. Explicit absolute byte overlap with offsets24B8..24BB; offset equality does not establish segment identity. Not arbitrary-byte discovery or a global writer proof.','independent_iced_instruction_lengths_checked':True,'counts':dict(counts),'decode_failures':failed,'absolute_overlap_operands':rows,'pointer_candidates':pointer,'direct_far_edges':edges,'encoded_far_pointer_occurrences':encoded,'global_alias_closure':False,'remaining_domains':['Unknown DS/segment values at non-runtime sites','Indexed/register-derived addresses, string stores and implicit writes','DOS/BIOS/interrupt/external writes and self-modifying or unenumerated code','Other binary versions and Windows16 relocation/segment mapping']}
(OUT/'RNG_state_reference_audit.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'counts':dict(counts),'decode_failures':len(failed),'absolute_overlap':len(rows),'writes':[x['pc'] for x in rows if x['write']],'pointer_candidates':pointer,'direct_far_edges':edges,'encoded_far_pointer_occurrences':encoded},indent=2))
