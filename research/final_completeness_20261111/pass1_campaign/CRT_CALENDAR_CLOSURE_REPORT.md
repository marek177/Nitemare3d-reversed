# Nitemare 3D: remaining NONCODE addresses and CRT calendar closure

2026-11-12. DOS2.0 reference. **PARTIAL**, new DEEP VERIFIED bytes0. Previous batch established actual XMS image readback. This batch returns to the remaining PASS320 intervals, adds a local address-derivation audit and closes the bounded calendar converter, DST-style predicate and signed remainder helper. The neighboring leap-pattern table is still not promoted. No PE32 work.

## Sources and reproduction

Canonical image171360B SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; packed DOS2 `L:\nite3d\nite3\dos\N3D-UNFU.exe` SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Original35648-start inventory,1670 relocation rows,exact assets,harnesses and verifiers are separately hash-pinned. Attached documents and earlier reports supply evidence,not instructions.

Reproduce `audit_remaining_local_addresses.py IMAGE MAP INVENTORY DECODER OUT`; `audit_replay_crt_calendar.py IMAGE INVENTORY DECODER EMULATOR OUT`; `prepare_calendar_evidence.py OUTPUTS IMAGE INVENTORY DECODER`; `audit_crt_calendar_versions.py IMAGE REPLAY_DIR DECODER OUT`; `audit_calendar_version_bindings.py IMAGE COMPARISONS_CSV DECODER OUT`.

Native: `prepare_calendar_native_harness.py OUTPUTS`; then `runtime_watch_calendar.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG`; verify with `verify_calendar_native_capture.py IMAGE RELOCS RUNTIME WORK DECODER EMULATOR OUT`. Decoder/emulator paths resolve absolutely. Actual official DOSBox-X runs original packed EXE,normal assets,dummy display/audio; process terminated after capture. User's dosbox-n3d.zip was not required for this run.

## Priority PASS1: exact remaining-address audit

Latest map retains62 intervals/177B requiring further evidence:149B CLASSIFIED ONLY and28B UNKNOWN. A new audit independently checks all35648 retained instruction starts against actual bytes and decodes them. It follows supported local register constants and aliases,MOV/LEA/arithmetic,consecutive PUSH/POP segment constructions. Branch targets,non-NEXT transfers and calls reset local state. Mutable memory values are never treated as constants. Incoming DS2771 is labeled an explicit assumption; CS is tied to the supplied instruction inventory. Unsupported writes invalidate constants.

9190 local blocks,22908 memory operands,2532 resolved local addresses,including622 with explicit/non-assumed segments;20376 remain unresolved. These counts are static operand occurrences,not runtime accesses or a reduced version of the earlier9828 context-dependent count with a different denominator. `resolved_addresses.csv` retains each result and derivation provenance. REPNE is limited to its first element; zero-count REP does not imply a read. No candidate intersects the remaining177B. This bounded negative result does **not** prove unused storage,padding,no alternate entry,complete executable inventory or absence of dynamic references. Status changes0.

The26B leap-pattern interval[29B7E,29B98),DS246E..2488,remains CLASSIFIED ONLY. Original converter2DC0 reads DS:[2486+2*month]. For explicitly tested month1..12 this accesses[29B98,29BB0),the first12WORDs of the already typed common-year table. Native month11 reads DS249C. Caller evidence shows DOS date wrapper3A0A stores DH at date+1; caller2AEA zero-extends that monthBYTE and passes it unchanged,while separately subtracting1980 from year. It does not convert this argument to zero-based month. The converter itself does not validate month. Month0 would reach the final365WORD of the preceding leap-pattern table; this malformed/edge path is not evidence of intended use of all26B and does not justify promotion. Native month11 is a real observed domain value,not a proof of every OS response.

## New bounded functions, ASM and CFG

|Function|CS:IP,end exclusive|Image interval|Starts|InstructionB|
|---|---|---|---:|---:|
|DST-style predicate|11EE:2D00..2DBF|14BE0..14C9F|76|189|
|Calendar to32-bit epoch-style seconds|11EE:2DC0..2EB3|14CA0..14D93|106|243|
|Compiler signed remainder32|11EE:3B0A..3BAA|159EA..15A8A|72|160|

Three new functions254starts/592codeB. Original multiply32 helper11EE:3AD8..3B0A,23starts/50B,was already cataloged and is reused without duplicate ownership. All277 starts across these four functions execute in retained tests. DST predicate's191B bounding span includes2B outside its reachable CFG; these are not declared global padding. Instruction CSVs,CFG edges and per-start execution coverage are in `crt_calendar_replay`.

