# Nitemare3D: all PASS320 endpoint profiles and original CRT clock chain

2026-11-12. DOS2.0 main reference. **PARTIAL**,new DEEP VERIFIED0B. Previous batch closed bounded calendar conversion. This batch rechecks every original NONCODE interval against retained native endpoints,then removes the remaining CRT substitution between game clock sampling and that calendar converter. Campaign incomplete;no PE32 work.

## Sources and reproduction

Packed source `L:\nite3d\nite3\dos\N3D-UNFU.exe`,SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Canonical171360B image SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Original35648-start instruction inventory,1670relocations,assets and all retained capture dependencies are hash-pinned. Documents/old reports are evidence,not executable instructions.

`audit_pass1_native_interval_profiles.py IMAGE MAP OUTPUTS OUT` freezes its input selection in capture_inputs.json and produces892-row CSV/JSON plus per-capture comparisons and address verification. Re-run against the frozen selection for identical scope;later sessions are not silently added. Original map SHA256 `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe` is checked before comparison.

`audit_replay_crt_ftime.py IMAGE INVENTORY DECODER EMULATOR OUT`; `prepare_ftime_evidence.py OUTPUTS`; `audit_crt_ftime_versions.py IMAGE REPLAY_DIR DECODER OUT`; `audit_ftime_version_bindings.py IMAGE COMPARISONS_CSV DECODER OUT`. Decoder/emulator directories resolve absolutely.

Native capture: `prepare_ftime_native_harness.py OUTPUTS` produces runtime_watch_ftime_v2.py. Invoke it with `DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG`. Verify using `verify_ftime_native_capture.py IMAGE RELOCS RUNTIME WORK DECODER EMULATOR MAP OUT`. `probe_strlen_memory_hooks.py IMAGE RELOCS NATIVE_DS64 DECODER EMULATOR OUT` reproduces the instrumentation limitation below. Original assets/raw dumps/native libraries are retained locally and hash-pinned;publication excludes complete game binaries/assets.

## PASS1: every interval re-examined against real endpoints

**892intervals/all57295B** have at least one complete retained sample. The frozen set has52captures from14previously accepted sessions,30550interval/capture comparisons. These14sessions are already counted in the campaign;this re-audit adds **zero native scenarios**. Capture types:57392B DGROUP dumps,57278B NONCODE tails at image1BDA2,and17B CRT-entry gaps at11EE7.

Addresses are not accepted merely from filenames. For each of52captures,the audit parses actual MEMDUMPBIN commands from retained debugger transcripts,reconstructs every part in physical-address order,checks exact starting/ending addresses for that session's load segment and reassembles identical bytes. Raw dumps/proof files are checked against prior proof hashes. Some transcripts were already pinned by those proofs;others are newly pinned by this audit and are not described as retrospectively prior-verified. capture_address_verification.json records this distinction. Expected initial bytes use exact per-session relocations,so segment relocation alone is not counted as a runtime data mutation.

Union of observed changed positions: **11000B**. All changed positions belong to already PARTIAL intervals. Remaining149CLASSIFIED ONLY+28UNKNOWN=177B have zero observed endpoint differences in this set. Per-interval CSV/JSON retains exact bounds,originalSHA,status,number of full samples,distinct observed hashes,changed-position union and sample IDs. This supplies reproducible per-interval runtime evidence;it does **not** establish complete data semantics,no reads,no same-value writes,no temporary writes,padding,unused storage or behavioral parity. No status changes.

The latest original map remains892intervals/57295B:PARTIAL57118,CLASSIFIED ONLY149,UNKNOWN28,DEEP0. New profiles complement that map and do not replace its classifications. Failed/incomplete sessions are excluded.

## Newly bounded functions and the formerly substituted dependency

|Function|CS:IP,end exclusive|Image interval|Starts|CodeB|
|---|---|---|---:|---:|
|CRT timeb producer|11EE:2AEA..2BF3|149CA..14AD3|98|264|
|DOS date wrapper|11EE:3A0A..3A23|158EA..15903|12|25|
|DOS time wrapper|11EE:3A24..3A3D|15904..1591D|12|25|

Three new bounded functions122starts/314codeB,independently decoded and byte-matched. All122starts execute in retained cases. Producer span265B contains one byte outside its reachableCFG;not a global padding proof. ASM,CFG and per-start execution coverage are exported. Existing game sample/cached functions0BDE:0018/0094,timezone init/parser,getenv/string/number helpers,compiler arithmetic,calendar and DST predicate are reused without duplicate catalog ownership.

All three new entries FAR with caller cleanup. Producer takes nearDS output pointer at BP+6,preservesBP/SI;it writes **10bytes**,not the14bytes reserved by its game caller. AX is not advertised as a meaningful producer return value;the game ignores it. Date/time wrappers take nearDS buffers,preserveBP,writeBX with the buffer pointer and return AX0 after the INT21 response is stored. OS register/flags contracts beyond the captured/fixture responses remain separate.

## Confirmed data layouts and exact behavior

