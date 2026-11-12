"""python compare_vga_page_versions.py IMAGE OLD_ROOT DECODER TRIG_VERSIONS_CSV WIN_EXE OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,root,dep,trig,win,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,OpKind,Register
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
spec=[('immediate',0x15ee,25),('synchronized',0x1608,47)];slots={};fmt=Formatter(FormatterSyntax.INTEL)
for name,a,n in spec:
    d=Decoder(16,b[a:a+n],ip=0);s=[]
    for i in d:
        assert not i.is_invalid;c=d.get_constant_offsets(i)
        if any(i.op_kind(k)==OpKind.MEMORY for k in range(i.op_count)) and i.memory_segment==Register.DS and i.memory_displacement in (0x12c,0x12e):
            assert c.displacement_size==2;s.append(i.ip+c.displacement_offset)
    assert len(s)==3;slots[name]=s
def matches(v,name,a,n):
    ref=b[a:a+n];masked={p+j for p in slots[name] for j in range(2)};hits=[];p=v.find(ref[:3])
    while p>=0:
        raw=v[p:p+n]
        if len(raw)==n and all(raw[k]==ref[k] for k in range(n) if k not in masked):
            deltas={((struct.unpack_from('<H',raw,k)[0]-struct.unpack_from('<H',ref,k)[0]+32768)%65536)-32768 for k in slots[name]}
            if len(deltas)==1:hits.append((p,deltas.pop(),raw))
        p=v.find(ref[:3],p+1)
    return hits
versions={r['label']:r for r in csv.DictReader(trig.open())};rows=[];edits=[];instructions=[]
for label in ('10','11','12','15','17','18','19','20'):
    path=root/('N3D-'+label)/'unpacked_image.bin';v=path.read_bytes();vr=versions[label];assert sha(v)==vr['image_sha256'];dsbase=int(vr['inferred_ds_image_base']);found=[]
    for name,a,n in spec:
        hits=matches(v,name,a,n);assert len(hits)==1,(label,name,[(p,d) for p,d,raw in hits]);p,delta,raw=hits[0];found.append((p,delta))
        l=list(Decoder(16,b[a:a+n],ip=0));r=list(Decoder(16,raw,ip=0));assert len(l)==len(r) and all((x.ip,x.len,x.flow_control)==(y.ip,y.len,y.flow_control) for x,y in zip(l,r))
        page=dsbase+0x12c+delta;assert v[page:page+4]==b'\x00\xa0\x00\xa4'
        rows.append(dict(label=label,image_sha256=sha(v),function=name,start=p,end_exclusive=p+n,raw_exact=raw==b[a:a+n],normalized_exact=True,operand_delta=delta,page_fields_image=page,page_fields_initial='A000,A400',range_sha256=sha(raw),ds_scope='DS base inherited from exact trig table/code inference; startup not independently proved'))
        for k in slots[name]:
            before=struct.unpack_from('<H',b,a+k)[0];after=struct.unpack_from('<H',raw,k)[0]
            if before!=after:edits.append(dict(label=label,function=name,relative_word_offset=k,canonical=before,version=after,delta=delta))
        for i in r:instructions.append(dict(label=label,function=name,relative_ip=i.ip,image_offset=p+i.ip,bytes=raw[i.ip:i.next_ip].hex(),instruction=fmt.format(i)))
    assert found[1][0]-found[0][0]==26 and found[0][1]==found[1][1]
w=win.read_bytes();ne=struct.unpack_from('<I',w,0x3c)[0];assert w[ne:ne+2]==b'NE';count=struct.unpack_from('<H',w,ne+0x1c)[0];tab=ne+struct.unpack_from('<H',w,ne+0x22)[0];shift=struct.unpack_from('<H',w,ne+0x32)[0];winhits=[];segments=[]
for index in range(count):
    sector,size,flags,alloc=struct.unpack_from('<4H',w,tab+index*8)
    if sector==0 or flags&1:continue
    p=sector<<shift;size=size or 65536;assert p+size<=len(w);segments.append(dict(segment=index+1,file_offset=p,size=size))
    for name,a,n in spec:
        for q,delta,raw in matches(w[p:p+size],name,a,n):winhits.append(dict(segment=index+1,offset=q,file_offset=p+q,function=name,operand_delta=delta,range_sha256=sha(raw)))
out.mkdir(parents=True,exist_ok=True)
for name,items in [('functions',rows),('operand_edits',edits),('instructions',instructions),('win_code_segments',segments)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(items[0]));wr.writeheader();wr.writerows(items)
s=dict(canonical_sha256=sha(b),labels=8,unique_dos_images=len({r['image_sha256'] for r in rows}),normalized_function_matches=len(rows),raw_exact_function_matches=sum(r['raw_exact'] for r in rows),operand_word_edits=len(edits),win110_sha256=sha(w),win_code_segments_scanned=len(segments),win110_same_template_matches=winhits,scope='two whole DOS bodies and local CFG byte parity after only decoded DS displacement edits; Win negative result limited to same template, no algorithm absence claim',runtime_tests=0,new_deep_verified_bytes=0)
s['inherited_ds_evidence_sha256']=sha(trig.read_bytes())
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
