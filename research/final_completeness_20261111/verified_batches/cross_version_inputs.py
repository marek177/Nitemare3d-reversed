"""Reproduce 8 DOS images and authenticate Win1.10 NE segment exports.
Usage: python cross_version_inputs.py ASM_ZIP OLD_DOS_OUTPUTS WIN110_EXE OUT_DIR DECODER_DIR
Version names are supplied archive labels, not independently dated releases.
"""
import csv,hashlib,json,struct,sys,zipfile
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()
def require(ok,msg):
    if not ok:raise ValueError(msg)
def word(b,p):return struct.unpack_from('<H',b,p)[0]
def csvout(p,rows):
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def unpack(exe):
    require(exe[:2]==b'MZ','not MZ');header=word(exe,8)*16
    size=(word(exe,4)-1)*512+(word(exe,2) or 512);require(size==len(exe),'MZ length mismatch')
    b=exe[header:];stub=word(exe,22)*16
    ip,cs,_,_,sp,ss,paras,sig=struct.unpack_from('<8H',b,stub);require(sig==0x4252,'not expected EXEPACK')
    mem=bytearray(paras*16);src=stub-1;dst=len(mem)-1;trim=0;blocks=[]
    while src>=0 and trim<16 and b[src]==255:src-=1;trim+=1
    packed_end=src+1
    while True:
        require(src>=2,'source underflow');opcode=b[src];count=word(b,src-2);src-=3
        require(opcode&254 in (0xb0,0xb2) and count>0 and dst-count+1>=0,'bad command')
        start,end=dst-count+1,dst+1
        if opcode&254==0xb0:
            require(src>=0,'fill source underflow');mem[start:end]=bytes([b[src]])*count;src-=1
        else:
            require(src-count+1>=0,'literal source underflow');mem[start:end]=b[src-count+1:src+1];src-=count
        blocks.append((opcode,count,start,end));dst-=count
        if opcode&1:break
    require(src==dst,'prefix source/output mismatch');mem[:dst+1]=b[:src+1]
    encoded=bytearray(mem[:dst+1])
    for opcode,count,start,end in reversed(blocks):
        chunk=mem[start:end];encoded.extend(chunk[:1] if opcode&254==0xb0 else chunk);encoded.extend(struct.pack('<HB',count,opcode))
    require(encoded==b[:packed_end],'roundtrip mismatch')
    cursor=stub+0x132;rel=[]
    for group in range(16):
        n=word(b,cursor);cursor+=2
        for _ in range(n):
            off=word(b,cursor);cursor+=2;p=group*65536+off;require(p+2<=len(mem),'reloc bounds');rel.append(p)
    require(cursor==len(b) and len(rel)==len(set(rel)),'relocation boundary/uniqueness mismatch')
    return bytes(mem),dict(command_count=len(blocks),relocations=len(rel),trimmed_ff=trim,entry_cs=cs,entry_ip=ip,ss=ss,sp=sp)

