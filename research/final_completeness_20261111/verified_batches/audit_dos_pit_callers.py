"""PIT caller inputs and exhaustive WORD denominator arithmetic, not reachability.
Usage: python audit_dos_pit_callers.py IMAGE INSTRUCTIONS DECODER_DIR OUT_DIR
"""
import csv,hashlib,json,sys
from pathlib import Path
image,old,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,OpKind,InstructionInfoFactory,Register,OpAccess
b=image.read_bytes();h=hashlib.sha256(b).hexdigest();assert h=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
rows=json.loads(old.read_text());fmt=Formatter(FormatterSyntax.INTEL);factory=InstructionInfoFactory();callers=[];gate=[]
descriptions={0x18af6:'constant AX=0952h',0x1917a:'AX=(1191180 / CS:34B9) low8 after DIV16; upstream DIV may fault',0x19234:'same low8 quotient formula as1917A',0x19299:'AX=CS:2C49',0x192e6:'AX=CS:2C49',0x19a5b:'constant AX=FFFFh; followed by gate=1',0x19fe2:'AX=1193180 / WORD ES:DI; upstream DIV may fault',0x1a171:'AX=low16(10 * high16(7795 * quotient)); quotient from external numerator / CS:2C5A'}
for i,r in enumerate(rows):
    raw=bytes.fromhex(r['bytes']);a=r['image_offset'];assert b[a:a+len(raw)]==raw
    ins=Decoder(16,raw,ip=r['ip']).decode();assert not ins.is_invalid and ins.len==len(raw)
    if ins.flow_control==FlowControl.CALL and ins.op_kind(0)!=OpKind.FAR_BRANCH16 and r['cs']*16+ins.near_branch_target==0x1a25a:
        assert a in descriptions
        callers.append(dict(image_offset=a,bytes=raw.hex(),input_formula=descriptions[a],scope='local provenance only; no global range proof',status='PARTIAL'))
    if r['cs']==0x15bf:
        for m in factory.info(ins).used_memory():
            if m.segment==Register.CS and m.base==Register.NONE and m.index==Register.NONE and m.displacement==0x201e:
                gate.append(dict(image_offset=a,bytes=raw.hex(),instruction=fmt.format(ins),access_enum=m.access,status='PARTIAL'))
assert len(callers)==8
domains=[]
for numerator,truncate in [(1191180,True),(1193180,False)]:
    counts={};zeros=[]
    for d in range(65536):
        if d==0:kind='upstream_divide_by_zero'
        elif numerator//d>65535:kind='upstream_quotient_overflow'
        else:
            value=(numerator//d)&(255 if truncate else 65535)
            kind='zero_helper_input' if value==0 else 'nonzero_helper_input'
            if value==0:zeros.append(d)
        counts[kind]=counts.get(kind,0)+1
    assert sum(counts.values())==65536
    domains.append(dict(numerator=numerator,truncate_to_low8=truncate,word_denominators=65536,classes=counts,zero_helper_input_denominators=zeros,scope='exhaustive arithmetic domain; no natural resource validity or runtime gate assumption'))
out.mkdir(parents=True,exist_ok=True)
for name,rs in [('callers.csv',callers),('gate_references.csv',gate)]:
    with (out/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
r=dict(image_sha256=h,callers=len(callers),gate_literal_references=len(gate),domains=domains,zero_input_natural_reachability_proven=False,global_gate_writes_complete=False,new_deep_verified_bytes=0,runtime_tests=0)
(out/'summary.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
