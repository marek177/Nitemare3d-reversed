# -*- coding: utf-8 -*-

"""Prepare a text evidence delta against verified remote blob metadata. No remote write."""

import hashlib,json,sys

from pathlib import Path

r=Path(sys.argv[1]);out=r/'publication_worx_bank_20261112';out.mkdir(exist_ok=True)

sha=lambda x:hashlib.sha256(x).hexdigest();blob=lambda x:hashlib.sha1(b'blob '+str(len(x)).encode()+b'\0'+x).hexdigest()

remote=json.loads((r/'publication_remote_snapshot_worx_bank_20261112.json').read_text());prior={x['path']:x['git_blob_sha'] for x in remote['files']};prefix=remote['prefix']

summary=json.loads((r/'campaign_catalog/summary.json').read_text());latest='pass1_xms_move_request';check=json.loads((r/latest/'independent_partition_check.json').read_text());assert check['map_sha256']==summary['latest_pass1_map_sha256']

selected=set(r.glob('*.py'));selected.update(p for p in r.glob('*REPORT.md') if not any(s in p.name for s in ('PUBLICATION','HISTORY','BEFORE')));omitted=[]

for folder in r.iterdir():

    if not folder.is_dir() or folder.name.startswith('publication') or '_attempt' in folder.name:continue

    if folder.name.startswith('dosbox') and '_runtime' in folder.name and not(folder/'independent_verification.json').exists():continue

    for p in folder.iterdir():

        if not p.is_file() or p.suffix not in ('.csv','.json','.conf'):continue

        if p.name.startswith('noncode_intervals') and folder.name!=latest:continue

        raw=p.read_bytes()

        if p.name.startswith('cases') or (len(raw)>=500000 and folder.name!='campaign_catalog' and not(p.name.startswith('noncode_intervals') and folder.name==latest)):

            omitted.append(dict(path=p.relative_to(r).as_posix(),bytes=len(raw),sha256=sha(raw),reason='generated evidence; reproduce locally from scripts and exact input manifest'));continue

        selected.add(p)

selected.add(r/'bsf_candidate_paths.txt');selected.add(r/'palette_candidate_paths.txt')

for runtime_dir in r.glob('dosbox*'):

    if not runtime_dir.is_dir():continue

    proof_path=runtime_dir/'independent_verification.json'

    if not proof_path.exists():continue

    proof=json.loads(proof_path.read_text())

    for item in proof['files']:

        path=Path(item['path'])

        raw=path.read_bytes();assert sha(raw)==item['sha256']

        if path.suffix=='.bin':omitted.append(dict(path=str(path),bytes=len(raw),sha256=sha(raw),reason='raw runtime memory capture; regenerate with published harness; excluded binary'))



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



Current bounded catalog: {summary['functions']} functional ranges, {summary['independent_instruction_count']:,} instructions / {summary['independent_instruction_bytes']:,} code bytes, {summary['data_bytes_with_local_evidence']:,} typed data bytes across the full image. These are campaign bounds, not the complete game inventory. Controlled original-instruction replay: {summary['controlled_instruction_replay_cases']:,} cases plus separately counted direction-prefix cases. Natural original-EXE DOSBox-X scenarios: {summary['runtime_tests']}. Runtime scope: {summary['runtime_tests_scope']}. Mocked dependencies, seeded replays and matching data layouts do not prove full gameplay or Win16 behavior parity.



