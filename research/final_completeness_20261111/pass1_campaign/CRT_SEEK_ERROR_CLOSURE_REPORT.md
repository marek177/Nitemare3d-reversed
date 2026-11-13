# CRT seek, signed offset checks and original error translation

## Sources and bounded contracts

Original DOS2 reproduced image SHA256 e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297 and historical instruction inventory are independently byte matched. New bounded bodies: seek11EE:1BD6..1C57 image[13AB6,13B37),129B/48starts; shared FAR return11EE:05B7..05C4 image[12497,124A4),13B/7starts; errno translator11EE:05CA..05F7 image[124AA,124D7),45B/21starts. Total187B/76starts, outside original PASS320 NONCODE. Error translator had previous1532 isolated cases; this batch newly catalogs its boundary and executes it from the original seek caller. Prior isolated cases are not counted again.

Artifacts: audit_replay_crt_seek.py, crt_seek_replay/{three instruction CSVs,CFG_edges.csv,execution_coverage.csv,DOS_events.csv,cases.csv,summary.json}; audit_crt_seek_versions.py and crt_seek_versions/{versions.csv,masked_operand_bindings.csv,summary.json}; prepare_crt_seek_fields.py and crt_seek_fields/{fields.csv,fields.json,summary.json}. Headers specify complete invocation arguments. Inputs and scripts are hash-pinned in summaries; generated cases remain locally reproducible. No new native DOSBox scenario or actual DOS failure is claimed.

## Seek algorithm and context

FAR parameters: unsigned WORD handle atBP+6, DWORD offset atBP+8, WORD origin atBP+C. Local4B stack, caller removes arguments; return advances SP by4 and preserves BP/SI/DI/ES/DS/SS under the modeled DOS register contract. Uses current DS for CRT state, SS for frame; both shared and split DS/SS are exercised. DOS42 fixtures preserve registers except AX/DX/CF; this assumption is explicit, not a proof of every DOS implementation.

An unsigned handle>=DS:2128 is rejected before DOS, using synthetic AX0900h. DS:2330 initially0 disables negative-offset prechecks. When enabled and offset high WORD has bit8000h, originWORD0 is rejected using AX1600h. Other origins first query DOS4201 withCX:DX=0. A failed current-position query enters the common error path. If origin bit1 is clear, current+offset is added modulo32bits and negative results rejected. If origin bit1 is set, the code saves current position, issues DOS4202 with zero offset, and adds returned DX:AX+offset. **CF from the end-position query is ignored.** If this sum is negative, DOS4200 attempts to restore the saved current position, then AX1600h replaces the result regardless of restoration CF. This is an original-code behavior under response fixtures, not a claim that real DOS normally returns these failure combinations.

On a valid path, final DOS42 uses AL=lowBYTE(origin) and the original signed offset inCX:DX. The precheck uses full originWORD, while the DOS service receives only its lowBYTE; origin0100h therefore differs from origin0000h in the precheck. Successful final seek ANDs DS:[212A+handle] withFDh, clearing bit1; return DX:AX is preserved. Failed final seek takes the shared error path. The handle-flag store occurs even if bit1 was already clear; ordered-store verification includes same-value writes.

Pseudocode: reject handle>=limit; if gate && signedOffset<0: reject originWORD==0; cur=queryCurrent(); fail if CF; if origin&2: end=queryEnd(); if signed32(end+offset)<0: restore(cur); reject EINVAL; else if signed32(cur+offset)<0: reject EINVAL. result=dosSeek(handle,offset,lowBYTE(origin)); if CF: translateError(); return -1; flags[handle]&=FDh; return result. Here queryEnd CF is deliberately unused and additions wrap32bits.

## Error translator and return flags

Shared error tail calls original05CA, then setsAX=FFFFh and CWD=>DX=FFFFh. Translator writes incoming AL to DS:2126, leaving its neighbor untouched. If incoming AH!=0, AH is used as signed8-bit errno. Thus synthetic0900/1600 yield errno9/22 and native-error-low0. If AH==0, DOS majorBYTE DS:2121>=3 remaps AL32/33 to index5; other low codes clamp to index19, with0..19 direct. XLAT reads signed BYTE table DS:2160[20], CBW sign-extends and stores WORD errno atDS:2118. BX becomes2160h on the table path; BX is not a preserved output contract.

CF at FAR return is not a dependable error Boolean: the translator's comparisons/OR overwrite it. In exercised failures AL<19 withAH0 leavesCF1, while synthetic AH errors and higher mapped codes can returnCF0 despite DX:AX=-1. DF remains unchanged. The harness initially assumed all error returns clearedCF; original execution disproved that assumption and the independent expected flags were corrected before accepting results.

## Reproduction and cross-version limits

