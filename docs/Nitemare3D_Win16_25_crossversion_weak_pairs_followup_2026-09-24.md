# Nitemare3D Win16 — check next 25 weak cross-version matches

Date: 24. 9. 2026

## Range

Check som first 25 z 38 items WIN marked weak/unresolved v cross_version_matches.csv, v order registra. Target build is Win16 V1.10; comparison covers available V1.3, V1.6 and V1.8 exporty.

This is not next 25 neauditovaných functions. Latest 12-point register already states manual static audit all 1 486 functions. This batch verify, whether weak automatic candidate actually corresponds to function v inom Win16 build.

## Zhrnutie result

- 17 z 25 targets has support counterpart v available older exportoch. Pätnásť has identical code vzor in all four build. Additional two are confirmed only for V1.6/V1.8/V1.10.
- 5 candidates has similar structure, but class, specifically message or helper ekvivalencia are not confirmed.
- During 3 target sa original candidate mismatch and older counterpart sa so far neurčil.
- Several weak candidates sa ukázalo as zlá address or as nejednoznačný súrodenecký constructor. Corrected map is listed during each item below.

„Confirmed match“ tu mean identical or correspond vzor v decompile C exportoch. Is not to confirmation raw instructions nor runtime behavior. This passability neotváral raw NE bytes nor did not run original Win16 program.

## Evidence and read stavov

confirm are based on z tiel functions, poradia priamych call, use fields and match adries v exportoch. Functional names without tela, similar score and same segment sa nepoužili as evidence. During each item are listed lines source C exportu.

Confirmed / probable / open distinguishes mieru evidence. „Confirmed“ opisuje only listed static match. Meaning classes, far-call ABI, reason difference resource text and runtime result can remain open.

## Register 25 items

