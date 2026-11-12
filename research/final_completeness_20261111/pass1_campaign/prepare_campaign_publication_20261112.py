# -*- coding: utf-8 -*-
"""Prepare a text evidence delta against verified remote blob metadata. No remote write."""
import hashlib,json,sys
from pathlib import Path
r=Path(sys.argv[1]);out=r/'publication_update_20261112';out.mkdir(exist_ok=True)
sha=lambda x:hashlib.sha256(x).hexdigest();blob=lambda x:hashlib.sha1(b'blob '+str(len(x)).encode()+b'\0'+x).hexdigest()
remote=json.loads((r/'publication_remote_snapshot_20261112.json').read_text());prior={x['path']:x['git_blob_sha'] for x in remote['files']};prefix=remote['prefix']
summary=json.loads((r/'campaign_catalog/summary.json').read_text());latest='pass1_fcb_prefix';check=json.loads((r/latest/'independent_partition_check.json').read_text());assert check['map_sha256']==summary['latest_pass1_map_sha256']
selected=set(r.glob('*.py'));selected.update(p for p in r.glob('*REPORT.md') if not any(s in p.name for s in ('PUBLICATION','HISTORY','BEFORE')));omitted=[]
for folder in r.iterdir():
    if not folder.is_dir() or folder.name.startswith('publication'):continue
    for p in folder.iterdir():
        if not p.is_file() or p.suffix not in ('.csv','.json'):continue
        if p.name.startswith('noncode_intervals') and folder.name!=latest:continue
        raw=p.read_bytes()
        if p.name.startswith('cases') or (len(raw)>=500000 and not(p.name.startswith('noncode_intervals') and folder.name==latest)):
            omitted.append(dict(path=p.relative_to(r).as_posix(),bytes=len(raw),sha256=sha(raw),reason='generated evidence; reproduce locally from scripts and exact input manifest'));continue
        selected.add(p)
selected.add(r/'bsf_candidate_paths.txt')
entries=[];manifest=[];unchanged=0
for p in sorted(selected):
    raw=p.read_bytes();name=p.relative_to(r).as_posix();text=raw.decode('utf-8-sig')
    # Preserve BOM when present: blob hashing and uploaded bytes must be identical.
    if raw.startswith(b'\xef\xbb\xbf'):text='\ufeff'+text
    assert text.encode('utf-8')==raw
    if prior.get(name)==blob(raw):unchanged+=1;continue
    entries.append(dict(path=prefix+name,content=text,mode='100644',type='blob'));manifest.append(dict(path=name,bytes=len(raw),sha256=sha(raw),git_blob_sha=blob(raw)))
c=check['status_bytes'];readme=f'''# Nitemare 3D evidence campaign — 2026-11-12 snapshot

The campaign is incomplete. This update extends verified commit {remote['commit']} without deleting historical evidence. No original game executable, complete asset, native decoder or emulator binary is included.

Current historical PASS320 NON-CODE map: `{latest}/noncode_intervals.csv` and `.json`, exactly 57,295 bytes: PARTIAL {c['PARTIAL']:,}; CLASSIFIED ONLY {c['CLASSIFIED ONLY']:,}; UNKNOWN {c['UNKNOWN']}; DEEP VERIFIED 0. SHA-256 `{check['map_sha256']}`. Independent partition checks prove membership, hashes and no gaps/overlaps; they do not prove complete semantics.

Current bounded catalog: {summary['functions']} functional ranges, {summary['independent_instruction_count']:,} instructions / {summary['independent_instruction_bytes']:,} code bytes, {summary['data_bytes_with_local_evidence']:,} typed data bytes across the full image. These are campaign bounds, not the complete game inventory. Controlled original-instruction replay: {summary['controlled_instruction_replay_cases']:,} cases plus separately counted direction-prefix cases. Natural DOSBox-X/game runtime: zero. Mocked dependencies, seeded replays and matching data layouts do not prove full gameplay or Win16 behavior parity.

See CAMPAIGN_CONSOLIDATED_REPORT.md for the current thirteen-area table. Historical batch reports retain their original counts and publication notes; those notes are not current branch status. New reports cover RNG/damage, scheduler/audio/VGA, CRT/heap/startup/FCB, actual BSF assets and DOS-version comparisons. Every open issue remains explicit; no new semantic percentage is invented without a full denominator.

Reproduction requires exact user-supplied files and historical inventories pinned by path and SHA in scripts. PUBLICATION_OMITTED_GENERATED.json records hashes and sizes for bulky generated evidence. Sources in dos_parse_reference/source_manifest.json are external Microsoft MS-DOS reference snapshots, retrieved from pinned URLs and hash-checked; their implementation is not the user's running DOS. This text-only publication excludes their complete source files; retrieve them from that manifest when needed.

PUBLICATION_DELTA_MANIFEST.json covers this update's changed content. Previously published files are retained. No PE32 port is included.
'''
raw=readme.encode('utf-8');entries.append(dict(path=prefix+'README.md',content=readme,mode='100644',type='blob'));manifest.append(dict(path='README.md',bytes=len(raw),sha256=sha(raw),git_blob_sha=blob(raw)))
for name,data in [('PUBLICATION_DELTA_MANIFEST.json',manifest),('PUBLICATION_OMITTED_GENERATED.json',omitted)]:entries.append(dict(path=prefix+name,content=json.dumps(data,indent=2)+'\n',mode='100644',type='blob'))
payload=json.dumps(entries,ensure_ascii=True,separators=(',',':'));(out/'payload.json').write_text(payload,encoding='ascii')
chunks=[payload[i:i+60000] for i in range(0,len(payload),60000)]
for i,text in enumerate(chunks):(out/('transfer_%03d.json'%i)).write_text(json.dumps(text),encoding='ascii')
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(out/'omitted.json').write_text(json.dumps(omitted,indent=2)+'\n')
meta=dict(repository='marek177/Nitemare3d-reversed',branch='codex/final-re-completeness-20261111',parent_commit=remote['commit'],base_tree=remote['tree'],prefix=prefix,entries=len(entries),content_entries=len(manifest),unchanged_selected_files=unchanged,serialized_characters=len(payload),payload_sha256=sha(payload.encode('ascii')),transfer_chunks=len(chunks),latest_map=latest+'/noncode_intervals.csv',latest_map_sha256=check['map_sha256'],status_bytes=c)
(out/'meta.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2))
