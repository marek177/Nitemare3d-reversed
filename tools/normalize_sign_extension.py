"""Correct width-sensitive 98/99 metadata; retain original decoder observations."""
from pathlib import Path
import json,sys,hashlib,collections
sys.path.insert(0,str(Path(__file__).resolve().parent/'decoder'))
from iced_x86 import Decoder,Formatter,FormatterSyntax

SOURCE='https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2a-manual.pdf'
EFFECTS={'cbw':(['al'],['ax']),'cwde':(['ax'],['eax']),'cwd':(['ax'],['dx']),'cdq':(['eax'],['edx'])}
FMT=Formatter(FormatterSyntax.INTEL)
def correction(raw,offset):
    i=Decoder(16,raw,ip=offset).decode()
    if i.is_invalid:return None
    mnemonic=FMT.format(i).lower()
    if mnemonic not in EFFECTS:return None
    assert i.len==len(raw)
    reads,writes=EFFECTS[mnemonic]
    return {'asm':mnemonic,'register_reads':reads,'register_writes':writes,'eflags_mask':0,'semantics_scope':'Architectural explicit low-width effects; upper-register preservation follows operand width; no interprocedural liveness claim'}

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('evidence_dir',type=Path);ap.add_argument('output_dir',type=Path);ap.add_argument('--apply',action='store_true');args=ap.parse_args()
    E=args.evidence_dir;O=args.output_dir;O.mkdir(exist_ok=True,parents=True)
    inventory=json.loads((E/'binary_inventory.json').read_text());images={}
    for v in inventory:
        raw=Path(v['source_path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==v['sha256'];images[v['id']]=raw
    rows=[];files=[];unique=set();counts=collections.Counter()
    for path in sorted((E/'function_cfg').glob('*.json')):
        before=path.read_bytes();cfg=json.loads(before);binary,seg,entry=cfg['function_id'].split(':');changes=0
        for ins in cfg['instructions']:
            raw=bytes.fromhex(ins['bytes'])
            # Avoid decoding unrelated opcodes: relevant bytes end in98 or99 and consist only of prefixes plus opcode.
            if raw[-1] not in (0x98,0x99):continue
            new=correction(raw,ins['offset'])
            if new is None:continue
            assert images[binary][ins['file_offset']:ins['file_offset']+len(raw)]==raw
            original=ins.get('raw_capstone_observation',{k:ins[k] for k in ('asm','register_reads','register_writes','eflags_mask')})
            if all(original[k]==new[k] for k in ('asm','register_reads','register_writes','eflags_mask')):continue
            pc=f'{seg}:{ins["offset"]:04X}';unique.add((binary,pc));counts[binary]+=1
            rows.append({'function_id':cfg['function_id'],'pc':pc,'bytes':raw.hex(),'original':original,'corrected':new,'source_sha256':next(v['sha256'] for v in inventory if v['id']==binary)})
            ins['raw_capstone_observation']=original;ins.update(new);ins['semantic_normalization']={'rule':'operand-size-sensitive sign extension98/99','authority':SOURCE,'iced_format_agrees':True};changes+=1
        if changes:
            encoded=json.dumps(cfg,separators=(',',':')).encode()
            if args.apply:path.write_bytes(encoded)
            files.append({'path':path.relative_to(E).as_posix(),'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(encoded).hexdigest(),'references':changes})
    result={'mode':'APPLIED' if args.apply else 'READ_ONLY_AUDIT','authority':SOURCE,'binary_sources_hash_verified':len(images),'affected_instruction_references':len(rows),'affected_unique_binary_PC':len(unique),'affected_CFG_files':len(files),'references_by_binary':dict(counts),'instruction_length_claim':'Prior zero length disagreements remains a length-only result; not semantic decoder equivalence','global_semantic_agreement':False,'rows':rows,'files':files}
    (O/'sign_extension_normalization.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ('rows','files')},indent=2))