| # | Function V1.10 | Original candidate | Result and priame comparison | C-export evidence |
|---:|---|---|---|---|
| 1 | FUN_1000_036and | NITE3W13 FUN_1008_2242 (0.5000) | **Candidate rejected; older counterpart open.** In V1.10 telo writes two pair values to first fields and nothing does not call. Proposed candidate in V1.3 calls FUN_1008_1e5c and writes other tag. Row tok also effect sa mismatch. Open: actual older counterpart sa z these exportov neurčil. | V1.10 L848–856; candidate V1.3 L11374–11381 |
| 2 | FUN_1000_0868 | NITE3W13 FUN_1000_0854 (0.6154) | **Probable match vzoru initialization.** Obe bodies initialize podobne layout arrays and save 0xFFFF as invalid value plus zero array. Tagy and text references sa differ; identita classes and meaning sentinelov are not confirmed. Open: Class, ownership handle and counterpart 1.6/1.8 needs to confirm z NE bytes and call miest. | V1.10 L1054–1064; V1.3 L1028–1038 |
| 3 | FUN_1000_0890 | NITE3W13 FUN_1000_087c (0.6296) | **Probable match vzoru initialization.** V oboch function sa second argument stores to array +4 and array +6 sa zeros; okolité initialize writes have same tvar. Tagy and text references sa differ, therefore confirm only konštrukčný vzor. Open: Exact class, register/stack ABI and counterpart 1.6/1.8 remain open. | V1.10 L1068–1078; V1.3 L1042–1052 |
| 4 | FUN_1000_3282 | NITE3W13 FUN_1000_326e (0.6000) | **Probable match generic loadera.** Obe functions call LOADSTRING with identify 0xFF and same pass output argumenty. V1.10 direction on text o zastaranej CONFIG.SAV, candidate on text o missing joystick driver. Code vzor fit, but text purpose sa differs. Open: Needs to compare call and resource map, aby sa confirm, whether is that certain obsluhu with vymeneným text. | V1.10 L3449–3457; V1.3 L3425–3432 |
| 5 | FUN_1000_338c | NITE3W13 FUN_1000_3378 (0.6552) | **Probable konštrukčná match; class open.** Obe bodies write three pair tag/text pointer and subsequently nulu to same relative array. Specifically tagy and text sa differ. Ten certain candidate sa offer also for other function, so unambiguous matching class is not supported. Open: Missing vtable/relocation and caller map for distinguish class and counterpart v 1.6/1.8. | V1.10 L3552–3565; V1.3 L3527–3540 |
| 6 | FUN_1000_33f4 | NITE3W13 FUN_1000_9ea8 (0.6111) | **Candidate rejected; older counterpart open.** V1.10 function calls FUN_1000_3418 and then restores tag object. V1.3 candidate calls FUN_1000_53c4 and writes other tag to konštruovaného object. Is different operations and difference direction toku. Open: Function 33f4 does not have z tohto compare confirm older match. | V1.10 L3584–3593; candidate V1.3 L8098–8105 |
| 7 | FUN_1000_6694 | NITE3W13 FUN_1000_6680 (0.7000) | **Probable match call sequences.** Order call and usage relative address sa match: first helper receive object +0x23, second entire object. Helper addresses and initial tag sa differ; without paired rozboru helperov is confirmed sequence, nie its complete meaning. Open: Needs to confirm, that dvojice helperov 0d8e/0d7and and 1666/1652 have identical effect. | V1.10 L5952–5960; V1.3 L5937–5945 |
| 8 | FUN_1000_9ebc | NITE3W13 FUN_1000_9ea8 (0.6471) | **Candidate rejected; older counterpart open.** V1.10 calls FUN_1000_53d8 and save tag 0x4C38. Proposed candidate calls FUN_1000_53c4 and save 0x48B0. Similar umiestnenie nor tvar constructor nepreukazujú same function. Open: Needs to search older counterpart according to caller/vtable links. | V1.10 L8099–8106; candidate V1.3 L8098–8105 |
| 9 | FUN_1008_028c | NITE3W13 FUN_1008_028c (0.6667) | **Confirmed match code vzoru in all 4 build.** Same function on same address initializes arrays v tom istom order in all four exportoch. Change sa tagy and text addresses, nie tvar write. Open: Name classes and meaning tagov remain uncertain. | V1.3 L10008–10019; V1.6 L10024–10035; V1.8 L10028–10039; V1.10 L9995–10006 |
| 10 | FUN_1008_0342 | NITE3W13 FUN_1008_0342 (0.6316) | **Confirmed match code vzoru in all 4 build.** In all four bodies is same condition nad array +4, call FUN_1008_0316, DIVIDE and reset object fields. Differences are v tagoch/text pointer. Open: Interpretation array +4 as own HDC is support API, but exact class remains open. | V1.3 L10079–10093; V1.6 L10095–10109; V1.8 L10099–10113; V1.10 L10066–10080 |
| 11 | FUN_1008_0c2c | NITE3W13 FUN_1008_0c2c (0.6471) | **Confirmed match code vzoru in all 4 build.** In all build sa executes FUN_1008_0316, RELEASEDC and subsequently FUN_1008_0342 v same order. Change are only tag/text references. Open: Ownership DC and reason separate paralelnej routines remain uncertain. | V1.3 L10473–10484; V1.6 L10489–10500; V1.8 L10493–10504; V1.10 L10460–10471 |
| 12 | FUN_1008_0c9e | NITE3W13 FUN_1008_0c2c (0.6471) | **Candidate is not jednoznačný; corrected counterpart is FUN_1008_0c9e.** FUN_1008_0c9e exist v each from four exportov on same address and executes same sequence as target. FUN_1008_0c2c is separate sesterská routine with same cleanup vzorom, therefore original proposal is not unique map. Open: Remains explain, why exist two takmer paralelné cleanup routines and whether sa differs source/type handle. | V1.10 L10501–10512; V1.3 L10514–10525; V1.6 L10530–10541; V1.8 L10534–10545; sibling candidate V1.3 L10473–10484 |
| 13 | FUN_1008_0d38 | NITE3W13 FUN_1000_3378 (0.6552) | **Original candidate rejected; confirmed counterpart on same address.** Same FUN_1008_0d38 exist in all four versions and preserves null guard also order initial write. FUN_1000_3378 is other routine with other tagmi. Open: Complete class and reason, why normalize select other constructor, are not z C exportu zrejmé. | V1.10 L10538–10551; V1.3 L10551–10564; V1.6 L10567–10580; V1.8 L10571–10584; candidate V1.3 L3527–3540 |
| 14 | FUN_1008_0e18 | NITE3W13 FUN_1000_9ea8 (0.6111) | **Original candidate rejected; confirmed counterpart on same address.** Same FUN_1008_0e18 in all build calls FUN_1008_0df6 and writes tagy v same order. Candidate FUN_1000_9ea8 calls FUN_1000_53c4 and has different effect. Open: Meaning tagov and object hierarchie remains open. | V1.10 L10620–10629; V1.3 L10633–10642; V1.6 L10649–10658; V1.8 L10653–10662; candidate V1.3 L8098–8105 |
| 15 | FUN_1008_1ed4 | NITE3W13 FUN_1008_1ed4 (0.6667) | **Confirmed match general wrappera in all 4 build.** All four bodies pass same value z array +0x30 total with same argumentmi to text helpera. V1.10 changes helper 3288 on 329c and text source; exact message sa between build differs. Open: Specific text resource and change helpera require caller/resource map. | V1.3 L11231–11237; V1.6 L11247–11253; V1.8 L11251–11257; V1.10 L11216–11222 |
| 16 | FUN_1008_2242 | NITE3W13 FUN_1008_2242 (0.6250) | **Confirmed match code vzoru in all 4 build.** Each build calls FUN_1008_1e5c and then sets same dvojpolový object tvar. Difference are only tag and text pointer. Open: Specific type create object cannot name only z tohto wrappera. | V1.3 L11374–11381; V1.6 L11390–11397; V1.8 L11394–11401; V1.10 L11359–11366 |
| 17 | FUN_1008_24d8 | NITE3W13 FUN_1008_24d8 (0.7143) | **Confirmed match code vzoru in all 4 build.** In all versions sa calls basic helper, writes sa same tvar object and array +0x1AND sa sets on nulu. V1.10 helper is 114and, older build use 1136. Open: Ekvivalencia helperov 1136/114and and name classes are not separate confirmed. | V1.3 L11508–11516; V1.6 L11524–11532; V1.8 L11528–11536; V1.10 L11493–11501 |
| 18 | FUN_1008_2ac2 | NITE3W13 FUN_1008_2242 (0.6250) | **Original candidate rejected; confirmed counterpart on same address.** Target also same older function call FUN_1008_24fa and initialize identical tvar. Proposed FUN_1008_2242 calls 1e5c, so is other branch. Open: Exact identita object classes and its caller links remains open. | V1.10 L11752–11759; V1.3 L11766–11773; V1.6 L11782–11789; V1.8 L11786–11793; wrong candidate V1.3 L11374–11381 |
| 19 | FUN_1008_3ea4 | NITE3W13 FUN_1008_3ea4 (0.6250) | **Confirmed match wrappera in all 4 build.** All bodies call 3e74 with same dvoma input, zero argumentom, text pointer and BP+1. Text sa changes z joystick messages on CONFIG.SAV message. Open: Text resource and specific event depend from callerov. | V1.3 L13157–13165; V1.6 L13173–13181; V1.8 L13177–13185; V1.10 L13141–13149 |
| 20 | FUN_1008_60fe | NITE3W13 FUN_1008_60fe (0.6923) | **Confirmed match terminate wrappera in all 4 build.** Each build calls FATALAPPEXIT with abnormal-termination text and second string argumentom. First text remains same, second sa between asset/build changes. Open: Exact semantika second argumentu importu remains open. | V1.3 L15641–15649; V1.6 L15657–15665; V1.8 L15661–15669; V1.10 L15626–15634 |
| 21 | FUN_1008_673and | NITE3W16 FUN_1018_23d6 (0.5000) | **Original candidate rejected; confirmed function on same address in all 4 build.** Target also same older address call GLOBALFREE. Proposed FUN_1018_23d6 namiesto toho calls 070c with text o zaseknutej weapon, therefore is not counterpart. Argument GLOBALFREE is v exporte ukázaný as address string+6; its handle/pointer ABI neuzatváram. Open: What exactly argument GLOBALFREE denotes, needs to confirm v raw ASM/caller trace. | V1.3 L16001–16006; V1.6 L16031–16036; V1.8 L16035–16040; V1.10 L15999–16004; wrong candidate V1.6 L33577–33583 |
| 22 | FUN_1010_0006 | NITE3W16 FUN_1010_0006 (0.6667) | **Confirmed match initialize vzoru in all 4 build.** All build call init helper with nulou and subsequently save tag 0x5D4 and string pointer. V1.10 helper is 3936, older build 3922. Open: Specific class and ekvivalencia helperov 3922/3936 wait on xref/relocation confirmation. | V1.3 L17275–17282; V1.6 L17305–17312; V1.8 L17309–17316; V1.10 L17270–17277 |
| 23 | FUN_1010_0424 | NITE3W13 FUN_1010_0420 (0.4000) | **Confirmed functional match in all 4 build; V1.3 has different offset.** Each version executes cleanup and terminate ten certain dialog result 6. Cleanup helper sa changes: V1.3 16d6, V1.6 1918, V1.8 19e2, V1.10 1and4and; event EndDialog remains same. Open: Reason different cleanup helpera across build requires caller and dialog-state map. | V1.3 L17471–17477; V1.6 L17501–17507; V1.8 L17505–17511; V1.10 L17465–17471 |
| 24 | FUN_1010_085e | NITE3W16 FUN_1010_085e (0.6471) | **Confirmed match in V1.6/V1.8/V1.10; V1.3 so far unidentified.** V troch newer build telo calls FUN_1008_1352 and sets tag 0x8DC with same poradím. V1.3 does not have found pair v this exporte; to nedokazuje, that function absentuje. Open: Counterpart V1.3 and exact class remain open. | V1.6 L17568–17575; V1.8 L17572–17579; V1.10 L17532–17539 |
| 25 | FUN_1010_097c | NITE3W13 FUN_1000_9ea8 (0.4000) | **Candidate V1.3 rejected; confirmed match in V1.6/V1.8/V1.10.** V1.10, V1.6 and V1.8 call FUN_1008_24d8 and set tag 0xBA0. Proposed V1.3 FUN_1000_9ea8 calls FUN_1000_53c4 and executes other initialize. V1.3 counterpart sa did not find. Open: Counterpart V1.3 needs to search through caller/vtable, nie according to original score. | V1.6 L17579–17586; V1.8 L17583–17590; V1.10 L17543–17550; wrong candidate V1.3 L8098–8105 |

