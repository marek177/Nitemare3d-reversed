"""Resolve Win1.10 NE raw records into bounded source sites and symbolic imports.
Usage: python expand_win110_fixups.py WIN110_EXE DECODER_DIR OUT_DIR
No Windows loader execution or runtime selector assignment is performed.
"""
import csv,collections,hashlib,json,struct,sys
from pathlib import Path

def need(ok,msg):
    if not ok:raise ValueError(msg)
def u16(b,p):need(0<=p<=len(b)-2,'word bounds');return struct.unpack_from('<H',b,p)[0]
def csvout(p,rows,fields=None):
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    path,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep))
    from iced_x86 import Decoder,Formatter,FormatterSyntax
    b=path.read_bytes();digest=hashlib.sha256(b).hexdigest()
    need(digest=='12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481','wrong EXE')
    ne=struct.unpack_from('<I',b,0x3c)[0];need(b[ne:ne+2]==b'NE','not NE')
    count=u16(b,ne+0x1c);table=ne+u16(b,ne+0x22);shift=u16(b,ne+0x32)
    segments={}
    for i in range(1,count+1):
        sector,length,flags,minimum=struct.unpack_from('<4H',b,table+8*(i-1));offset=sector<<shift;size=(length or 65536) if sector else 0
        need(offset+size<=len(b),'segment bounds');segments[i]=dict(offset=offset,size=size,flags=flags,raw=b[offset:offset+size] if sector else b'')
    imports=ne+u16(b,ne+0x2a);module_table=ne+u16(b,ne+0x28);module_count=u16(b,ne+0x1e)
    def name_at(relative):
        p=imports+relative;need(0<=p<len(b),'import name bounds');n=b[p];need(p+1+n<=len(b),'import string bounds');return b[p+1:p+1+n].decode('ascii')
    modules={i:name_at(u16(b,module_table+2*(i-1))) for i in range(1,module_count+1)}
    sites=[];records=[];calls=[];seen_sites={};patched_bytes={};fmt=Formatter(FormatterSyntax.INTEL)
    for seg,s in segments.items():
        if not s['size'] or not s['flags']&0x100:continue
        p=s['offset']+s['size'];n=u16(b,p);p+=2;need(p+8*n<=len(b),'fixup records bounds')
        for rec_index in range(n):
            rec=b[p+8*rec_index:p+8*(rec_index+1)];stype,flags=rec[0],rec[1];source=u16(rec,2);a,c=u16(rec,4),u16(rec,6);kind=flags&3
            width={2:2,3:4,5:2}.get(stype&15);need(width is not None,'unsupported source type')
            if kind==0:
                targetseg=rec[4];need(rec[5]==0,'reserved internal target byte nonzero');need(targetseg!=255,'movable internal target requires entry-table resolution');need(targetseg in segments,'internal segment out of bounds')
                target=('internal_selector:%d'%targetseg) if stype&15==2 else 'internal_segment:%d+0x%04X'%(targetseg,c)
                module='';target_name='';ordinal=''
            elif kind in (1,2):
                need(a in modules,'module reference out of bounds');module=modules[a];ordinal=c if kind==1 else '';target_name=name_at(c) if kind==2 else '';target=module+(':#%d'%c if kind==1 else ':'+target_name);targetseg=''
            else:raise ValueError('unresolved OS fixup')
            chain=[];visited=set();current=source
            while current!=65535:
                need(current not in visited,'cycle in fixup chain');need(current+max(width,2)<=s['size'],'fixup source outside segment');visited.add(current)
                key=(seg,current);need(key not in seen_sites,'duplicate source fixup site');seen_sites[key]=(rec_index,target)
                for byte in range(current,current+width):
                    need((seg,byte) not in patched_bytes,'overlapping fixup write footprints')
                    patched_bytes[(seg,byte)]=(rec_index,current)
                following=u16(s['raw'],current);site=dict(segment=seg,record_index=rec_index,chain_index=len(chain),source_offset=current,file_offset=s['offset']+current,width=width,source_type=stype,target_kind=kind,target=target,module=module,ordinal=ordinal,name=target_name,initial_bytes=s['raw'][current:current+width].hex(),next_source_offset=None if flags&4 else following,status='PARTIAL',runtime_selector='UNRESOLVED')
                sites.append(site);chain.append(current)
                # A relocation-backed FAR opcode is a candidate instruction, not a CFG proof.
                start=current-1 if stype&15==3 else current-3 if stype&15==2 else -1
                if start>=0 and s['raw'][start] in (0x9a,0xea):
                    ins=Decoder(16,s['raw'][start:start+5],ip=start).decode()
                    if not ins.is_invalid and ins.len==5:
                        effective_offset=u16(s['raw'],start+1) if stype&15==2 else c if kind==0 else ''
                        inside=(effective_offset<segments[targetseg]['size']) if targetseg!='' and segments[targetseg]['size'] else None
                        target_class=('DATA' if segments[targetseg]['flags']&1 else 'CODE') if targetseg!='' else 'EXTERNAL_SYMBOL'
                        calls.append(dict(segment=seg,instruction_offset=start,opcode=s['raw'][start],file_offset=s['offset']+start,raw_instruction=s['raw'][start:start+5].hex(),decoded_unfixed=fmt.format(ins),fixup_source_offset=current,source_type=stype,target=target,effective_internal_segment=targetseg,effective_internal_offset=effective_offset,target_segment_flag_class=target_class,target_offset_inside_file_backed_segment=inside,scope='relocation-backed FAR CALL/JMP candidate; no reachability proof'))
                if flags&4:break
                current=following
            records.append(dict(segment=seg,record_index=rec_index,raw_hex=rec.hex(),source_type=stype,target_flags=flags,target=target,site_count=len(chain),additive=bool(flags&4),termination='additive_single_site' if flags&4 else 'FFFF',status='PARTIAL'))
    out.mkdir(parents=True,exist_ok=True)
    csvout(out/'expanded_sites.csv',sites);csvout(out/'record_chains.csv',records);csvout(out/'far_candidates.csv',calls)
    csvout(out/'modules.csv',[dict(module_index=i,name=n) for i,n in modules.items()])
    summary=dict(exe_sha256=digest,raw_records=len(records),expanded_source_sites=len(sites),unique_source_sites=len(seen_sites),unique_fixup_write_bytes=len(patched_bytes),overlapping_fixup_write_bytes=0,all_chains_terminate_within_segment=True,cycles=0,duplicate_source_sites=0,source_type_site_counts=dict(collections.Counter(str(x['source_type']) for x in sites)),target_kind_site_counts=dict(collections.Counter(str(x['target_kind']) for x in sites)),module_site_counts=dict(collections.Counter(x['module'] for x in sites if x['module'])),imported_by_name=sorted(set(x['target'] for x in sites if x['target_kind']==2)),far_opcode_candidates=len(calls),far_opcode_counts=dict(collections.Counter(hex(x['opcode']) for x in calls)),candidate_internal_offsets_outside_file_backed_segment=sum(x['target_offset_inside_file_backed_segment'] is False for x in calls),modules=modules,unresolved_runtime_selectors=True,unresolved_import_ordinal_names=True,new_deep_verified_bytes=0,runtime_tests=0,scope='Static NE chain expansion and symbolic bindings only; no proof of all executable callsites or Windows loader behavior')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
