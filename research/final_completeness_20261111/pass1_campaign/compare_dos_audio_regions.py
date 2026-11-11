"""Cross-version exact lookup and explicitly normalized bounded code regions.
Usage: python compare_dos_audio_regions.py ASM_ZIP DOS_BUILDS_CSV DECODER_DIR OUT_DIR
"""
import csv,hashlib,itertools,json,struct,sys,zipfile
from pathlib import Path
archive,buildcsv,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Register,Code
from cross_version_inputs import unpack
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(archive.read_bytes())=='b0e8b4d81cfbce9dcab4ee432aee6320080c35f6181fec8c585d4b7970a2bdb3'
builds=list(csv.DictReader(buildcsv.open(encoding='utf-8-sig')));regions=[];patches=[];tables=[];images={}
spec=[('sample_irq',0x3651,145),('pit_divisor_setter',0x466a,53),('callback_setter',0x389a,13),('timer_base_setter',0x34bb,6)]
with zipfile.ZipFile(archive) as z:
    for row in builds:
        label=row['archive_label'];exe=z.read(label+'/original.exe');assert sha(exe)==row['source_sha256']
        image,_=unpack(exe);assert sha(image)==row['image_sha256'];base=int(row['library_base']);delta=int(row['library_layout_delta']);images[label]=image
        rawtable=image[base+0x33b9+delta:base+0x34b9+delta];assert len(rawtable)==256
        tables.append(dict(label=label,image_start=base+0x33b9+delta,image_end_exclusive=base+0x34b9+delta,sha256=sha(rawtable),timer_base_initial=struct.unpack_from('<H',image,base+0x34b9+delta)[0]))
        for name,ip,length in spec:
            raw=image[base+ip+delta:base+ip+delta+length];norm=bytearray(raw);d=Decoder(16,raw,ip=ip+delta);count=0
            for ins in d:
                assert not ins.is_invalid;count+=1;loc=ins.ip-(ip+delta);c=d.get_constant_offsets(ins)
                if ins.segment_prefix==Register.CS and c.displacement_size==2:
                    pos=loc+c.displacement_offset;value=struct.unpack_from('<H',norm,pos)[0]
                    # This consumer displacement is a runtime-patched placeholder,
                    # not a build-layout pointer. Preserve its initial 5555h.
                    if name=='sample_irq' and loc==0x3e:
                        assert value==0x5555
                        continue
                    if delta:struct.pack_into('<H',norm,pos,(value-delta)&65535);patches.append(dict(label=label,region=name,region_byte=pos,kind='CS_displacement16',before=value,after=(value-delta)&65535))
                if name=='sample_irq' and ins.code==Code.ADD_AX_IMM16:
                    assert ins.immediate16==0x33b9+delta and c.immediate_size==2
                    pos=loc+c.immediate_offset
                    if delta:struct.pack_into('<H',norm,pos,0x33b9);patches.append(dict(label=label,region=name,region_byte=pos,kind='lookup_base_ADD_AX_imm16',before=ins.immediate16,after=0x33b9))
            regions.append(dict(label=label,region=name,image_start=base+ip+delta,length=length,instructions=count,layout_delta=delta,raw_sha256=sha(raw),normalized_sha256=sha(norm),status='PARTIAL'))
    reference=images['DOS_2.0'][0x18fa9:0x190a9];win=z.read('WIN_1.10/original.exe');assert sha(win)=='12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481'
    ne=struct.unpack_from('<I',win,60)[0];w=lambda p:struct.unpack_from('<H',win,p)[0];matches=[];scanned=[]
    for n in range(1,w(ne+28)+1):
        sector,size,flags,_=struct.unpack_from('<4H',win,ne+w(ne+34)+8*(n-1))
        if not sector:continue
        off=sector<<w(ne+50);size=size or 65536;assert off+size<=len(win);payload=win[off:off+size];scanned.append(dict(segment=n,file_offset=off,size=size))
        start=0
        while True:
            pos=payload.find(reference,start)
            if pos<0:break
            matches.append(dict(segment=n,offset=pos,file_offset=off+pos));start=pos+1
pairs=[]
for a,b in itertools.combinations(builds,2):
    la,lb=a['archive_label'],b['archive_label']
    for name,_,_ in spec:
        ra=next(r for r in regions if r['label']==la and r['region']==name);rb=next(r for r in regions if r['label']==lb and r['region']==name)
        pairs.append(dict(a=la,b=lb,region=name,raw_equal=ra['raw_sha256']==rb['raw_sha256'],normalized_equal=ra['normalized_sha256']==rb['normalized_sha256']))
out.mkdir(parents=True,exist_ok=True)
for name,rows,fields in [('tables.csv',tables,None),('regions.csv',regions,None),('normalization_patches.csv',patches,None),('pairs.csv',pairs,None),('win110_exact_matches.csv',matches,['segment','offset','file_offset'])]:
    with (out/name).open('w',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=fields or list(rows[0]));wr.writeheader();wr.writerows(rows)
r=dict(archive_sha256=sha(archive.read_bytes()),dos_labels=len(builds),unique_dos_exes=len({r['source_sha256'] for r in builds}),identical_lookup_tables=len({t['sha256'] for t in tables})==1,table_pair_comparisons=len(tables)*(len(tables)-1)//2,code_region_pair_comparisons=len(pairs),normalized_equal_pairs=sum(p['normalized_equal'] for p in pairs),raw_equal_pairs=sum(p['raw_equal'] for p in pairs),normalization_edits=len(patches),win110_scanned_segments=scanned,win110_exact_lookup_matches=len(matches),cross_version_behavior_proven=False,new_deep_verified_bytes=0,runtime_tests=0)
(out/'summary.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