## Summary according to build

- V1.3: 15 correspond tiel is support priamym compare; during 0424 is older offset 0420. Additional old targets 036and, 0868, 0890, 3282, 338c, 33f4, 6694 and 9ebc are probable or open according to tables.
- V1.6 and V1.8: 17 map is supported telom v exporte. Functions 1010:085e and 1010:097c are confirmed v these dvoch build, nie however in V1.3.
- V1.10: all 25 target tiel is lokalizovaných and check.
- Four available Windows build represent V1.3, V1.6, V1.8 and V1.10; match v C exporte sa do not transfer on missing or unverified historical release.

## Zdroje and hranice

- C export V1.10, nite3w110.exe.c, SHA-256 71ca365f8c6and61fa9cadad8631e9fcd6ce134e36c714878889c75b7399280168.
- C export V1.3, NITE3W13.EXE.c, SHA-256 4ceccb6and7b91fa7and145502974961c0e7b1dd41d8e8and842eb0eb11f6af99cfe0d.
- C export V1.6, NITE3W16.EXE.c, SHA-256 81355c8b54ddce7da77fc9fef7ab5b39fb3087e3485df37d3and83c2b24f940c0c.
- C export V1.8, NITE3W18.EXE.c, SHA-256 0917624ccdc53and98and6ea04760689d989692bf2d86b818d86fd2and26c889f8cc94.
- Automatic register candidates, cross_version_matches.csv, SHA-256 e43292295c806b8d4ec8f9f6cca52e49e11e179195176fadea606c02and2937f1d.
- Manual status functions: Nitemare3D_1486_function_12_point_status_2026-09-24.csv.

C export is not original source code and can skresliť boundary, registers, far-pointer argumenty or class arrays. Row references determine exact export, nie file offset v EXE. Runtime, relocation and raw instructions these 25 tiel v this batch were not znovu verify.

## What remains

V this Win16 set remains 13 z 38 weak row still nepreverených. Z just check 25 remains five probable paired and three targets without determine older matches. DOS candidate are separate next okruh; their lines sa touto batch nemenia.