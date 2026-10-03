# Nitemare 3D — detailed map SND.DAT and sound events Win16

**Date analysis:** 23. 9. 2026  
**Analyzed archive:** snd.dat (843 918 bytes), whose WAV/MIDI content sa match with snd.zip.  
**Code evidence:** decompilation listing nite3w110.exe.c; functions and numbers row are below.  
**Purpose:** distinguish physical items v SND.DAT from numbers events, ktorými their play EXE, and assign their k guard, weapon, door, pickupom and skriptovaným state.

## Main result: number v EXE is not physical index SND.DAT

SND.DAT has 111 physical records with index **0–110**. Win16 routine 5132 skips first **0xC0 = 192 bytes**, therefore 32 records × 6 bytes, and loads **0x1DA = 474 bytes**, therefore 79 records for index 32–110. Subsequently routine e3b0 index load table as event × 6. Therefore applies:

**physical index SND.DAT = number zvukovej events v EXE + 32**

Example, which handle time zmätok:

- Physical slot **1** is v this archive Song 001.mid; is not to death guard.
- EXE event **35** play physical slot **67**, candidate label GUARD_BAT_DIE; class raw 8 corresponds to according to krížovej check GUARD1 Bat.
- Pistol: EXE event **27** → physical slot **59**. Plazma: event **33** → slot **65**. Physical sloty 2 and 3 are MIDI consist.
- EXE event 37/38 → physical sloty 69/70, oba contain **ten certain audio payload**. EXE their launch during different prechodoch curtain/door; z WAV data sa direction open/close cannot distinguish.
- EXE event 39 → slot **71**, play during interaction with type target 3; corresponds to open tajného panel/prestupu.

To mean, that names type „SND item 01 = guard1Kill“ or „item 02 = pistolfire“ nesedia on physical index this versions. Sound routine uses own event ID and table v SND.DAT has still posun +32.

## As read evidence

- **EXE path confirmed** mean, that v listing-u exist call-site or class dispatcher, which selects given event; to confirms trasu k slotu.
- **Class GUARD n** is derive z internal byte code v dispatcheri and mien GUARD v OBJECTS.1–3. Krížový key raw class = GUARD number + 7 is strong inferencia, nie doslovná constant v EXE.
- Name v column „Candidate label“ come from z listu Sounds v provided zošite. Itself zošit ho denotes as source C (OpenNitemare3D), nie as evidence z original EXE.
- During dispatcheri b5e4 is action context **attack**. b862 is state/alertová reakcia. b6and0 is class reakcia v prechode and during damage; v some item label suggests death, no without behu game cannot each sound mark as kill/death.

## Inventory each physical record

Size is count bytes payloadu v SND.DAT; offset is miesto payloadu v this specific snd.dat. Names WAV v ZIP-e have still 44-byte header WAV.

### Indexes 0–33: bank, music and empty records

| Slot | EXE event | Bytes @ offset | Content / note |
|---:|---:|---:|---|
| 0 | — | 3204 @ 960 | Nitemare 3d.ibk — instrument bank |
| 1 | — | 20517 @ 4164 | Song 001.mid |
| 2 | — | 15264 @ 24681 | Song 002.mid |
| 3 | — | 13427 @ 39945 | Song 003.mid |
| 4 | — | 16990 @ 53372 | Song 004.mid |
| 5 | — | 18840 @ 70362 | Song 005.mid |
| 6 | — | 21717 @ 89202 | Song 006.mid |
| 7 | — | 12677 @ 110919 | Song 007.mid |
| 8 | — | 10321 @ 123596 | Song 008.mid |
| 9 | — | 7939 @ 133917 | Song 009.mid |
| 10 | — | 8943 @ 141856 | Song 010.mid |
| 11 | — | 3238 @ 150799 | Song 011.mid |
| 12 | — | 4873 @ 154037 | Song 012.mid |
| 13 | — | 14031 @ 158910 | Song 013.mid |
| 14 | — | 4229 @ 172941 | Song 014.mid |
| 15 | — | 8403 @ 177170 | Song 015.mid |
| 16 | — | 0 @ 185573 | empty record (size 0) |
| 17 | — | 0 @ 0 | empty record (size 0) |
| 18 | — | 0 @ 0 | empty record (size 0) |
| 19 | — | 0 @ 0 | empty record (size 0) |
| 20 | — | 0 @ 0 | empty record (size 0) |
| 21 | — | 0 @ 0 | empty record (size 0) |
| 22 | — | 0 @ 0 | empty record (size 0) |
| 23 | — | 0 @ 0 | empty record (size 0) |
| 24 | — | 0 @ 0 | empty record (size 0) |
| 25 | — | 0 @ 0 | empty record (size 0) |
| 26 | — | 0 @ 0 | empty record (size 0) |
| 27 | — | 0 @ 0 | empty record (size 0) |
| 28 | — | 0 @ 0 | empty record (size 0) |
| 29 | — | 0 @ 0 | empty record (size 0) |
| 30 | — | 0 @ 0 | empty record (size 0) |
| 31 | — | 0 @ 0 | empty record (size 0) |
| 32 | 0 | 0 @ 185573 | empty record (size 0) |
| 33 | 1 | 0 @ 185573 | empty record (size 0) |

