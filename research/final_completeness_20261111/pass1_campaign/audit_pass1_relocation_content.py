"""PASS1 relocated WORDs, content runs, and string patterns; no FAR-pointer inference.
Usage: python audit_pass1_relocation_content.py IMAGE RELOCS NONCODE_CSV STRUCTURAL_CSV OUT_DIR
"""
import collections,csv,hashlib,json,re,struct,sys
from pathlib import Path
image,relocs,baseline,structural,out=map(Path,sys.argv[1:]);b=image.read_bytes();sha=lambda v:hashlib.sha256(v).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
read=lambda p:list(csv.DictReader(p.open(encoding='utf-8-sig')))
base=read(baseline);layout=read(structural);expected=set();layout_by_byte={}
for r in base:
    a,e=int(r['start']),int(r['end_exclusive']);assert sha(b[a:e])==r['range_sha256'];expected.update(range(a,e))
for i,r in enumerate(layout):
    for p in range(int(r['start']),int(r['end_exclusive'])):assert p not in layout_by_byte;layout_by_byte[p]=i
assert expected==set(layout_by_byte) and len(expected)==57295
allrel=read(relocs);rel_by_pos={int(r['image_offset']):r for r in allrel};assert len(allrel)==len(rel_by_pos)==1670
assert sha(relocs.read_bytes())=='5faab828945fa774c340ce1b612a0cd6379f7507cfddcdcccd395d37a58b3256'
words=[];owner={}
for pos,r in sorted(rel_by_pos.items()):
    if pos not in expected:continue
    assert pos+1 in expected and struct.unpack_from('<H',b,pos)[0]==int(r['original_word'])
    assert pos not in owner and pos+1 not in owner
    index=len(words);owner[pos]=index;owner[pos+1]=index;value=int(r['original_word']);prev=struct.unpack_from('<H',b,pos-2)[0]
    words.append(dict(field_id=index,start=pos,end_exclusive=pos+2,type='loader_relocated_WORD',storage_role='data_or_code_operand_UNRESOLVED',initial_word=value,loader_transform='(initial_WORD + load_segment) & 0xFFFF',candidate_segment_base=value*16,preceding_word=prev,preceding_word_also_relocated=pos-2 in rel_by_pos,far_pointer_interpretation='NOT_PROVEN',candidate_far_target=value*16+prev,range_sha256=sha(b[pos:pos+2]),status='PARTIAL',evidence='actual EXEPACK relocation entry; byte value checked against image'))
runs=[];strings=[];boundary_strings=[];partition=[]
for r in base:
    a,e=int(r['start']),int(r['end_exclusive']);pos=a
    while pos<e:
        end=pos+1;zero=b[pos]==0
        while end<e and (b[end]==0)==zero:end+=1
        runs.append(dict(start=pos,end_exclusive=end,length=end-pos,initial_content='ALL_ZERO' if zero else 'ALL_NONZERO',range_sha256=sha(b[pos:end]),semantic_type='UNRESOLVED',status='CLASSIFIED ONLY',scope='content census only; no padding/BSS/code exclusion'))
        pos=end
    for m in re.finditer(rb'[\x20-\x7e]{4,}\x00',b[a:e]):
        x,y=a+m.start(),a+m.end();strings.append(dict(start=x,end_exclusive=y,length=y-x,ascii_text=m.group()[:-1].decode('ascii'),range_sha256=sha(b[x:y]),overlap_relocated_word_bytes=sum(p in owner for p in range(x,y)),status='CLASSIFIED ONLY',scope='maximal printable ASCII + NUL pattern; consumption/lifetime unproven'))
    masked=bytes(0xff if p in owner else b[p] for p in range(a,e))
    for m in re.finditer(rb'[\x20-\x7e]{4,}\x00',masked):
        x,y=a+m.start(),a+m.end();assert b[y-1]==0 and not any(p in owner for p in range(x,y))
        boundary_strings.append(dict(start=x,end_exclusive=y,length=y-x,ascii_text=b[x:y-1].decode('ascii'),range_sha256=sha(b[x:y]),status='CLASSIFIED ONLY',scope='ASCII+actual NUL excluding relocated WORD boundaries; not a consumed-string proof'))
    def key(p):
        i=layout_by_byte[p];field=owner.get(p)
        return (i,field,'PARTIAL' if field is not None else layout[i]['status'])
    pos=a;prior=key(a)
    for cur in range(a+1,e+1):
        now=key(cur) if cur<e else None
        if now!=prior:
            partition.append(dict(start=pos,end_exclusive=cur,length=cur-pos,status=prior[2],relocation_field_id=prior[1] if prior[1] is not None else '',structural_class=layout[prior[0]]['structural_class'],semantic_type='loader_relocated_WORD; storage role unresolved' if prior[1] is not None else 'UNRESOLVED',range_sha256=sha(b[pos:cur]),original_baseline_interval_id=r['baseline_interval_id'],deep_verified=False))
            pos=cur;prior=now
assert sum(r['length'] for r in partition)==57295 and len(owner)==2*len(words)
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('relocated_words',words),('initial_content_runs',runs),('ascii_nul_patterns',strings),('ascii_after_relocation_boundaries',boundary_strings),('noncode_intervals',partition)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/'noncode_intervals.json').write_text(json.dumps(partition,indent=2)+'\n',encoding='utf-8')
counts=collections.Counter()
for r in partition:counts[r['status']]+=r['length']
summary=dict(image_sha256=sha(b),relocations_sha256=sha(relocs.read_bytes()),baseline_sha256=sha(baseline.read_bytes()),structural_map_sha256=sha(structural.read_bytes()),noncode_bytes=57295,relocation_words=len(words),relocation_word_bytes=len(owner),relocation_words_before_default_DS=sum(r['start']<0x27710 for r in words),initial_content_runs=len(runs),zero_bytes=sum(r['length'] for r in runs if r['initial_content']=='ALL_ZERO'),nonzero_bytes=sum(r['length'] for r in runs if r['initial_content']=='ALL_NONZERO'),ascii_nul_patterns=len(strings),ascii_nul_pattern_bytes=sum(r['length'] for r in strings),partition_intervals=len(partition),status_bytes=dict(counts),partial_scope='loader WORD transformation only; not certified data objects or closed FAR pointers',runtime_tests=0,new_deep_verified_bytes=0)
summary['raw_ascii_patterns_overlapping_relocations']=sum(r['overlap_relocated_word_bytes']>0 for r in strings)
summary['ascii_patterns_after_relocation_boundaries']=len(boundary_strings)
summary['ascii_bytes_after_relocation_boundaries']=sum(r['length'] for r in boundary_strings)
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2))