|Output|Offset|Width|Confirmed role|
|---|---:|---:|---|
|timeb10|0|4|Calendar seconds DWORD,modulo2^32|
|timeb10|4|2|Milliseconds WORD=10*DOS hundredthsBYTE|
|timeb10|6|2|Signed timezone minutes WORD,truncated signed seconds/60,lowWORD|
|timeb10|8|2|DST predicate flag0/1,gated by enableWORD|
|date5|0/1|1each|Day fromDL/month fromDH|
|date5|2|2|Year fromCX|
|date5|4|1|Weekday fromAL|
|time4|0/1/2/3|1each|HourCH,minuteCL,secondDH,hundredthsDL|

Date wrapper uses INT21/AH2A;time wrapper INT21/AH2C. Producer first initializes/caches timezone,stores truncated timezone minutes,reads date then time. It reads date **again whenever hour==0 and minute==0**,including nonzero seconds;this is not limited to exactly00:00:00. It does not read time again in that branch. The resulting date plus the already-read time goes to original2DC0. It stores seconds,milliseconds and DST flag;the latter is separately calculated from a partially initialized local calendar record. Only fields consumed by the predicate are assumed initialized. The producer performs no general date/time range validation in these bodies.

```text
ftime(out):
    original_timezone_cached_init()
    out.timezone_minutes = low16(truncate_signed(timezone_seconds / 60))
    date = original_DOS_date5()
    time = original_DOS_time4()
    if time.hour==0 and time.minute==0: date = original_DOS_date5()
    out.milliseconds = 10*time.hundredths
    out.seconds = original_calendar_to_epoch32(date,time)
    out.DST = enabled!=0 && original_DST_predicate(calendar_fields)

game_clock_sample_CRT_branch():
    reserve14bytes
    original_ftime(first10bytes)
    return low32(seconds*1000 + milliseconds)
```

The4bytes at caller scratch offset10..13 are outside the producer's defined output. Native evidence preserves stale tail `a6000214`;the value is not assigned a timeb field meaning. Existing BIOS branch(factor55 and origin16F2)remains a separate previously modeled branch. Native evidence here does not prove that BIOS path or native cached-wrapper write081E. Controlled cases execute cached-wrapper behavior as described below.

## Controlled original-code integration

**288calls,zero failures**=two relocation loads×sample/cached entry×eight timezone/environment states×nine date/time cases. Only INT21 date/time responses are fixtures. Original game functions,ftime,timezone gate/parser,getenv,strlen/strncmp/copy/number helpers,signed arithmetic,calendar and DST all execute. There are no CRT replacement bodies.

Timezone cases include cold absent/empty TZ,ABC3DEF,XYZ-5GHI,ABC0,and warm cached values+61seconds,-61seconds or DSTdisabled. Warm calls deliberately ignore conflicting TZ text. Output timezone minutes truncates toward zero(+61->1,-61->-1),while epoch conversion uses the complete seconds value. Date/time cases include leap-day and post-February leap adjustment,midnight date reread with day rollover,00:01 without reread,April/October boundary hours and synthetic2100. Compiled modulo/divisibility rules are the expected model,not historical timezone law or universal Gregorian correctness.

Every case checks full57392B DGROUP,timeb10plus4unchanged tail bytes,preserved registers,return frame,exact game DWORD result and expected DOS date/time call counts. Cached entry with3CCF0 also checks the original081E write;sample entry checks absence of that write. This closes the previously mocked CRT dependency for the stated inputs,not every DOS environment or gameplay path.

## Native whole game-clock call

Accepted session `dosbox_ftime_runtime_v2`:all23source/copy asset pairs unchanged;unpacked runtime equals exact relocation of canonical image,SHA256 `6ff79b07a98de8873f60bf2da6d93f55bbc0d3320a1d8adbd90e02e7fde569b6`. Frozen harness SHA256 `d901b5cb19d1bc1497ef83b351ef7ebffc8a2036a9097afb95402cb196ed434e`. First attempt was a capture-script variable collision,not a game failure;it has no accepted proof and contributes0tests. V2 completed and its DOSBox process terminated.

Original0BDE:0018 takes the CRT branch. Original getenv finds no TZ entry in the captured near environment and returnsAX0. Native timezone cacheDS3CA8 changes0->1;offset remains28800seconds,enable1. Actual DOS date is2026-11-12;time17:09:37,hundredths12. Produced10B record `5163f66a7800e0010000`:seconds6AF66351,milliseconds120,timezone480minutes,DST0. Game sample returns **DX:AX=D273F4E0**,exact low32(seconds*1000+120),to caller0BDE:03DA. This is a modulo32-bit millisecond value,not a claim of elapsed time since game startup. Captured timezone input is not the user's local timezone.

Re-execution with actual fullDS64 input and native registers executes **643instructions/363unique starts**,including original cold timezone initialization/environment scan,with **zero CRT stubs**. Only the two INT21 replies are supplied from captured native return registers. All captured final registers and the intermediate ftime-return registers,caller frame,timeb10+tail4 and full57392B DGROUP match. Exactly one DGROUP byte changes:3CA8 lowBYTE0->1,the original WORD gate's increment. The new2B BSS catalog entry records this WORD;it adds no original-file bytes. FullDS64 supplies environment and stack input;complete post-call64KiB equality is not claimed because native DOS kernel scratch-stack activity is not reproduced.