EXE event 0 and 1 by according to posunu odkazovali on physical sloty 32 and 33; oba are empty. Physical sloty 16–33 are empty.

### Indexes 34–110: SFX and hlasy

| Slot | EXE event | Bytes @ offset | Usage according to Win16 listing-u | Candidate label from workbook |
|---:|---:|---:|---|---|
| 34 | 2 | 5256 @ 185573 | b6and0: raw 27/28 (≈ GUARD20 Goldie / GUARD21 Greenie), event 2; class reakcia, hit/death meaning is not isolated. | — |
| 35 | 3 | 10968 @ 190829 | V dodanom Win16 C listing-u som did not find call-site for event 3. | — |
| 36 | 4 | 6382 @ 201797 | b6and0: raw 12 (≈ GUARD5 Mrs H.), event 4; triedna reakcia. | — |
| 37 | 5 | 10016 @ 208179 | V dodanom Win16 C listing-u som did not find call-site for event 5. | — |
| 38 | 6 | 9735 @ 218195 | b862: raw 17 (≈ GUARD10 Dracula), event 6; alert/secondary reakcia. | — |
| 39 | 7 | 3916 @ 227930 | b6and0: raw 10, 18, 19 (≈ GUARD3 Mummy, GUARD11 cemetery spawner, GUARD12 garden spawner), event 7. | — |
| 40 | 8 | 9930 @ 231846 | b6and0: raw 9 (≈ GUARD2 Frankenstein), event 8. | — |
| 41 | 9 | 16356 @ 241776 | b6and0: raw 29 (≈ GUARD22 Demon), event 9. | — |
| 42 | 10 | 24663 @ 258132 | During zero player HP: event 10 v 8c0and and be62 → this slot. Priama link on death player. | PLAYER_DIE |
| 43 | 11 | 3840 @ 282795 | b6and0: raw 15/16 (≈ GUARD8/9, ľudskí guard), randomly eventy 11–13 → sloty 43–45. | GUARD_HUMAN_DIE01 |
| 44 | 12 | 3584 @ 286635 | b6and0: same random trojica for raw 15/16. | GUARD_HUMAN_DIE02 |
| 45 | 13 | 5888 @ 290219 | b6and0: raw 15/16, randomly eventy 11–13; at the same time b862 raw 27/28 (≈ GUARD20/21) calls event 13. Candidate name „human die 03“ therefore nevystihuje all call-site. | GUARD_HUMAN_DIE03 |
| 46 | 14 | 8275 @ 296107 | b6and0: raw 14 (≈ GUARD7 Vampira), event 14; triedna reakcia. | GUARD_WITCH_DIE01 |
| 47 | 15 | 4479 @ 304382 | V dodanom Win16 C listing-u som did not find call-site for event 15. | — |
| 48 | 16 | 9455 @ 308861 | b862: raw 14 (≈ GUARD7 Vampira), event 16; alert/secondary reakcia. | GUARD_WITCH_ALERT01 |
| 49 | 17 | 8199 @ 318316 | V dodanom Win16 C listing-u som did not find call-site for event 17. | GUARD_WITCH_ALERT02 |
| 50 | 18 | 36541 @ 326515 | b862: raw 22 (≈ GUARD15 Dr. Hamerstein), event 18; class reakcia. and0ee uses ten certain event v special state raw 22. | — |
| 51 | 19 | 8211 @ 363056 | b6and0: raw 13 (≈ GUARD6 Zelda), event 19; triedna reakcia. | — |
| 52 | 20 | 10493 @ 371267 | b862: raw 12 (≈ GUARD5 Mrs H.), event 20; alert/secondary reakcia. | GUARD_WITCH_ALERT03 |
| 53 | 21 | 11920 @ 381760 | b862: raw 13 (≈ GUARD6 Zelda), event 21; alert/secondary reakcia. | GUARD_WITCH_ALERT04 |
| 54 | 22 | 6599 @ 393680 | V dodanom Win16 C listing-u som did not find call-site for event 22. | — |
| 55 | 23 | 7036 @ 400279 | b5e4 — útočný dispatcher: randomly eventy 23–25 for raw 15/16/22 (≈ GUARD8/9/15). | — |
| 56 | 24 | 8827 @ 407315 | b5e4 — same random trojica attack sound. | — |
| 57 | 25 | 7075 @ 416142 | b5e4 — same random trojica attack sound. | — |
| 58 | 26 | 2432 @ 423217 | b594: status player weapons 1 → event 26. Candidate name: Magic Wand. | WEAPON_MAGICWAND |
| 59 | 27 | 8060 @ 425649 | b594: status weapons 2 → event 27. Candidate name: Revolver/pistol fire. | WEAPON_REVOLVER01 |
| 60 | 28 | 3635 @ 433709 | V provided Win16 C listing-u som did not find event 28; database name „WEAPON_REVOLVER02“ remains candidate without call-site. | WEAPON_REVOLVER02 |
| 61 | 29 | 8678 @ 437344 | b5e4 — attack dispatcher: raw 25 (≈ GUARD18 Cannon/turret) → event 29. | GUARD_TURRET_FIRE |
| 62 | 30 | 0 @ 446022 | empty payload; Empty record; event 30 by smeroval sem, no payload does not have. | — |
| 63 | 31 | 1757 @ 446022 | b5e4 — attack dispatcher: raw 23 (≈ GUARD16, high do) → event 31. | — |
| 64 | 32 | 12181 @ 447779 | b5e4 — attack dispatcher: raw 12/13/14/24 (≈ GUARD5/6/7/17) → event 32. | — |
| 65 | 33 | 3512 @ 459960 | b594: player weapon status 3 → event 33. Candidate name: Plasma. | WEAPON_PLASMA |
| 66 | 34 | 14062 @ 463472 | b862 raw 8 (≈ GUARD1 Bat) → event 34; at the same time and0ee during raw 17 changes class on raw 20 and play event 34. Shared Bat-alert/special prechodový sound. | GUARD_BAT_ALERT |
| 67 | 35 | 11963 @ 477534 | b6and0 raw 8 and raw 20 → event 35. Candidate is Bat death, but raw 20 is transform/nezmapovaný status; sound is shared. | GUARD_BAT_DIE |
| 68 | 36 | 3697 @ 489497 | b6and0 raw 11 (≈ GUARD4 Skeleton) → event 36. Pozor: old name say „SKELETON_ATTACK“, but this call-site is v b6and0 reakčnom dispečeri, nie v útočnom b5e4. | GUARD_SKELETON_ATTACK |
| 69 | 37 | 19125 @ 493194 | 188and: event 37 during jednej change state curtain/door. | CURTAIN_OPEN |
| 70 | 38 | 19125 @ 493194 | 188and: event 38 during opposite change state curtain/door. Content is bit same as slot 69; direction open/close neviem z audio data distinguish. | CURTAIN_CLOSE |
| 71 | 39 | 15706 @ 512319 | 1and22: interaction, when target has type 3 → event 39. Fit on open special panel/tajného prechodu. | HIDDENPANEL_OPEN |
| 72 | 40 | 0 @ 528025 | empty payload; Empty record; event 40 by smeroval sem. | — |
| 73 | 41 | 11424 @ 528025 | 9b64: explosive wall → event 41. b5c8 also calls event 41 during state weapons 0 or 3; therefore shared explosion/impact effect. | — |
| 74 | 42 | 11424 @ 528025 | Same payload and offset as slot 73, but event 42 som v listing-u did not find. | — |
| 75 | 43 | 0 @ 539449 | empty payload; Empty record; 1and22 tests event 43. | — |
| 76 | 44 | 0 @ 539449 | empty payload; Empty record; 1and22 tests event 44. | — |
| 77 | 45 | 0 @ 539449 | empty payload; Empty record; event 45 som did not find. | — |
| 78 | 46 | 2544 @ 539449 | b7fc: type object 0x3AND → event 46; also confirmation zapnutia zvuku v menu. Candidate: Magic Eye pickup. | PICKUP_EYE |
| 79 | 47 | 5030 @ 541993 | b7fc: type object 0x33 → event 47; pickup sound, specific predmet undetermined. | — |
| 80 | 48 | 28039 @ 547023 | abfc: branches restore zdravia and added nábojov (parametre 2–5) → event 48. | — |
| 81 | 49 | 14344 @ 575062 | abfc: set key/kartových flag → event 49; b7fc type 0x2F/0x30/0x3C/0x3D also → 49. | PICKUP_KEY |
| 82 | 50 | 2548 @ 589406 | b7fc: type object 0x36 → event 50; zodvihnutie weapons. | PICKUP_WEAPON |
| 83 | 51 | 848 @ 591954 | b7fc: type object 0x3B → event 51; candidate Crystal Ball pickup. | PICKUP_GLASSBALL |
| 84 | 52 | 7546 @ 592802 | b7fc: type object 0x39 → event 52; candidate Plasma Ammo pickup. | PICKUP_AMMO_PLASMA |
| 85 | 53 | 2320 @ 600348 | V dodanom Win16 C listing-u som did not find call-site for event 53. | — |
| 86 | 54 | 2944 @ 602668 | b862: raw 15/16 (≈ GUARD8/9, ľudskí guard) randomly eventy 54–55 → sloty 86–87. | GUARD_HUMAN_ALERT01 |
| 87 | 55 | 4032 @ 605612 | b862: same random dvojica alert/reakcia for raw 15/16. | GUARD_HUMAN_ALERT02 |
| 88 | 56 | 18367 @ 609644 | b862: raw 9/10 (≈ GUARD2/3) randomly eventy 56–58; raw 29 (≈ GUARD22 Demon) also event 56. | GUARD_MONSTER_ALERT01 |
| 89 | 57 | 7872 @ 628011 | b862: second varianta trojice eventov for raw 9/10. | GUARD_MONSTER_ALERT02 |
| 90 | 58 | 8048 @ 635883 | b862: tretia varianta trojice eventov for raw 9/10. | GUARD_MONSTER_ALERT03 |
| 91 | 59 | 7872 @ 643931 | b862: raw 11 (≈ GUARD4 Skeleton) → event 59. | GUARD_SKELETON_ALERT |
| 92 | 60 | 10687 @ 651803 | b862: raw 19 (≈ GUARD12 garden spawner) → event 60. | — |
| 93 | 61 | 4803 @ 662490 | b862: raw 30/31 (≈ GUARD23/24 Aliens) → event 61. | — |
| 94 | 62 | 4608 @ 667293 | b5e4 — attack dispatcher: raw 18 (≈ GUARD11 cemetery spawner) → event 62. | — |
| 95 | 63 | 9020 @ 671901 | b862: raw 18 (≈ GUARD11 cemetery spawner) → event 63. | — |
| 96 | 64 | 3648 @ 680921 | b5e4 — attack dispatcher: raw 19 (≈ GUARD12 garden spawner) → event 64. | — |
| 97 | 65 | 3200 @ 684569 | b5e4 — attack dispatcher: raw 9/10 (≈ GUARD2 Frankenstein / GUARD3 Mummy) → event 65. | ATTACK_FRANKENSTEIN |
| 98 | 66 | 29530 @ 687769 | event 66 through acee; call-site include state/prechodové branches. Exact event nor postava are not z these call-site confirmed. | — |
| 99 | 67 | 12764 @ 717299 | event 67 through acdc z 21b6 during set state map/actor object on 8. Exact object and meaning sound undetermined. | — |
| 100 | 68 | 11358 @ 730063 | event 68 through acca during interaction with map type 9/10, also v next prechodových function. Candidate LEVEL_END is vierohodný, but name is not v EXE. | LEVEL_END |
| 101 | 69 | 22720 @ 741421 | ae56: during run also terminate sequences tanečníkov/radia calls event 69 and switches hudobnú stopu on number 3. Candidate RADIO_TUNE. | RADIO_TUNE |
| 102 | 70 | 13533 @ 764141 | b6and0: raw 23/24/30/31 (≈ GUARD16/17/23/24) → event 70; triedna reakcia. | — |
| 103 | 71 | 9541 @ 777674 | b862: raw 24 (≈ GUARD17 Trashcan robot) → event 71. | — |
| 104 | 72 | 5668 @ 787215 | b862: raw 23 (≈ GUARD16 high robot) → event 72. | — |
| 105 | 73 | 8940 @ 792883 | b862: raw 26 (≈ GUARD19 Ghost) → event 73. | GUARD_GHOST_ALERT |
| 106 | 74 | 10963 @ 801823 | b6and0: raw 26 (≈ GUARD19 Ghost) → event 74. | GUARD_GHOST_DIE |
| 107 | 75 | 9129 @ 812786 | b5e4 — útočný dispatcher: raw 27–31 (≈ GUARD20–24) randomly eventy 75–78 → sloty 107–110. | — |
| 108 | 76 | 10082 @ 821915 | b5e4 — same random group of four attack sound. | — |
| 109 | 77 | 6209 @ 831997 | b5e4 — same random group of four attack sound. | — |
| 110 | 78 | 5712 @ 838206 | b5e4: event 78 for raw 11 (≈ GUARD4 Skeleton) and raw 26 (≈ GUARD19 Ghost); at the same time last variant random eventov 75–78 for raw 27–31. | — |