1592 cases pass with all76 starts executed: two relocation loads, DS/SS equal or split, DF0/1, positive/negative/wrapping offsets, origins0/1/2/3/0100/FFFF, handle bounds, disabled/enabled prechecks, current/end positions near signed limits, each DOS-stage failure, restoration after ignored query error, error5/1234/19/20/32/33/34/255 and DOS major2/3. Exact ordered nonstack stores, complete2MiB RAM outside84 control-stack bytes, unchanged argument frame, AX/DX/CF/DF and preserved registers match independent expectations. DOS outputs are fixtures; filesystem side effects and error frequency are not inferred.

Eight DOS labels10/11/12/15/17/18/19/20 (seven distinct source images) produce24 equal normalized bodies/branch graphs. DS displacements, indexed flag-table base and error-table near immediate are masked only with explicit per-version bindings; raw body hashes remain separate. This is bounded structure/code identity, not full CRT/runtime/gameplay parity. Win16 counterparts remain unverified.

## Original NONCODE and field catalog

Seven already-PARTIAL roles/48B are refined: handle limitWORD2128(initial20), gateWORD2330(initial0), initial-limit20B flags window212A, errnoWORD2118, native-errorBYTE2126, DOS-majorBYTE2121 and20 signedBYTE error table2160. The20B flag window is not proof of total allocated capacity after mutable limit changes. No new typed-file/BSS bytes, interval status promotion, pointer ownership closure or nonuse inference follows.

## Coverage update: 13 areas

Previous185functions/8165starts/20677codeB/1066991controlled cases/41native. New188functions/8241starts/20864codeB/1068583controlled cases/41native. Add187codeB/76starts and1592controlled cases; no native count increase. Typed data59469B/BSS5164B unchanged. Campaign UNKNOWN_CONTENT91027 is a bounded campaign metric, not original NONCODE reclassification. Central instruction hash and dependent retry-reference/field summaries regenerated; decoded inventory union remains35813.

Original PASS320 unchanged:892 intervals/57295B =57118 PARTIAL+149 CLASSIFIED ONLY+28 UNKNOWN+0 DEEP VERIFIED; mapSHA256497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe. No evidence-derived whole-area semantic percentage is available; historical estimates below are not new completion claims.

|Area|Previous orientation|New % / method|New confirmed findings|Unknowns / blockers|Next step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; complete area denominator and remaining behaviors unclosed|Uncovered map replacement consumers|
|Data types and constants|95%|N/A; complete semantic denominator absent|Seven roles/48 already-PARTIAL bytes refined; no new typing|PARTIAL; complete area denominator and remaining behaviors unclosed|Resolve remaining 149 classified-only and 28 unknown bytes through actual consumers|
|Tables and pointers|93%|N/A; complete semantic denominator absent|Handle flag bit1 cleared on final seek success; initial20B window only|PARTIAL; complete area denominator and remaining behaviors unclosed|Trace driver MIDI event consumers and buffer lifetime|
|Functions/ASM/CFG|90%|N/A; complete semantic denominator absent|Three bodies/187B/76starts;1592 cases,all starts exercised|PARTIAL; complete area denominator and remaining behaviors unclosed|Open fatal/callback bodies and remaining unknown functions|
|RNG|97%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; complete area denominator and remaining behaviors unclosed|Capture RNG/DEMO ordering|
|Scheduler|96%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; complete area denominator and remaining behaviors unclosed|Capture natural resource replacement timing|
|DEMO/input|96%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; complete area denominator and remaining behaviors unclosed|Capture actual DEMO playback|
|Renderer/VGA|94%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; complete area denominator and remaining behaviors unclosed|Exercise clipped draws|
|GUARD/bosses|93%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; complete area denominator and remaining behaviors unclosed|Uncovered boss/attack transitions|
|Weapons/projectiles|92%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; complete area denominator and remaining behaviors unclosed|Original impact/damage lifecycle|
|Sprites/HUD/palette|92%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; complete area denominator and remaining behaviors unclosed|Native populated cleanup/refill|
|SAVE/LOAD|92%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; complete area denominator and remaining behaviors unclosed|Actual LOAD/reset ordering|
|Windows Win16|92%|N/A; complete semantic denominator absent|24 bounded DOS body/CFG comparisons; no Win16 counterpart|PARTIAL; complete area denominator and remaining behaviors unclosed|Locate Win16 resource-reader and driver counterparts|

All13 areas remain PARTIAL. New bounded coverage does not close external CRT, remaining unknown functions or whole game parity.

## Required next runtime tests

Capture actual DOS42 entry/return for the previously natural four music reader seeks, including handle-flag before/after and full CRT state. Exercise real invalid-handle/negative-seek failures where reachable, separately tracking DOS errors versus synthetic CRT errors. Continue whole original CRT open and SND-reader integration with fewer response fixtures. Return to177 original remaining classified/unknown bytes through consumers, MIDI event/buffer ownership, Win16 counterpart mapping and uncovered gameplay/renderer/RNG/DEMO/SAVE/LOAD. No PE32 port.
