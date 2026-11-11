"""python prepare_campaign_publication.py OUTPUTS_DIR; prepare text-only delta, no remote writes."""
import ast,hashlib,json,re
from pathlib import Path
import sys
r=Path(sys.argv[1]);dest=r/'publication_update';dest.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
blob=lambda b:hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
folders=set()
for n in ast.walk(ast.parse((r/'independent_decode_and_catalog.py').read_text())):
    if isinstance(n,ast.Constant) and isinstance(n.value,str):
        d=n.value.split('/')[0]
        if re.fullmatch('[A-Za-z0-9_]+',d) and (r/d).is_dir():folders.add(d)
folders.update(['trig_cross_version','win110_trig_callers','crt_unloaded_hooks','direction_index_replay','runtime_bundle_probe','win110_fixups'])
selected=set();omitted=[]
for d in folders:
    for p in (r/d).glob('*'):
        if not p.is_file() or p.suffix not in ['.csv','.json']:continue
        if p.name.startswith('noncode_intervals'):continue
        if p.name.startswith('cases') or p.stat().st_size>=500000:
            omitted.append(dict(path=p.relative_to(r).as_posix(),sha256=sha(p.read_bytes()),bytes=p.stat().st_size,reason='generated bulky evidence; reproduce using published script'))
        else:selected.add(p)
selected.update(r.glob('*.py'))
selected.update(p for p in r.glob('*REPORT.md') if not any(x in p.name for x in ['PUBLICATION','HISTORY','BEFORE']))
selected.update([r/'pass1_episode_files/noncode_intervals.csv',r/'pass1_episode_files/noncode_intervals.json'])
old={x['path']:x for x in json.loads((r/'CONSOLIDATION_PUBLICATION_META.json').read_text())}
entries=[];manifest=[]
prefix='research/final_completeness_20261111/pass1_campaign/'
for p in sorted(selected):
    raw=p.read_bytes();name=p.relative_to(r).as_posix()
    if name in old and old[name]['sha256']==sha(raw):continue
    content=raw.decode('utf-8');assert content.encode('utf-8')==raw
    entries.append(dict(path=prefix+name,content=content,mode='100644',type='blob'))
    manifest.append(dict(path=name,bytes=len(raw),sha256=sha(raw),git_blob_sha=blob(raw)))
s=json.loads((r/'campaign_catalog/summary.json').read_text())
readme='''# Nitemare 3D evidence campaign snapshot

This publication extends commit a43690cac60dea52020b557c733c239504ba9bf1. The campaign is incomplete. No original game executable, asset, native decoder or emulator binary is included.

Current NON-CODE map: `pass1_episode_files/noncode_intervals.csv` and `.json`, exactly 57,295 baseline bytes: PARTIAL 54,746; CLASSIFIED ONLY 2,505; UNKNOWN 44; DEEP VERIFIED 0. See `CAMPAIGN_CONSOLIDATED_REPORT.md` for current scope and the thirteen-area report. Historical batch reports retain the state and publication notes at their original analysis time; those notes are not current branch status.

Current bounded function catalog: 48 ranges, 1,691 instructions / 4,028 code bytes; 55,592 typed data bytes across the whole image. These are campaign bounds, not an inventory of every game function. Controlled replay: 7,909 cases plus a separate 65,548-case normalization-prefix campaign. Original DOSBox-X/game runtime tests: zero. A mock, fixture, seeded replay or chunk parser never proves full gameplay parity.

New findings include the real MAP.1 count of eleven levels, conditional music-table cross-row access, signed-only upper level guard, audio selectors/loader/toggles, DOS I/O wrappers, Win110 relocation-backed trig callers and corrected angle-function boundary. Follow individual reports for limitations.

Reproduction requires the exact user-supplied game files and historical inventories pinned in the scripts. The latest map has an independent membership/hash/overlap check. Full generated case dumps can be regenerated; `PUBLICATION_OMITTED_GENERATED.json` records their local hashes and sizes. Existing remote files are retained, including older snapshots. Publication manifests cover this delta only, and do not assert semantic completeness.
'''
raw=readme.encode();entries.append(dict(path=prefix+'README.md',content=readme,mode='100644',type='blob'));manifest.append(dict(path='README.md',bytes=len(raw),sha256=sha(raw),git_blob_sha=blob(raw)))
for name,data in [('PUBLICATION_DELTA_MANIFEST.json',manifest),('PUBLICATION_OMITTED_GENERATED.json',omitted)]:
    content=json.dumps(data,indent=2)+'\n';entries.append(dict(path=prefix+name,content=content,mode='100644',type='blob'))
payload=json.dumps(entries,ensure_ascii=True,separators=(',',':'));(dest/'payload.json').write_text(payload,encoding='ascii')
chunks=[payload[i:i+90000] for i in range(0,len(payload),90000)]
for i,c in enumerate(chunks):(dest/('transfer_%03d.json'%i)).write_text(json.dumps(c),encoding='ascii')
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(dest/'omitted.json').write_text(json.dumps(omitted,indent=2)+'\n')
meta=dict(entries=len(entries),verified_content_entries=len(manifest),serialized_characters=len(payload),transfer_chunks=len(chunks),payload_sha256=sha(payload.encode('ascii')),parent_commit='a43690cac60dea52020b557c733c239504ba9bf1',base_tree='fb5fd44edb00a3fb9f810d9a6b81bc6234e918ad',repository='marek177/Nitemare3d-reversed',branch='codex/final-re-completeness-20261111')
(dest/'meta.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))