## Audio skupiny according to enemy

V troch dispatch function sa reads byte on offset +6 data structures guard. Following prevod raw class on GUARD n fit on repeated kotvy: Bat raw 8 → sloty 66/67, Skeleton raw 11 → 68/91/110, Cannon raw 25 → 61, Ghost raw 26 → 105/106, plus order object v OBJECTS.1–3. Is strong inferenciu; source data unnamed this byte slovom GUARD.

| GUARD | Object according to OBJECTS | raw class v dispatcheri | Attack sound, b5e4 | Alert/answer, b862 | Reakcia, b6and0 |
|---:|---|---:|---|---|---|
| 1 | Bat | 8 | without own case v b5e4 | 66 (alert/reakcia) | 67 (reakcia; candidate death) |
| 2 | Frankenstein | 9 | 97 (shared with GUARD3) | 88–90 (randomly) | 40 |
| 3 | Mummy | 10 | 97 (shared with GUARD2) | 88–90 (randomly) | 39 |
| 4 | Skeleton | 11 | 110 | 91 | 68 (candidate label attack, call-site to nepotvrdzuje) |
| 5 | Mrs H. | 12 | 64 | 52 | 36 |
| 6 | Zelda | 13 | 64 | 53 | 51 |
| 7 | Vampira | 14 | 64 | 48 | 46 |
| 8 | Baddie #1 / blue coat | 15 | 55–57 (randomly) | 86–87 (randomly) | 43–45 (randomly) |
| 9 | Baddie #2 / green coat | 16 | 55–57 (randomly) | 86–87 (randomly) | 43–45 (randomly) |
| 10 | Dracula | 17 | without separate case v b5e4 | 38; during transform event 34 | transform raw17 → raw20 |
| 11 | Cemetery wall Gargoyle | 18 | 94 | 95 | 39 |
| 12 | Garden wall Gargoyle | 19 | 96 | 92 | 39 |
| 13 | without GUARD13 record v OBJECTS.1–3 | 20 | unconfirmed | unconfirmed | 67 shared with raw8 |
| 14 | Penelope | 21 | without generic call-site v troch dispečeroch | without generic call-site | without generic call-site |
| 15 | Dr. Hamerstein | 22 | 55–57 (randomly) | 50; also special event 18 | without case v b6and0 |
| 16 | Tall slim robot | 23 | 63 | 104 | 102 |
| 17 | Trashcan robot | 24 | 64 | 103 | 102 |
| 18 | Cannon / turret | 25 | 61 | without alert case | without class case |
| 19 | Ghost | 26 | 110 | 105 | 106 |
| 20 | Goldie | 27 | 107–110 (randomly) | 45 (shared with GUARD21) | 34 (shared with GUARD21) |
| 21 | Greenie | 28 | 107–110 (randomly) | 45 (shared with GUARD20) | 34 (shared with GUARD20) |
| 22 | Demon | 29 | 107–110 (randomly) | 88 (shared monster-alert rodinu) | 41 |
| 23 | Alien #1 | 30 | 107–110 (randomly) | 93 | 102 |
| 24 | Alien #2 | 31 | 107–110 (randomly) | 93 | 102 |

