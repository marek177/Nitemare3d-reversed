"""Extract unresolved control sites and verify a guarded callback source window.
Usage: python audit_win110_callback_slots.py EXE CFG_DIR FIXUP_DIR OUT_DIR
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
exe,cfg,fix,out=map(Path,sys.argv[1:]);out.mkdir(parents=True,exist_ok=True)
b=exe.read_bytes();sha=hashlib.sha256(b).hexdigest()
assert sha=='12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481'
word=lambda p:struct.unpack_from('<H',b,p)[0]
ne=struct.unpack_from('<I',b,60)[0];table=ne+word(ne+34);shift=word(ne+50)
def segment(n):
    sector,length,flags,alloc=struct.unpack_from('<4H',b,table+8*(n-1))
    assert sector
    return sector<<shift,length or 65536,flags,alloc
assert word(ne+14)==10 and word(ne+26)==10
off,size,flags,alloc=segment(10);raw=b[off+0x20d0:off+0x20dc];assert raw==bytes(12)
rows=lambda p:list(csv.DictReader(p.open(encoding='utf-8-sig',newline='')))
ins={(int(r['segment']),int(r['offset'])):r for r in rows(cfg/'instructions.csv')}
checks={0x382f:'16',0x3830:'1f',0x3831:'8b0ed220',0x3835:'e329',0x3849:'ff1ed020',0x385c:'ff1ed020',0x396b:'8b0ed220',0x396f:'e307',0x3974:'ff1ed020'}
for ip,expected in checks.items():assert ins[2,ip]['bytes']==expected,(hex(ip),ins[2,ip]['bytes'])
fixups=rows(fix/'expanded_sites.csv')
overlap=[r for r in fixups if int(r['segment'])==10 and int(r['source_offset'])<0x20dc and int(r['source_offset'])+int(r['width'])>0x20d0]
assert not overlap
sites=[]
for e in rows(cfg/'edges.csv'):
    if not e['kind'].startswith('unresolved_indirect'):continue
    i=ins[int(e['source_segment']),int(e['source_offset'])]
    context='UNRESOLVED'
    if int(i['segment'])==2 and int(i['offset'])==0x3849:context='DS=SS via PUSH SS/POP DS at 2:382F..3830; runtime SS selector unresolved'
    elif int(i['segment'])==2 and int(i['offset'])==0x385c:context='DS preservation across callback 2:3849 required; not proven'
    elif int(i['segment'])==2 and int(i['offset'])==0x3974:context='incoming DS; no local assignment before call'
    sites.append(dict(segment=i['segment'],offset=i['offset'],bytes=i['bytes'],instruction=i['instruction'],owner_roots=i['owner_roots'],segment_context=context,status='PARTIAL',target_set='UNKNOWN'))
with (out/'indirect_sites.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(sites[0]));w.writeheader();w.writerows(sites)
evidence=dict(exe_sha256=sha,ne_automatic_data_segment=10,ne_initial_stack_segment=10,ne_initial_sp=word(ne+24),data_segment_index=10,data_start=0x20d0,data_end_exclusive=0x20dc,data_file_offset=off+0x20d0,initial_bytes=raw.hex(),initial_bytes_sha256=hashlib.sha256(raw).hexdigest(),loader_fixup_overlap=len(overlap),checked_instruction_sites=len(checks),indirect_control_sites=len(sites),callback_pointer_candidate='DS:20D0 offset WORD + DS:20D2 selector WORD',first_guard='2:3835 JCXZ 3860 skips both callback sites when loaded selector word is zero',cleanup_guard='2:396F JCXZ 3978 skips callback when incoming DS:20D2 is zero',global_writes_excluded=False,callback_abi_closed=False,closed_indirect_targets=0,new_deep_verified_bytes=0,runtime_tests=0)
(out/'summary.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8');print(json.dumps(evidence,indent=2))
