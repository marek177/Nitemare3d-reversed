#!/usr/bin/env python3
"""Nitemare 3D Win16 1.10: reproducible static call-site audit, NOT runtime verification."""
from pathlib import Path
import struct,json,hashlib,csv
ROOT=Path(__file__).resolve().parent
B=(ROOT/'nite3w - 110(3).exe').read_bytes()
u16=lambda x:struct.unpack_from('<H',B,x)[0]
NE=struct.unpack_from('<I',B,0x3c)[0]
assert B[:2]==b'MZ' and B[NE:NE+2]==b'NE'
shift=u16(NE+0x32);tbl=NE+u16(NE+0x22);count=u16(NE+0x1c)
segs={}
for i in range(1,count+1):
    units,size,flags,minimum=struct.unpack_from('<HHHH',B,tbl+(i-1)*8)
    if units:segs[i]={'base':units<<shift,'length':size or 65536,'flags':flags}
base=segs[2]['base'];length=segs[2]['length']; assert base==0xe8a0
sites=[0x5ac7,0x5ad3,0x5adf,0x5af6,0x5b1a,0x5b5c,0x5b78,0x5b84]
fixups=[]
for seg,s in segs.items():
    if not s['flags']&0x100:continue
    pos=s['base']+s['length'];n=u16(pos);pos+=2
    for _ in range(n):
        typ,fl,src,a,b=struct.unpack_from('<BBHHH',B,pos);pos+=8
        fixups.append((seg,typ,fl,src,a,b))
fixup_by_site={(seg,src):dict(type=typ,flags=fl,a=a,b=b) for seg,typ,fl,src,a,b in fixups}
selectors={}
for seg,typ,fl,src,a,b in fixups:
    if typ!=2 or fl!=0:continue
    pos=src;seen=set();sg=segs[seg]
    while pos!=65535:
        if pos in seen or pos+2>sg['length']:break
        seen.add(pos);selectors[(seg,pos)]=a;pos=u16(sg['base']+pos)
rows=[]
for off in sites:
    op=B[base+off]
    target=(u16(base+off+3),u16(base+off+1)) if op==0x9a else None
    operand_sites=list(range(off+1,off+5)) if target else []
    rows.append({'site':f'2:{off:04X}','bytes':B[base+off:base+off+(5 if target else 4)].hex(' '),'opcode':f'{op:02X}', 'disk_target':f'{target[0]:04X}:{target[1]:04X}' if target else 'indirect', 'direct_fixups':{f'{p:04X}':fixup_by_site[(2,p)] for p in operand_sites if (2,p) in fixup_by_site},'selector_chain':{f'{p:04X}':selectors[2,p] for p in operand_sites if (2,p) in selectors}})
# All occurrences of four-byte potential immediate pointers to suspicious target operand locations, informational only.
refs={}
for off in (0x5ac8,0x5ae0,0x5b5d,0x5b85):
    needle=struct.pack('<H',off)
    refs[f'{off:04X}']=[f'{p:04X}' for p in range(length-1) if B[base+p:base+p+2]==needle][:120]
# Structural fallthrough checkpoints for main allocator, grounded in disassembled bytes.
assert B[base+0x5ac7]==0x9a and B[base+0x5ad3]==0x9a and B[base+0x5adf]==0x9a
assert B[base+0x5ae4:base+0x5ae8]==bytes.fromhex('83 7e fc 00')
assert B[base+0x5ae8:base+0x5aea]==bytes.fromhex('75 17')
assert B[base+0x5aff:base+0x5b01]==bytes.fromhex('75 c2')
result={'sha256':hashlib.sha256(B).hexdigest(),'segment_2_base':base,'site_details':rows,'raw_word_reference_candidates':refs,'branch_evidence':{'5AE8':'JNE 5B01 (skip retry on allocation success)','5AFF':'JNE 5AC3 (retry on callback request)','5AE4':'CMP word [BP-4], 0 (allocation result)'},'caveat':'No Win16 execution trace, pointer write proof, or original game behavior parity'}
(ROOT/'n3d_pass21_audit.json').write_text(json.dumps(result,indent=2)+'\n')
with (ROOT/'n3d_pass21_sites.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['site','bytes','target','direct_fixup_count','selector_chain_count'])
    for r in rows:w.writerow([r['site'],r['bytes'],r['disk_target'],len(r['direct_fixups']),len(r['selector_chain'])])
print(json.dumps({'sha256':result['sha256'],'sites':len(rows),'suspicious_targets':['5B5D','5B85'],'static_audit':'PASS'},indent=2))