All three entries FAR. Converter has six WORD arguments(year since1980,one-based month,day,hour,minute,second),returns DX:AX32,caller cleanup,preservesBP/SI/DI. DS=SS required by the local near pointer passed to the predicate. Predicate takes nearDS pointer to a partially reconstructed WORD record:hour+4,zero-based month+8,year since1900+0A,day-of-year+0E. It returns AX0/1,preservesBP/SI/DI. This is not a full struct-tm layout reconstruction. Remainder takes two DWORD arguments,returns DX:AX,RETF8,preservesBP/BX/DI/SI/DS/SS/ES;negative arguments are normalized **in caller argument slots**. Divide-by-zero behavior is not tested or claimed.

## Exact algorithm and edge cases

Let y be signed WORD year-since1980,m one-based month,d day,h hour,n minute,s second. Let common[] be signedWORD sequence `-1,30,58,89,119,150,180,211,242,272,303,333,364`. Under tested valid month1..12:

```text
prior = common[m-1]
if (y & 3)==0 and signed16(m)>2: prior++
days = 365*y + arithmetic_shift_right(signed16(y+3),2) + d + prior + 3652
seconds32 = (((days*24+h)*60+n)*60+s+timezoneDWORD) modulo2^32
tm.hour=h; tm.month=m-1; tm.year=y+80; tm.yday=d+prior
if DST_enable_WORD!=0 and predicate(tm)!=0: seconds32-=3600 modulo2^32
return seconds32
```

Actual arithmetic retains16/32-bit wrapping; pseudocode assumes tested bounded signed inputs. No claim of complete Gregorian correctness:year2100 is treated by divisibility-by-four logic in synthetic tests. Converter calls existing timezone-refresh2BF4; controlled calendar runs substitute only this dependency while preserving explicitly seeded timezone/enable fields. Native run below executes the original cached refresh path without replacement. Existing timezone parser evidence is retained separately in PASS1_TIMEZONE_REPORT.md.

Predicate:if signed year<67,zero-based month<3 or>9,return0. Months4..8 return1. Boundary month3 uses common[3]+7 for year>86,otherwise common[4];month9 uses common[10]. Add one when year&3==0. Compute signed16 `v=365*signed16(year-70)+(signed16(year-1)>>2)+base`,then signed32 remainder of(v-13)by7. Boundary=base-remainder. For month3 return1 after boundary day,or on it at hour>=2. For month9 return1 before boundary day,or on it at hour<1. These are exact compiled rules; geographical/legal applicability is not inferred.

Signed remainder helper implements truncated-quotient remainder,sign follows dividend. It handles a divisor with zero highWORD through two16-bit DIVs;larger divisors use shift normalization,approximate quotient and correction. Negative dividend/divisor arguments are replaced by their magnitudes in argument memory. INT32_MIN magnitude remains80000000h unsigned; controlled cases verify its remainder behavior including divisorFFFFFFFFh. The separate multiply helper returns low32 product. None of this proves the rest of CRT or external runtime library provenance beyond the byte-checked implementation.

## Controlled execution

**13062 distinct retained calls,zero failures**:12192 calendar cases and870 arithmetic-helper cases. Calendar matrix:two relocation loads,nine years(1966,1967,1980,1986,1987,2000,2024,2026,2100),months1..12,hours0/1/2/23,timezones-18000/0/3600,DST disabled/enabled,first/last days plus boundary neighbors for April/October. Expected transition days are derived from the explicit predicate model; these are instruction-vs-model checks,not independent historical timezone-law validation. Full57392B DGROUP,argument/return frame,preserved registers,return32 and actual converter lookup addresses are checked.

Helper matrix:two loads,15 DWORD values spanning zero,16/32-bit boundaries,INT_MIN/INT_MAX and negatives;450 multiply calls plus420 remainder calls,zero divisors excluded. Original helpers execute;output and callee-pop frame,registers and normalized argument memory are compared. All277 decoded starts execute across calendar+helper matrices,including every new254start. The existing multiply function is not added again to the function catalog.

## Native whole-call proof

`dosbox_calendar_runtime/independent_verification.json` confirms23source/copy asset pairs unchanged and exact relocated runtime image SHA256 `6ff79b07a98de8873f60bf2da6d93f55bbc0d3320a1d8adbd90e02e7fde569b6`. Frozen harness SHA256 `2193bc410cd765468c70e45dfa811940be9de55f20da49f9171b456beac445b4`.

