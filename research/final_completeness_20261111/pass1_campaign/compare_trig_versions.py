"""python compare_trig_versions.py IMAGE OLD_OUTPUT_ROOT DECODER_DIR WIN110_EXE OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,root,dep,win,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,FlowControl
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
spec=[('sin',0xcfb2,76),('cos',0xcffe,76),('tangent_magnitude',0xd04a,76),('angle_lookup',0xd096,149)]
allowed={0x17e8,0x1950,0x1680,0x1ab8,0x189e,0x1a06,0x1736,0x1b6e,0x1954,0x1abc,0x17ec,0x1c24}
def slots(start,size):
    dec=Decoder(16,b[start:start+size],ip=0);result=[];pos=0
    for ins in dec:
        assert not ins.is_invalid;c=dec.get_constant_offsets(ins)
        for offset,length in [(c.displacement_offset,c.displacement_size),(c.immediate_offset,c.immediate_size)]:
            if length==2 and struct.unpack_from('<H',b,start+pos+offset)[0] in allowed:result.append(pos+offset)
        pos+=ins.len
    assert pos==size;return result
maskslots={name:slots(start,size) for name,start,size in spec}
def match(v,start,name,a,size):
    if start<0 or start+size>len(v):return None
    reference=b[a:a+size];candidate=v[start:start+size];masked={i+j for i in maskslots[name] for j in range(2)}
    if any(reference[i]!=candidate[i] for i in range(size) if i not in masked):return None
    deltas={((struct.unpack_from('<H',candidate,i)[0]-struct.unpack_from('<H',reference,i)[0]+32768)%65536)-32768 for i in maskslots[name]}
    return deltas.pop() if len(deltas)==1 else None
versions=[];edits=[];functions=[]
for label in ['10','11','12','15','17','18','19','20']:
    path=root/('N3D-'+label)/'unpacked_image.bin';v=path.read_bytes();table=v.find(b[0x28ef8:0x2911a]);assert table>=0 and v.find(b[0x28ef8:0x2911a],table+1)<0
    prefix=b[0xcfb2:0xcfba];p=v.find(prefix);groups=[]
    while p>=0:
        ds=[]
        for name,a,size in spec:
            q=p+a-0xcfb2;ds.append(match(v,q,name,a,size))
        if None not in ds and len(set(ds))==1:
            delta=ds[0];inferred_ds=table-(0x17e8+delta)
            if inferred_ds>=0 and inferred_ds%16==0:groups.append((p,delta,inferred_ds))
        p=v.find(prefix,p+1)
    assert len(groups)==1,(label,groups)
    codebase,delta,dsbase=groups[0]
    versions.append(dict(label=label,path=str(path),image_sha256=sha(v),table_image=table,table_bytes=546,code_group_image=codebase,operand_delta=delta,inferred_ds_image_base=dsbase,ds_scope='inferred from exact table and code references; not independent startup proof'))
    for name,a,size in spec:
        q=codebase+a-0xcfb2;candidate=v[q:q+size];reference=b[a:a+size]
        # Exact bytes outside decoded data-address slots also preserve branch encodings/CFG.
        functions.append(dict(label=label,function=name,start=q,end_exclusive=q+size,raw_exact=(candidate==reference),normalized_exact=True,operand_delta=delta,range_sha256=sha(candidate)))
        for i in maskslots[name]:
            before=struct.unpack_from('<H',reference,i)[0];after=struct.unpack_from('<H',candidate,i)[0]
            if before!=after:edits.append(dict(label=label,function=name,relative_word_offset=i,canonical_value=before,version_value=after,delta=delta))
        # Decode candidate independently: validity and relative instruction boundaries must agree.
        left=list(Decoder(16,reference,ip=0));right=list(Decoder(16,candidate,ip=0));assert len(left)==len(right)
        assert all(not y.is_invalid and x.ip==y.ip and x.len==y.len and x.flow_control==y.flow_control for x,y in zip(left,right))
winbytes=win.read_bytes();winhits={name:winbytes.find(b[a:a+size]) for name,a,size in spec};winhits['table546']=winbytes.find(b[0x28ef8:0x2911a])
ne=struct.unpack_from('<I',winbytes,0x3c)[0];assert winbytes[ne:ne+2]==b'NE'
count=struct.unpack_from('<H',winbytes,ne+0x1c)[0];segment_table=ne+struct.unpack_from('<H',winbytes,ne+0x22)[0];shift=struct.unpack_from('<H',winbytes,ne+0x32)[0]
win_table_segments=[];hit=winhits['table546']
if hit>=0:
    assert winbytes.find(b[0x28ef8:0x2911a],hit+1)<0
    for i in range(count):
        sector,size,flags,allocation=struct.unpack_from('<4H',winbytes,segment_table+i*8)
        if sector==0:continue
        start=sector<<shift;size=size or 65536
        if start<=hit and hit+546<=start+size:
            assert start+size<=len(winbytes)
            win_table_segments.append(dict(segment=i+1,file_start=start,file_bytes=size,flags=flags,is_data=bool(flags&1),table_offset=hit-start,table_end_exclusive=hit-start+546))
    assert len(win_table_segments)==1
win_helpers=[];win_edits=[];win_groups=[]
if win_table_segments:
    expected_delta=win_table_segments[0]['table_offset']-0x17e8
    for segment_index in range(count):
        sector,size,flags,allocation=struct.unpack_from('<4H',winbytes,segment_table+segment_index*8)
        if sector==0 or flags&1:continue
        file_start=sector<<shift;size=size or 65536;v=winbytes[file_start:file_start+size]
        prefix=b[0xcfb2:0xcfba];p=v.find(prefix)
        while p>=0:
            deltas=[match(v,p+a-0xcfb2,name,a,n) for name,a,n in spec]
            if all(d==expected_delta for d in deltas):win_groups.append((segment_index+1,p,file_start,v))
            p=v.find(prefix,p+1)
    assert len(win_groups)==1
    seg,base,file_start,v=win_groups[0]
    for name,a,size in spec:
        q=base+a-0xcfb2;reference=b[a:a+size];candidate=v[q:q+size]
        left=list(Decoder(16,reference,ip=0));right=list(Decoder(16,candidate,ip=0))
        assert len(left)==len(right) and all(not y.is_invalid and x.ip==y.ip and x.len==y.len and x.flow_control==y.flow_control for x,y in zip(left,right))
        win_helpers.append(dict(function=name,segment=seg,offset=q,end_exclusive=q+size,file_offset=file_start+q,normalized_exact=True,raw_exact=(reference==candidate),operand_delta=expected_delta,range_sha256=sha(candidate)))
        for i in maskslots[name]:
            before=struct.unpack_from('<H',reference,i)[0];after=struct.unpack_from('<H',candidate,i)[0]
            if before!=after:win_edits.append(dict(function=name,relative_word_offset=i,canonical_value=before,win16_value=after,delta=expected_delta))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('versions',versions),('functions',functions),('operand_edits',edits)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for name,rows in [('win110_functions',win_helpers),('win110_operand_edits',win_edits)]:
    if rows:
        with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(canonical_sha256=sha(b),version_labels=len(versions),unique_images=len({r['image_sha256'] for r in versions}),table_bytes_identical=546,normalized_function_comparisons=len(functions),raw_exact_function_comparisons=sum(r['raw_exact'] for r in functions),operand_word_edits=len(edits),win110_sha256=sha(winbytes),win110_raw_file_exact_pattern_first_offsets=winhits,win110_table_segments=win_table_segments,win110_auto_data_segment=struct.unpack_from('<H',winbytes,ne+14)[0],win110_normalized_helpers=len(win_helpers),win110_operand_word_edits=len(win_edits),win_scope='exact table and normalized local helper CFG/body parity; natural selector/caller behavior unverified',runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