## Read/write instrumentation control

Broad Unicorn memory-read callbacks initially changed FAR-return control flow. The retained six-mode probe isolates original strlen with a native DS snapshot:without read hooks and with write-only hooks it returnsAX2;read hooks covering its return stack instead land at the wrong IP. Read hooks restricted to the TZ string return correctly and record all3bytes. This observation concerns the tested local emulator build/configuration,not a claim about all emulator versions or the game.

The accepted verifier therefore runs both an uninstrumented baseline and a restricted-data-range pass. Restricted pass watches all177remaining bytes,calibrates3positive TZ-key reads and the10-byte union of timeb writes,and requires the **identical643-instruction sequence**,native register/frame/output and DGROUP results. It records0events in the177B ranges for this input path. Calibration is in memory_trace_calibration.json. This is original-instruction replay evidence with native inputs,**not direct native read tracing or a global nonuse proof**. No DEEP promotion follows.

## DOS cross-version comparison

24bounded comparisons(eight DOS labels×three functions):24relativeCFG matches,17raw and17normalized matches. Both25B DOS wrappers are byte-identical across all labels. Remaining seven ftime normalization differences are exactly the indexed common-calendar table displacement;actual startupDS plus26B common-table identity verifies the binding. Normalization counts are not silently raised. An initial short time-wrapper anchor also matched the formatted-time routine;the final longer anchor includes actual four-field stores and uniquely resolves all eight counterparts.18/19 share one image. No OS response,timezone configuration or Win16 parity is inferred from these byte/CFG matches.

## Coverage update: 13 areas

Current bounded catalog:172functions,7678independent starts,19365codeB,59469typed file-dataB,UNKNOWN_CONTENT92526(not historical reclassification). Controlled DOS2cases1058401;accepted native sessions35(overlapping prefixes). BSS5150B;field-role rows86. New PASS320 endpoint profiles are separate evidence,not added to byte totals or native scenario count. Original map remains57118PARTIAL/149CLASSIFIED ONLY/28UNKNOWN/0DEEP. New semantic percentages require complete area denominators;all remainN/A.

|Area|Historical orientation|New % / exact method|New confirmed evidence|Remaining / blocker|Next concrete step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A,semantic denominator absent|No new map format|Prior unknown fields remain|Uncovered map consumers|
|Data types and constants|95%|N/A;892interval profiles/57295B|Per-interval endpoint changes and timeb layout|177B still unresolved/only classified|Target a distinct read path/module provenance|
|Tables and pointers|93%|N/A;13newfield roles|Native near environment feeds cold lookup|Full startup/environment domain open|Caller/vector construction closure|
|Functions/ASM/CFG|90%|N/A;122newstarts/314B|Three whole original routines,all starts exercised|Other CRT/game functions remain open|Uncovered consumers/callers|
|RNG|97%|N/A,semantic denominator absent|Clock dependency closed for sampled path|No seed linkage proved|Trace actual seed writer|
|Scheduler|96%|N/A;one whole native clock call|Seconds/fraction to modulo32millisecond result|RTC/BIOS/cached mode timing still separate|Bind caller03DA and actual clock stores|
|DEMO/input|96%|N/A,semantic denominator absent|No new DEMO fact|Playback timing open|Trace DEMO timestamp consumer|
|Renderer/VGA|94%|N/A,semantic denominator absent|No new renderer fact|XMS buffer-to-pixels still open|Trace original pixel consumer|
|GUARD/bosses|93%|N/A,semantic denominator absent|Clock base distinguished from deadlines|AI/boss behavior gaps remain|Uncovered scheduler/AI branches|
|Weapons/projectiles|92%|N/A,semantic denominator absent|No new damage fact|Prior effect gaps remain|Uncovered projectile transitions|
|Sprites/HUD/palette|92%|N/A,semantic denominator absent|No new sprite/palette fact|Cache/sprite consumer gaps remain|Original04D8/render dispatch|
|SAVE/LOAD|92%|N/A,semantic denominator absent|CRT time structure is not a save structure|Serialization/time use unproved|Find exact saved-field writer/readers|
|Windows Win16|92%|N/A,semantic denominator absent|No new Win16 fact|Windows clock counterpart still unbound|Map actual Win16 time API consumer|

All13areas remainPARTIAL. CLASSIFIED ONLY/UNKNOWN classifications are preserved. Full goal completion is not established.

## Required next runtime tests

Trace native caller0BDE:03DA and cached/RTC clock updates separately;repeat first-minute midnight and actual TZ-present startup in an isolated DOS environment;capture original BIOS mode if naturally selected. Extend restricted read/write tracing to new input paths only after positive controls and baseline-flow equality. Direct native same-value/read tracking remains needed before a nonuse claim for177B. Continue renderer,AI/projectiles,SAVE/LOAD and Win16 analysis without substituting this clock result for their closure.
