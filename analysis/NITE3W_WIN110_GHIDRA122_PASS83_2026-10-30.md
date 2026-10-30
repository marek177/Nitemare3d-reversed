# Win110 pass83 — reserve target and rebuild eligibility

## Finding
Confirmed / High: application constructor3936 sets+78=0200 (512-byte desired reserve) and+7A=0.2840's eligibility prefix rebuilds only when application exists, desired size is nonzero and reserve is absent or its reported size is strictly below desired.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Constructor sets desired reserve512 |1000:3995, raw file3E55 | High |
| Confirmed | Constructor clears reserve pointer using AX previously zeroed |397C,399A | High |
| Confirmed | Constructor publishes application pointer at081C |399D | High |
| Confirmed | Null application bypasses rebuild |289C–289E | High |
| Confirmed | Existing capacity>=desired bypasses rebuild, unsigned |28AF–28B2 | High |
| Confirmed | Desired0 bypasses even when reserve absent |28B4–28B8 | High |

Field-offset searches also encounter unrelated objects and virtual-table slots. A matching+78 or+7A displacement alone is not proof of application-field access. The confirmed constructor store supplies a default512 target, not proof that all runtime capacities equal512 or that no indirect writer can alter it.

## Behavior model
`eligible = app != 0 && app.desired != 0 && (app.reserve == 0 || size(app.reserve) < app.desired);`

At desired512, capacities0..511 rebuild,512..FFFF skip. An absent reserve bypasses the size query but still honors desired0. The earlier outer2840 countdown and cleanup conditions must also be satisfied before this prefix is reached; they are not executed here.

This strengthens the source of the512 fixture used in passes80–82. It does not validate their synthetic FFFC..FFFF allocation requests as actual gameplay inputs. Desired reserve size and failed allocation request are different quantities.

## Verification
65,585 cases passed:65,536 reported capacity words for desired512 and present reserve7400;48 cases crossing desired0/1/512/FFFF, absent/present reserve and six capacities; one null application. Original289C–28B8 instructions execute, stopping at28BA before rebuild or291B after bypass. The size query at28A9 is stubbed, returns declared capacity, and leaves the argument for original POP BX. SP returns to region-entryCFF0.

DS1048, SS4000, CS2000. No code patch is needed because execution intercepts the size-query CALLF. Constructor behavior is statically checked through raw instruction bytes and preserved native export, not constructor execution. No actual LOCALSIZE, allocation, Windows process or full2840 execution occurs.

Run `python3 pass83/verify_reserve_target.py` with Unicorn2.1.4. EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Original EXE and preserved Ghidra12.2 export; no fresh database update.

## Implementation-ready findings
Default desired reserve to512 and pointer0 for this application constructor. Use unsigned strict-less eligibility, preserve existing equal/larger blocks, and honor desired0. Keep the outer countdown guard and actual rebuild mechanics separate from eligibility.

## Unknowns and next test
Recover2840's outer countdown semantics at0824/0826 and its incrementing callers to establish when reserve rebuild runs. Other runtime setters and allocation-request ranges remain unproven. Confidence High for default and isolated eligibility; complete runtime timing remains Unknown.