**read column:** numbers v table are physical sloty SND.DAT, nie eventy. If is range random, code selects one z listed sample slotov. „Without case“ mean, that specific raw class v danom dispečeri nedostane sound z tej functions; does not exclude to other skriptovaný sound.

GUARD13 is not v OBJECTS.1–3 named. Raw 20 however exist: and0ee ho sets after prechode z raw17 and play event 34; b6and0 shared event 35 for raw8 also raw20. Neprekladám therefore raw20 on new named enemy. GUARD26 Dancers is zvláštna class v OBJECTS.1; their sequence sa handles separate routine ae56 and sound slot 101.

### What exactly do three dispečery

- **b5e4 (attack):** calls sa v guard state 4 after successful condition attack; according to raw class selects specific event or random variáciu. To is najsilnejší source for map attack sound.
- **b862 (alert / state answer):** uses sa v state 2 and also during jednej branch damage. Code confirmed classes and sloty are v table above; exact meaning each tónu as „videl player“, „was zasiahnutý“ whether „change status“ sa static cannot separate.
- **b6and0 (class reakcia):** uses sa v state 9 and during damage. Therefore is path k class confirmed, no name death z candidate workbook is not for each slot proven.

## Directly confirmed ne-enemy sounds

| Function game | EXE event → physical slot | Evidence v code | Conclusion |
|---|---:|---|---|
| Death player | 10 → 42 | 8c0and during HP = 0; also be62 | SND42 is player death; label PLAYER_DIE fit. |
| Weapon Magic Wand | 26 → 58 | b594, status weapons 1 | Candidate WEAPON_MAGICWAND. |
| Weapon pistol/revolver | 27 → 59 | b594, status weapons 2 | Candidate WEAPON_REVOLVER01. |
| Weapon plasma | 33 → 65 | b594, status weapons 3/default | Candidate WEAPON_PLASMA. |
| weapon label without call-site | 28 → 60 | event 28 sa v overview listing-u nevyskytol | WEAPON_REVOLVER02 is so far only candidate. |
| Doors/záves | 37 → 69; 38 → 70 | 188and changes status animations | Obe items reference on identical data; exact directional open/close remains uncertain. |
| Tajný panel/prestup | 39 → 71 | 1and22 during interaction with target type 3 | Strong priama link on interaktívny panel; label HIDDENPANEL_OPEN fit. |
| Explosive wall / impact | 41 → 73 | 9b64 has branch Explode wall; b5c8 uses event during weapon state 0 or 3 | Shared explosion/impact; slot 74 is exact copy without find eventu. |
| Magic Eye / enabled sound | 46 → 78 | b7fc type 0x3AND; ddfc and 2596 during enabled sound | Same SFX sa uses on pickup also set sound. |
| Pickup general | 47 → 79 | b7fc type 0x33 | Specific predmet som from zdrojov neidentifikoval. |
| Restore zdravia/nábojov | 48 → 80 | abfc parametre 2–5 | Generic feedback for selected pickupy. |
| Keys/cards | 49 → 81 | abfc sets key/kartové flags; b7fc type 2F/30/3C/3D | Candidate PICKUP_KEY. |
| Zodvihnutie weapons | 50 → 82 | b7fc type 0x36 | Candidate PICKUP_WEAPON. |
| Crystal Ball | 51 → 83 | b7fc type 0x3B | Candidate PICKUP_GLASSBALL. |
| Plazmová ammo | 52 → 84 | b7fc type 0x39 | Candidate PICKUP_AMMO_PLASMA. |
| End/prechod level | 68 → 100 | acca z map interaction type 9/10 and multiple prechodových routines | LEVEL_END is rozumný candidate, no EXE neobsahuje this name. |
| Dancers/radio sequence | 69 → 101 | ae56 during startup also return sequences, at the same time changes MIDI stopu | Candidate RADIO_TUNE; priame linked with scénou tanečníkov/radia. |
| Map/actor trigger | 67 → 99 | 21b6 sets object status 8 and play acdc | Sound is confirmed, exact object/purpose nie. |
| State/prechodové cue | 66 → 98 | acee v ba74, bef4 and c126 | Without safe named v EXE. |