def main():
    archive,old,winpath,out,decoder_dir=map(Path,sys.argv[1:]);out.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(decoder_dir))
    from iced_x86 import Decoder,Register,OpKind
    def normalized_dispatch(raw,delta):
        normalized=bytearray(raw);decoder=Decoder(16,raw,ip=0)
        for ins in decoder:
            require(not ins.is_invalid,'invalid dispatcher decode')
            if any(ins.op_kind(n)==OpKind.MEMORY for n in range(ins.op_count)) and ins.memory_segment==Register.CS:
                constants=decoder.get_constant_offsets(ins)
                require(constants.displacement_size==2,'unexpected CS displacement size')
                struct.pack_into('<H',normalized,ins.ip+constants.displacement_offset,(ins.memory_displacement-delta)&65535)
        return bytes(normalized)
    dos=[];segments=[];fixups=[]
    with zipfile.ZipFile(archive) as z:
        for label,folder in [('1.0','10'),('1.1','11'),('1.2','12'),('1.5','15'),('1.7','17'),('1.8','18'),('1.9','19'),('2.0','20')]:
            source=z.read('DOS_'+label+'/original.exe');mem,meta=unpack(source)
            old_image=(old/('N3D-'+folder)/'unpacked_image.bin').read_bytes()
            raw=z.read('DOS_'+label+'/load_image.bin')
            require(raw==source[word(source,8)*16:],'archive load-image mismatch')
            require(mem==old_image,'old image mismatch '+label)
            # Fingerprint-relative base hypothesis is accepted only with several distinct checks.
            pattern=bytes.fromhex('2eff94')
            hits=[i for i in range(len(mem)) if mem.startswith(pattern,i)]
            base=None;delta=None
            if len(hits)==1:
                shift=word(mem,hits[0]+3)-0x2020;candidate=hits[0]-0x3103-shift
                if shift in (0,4) and candidate>=0 and mem[candidate+shift+0x5998:candidate+shift+0x599c]==b'RIFF' and mem[candidate+shift+0x59bc:candidate+shift+0x59c0]==b'data' and mem[candidate+shift+0x4630:candidate+shift+0x4634]==bytes.fromhex('50528cc0'):
                    base=candidate;delta=shift
            table=mem[base+delta+0x2020:base+delta+0x20c4] if base is not None else b''
            normalized_table=b''.join(struct.pack('<H',(v-delta)&65535 if v else 0) for v in struct.unpack('<82H',table)) if table else b''
            dispatch=mem[base+delta+0x30e6:base+delta+0x3129] if base is not None else b''
            row=dict(archive_label='DOS_'+label,source_bytes=len(source),source_sha256=sha(source),image_bytes=len(mem),image_sha256=sha(mem),old_image_exact_match=True,roundtrip_exact=True,library_base=base,library_layout_delta=delta,service_table164_sha256=sha(table) if table else '',service_table164_normalized_sha256=sha(normalized_table) if table else '',dispatcher67_sha256=sha(dispatch) if dispatch else '',dispatcher67_normalized_sha256=sha(normalized_dispatch(dispatch,delta)) if dispatch else '',header44_sha256=sha(mem[base+delta+0x5998:base+delta+0x59c4]) if base is not None else '',**meta)
            dos.append(row)
        win=z.read('WIN_1.10/original.exe');require(win==winpath.read_bytes(),'local Win110 differs from archive')
        require(sha(win)=='12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481','unexpected Win110 identity')
        ne=struct.unpack_from('<I',win,0x3c)[0];require(win[ne:ne+2]==b'NE','not NE')
        count=word(win,ne+0x1c);table=ne+word(win,ne+0x22);shift=word(win,ne+0x32)
        for index in range(1,count+1):
            sector,length,flags,minimum=struct.unpack_from('<4H',win,table+8*(index-1));size=length or 65536;offset=sector<<shift
            backed=sector!=0;export='WIN_1.10/segments/SEG%02d.bin'%index
            exact=None;digest='';reloc_count=0
            if backed:
                require(offset+size<=len(win),'NE segment bounds');raw=win[offset:offset+size];digest=sha(raw)
                if export in z.namelist():exact=(raw==z.read(export));require(exact,'NE export mismatch')
                if flags&0x100:
                    p=offset+size;reloc_count=word(win,p);p+=2;require(p+8*reloc_count<=len(win),'NE fixup bounds')
                    for n in range(reloc_count):
                        rec=win[p+8*n:p+8*(n+1)];fixups.append(dict(segment=index,record_index=n,source_type=rec[0],target_flags=rec[1],source_offset=word(rec,2),target_word1=word(rec,4),target_word2=word(rec,6),raw_hex=rec.hex(),scope='raw fixup record only; source chains and imports not resolved'))
            segments.append(dict(segment=index,file_backed=backed,file_offset=offset if backed else None,length_word=length,file_data_bytes=size if backed else 0,minimum_allocation_word=minimum,minimum_allocation_interpreted=minimum or 65536,flags=flags,kind_from_NE_flag='DATA' if flags&1 else 'CODE',raw_sha256=digest,archive_export_exact_match=exact,raw_relocation_records=reloc_count,semantic_status='CLASSIFIED_ONLY'))
    csvout(out/'dos_builds.csv',dos);csvout(out/'win110_segments.csv',segments);csvout(out/'win110_raw_fixups.csv',fixups)
    pairs=[]
    for i,a in enumerate(dos):
        for b in dos[i+1:]:pairs.append(dict(a=a['archive_label'],b=b['archive_label'],same_exe=a['source_sha256']==b['source_sha256'],same_image=a['image_sha256']==b['image_sha256'],same_service_table164=(a['service_table164_sha256']==b['service_table164_sha256']) if a['library_base'] is not None and b['library_base'] is not None else None,same_service_table164_normalized=(a['service_table164_normalized_sha256']==b['service_table164_normalized_sha256']) if a['library_base'] is not None and b['library_base'] is not None else None,same_dispatcher67=(a['dispatcher67_sha256']==b['dispatcher67_sha256']) if a['dispatcher67_sha256'] and b['dispatcher67_sha256'] else None,same_dispatcher67_normalized=(a['dispatcher67_normalized_sha256']==b['dispatcher67_normalized_sha256']) if a['dispatcher67_sha256'] and b['dispatcher67_sha256'] else None,same_header44=(a['header44_sha256']==b['header44_sha256']) if a['header44_sha256'] and b['header44_sha256'] else None))
    csvout(out/'dos_exact_region_pairs.csv',pairs)
    summary=dict(archive=str(archive),archive_sha256=sha(archive.read_bytes()),DOS_builds=len(dos),all_DOS_roundtrip_and_reference_matches=True,DOS_library_base_matches=sum(x['library_base'] is not None for x in dos),DOS_pair_comparisons=len(pairs),win110_sha256=sha(win),win110_bytes=len(win),win110_NE_offset=ne,win110_entry_segment=word(win,ne+0x16),win110_entry_offset=word(win,ne+0x14),win110_segments=len(segments),win110_file_backed_segments=sum(x['file_backed'] for x in segments),win110_raw_fixup_records=len(fixups),win110_fixup_chains_resolved=False,behavioral_parity_proven=False,new_deep_verified_bytes=0,runtime_tests=0)
    summary['same_normalized_table_pairs']=sum(p['same_service_table164_normalized'] is True for p in pairs)
    summary['same_normalized_dispatcher_pairs']=sum(p['same_dispatcher67_normalized'] is True for p in pairs)
    summary['same_raw_header_pairs']=sum(p['same_header44'] is True for p in pairs)
    summary['same_raw_table_pairs']=sum(p['same_service_table164'] is True for p in pairs)
    (out/'cross_version_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