See CAMPAIGN_CONSOLIDATED_REPORT.md for the current thirteen-area table. Historical batch reports retain their original counts and publication notes; those notes are not current branch status. The latest GUARD_MAP_WRITER_REPORT.md resolves all four map endpoint targets with98native exact pre/post MOVBYTE pairs:49underlay restores044C and49occupancy writes06A9, GUARD24/actor168/A5 andGUARD25/actor174/A4, unchanged whole actor block and stack per store. New wholecaller04C70422 has683codeB/249instructions,6912controlledreplays with7stubbed dependencies; native endpoint06AD is mid-function, not a full GUARD return.108alreadytyped record bytes refined, no PASS1 promotion. EightDOSlabels/sevenimages match normalized687B caller/CFG, operand bindings not semantic parity. The previous PALETTE_EFFECT_NATIVE_REPORT.md resolves DAC227/235 writer: native reset0D29:16CA sets80/0 and writes235 then scene227 black, first tick decrements80to79; second retained scenario completes black/white/black through24originalOUT instructions, actual6bitDAC63white, native RNG1to2745024/AX41/countdown201 and EA0followup return. Two new boundedfunctions233codeB/77instructions and2288replays; eightDOSlabels share exact29B colourhelper and normalized205BflashCFG, masked operands not semantic parity. Four mapBYTE1 endpoint changes A4/A5 remain writer-unassigned. PASS1 UNKNOWN28 and DEEP0 unchanged. The previous SCHEDULER_FIRST_RUNTIME_REPORT.md confirms first native post-map scheduler entry-to-return0D29:16EA, due buckets1/1, world counter1to2, elapsed18/synchronized flip, deadlinesR0/2/2 and a visibleA000 VRAM world+HUD snapshot rendered with actual DAC. DAC227/235 differ from RAM and are unused in this frame; writer unknown. UNKNOWN28 remain unchanged: all four zero gaps end at paragraph boundaries, but padding semantics remain unproven;602exactCSabsolute references audited,9828context/index dependent accesses unclosed. A second explicit generated PNG is hash-verified; no host screenshot or independent pixel golden claimed. The previous NEWGAME_MAP_XMS_CACHE_REPORT.md confirms native map-init return and exact8192B MAP1 level0, reconstructs474B sound directory with68 changed negative-XMS-offset records and66allocations, adds2boundedfunctions/806replays and one retained native scenario. It corrects the legacy game_loop_entry marker:0D29:0A31 calls known music selector083D:288C, not the gameplay loop. First gameplay frame remains unverified. The previous XMS_REQUEST_RUNTIME_REPORT.md promotes16B from UNKNOWN to PARTIAL using original descriptor writers/consumer,2400replays and the first successful native XMS call return after New game/episode1/difficulty1; all57295NONCODE endpoint bytes are retained locally, without semantic closure. Episode selector adds256replays. The previous report reaches the original main menu through three real key waits and retains its414B descriptors, both VGA pages and DAC. Two new bounded functions and780replays cover menu descriptor selection and DOS2 USER.SAV header gating against five real candidate files. A generated menu PNG is a visualization of retained VGA planes/DAC, not a host screenshot or original distributed asset; it is separately blob-hash verified. Earlier reports reconstruct a WORX private-stack callback and timer dispatcher, with1152replays and two retained stack/frame scenarios. Only30direct data bytes are typed;512B full stack capacity remains a candidate. The explicit paused private-stack window did not reproduce a keyboard IRQ on that stack. Earlier reports reconstruct the original INT09h/IRQ1 handler, retains14336controlled replay cases and an actual AUTOTYPE make/break/BDA/wait/font1 scenario. Font1header11x11 differs from actual max10x10; its role remains open. Current campaign_catalog files are included despite the generic generated-table size cutoff. Earlier reports distinguish native programmed display-start from later latched real-start, verify all used CD image colors at6bit DAC precision, and refine the font0 buffer plus128runtime FAR pointers. Earlier new reports cover the UIF bitmap group, DOS/Win16 palettes, sound directory and CPU trace, optional CD PCX decoder, column blitter, original-DOSBox four-plane back-buffer readback and eight-label DOS comparison. Earlier reports cover RNG/damage, scheduler/audio/VGA, CRT/heap/startup/FCB and BSF assets. Every open issue remains explicit; no new semantic percentage is invented without a full denominator.



Reproduction requires exact user-supplied files and historical inventories pinned by path and SHA in scripts. PUBLICATION_OMITTED_GENERATED.json records hashes and sizes for bulky generated evidence. Sources in dos_parse_reference/source_manifest.json are external Microsoft MS-DOS reference snapshots, retrieved from pinned URLs and hash-checked; their implementation is not the user's running DOS. This evidence publication excludes their complete source files; retrieve them from that manifest when needed.



Runtime proofs pin local raw capture paths. Raw memory dumps and original assets are excluded; regenerate them with runtime_dosbox_startup.py or the per-scenario runtime_watch scripts and their matching independent verifier using the pinned original files and DOSBox-X binary. Included .conf files record the capture settings, not portable absolute paths.\n\nPUBLICATION_DELTA_MANIFEST.json covers this update's changed content. Previously published files are retained. No PE32 port is included.