## Empty, unused and shared items

- **Empty SFX sloty:** 62, 72, 75, 76, 77. V some path sa event 30, 40, 43 or 44 also calls, but payload missing.
- **Vzorky without find call-site v this Win16 listing-u:** sloty 35/event3, 37/event5, 47/event15, 49/event17, 54/event22, 60/event28, 74/event42, 85/event53. To nepreukazuje, that are unused v each release game; mean to only, that their v provided listing-u neviem assign.
- **Exact duplicity v snd.dat:** sloty 69 and 70 shared size 19 125 and offset 493 194; 73 and 74 shared size 11 424 and offset 528 025. WAV files 69/70 also 73/74 have same hashe.
- **Shared events:** slot66 sa uses for Bat alert also Dracula/raw20 prechod; slot67 for raw8 also raw20; slot45 for raw15/16 variant and at the same time raw27/28 v b862. One name therefore does not have to vystihovať each usage.

## Version and boundary analysis

1. Semantic inventúra above is for **snd.dat** z provided file. snd.zip contains 72 WAV file and 15 MIDI file; size each WAV file is exactly payload SND slotu + 44 bytes WAV headers. Sloty with same offset 69/70 and 73/74 sa match also obsahom.
2. File SND(5).DAT has also 111 records, but other length and other size/offset sound than snd.dat. Nemiešaj its offset nor assume o identical obsahu with touto table.
3. Obe available copies nite3w.exe have identical SHA256 12fe5168783446275802e0e947898261b5eca6b88288f3and895fc1faa4c544481, but link between this binary hashom and decompilation listing-om nite3w110.exe.c som separate kryptograficky unverified. Code conclusions are therefore formulované as evidence z provided Win16 listing-u.
4. Names as GUARD_BAT_DIE whether WEAPON_PLASMA are candidate label from workbook / OpenNitemare3D. For confirmed consider event→slot and its code path; exact akustickú interpretation unknown sample-ov by define confirm up to comparison play WAV-ov with behom game.

## Reproduction source v poskytnutom materiáli

- snd.dat: 111 records, table size/offset v 6-byte item.
- snd.zip: instrument bank, Song 001–015 MIDI and Sound 034–110 WAV; missing Sound WAV correspond zero SFX slotom.
- nite3w110.exe.c: routine 5132 on row 22056; e3b0 on 30845; door routines 188and/1and22 on 18194 and 18288; player death on 25226; explosive wall on 26144; change Dracula/raw17 on 26491; weapon fire on 27682; guard dispatchery b5e4/b6and0/b7fc/b862 on 27723, 27778, 27894, 27928; dancers/radio ae56 on 27317.
- OBJECTS.1–3: names objektov and tried GUARD.
- Nitemare3D_Enemy_Weapon_Database_v2(1).xlsx, list Sounds: candidate label with level C.