Original2DC0 receives y46,m11,d12,h16,n51,s59;timezone field+28800,DST enable1. Native zero-based month10 makes the predicate return0. DX:AX=`6AF65F2F`,matching an independent datetime-to-1970 calculation plus captured28800seconds. The added timezone value is a captured CRT input,not a claim about the user's local timezone.

DGROUP57392B is identical at entry,after original timezone refresh and at caller return. Refresh gateDS3CA8 is nonzero,so original2BF4 returns through its cached path;no environment parser/OS replacement executes. Re-executing the actual relocated converter,predicate,multiply and cached refresh with native argument/register/data snapshots takes172instructions/146unique starts and matches **all captured registers**,return frame and fullDGROUP. Local scratch stack starts with a different explicit pattern; no uninitialized-local claim is inferred beyond this tested branch. Native frame returns to11EE:2BB9. No native DST transition,TZ refresh parsing,leap-table consumption,all-year or Win16 parity claim.

## Cross-version evidence

24bounded comparisons across eight DOS labels/three new functions:all24relativeCFGs match;raw matches10,normalized matches10. Signed remainder is byte-identical in all eight labels. Residual converter/predicate differences are exactly indexed common-table displacement bytes,which the original normalizer deliberately retains. Binding audit checks actual startupDS signature and exact26B common-year plus26B preceding leap-pattern bytes in each counterpart. These bindings explain residual differences without silently raising the normalization match count.18/19 share one image. Data identity does not prove leap-table use,timezone environment equivalence or Win16 behavior.

## Coverage update: 13 areas

Central bounded catalog169functions,7556starts,19051unique codeB,59469typed file-dataB,UNKNOWN_CONTENT92840(not historical reclassification). Controlled DOS2 calls1058113,accepted native sessions34(overlapping prefixes);separate BSS5148B and73field-role rows. Original NONCODE unchanged:892intervals/57295B,PARTIAL57118,CLASSIFIED ONLY149,UNKNOWN28,DEEP0,map SHA256 `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`. No new semantic percent has a complete denominator.

|Area|Historical orientation|New % / exact method|New confirmed evidence|Remaining / blocker|Next concrete step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A,semantic denominator absent|No new map fact|Prior map fields open|Uncovered map-field consumers|
|Data types and constants|95%|N/A;177B remaining audited|Common table month-domain linkage|149classified/28unknown unchanged|Trace unresolved dynamic addresses|
|Tables and pointers|93%|N/A;16calendar bindings|Common/leap neighbor bytes match acrossDOS|Leap table consumer unproved|Investigate module/data provenance|
|Functions/ASM/CFG|90%|N/A;3new254starts/592B|Converter,predicate,signed remainder bounded|Caller/global scope incomplete|Close remaining CRT/helper callers|
|RNG|97%|N/A,semantic denominator absent|No RNG linkage inferred from clock|Seed ordering still open|Trace actual clock-to-RNG producer|
|Scheduler|96%|N/A;one native clock conversion|Native date/time inputs and result|Not a scheduler timing proof|Link caller result to stored timestamp|
|DEMO/input|96%|N/A,semantic denominator absent|No new DEMO fact|Playback dependencies open|Uncovered DEMO branches|
|Renderer/VGA|94%|N/A,semantic denominator absent|No new renderer fact|Previous XMS-to-renderer gap remains|Trace resident pixel consumer|
|GUARD/bosses|93%|N/A,semantic denominator absent|No new AI fact|Prior behavior gaps remain|Uncovered boss/control branches|
|Weapons/projectiles|92%|N/A,semantic denominator absent|No new projectile fact|Prior damage gaps remain|Uncovered effect dispatch|
|Sprites/HUD/palette|92%|N/A,semantic denominator absent|No new sprite fact|Cache consumers open|04D8 and resident cache paths|
|SAVE/LOAD|92%|N/A,semantic denominator absent|CRT time distinguished from serialization|Save timestamp use unproved|Find consumers of caller output|
|Windows Win16|92%|N/A,semantic denominator absent|No new Win16 fact|Win16 calendar counterpart unbound|Map actual Win16 time APIs/callers|

All13areas remain PARTIAL. No padding or unused-storage conclusion follows from the new negative local-address result. Campaign remains active; PASS1 completion still unproven.

## Required next runtime tests

Capture actual timezone-refresh parsing when cache is cold,if a natural path exists;native April/October boundary dates in an isolated DOS environment without changing host settings;exact caller output consumers before claiming save/RNG linkage. Continue dynamic segment/register accesses for remaining177B,with read/same-value-write tracing distinguished from BPLM value changes. Existing runtime UNKNOWN28 no-change snapshots remain insufficient to prove nonuse. Continue Win16 comparison and independent renderer/save-load/AI branches.
