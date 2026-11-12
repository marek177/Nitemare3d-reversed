# Whole music resource replacement and original WORX bank copy

## Evidence and reproducibility

Reference: original DOS2 packed N3D-UNFU.exe, SHA256 552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301. Reproduced image e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297. SND.DAT SHA256 f3434984d315531602d32285cb8ff55990bba786f5fb37f53710e88379388614. No executable or asset bytes patched for native capture. Native v2 harness and independent verifier pin source, emulator, command transcript and capture hashes. Failed v1 stalled on a stale return breakpoint and contributes zero native tests; v2 resumes these breakpoints and gives every pointer snapshot a unique name.

Reproduce with runtime_watch_music_resource_pair_v2.py and verify_music_resource_pair_capture.py (argument contracts in their headers), audit_replay_music_snd_reader.py and audit_replay_worx_bank_original_resolver.py. Native directory dosbox_music_resource_pair_runtime_v2 contains independent_verification.json, verification_metrics.json, payload_bindings.csv, reader_bindings.csv and bank_RAM_residuals.csv. Raw native RAM/source binaries remain local and are hash-pinned, not published. Controlled fixtures are distinguished below.

## Newly bounded reader and CRT contracts

0277:008A..00EB, image [027FA,0285B), is a 97B/32-start FAR SND reader. Arguments are FAR destination at BP+6, DWORD file offset at BP+A and WORD count at BP+E. It leaves argument cleanup to caller. DS:01AC is a cached WORD handle (image [278BC,278BE)); DS:01AE is the eight-byte snd.dat NUL string ([278BE,278C6)). These were already typed/PARTIAL: no new file-data coverage is claimed.

Cached zero invokes CRT open 11EE:1C72 with mode8000h and near filename01AE, stores AX, and treats FFFFh as fatal. Open returning zero is accepted but reopens on the next call. An initially cached FFFFh bypasses open and is passed to seek/read. CRT seek11EE:1BD6 receives handle, signed DWORD offset, origin0; its return is ignored. CRT farread0FBA:009E receives handle/FAR destination/count. AX must equal requested count exactly; short or excess reported counts enter fatal0FBA:000C. Postfatal MOV SP,BP at0277:00B4 remains unexecuted and is not forced reachable.

Pseudocode: if cache==0: cache=open(filename,8000h); if cache==FFFFh: fatal(open_messages). seek(cache,offset,0); got=farread(cache,dest,count); if got!=count: fatal(read_messages); return FAR. Fatal return behavior is not reconstructed here. DS and SS may differ for this reader; the enclosing music caller's SS-local directory/DS reads are only naturally validated with DS=SS.

276 controlled cases cover cache/open0,5,FFFF, repeated calls, seek failure, exact/short/excess/zero read counts, two loads and DS/SS split. Original reader stores, return frames and full2MiB memory outside80 control-stack bytes match independent expectations. CRT response/data writes are explicit fixtures, not original reader stores or native DOS failure evidence.

## Native whole music ID0 then ID1

Both original 0C2B:0298..039D calls finish naturally. Four whole reader calls issue one CRT open, four seeks and four farreads: (offset,count)=(0,192),(960,3204),(0,192),(4164,20290). Native cached handle becomes5. All nine CRT entry/return argument frames and directory/payload bytes are checked. These are CRT API captures, not individual DOS INT21 instruction traces.

SND starts with32 records of WORD length and signed DWORD offset. ID0 payload is SND[3C0,1044),3204B, native3F96:0016, SHA25613f761cfe691e90555c276f67606ab2d627de6b76018e5fbf764699c582136f9. ID1 payload is SND[1044,5F86),20290B, native8D9B:0016, SHA256c97e7236b445656156714fed5556eb5f7a991a73d5669de29005bb1357ef04e0. MIDI header fields are format1/tracks19/division240; event interpretation, tempo, audible output and scheduling remain open.

DS:17D0 ([28EE0,28EE4)) retains old3F96:0016 through ID1 free/stop/directory/new malloc return; only subsequent original pointer stores install8D9B:0016. Old heap tag0C84 becomes0C85; the old3204B remain unchanged through ID1 return. Both new payloads remain identical before/after driver and at whole caller return. This establishes this observed replacement order, not all driver ownership or eventual reuse behavior.

## Actual bank copy and independent original-code replay

ID0 driver command39h naturally enters15BF:5973 and returns via5997 to3108. Source3F96:0016 is normalized by the ORIGINAL4630 helper to3F97:0006, then skips4 prefix bytes. The loader copies128 records,11B per16B source stride, to driver bank image[18103,18683). Prefix bytes are skipped, not validated by this loader. Final ES:DI=3F97:080A,SI=2A93,BX=128,CX=0,AX=0; NEAR return advances SP by2. DS=CS and SS is game stack.

