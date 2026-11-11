"""PASS1 structural split from relocated CRT startup; no padding/BSS promotion.
Usage: python audit_pass1_startup_segments.py IMAGE RELOCATIONS_CSV NONCODE_CSV DECODER_DIR OUT_DIR
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,relocs,noncode,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
word=lambda a:struct.unpack_from('<H',b,a)[0]
expected={0x11f05:'bf7127',0x11f17:'fa8ed781c42ee0fb',0x11f7d:'368c1e1e21',0x11f82:'1607fcbf5026b930e02bcf33c0f3aa161f'}
for a,v in expected.items():assert b[a:a+len(bytes.fromhex(v))]==bytes.fromhex(v)
rel=list(csv.DictReader(relocs.open(encoding='utf-8-sig')));match=[r for r in rel if int(r['image_offset'])==0x11f06]
assert len(match)==1 and int(match[0]['original_word'])==0x2771 and word(0x11f06)==0x2771
baseline=list(csv.DictReader(noncode.open(encoding='utf-8-sig')));assert [(int(r['start']),int(r['end_exclusive'])) for r in baseline]==[(0x11ee7,0x11ef8),(0x1bda2,0x29d60)]
for r in baseline:assert sha(b[int(r['start']):int(r['end_exclusive'])])==r['range_sha256']
assert b[0x11ee7:0x11ef8]==bytes(17)
fmt=Formatter(FormatterSyntax.INTEL);insrows=[]
for ins in Decoder(16,b[0x11ef8:0x11fc5],ip=0x18):
    assert not ins.is_invalid;a=0x11ee0+ins.ip
    insrows.append(dict(image_offset=a,cs=0x11ee,ip=ins.ip,bytes=b[a:a+ins.len].hex(),instruction=fmt.format(ins),status='PARTIAL',scope='startup candidate; normal path preconditions and external DOS ABI remain open'))
spans=[]
for parent,a,e,status,kind in [(1484,0x11ee7,0x11ef8,'CLASSIFIED ONLY','zero-filled bytes before CRT entry; padding not proven'),(1487,0x1bda2,0x27710,'UNKNOWN','file-backed region preceding proven default DS base; semantic types unresolved'),(1487,0x27710,0x29d60,'CLASSIFIED ONLY','file-backed default-DS prefix; individual fields not reconstructed')]:
    spans.append(dict(baseline_interval_id=parent,start=a,end_exclusive=e,length=e-a,status=status,structural_class=kind,semantic_type='UNRESOLVED',range_sha256=sha(b[a:e]),zero_bytes=b[a:e].count(0),semantic_contract_closed=False,evidence='startup_instructions.csv + relocation at11F06 + original NONCODE boundaries'))
assert sum(r['length'] for r in spans)==57295
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('startup_instructions',insrows),('noncode_structural_map',spans)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/'noncode_structural_map.json').write_text(json.dumps(spans,indent=2)+'\n',encoding='utf-8')
r=dict(image_sha256=sha(b),noncode_baseline_sha256=sha(noncode.read_bytes()),relocation_source_sha256=sha(relocs.read_bytes()),default_segment_unrelocated=0x2771,default_ds_image_base=0x27710,segment_immediate_word_location=0x11f06,segment_word_is_relocation=True,file_backed_ds_start=0x27710,file_backed_ds_end_exclusive=0x29d60,file_backed_ds_bytes=0x2650,pre_default_ds_noncode_bytes=47470,crt_clear_offset_start=0x2650,crt_clear_offset_end_exclusive=0xe030,crt_clear_linear_start=0x29d60,crt_clear_linear_end_exclusive=0x35740,crt_clear_bytes=0xe030-0x2650,crt_clear_intersection_original_noncode_bytes=0,structural_status_bytes={'CLASSIFIED ONLY':9825,'UNKNOWN':47470,'PARTIAL':0,'DEEP VERIFIED':0},semantic_type_closed_bytes=0,new_deep_verified_bytes=0,runtime_tests=0,scope='structural facts conditional on normal startup path; do not equate zero bytes with padding or runtime BSS')
(out/'summary.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