'''

readme = '# Latest batch: original GUARD validator and door predicates\n\nSee [GUARD_VALIDATOR_REPORT.md](GUARD_VALIDATOR_REPORT.md). Four newly bounded functions, 10472 controlled cases without failure, one sparse native allowed/blocked return scenario. Catalogue150 functions/15846 instruction bytes/1013689 controlled cases/27 native scenarios; BSS tables4566 bytes. PASS1 unchanged: PARTIAL57118, CLASSIFIED ONLY149, UNKNOWN28, DEEP0. Two 256-byte classification tables are BSS, not new original NONCODE coverage. Blocked snapshot door7 state2 does not establish its entry state or interaction transition. Prior sections below are historical.\n\n' + readme
readme = '# Latest batch: whole door interaction and real DOS version difference\n\nSee [DOOR_INTERACTION_REPORT.md](DOOR_INTERACTION_REPORT.md). Native whole original0598 call proves source door7 and neighbor6 state1-to2 with exact2BYTE world delta and unchanged57392B DGROUP. Original-code replay matches final registers/data without executed stubs.8192 DOS2 controlled cases/all126 instruction starts;64 separate cross-version cases prove early DOS10/11/12 propagate state4 while15/17/18/19/20 return early. Catalogue151 functions/16208 instruction bytes/1021881 DOS2 controlled cases/28 native scenarios. PASS1 unchanged; no new DEEP bytes. Prior sections are historical.\n\n' + readme
readme = '# Latest batch: MAP classification producers and omitted RTC target\n\nSee [CLASSIFICATION_PRODUCERS_REPORT.md](CLASSIFICATION_PRODUCERS_REPORT.md). Two original no-argument table generators retain local bit80h;1088 controlled calls check278528 entries. Separate native run verifies MAP1header514B identity and512generated flags with inherited seeds0/7. Second call additionally has cached clockDWORD+1; original RTC handler identified and controlled-tested100cases, but native writerPC is not captured. Handler20instruction starts were absent from old inventory and outside original NONCODE.24DOS CFG/normalized comparisons match. Catalogue154functions/16557instructionB/1023069DOS2cases/29native scenarios/BSS5080B. PASS1 unchanged, DEEP0. Prior sections are historical.\n\n' + readme
readme = '# Latest batch: remaining-reference context and WORX register bank\n\nSee [WORX_REGISTER_BANK_REPORT.md](WORX_REGISTER_BANK_REPORT.md). Raw1812D mask-reference candidate lies across sound-bank record boundaries; original128x11 loader/consumer validated.6166 controlled calls cover five functions, two previously owned helpers retained without duplicate count. Three new functions140instructions/283B,1435new filedataB outside originalNONCODE.40DOS CFG/normalized comparisons and8whole-bank byte matches. Catalogue157functions/16840instructionB/59469filedataB/1029235controlled executions,29native scenarios. No native audio test added; PASS1 unchanged,DEEP0. Prior sections historical.\n\n' + readme
raw=readme.encode('utf-8');entries.append(dict(path=prefix+'README.md',content=readme,mode='100644',type='blob'));manifest.append(dict(path='README.md',bytes=len(raw),sha256=sha(raw),git_blob_sha=blob(raw)))

preview=json.loads((r/'main_menu_runtime_fields/generated_preview_manifest.json').read_text());preview_raw=(r/preview['path']).read_bytes();assert sha(preview_raw)==preview['sha256'] and blob(preview_raw)==preview['git_blob_sha']

entries.append(dict(path=prefix+preview['path'],sha=preview['git_blob_sha'],mode='100644',type='blob'));manifest.append(dict(path=preview['path'],bytes=len(preview_raw),sha256=preview['sha256'],git_blob_sha=preview['git_blob_sha'],kind='derived_runtime_preview_not_original_asset'))

preview2=json.loads((r/'scheduler_runtime_fields/generated_preview_manifest.json').read_text());preview2_raw=(r/preview2['path']).read_bytes();assert sha(preview2_raw)==preview2['sha256'] and blob(preview2_raw)==preview2['git_blob_sha']

entries.append(dict(path=prefix+preview2['path'],sha=preview2['git_blob_sha'],mode='100644',type='blob'));manifest.append(dict(path=preview2['path'],bytes=len(preview2_raw),sha256=preview2['sha256'],git_blob_sha=preview2['git_blob_sha'],kind='derived_runtime_preview_not_original_asset'))

for name,data in [('PUBLICATION_DELTA_MANIFEST.json',manifest),('PUBLICATION_OMITTED_GENERATED.json',omitted)]:entries.append(dict(path=prefix+name,content=json.dumps(data,indent=2)+'\n',mode='100644',type='blob'))

payload=json.dumps(entries,ensure_ascii=True,separators=(',',':'));(out/'payload.json').write_text(payload,encoding='ascii')

chunks=[payload[i:i+60000] for i in range(0,len(payload),60000)]

for i,text in enumerate(chunks):(out/('transfer_%03d.json'%i)).write_text(json.dumps(text),encoding='ascii')

(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(out/'omitted.json').write_text(json.dumps(omitted,indent=2)+'\n')

meta=dict(repository='marek177/Nitemare3d-reversed',branch='codex/final-re-completeness-20261111',parent_commit=remote['commit'],base_tree=remote['tree'],prefix=prefix,entries=len(entries),content_entries=len(manifest),unchanged_selected_files=unchanged,serialized_characters=len(payload),payload_sha256=sha(payload.encode('ascii')),transfer_chunks=len(chunks),latest_map=latest+'/noncode_intervals.csv',latest_map_sha256=check['map_sha256'],status_bytes=c)

(out/'meta.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2))