Original loader+normalizer replay executes7716 instruction events/46 unique starts and1408 BYTE stores. All captured16 registers plus CF/DF match. Full640KiB native RAM matches replay with zero residual positions; independent2MiB model excludes72 stack bytes. Final1408B bank SHA256aa7f201844944b95f679270f9aa704cabed8126f31cb0f77ee7ef38319a9ae04;1181 positions differ from its captured before state. This closes the previous untrapped-copy-history gap for this scenario.

96 additional controlled original-loader+original-normalizer cases cover segment/offset normalization includingFFF0/FFFF, two loads, DF0/1 and arbitrary four-byte prefixes. No resolver/API/IRQ fixtures execute in these cases. Exact1408 ordered stores, complete memory outside72 stack bytes and frame/register effects match. This is 96 new controlled cases, not new functions: both bodies were already cataloged.

## Coverage update: 13 areas

Previous184 functions/8133 starts/20580 codeB/1066619 controlled cases/40 native scenarios. New185 functions/8165 starts/20677 codeB/1066991 controlled cases/41 native scenarios: +one97B reader, +276 reader cases,+96 original-resolver cases,+one independently verified native scenario. Native bank replay belongs to that verification, not another central case. Typed file data59469B and BSS5164B remain unchanged. Campaign UNKNOWN_CONTENT decreases91311 to91214 by the newly bounded97B code, not by historical NONCODE promotion. Reference census stays35813 because the new reader was already in historical inventory; central CSV and dependent reference/field hashes are regenerated in order.

Original PASS320 map unchanged:892 intervals,57295B =57118 PARTIAL+149 CLASSIFIED ONLY+28 UNKNOWN+0 DEEP VERIFIED. SHA256497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe. No new semantic percentages are invented; historical orientations below are estimates, not evidence-derived completion.

|Area|Previous orientation|New % / method|New confirmed findings|Unknowns / blockers|Next step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; bounded evidence does not close this area|Uncovered map replacement consumers|
|Data types and constants|95%|N/A; complete semantic denominator absent|Cached WORD handle, filename, FAR buffer and 32x6B SND directory bound to native reads|PARTIAL; bounded evidence does not close this area|Resolve remaining 149 classified-only and 28 unknown bytes through actual consumers|
|Tables and pointers|93%|N/A; complete semantic denominator absent|Actual bank copy entry/return; 128x11B projection and ID1 pointer replacement order|PARTIAL; bounded evidence does not close this area|Trace driver MIDI event consumers and buffer lifetime|
|Functions/ASM/CFG|90%|N/A; complete semantic denominator absent|97B/32-start reader; 276 reader cases plus 96 original-resolver bank cases|PARTIAL; bounded evidence does not close this area|Open fatal/callback bodies and remaining unknown functions|
|RNG|97%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; bounded evidence does not close this area|Capture RNG/DEMO ordering|
|Scheduler|96%|N/A; complete semantic denominator absent|Two whole music loader calls captured; no scheduler timing proof|PARTIAL; bounded evidence does not close this area|Capture natural resource replacement timing|
|DEMO/input|96%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; bounded evidence does not close this area|Capture actual DEMO playback|
|Renderer/VGA|94%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; bounded evidence does not close this area|Exercise clipped draws|
|GUARD/bosses|93%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; bounded evidence does not close this area|Uncovered boss/attack transitions|
|Weapons/projectiles|92%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; bounded evidence does not close this area|Original impact/damage lifecycle|
|Sprites/HUD/palette|92%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; bounded evidence does not close this area|Native populated cleanup/refill|
|SAVE/LOAD|92%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; bounded evidence does not close this area|Actual LOAD/reset ordering|
|Windows Win16|92%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; bounded evidence does not close this area|Locate Win16 resource-reader and driver counterparts|

All13 areas remain PARTIAL. Native source/data/entry-return proof is narrower than instruction replay of the entire music driver, audible playback, full gameplay or Win16 parity.

## Required next runtime tests

Trace positive MIDI entry0B7A through event consumption and subsequent buffer reuse; negative-offset0B25 path has no native witness here. Capture actual sound/tempo output with known MIDI events. Trace natural populated cleanup/LOAD/refill, callback setters and fatal handlers without forcing return. Continue177 remaining original NONCODE bytes through actual consumers, unknown functions, clipped renderer, GUARD/boss/projectile branches, RNG/DEMO/SAVE/LOAD and Win16 counterparts. No PE32 port performed.
