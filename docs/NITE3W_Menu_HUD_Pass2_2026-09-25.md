# NITE3W 1.10 — Menu/HUD, second priamy binary priechod

**Date:** 25. 9. 2026  
**Range:** obsluha key and mouse v internom menu, format items menu, konfigurácia and cheats, softvérové prekrytie and return to game screens.  
**Input:** use provided `nite3w(20260925-063336).exe`, 230 400 B.  
**SHA-256:** `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.

## 1. Result and evidence boundary

This priechod nadväzuje on previous analysis HUD dispatchera, portrétov, ammo, automapy and UIF.DAT. Tie nepovažuje for new objavy. Novým result is specific reconstruction path input → item menu → action, right uplatnenia set and restore draw pozadia.

Z original bytes was vyčítaných **14 tabuliek with 80 neprázdnymi 18-byte item** and table **40 numeric input akčného dispatchera**. Ten z these 40 input vedie directly on shared return. Nejde therefore o 40 separate functions or 40 same podrobných semantic auditov.

**Performed verify:** 64 check identity, bytes, relocation and structure; 18 skupín test odvodeného C++ modelu, total 498 902 úspešných assertions. C++ model was skompilovaný and running. Original EXE sa nespúšťalo in Windows nor v emulátore procesora. Test modelu are not runtime confirm original game.

Addresses `3:xxxx`, `4:xxxx` and podobne mean poradové number NE segment and offset. Are not to runtime selectory. Names functions are analytické proposal, nie restore original symbol. Project Ghidra aliasy v katalógu sa relationship k doterajšiemu spôsobu importu; are not univerzálnymi address each new importu.

Main primary evidence is `evidence/annotated_pass2.asm`. Contains original instructions with NE relocation and vyriešenými priamymi far call. Table skokov is označená as **DATA**, aby sa its words nezapočítali as instructions.

## 2. Architektúra interného menu

Main parts identify toku:

```text
Klávesnica / poll tlačidiel myši
    → Ui_RouteInput (4:2FC6)
    → Menu_HandleKey (4:2E12), keď DS:04A2 == 3
    → lokálna zmena hodnoty, zmena výberu alebo Menu_DispatchAction (4:27DE)
    → prípadný callback položky / zmena obrazovky
```

Mouse najprv iterate through `3:95AE` and check hit text obdĺžnikov `4:128A`. Corresponding synthetic Enter or Escape sa then passes UI path.

`DS:04A2` distinguishes viac UI state. Value 3 vedie to menu, 4 to osobitnej modálnej obsluhy and 5 to prehliadača instructions. Values 0 and 2 have initialize/titulnú path. **These values nezamieňať with state `DS:46B4` and `DS:46B6`**, which patria to iných rozhodovacích vetiev.

### Format 18-byte record

| Offset | Size | Meaning v preskúmaných path |
|---:|---:|---|
| +00 | 1 B | Numeric action items. |
| +01 | 1 B | In all vyčítaných item nula; exact meaning unclosed. |
| +02 | 2 B | Value; meaning depends from typu items. |
| +04 | 1 B | Designation current vybratej items. |
| +05 | 1 B | Type/behavior items. |
| +06 | 4 B | Far pointer callbacku. |
| +0AND | 2 B | X poloha. |
| +0C | 2 B | Y poloha. |
| +0E | 4 B | Far pointer textu. |

Value on +02 is not univerzálne „slider“. During different type can be switch, znamienkovou size or data slotu. Byte +01 sa only on základe zero values neoznačuje for dokázané padding array.

Preskúmané type: 1 = command, 2 = switch bitu, 3 = switch znamienková value/posuvník, 4 = editácia text, 6 = neprístupná item. Type 5 sa nepriraďuje nepodložená semantic.

### Vyčítané tables

| NE address | Items | Content |
|---|---:|---|
| 7:0FAA | 6 | Main menu without active game. |
| 7:1028 | 7 | Main menu with návratom to game. |
| 7:10B8 | 7 | Main menu with Restart at last save. |
| 7:1148 | 3 | Selection episodes. |
| 7:1190 | 3 | Selection difficulty levels. |
| 7:11D8 | 3 | Konfigurácia. |
| 7:1220 | 10 | load save. |
| 7:12E6 | 10 | Game saving. |
| 7:13AC | 5 | Hardware. |
| 7:1418 | 6 | Cheats, Done and Cancel. |
| 7:1496 | 10 | Selection podlažia. |
| 7:155C | 3 | Movement after schodoch hore/dolu and zrušenie. |
| 7:15AND4 | 2 | Zostup and zrušenie. |
| 7:15DA | 5 | Distance doors, kanóny and zrušenie. |

Each table terminate 18 zero bytes. result range ends exactly on konci data segment 7, `0x1646`. Ten items load/save has v surových table zero text pointer, which sa dopĺňajú for behu. Is not correctly interpretovať their as ten doslovných text „None“.

Complete strojovo čitateľný rozpis including action, type, field and callbackov is v `menu_records.csv` and `menu_records.json`.

## 3. Akcie menu: 40 vstupov, nie 40 functions

Dispatcher `4:27DE` subtracts from action 1, compares unsigned result with 39 and uses 40-slovnú table on `4:27FA`. After table continues code on `4:284A`.

Important skupiny: 1 main menu, 2 new game, 3 konfigurácia, 4/5 selection/load save, 6 screen save, 8 instructions, 10 demo, 11 return/reštart, 17 cheats, 18–20 episodes, 21–23 difficulty, 26 selection podlažia, 27–29 schody, 30–31 distance doors, 32–33 kanóny, 38 hardware, 39 save konfigurácie and 40 confirmation cheats.

Action **7, 12–16 and 34–37** v this dispatcheri vedú on shared return `4:2B7A`. Z toho nevyplýva, that corresponding items are nefunkčné. Switches for example changes directly obsluha key; editácia save name uses other path.

Some different action shared execute block. V this priechode sa nevyhlasuje complete pochopenie all vedľajších účinkov save, podlaží or distance commands only on základe addresses their target.

## 4. Keyboard and movement selection

### `4:2E12` — meaning key

| Input | Effect |
|---|---|
| Enter or Space | During type 1 executes action; during type 2 switches low bit values; during type 3 neguje 16-bitovú value; during type 4 začne editáciu. |
| Escape | Shared return `4:1512`. |
| Šípka hore/dolu | Move selection through `4:11F6`. |
| Šípka vľavo/vpravo | Change values only during type 3. |
| Other key | Without listed local operations; still can nasledovať callback items. |

Numeric codes correspond Windows virtuálnym key: Enter 13, Space 32, Escape 27, Left 37, Up 38, Right 39, Down 40. Named these konštánt is verify proti dokumentácii Microsoftu; themselves behavior pochádza z EXE.

### Selection neprechádza through konce list

`4:11F6` moves pointer o 18 B and preskakuje type 6. On element record šípka hore remains on start, on poslednom šípka dolu remains on konci. Is not tu kruhový prechod posledná → first.

Loop has limit 100 pokusov; during nenájdení available items restores original selection. **100 is not dokázaný maximálny count items format.** Is to ochranný limit tohto search.

During change sa prekreslí original and new vybraná item. Is not needed z toho vyvodzovať complete prekreslenie entire menu during each movement selection.

## 5. Znamienkové posuvníky

Type 3 uchováva size also zapnutie v jednom 16-bitovom slove. Positive value mean zapnutú item; negative uchováva size vypnutej items. Enter/Space executes `NEG word [entry+2]`.

Šípky use 16-bitovú absolútnu value, add −5 or +5 and result obmedzia on 0–100. Change normal nonzero value is positive, therefore šípka can at the same time item znovu zapnúť.

```text
+50 → Enter → −50 → Enter → +50
−50 → Right → +55
−50 → Left  → +45
0   → Enter → 0
```

This model sa nesmie nahradiť dvojicou bool/int without zachovania listed behavior. During nule negácia does not change value. Value `−32768` remains after 16-bitovej absolútnej operation negative bitovým vzorom; subsequent arithmetic can during Left 100 and during Right 0. Is confirmed consequence instructions for this input, nie o tvrdenie, that štandardné ovládanie this invalid range reach.

Conclusion part obsluhy checks callback on +06. Does not have to sa call only after actual change values. To is important during napodobnení interim aplikácie Hardware. Katalóg neprezentuje all okolnosti callbacku as jednu univerzálnu event „onChange“.

## 6. Mouse: confirmation during free and separate return latch

`3:95AE` calls import USER ordinal 249 for virtuálne tlačidlá 1 and 2. Primary exportná špecifikácia Wine ho denotes as `GetAsyncKeyState`; its upper bit opisuje current stlačenie. V this code sa therefore pracuje with okamžitým state, nie with lower bitom „was stlačené from previous read“.

Derived model:

```text
leftReleased = !leftDown && previousLeft
key = leftReleased ? Enter : (rightDown && !cancelLatch ? Escape : 0)
previousLeft = leftDown
cancelLatch = rightDown || leftReleased
```

Dôsledky: left tlačidlo confirms during prechode stlačené → free; right vyvolá Escape, when is stlačené and return latch is not set. During súbehu has free left tlačidla prioritu. Latch is not only named `previousRight`: sets sa also after free left tlačidla, and therefore záleží on order events.

Hit test `4:128A` uses text obdĺžnik according to active bitmapového fontu. Upper boundary test are **inkluzívne**: `x ≤ mouseX ≤ x+text` and obdobne for Y/fontHeight. Type 6 is vyradený.

Movement mouse changes vybranú item only vtedy, when sa field differs from cache `DS:40FE/4100`. Stojaca mouse therefore does not have hneď zobrať selection, which player move key. Enter mimo valid hit neaktivuje item; Escape sa can pass also mimo hit.

V preskúmanej path was not found record „item, on ktorej začalo stlačenie left tlačidla“. Therefore sa without next evidence nepridáva moderné right capture items during stlačení. Nor frekvencia repeated key sa tu neoznačuje for odmeranú; systémová provided events still requires runtime verify.

## 7. Hardware: change sa aplikujú interim

Table `7:13AC` contains Mouse, Joystick, Music, Sound FX and Save. All five vyčítaných callbackov direction to `4:2596`.

`4:2516` loads runtime values to items menu. `4:2596` their iterate through, prenáša zapnutie and size to game global premenných and corresponding zariadení; subsequently synchronizuje display values back.

| Zariadenie | Zapnutie | Size |
|---|---|---|
| Mouse | DS:4BE0 | DS:4BDC |
| Joystick | DS:4BE3 | DS:4BDD |
| Music | DS:4BE1 | DS:4BDE |
| Sound FX | DS:4BE2 | DS:4BDF |

Normal change items therefore is not odložená up to on Save. **Return z Hardware itself nevracia already uplatnené runtime values.** Action 39/Save moreover calls konfiguračnú write path `3:534E` and returns sa through `4:1512`. V this priechode sa znovu nedokazuje entire format konfiguračného file nor result work ovládača during behu.

## 8. Cheats: working values and confirmation Done

Table `7:1418` has on difference from Hardware zero callbacky. Its four switches are type 2. During open `4:26F0` skopíruje status `4BE4/4BE5/4BE7/4BE6` to menu; obsluha switches najprv only values items.

Done has action 40 and calls `4:2746`. Function writes values to runtime, calls check `3:C772(1)` and during success continues through `3:B128` to aplikácie účinkov. During neúspechu **zeros all four runtime cheat flags** and displays message; is not correctly hovoriť, that check always predchádza akémukoľvek write. Vstavaný text hovorí o available cheats with complete trilógiou.

Cancel has action 25 and ide through shared return without this aplikácie. Rozpracované switches menu sa therefore nepreberú to game. Is not to general mechanizmus undo already execute game účinkov.

Difference important for port: Hardware is interim aplikované set; Cheats uses working values with osobitným confirm. Jednotný general dialog with same Apply/Cancel behavior for obe screens by this different stratil.

## 9. Selection difficulty levels and episodes: text is linked with setterom

On `4:29E0` sa from numeric action subtracts 21 and result sa stores to `DS:4C14`. V spojení with table `7:1190` to dokazuje:

| Text | Akcia | Stored difficulty |
|---|---:|---:|
| Be gentle! | 21 | 0 |
| I'm tough! | 22 | 1 |
| Let'with party! | 23 | 2 |

Nejde only o estimate poradia according to text or behavior enemies. V this priechode was spojená table items with specific write.

episode branch `4:29CE` uses action 18–20, subtract 17 and write 1–3 to `DS:4102`. V surovom EXE have three episode items type 6. `4:244C` format names `map.%d`, checks available and related bránu and allow items. Raw type 6 therefore is not evidence, that episode nikdy cannot vybrať.

## 10. Softvérové prekrytie: najprv save podklad, then ho restore

Function `3:440A` has three operations:

| Operation | Role |
|---:|---|
| 0 | Sets posledné X on −1, čím zneplatní store field; sama nevymaže image. |
| 1 | If is field valid, restores capture pozadie on original coordinate. |
| 2 | Clip field, capture new pozadia and vykreslenie priehľadného image. |

Restore operation 1 **sama nenastavuje X back on −1**. During reconstruction sa therefore nesmie automaticky add jednorazové spotrebovanie zálohy, which v this tele is not.

During operation 2 sa calls `3:4368`, then `3:41A2` with priehľadným index `0x29`. Clip uses stored right and spodné boundary mínus rozmery image; model nepridáva svojvoľné +1. For určených condition uses entire rozmery 320×200, otherwise boundary viewportu.

In windowed branch `3:4368` has source framebuffer row step 320, but záloha sa creates after column:

```text
sourceIndex = (y0+y)*320 + (x0+x)
backupIndex = x*height + y
```

HUD operation 23 restores prekrytie. Operation 24 during svojich mode and input condition draw vybraný image descriptor; operation 25 has next DOS branch. These blocks are v katalógu marked as **blocks v HUD dispatcheri**, nie new separate functions.

Prekrytia already are not only hypotézou o „dirty rectangles“: save and restore specific podkladu is visible v code. Exact vzhľad select IMG images and match rozmerov all descriptorov however still require corresponding IMG data.

## 11. Return to game restores entire HUD

Previous audit ukázal, that right `3:BA54` update only selected layer. Teraz is doložená also separate complete restore.

`4:1E7C` contains load **UIF screens 5**, call render/presentačnej path, condition opätovné load pozadia v DOS branch and **`Hud_Dispatch(0)`**. Then nasledujú additional row/palette and kalibračné steps. `3:BA74` v this string is not named as next complete HUD redraw; has different palette/event role.

`4:1ED0` sets game state and this restore calls. Is available z návratu/reštartu action 11 also z úspešnej load branches action 5. Next modálna load path also explicitne uses UIF5 and HUD0.

**result model:** normal frames draw selected dynamic layer, events menia individual data and prechod back to game has osobitnú path on znovuvytvorenie image. Thereby still are not test all Windows paint/expose/minimize situácie.

## 12. Strata fokusu and osobitný DOS Mode

MFC message-map record for message 8 vedie to `3:0ABE`; that požaduje mode 4 through `3:2D9C`. Is path process straty fokusu. V display dispatcheri this požadovaný mode vedie through `3:2D58` k opusteniu DOS Mode and k restore okenného mode.

When is DOS flag set, `3:2D58` najprv uses HUD operation 23 on restore prekrytia, further calls video/DisplayDib path, free capture mouse and pracuje with kurzorom. On konci nuluje `DS:46B0`.

Vstavané varovanie EXE explicitly different osobitný DOS Mode from maximalizovaného fullscreen window. This is property and varovanie provided binaries, nie new záruka compatibility with modernými Windows. Switch display, palette and fokus require runtime stopu; do not have sa považovať for test only úspešným test C++ arithmetic.

## 13. Katalóg proposal name

`evidence/function_names.csv` contains **25 functions and 3 internal blocks**. Important new names:

| NE address | Proposal |
|---|---|
| 4:11F6 | Menu_MoveSelection |
| 4:128AND | Menu_HandleMouseHit |
| 4:2516 | Settings_ReadToMenu |
| 4:2596 | Settings_ApplyMenuToRuntime |
| 4:26F0 | Cheats_ReadToMenu |
| 4:2746 | Cheats_ApplyAndValidate |
| 4:27DE | Menu_DispatchAction |
| 4:2E12 | Menu_HandleKey |
| 4:2FC6 | Ui_RouteInput |
| 3:95AE | Input_PollMenuMouseEdges |
| 3:4368 | Video_CaptureRectColumnMajor |
| 3:440AND | Overlay_SaveDrawRestore |
| 4:1E7C | Ui_RebuildGameScreen |
| 4:1ED0 | Ui_EnterGameplay |

Katalóg pomenúva doloženú main role. Nepredstiera, that each listed prototyp, each call and all vedľajšie branches are already completely zrekonštruované. Block `3:A7AC/A7C2/A7FA` sa do not have automaticky create new function boundaries v IDA/Ghidre.

## 14. Performed tests and their meaning

| Overenie | Result | Hranica |
|---|---:|---|
| Identita, inštrukčné bytes, relocations, tables | 64/64 | Fixed zvolené check body, nie each instruction EXE. |
| Skupiny C++ modelových test | 18/18 | Derived model, nie emulované original instructions. |
| Individual assertions | 498 902 úspešných | Count check tvrdení, nie count jedinečných game scén. |
| CMake/CTest | 1/1 | Zostavenie and run local modelu. |
| Beh original game in Windows | 0 new records | V this priechode nevykonaný. |

Modelové pokrytie zahŕňa all 256 input bytes key during šiestich value type items, all 65 536 bit vzorov values switch and posuvníka, 256 masiek neprístupnosti during eight item and oboch direction, 16 state combination tlačidiel mouse and 95 631 logical field during clip prekrytia. Test also inkluzívne boundary, stojacu mouse, trvanie store field and copy synthetic podkladu.

Check invalid input modelu are explicitly moderné safe behavior. Neopisujú automaticky valid in the original EXE. Test verify internal konzistenciu odvodeného modelu; independent match with original programom during behu remains separate role.

## 15. What remains open

Exact visually assign all IMG ikon and descriptorov, complete editor name save including all key, all vedľajšie effects modálnych image and systémového repeated key, runtime paint/expose/minimize path and behavior during switch DisplayDib/WinG. Some rozpracované elements are static named, but nie pixel nor time compare with bežiacou hrou.

Overall Menu/HUD sa nepriraďuje new nepodložené percento. result are specifically closed questions, addresses and performed test. To GitHubu this priechod nič nezapísal.

## 16. Source and reprodukovateľnosť

Primary source: use provided EXE with hashom v úvode. evidence files and test are part of package; original EXE, UIF, fonty and grafické assety sa v this doplnkovom package nepribaľujú.

Externé primary referencie slúžia only on named Windows API/konštánt, nie as evidence game logic:

- Microsoft, Virtual-Key Codes: https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
- Microsoft, GetAsyncKeyState: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getasynckeystate
- Wine, primary exportná špecifikácia USER Win16: https://raw.githubusercontent.com/wine-mirror/wine/master/dlls/user.exe16/user.exe16.spec
- Microsoft, WM_KILLFOCUS: https://learn.microsoft.com/en-us/windows/win32/inputdev/wm-killfocus

Postup repeated static check and kompilácie is v `README.md`. Test logy are v `valid/`; manifest hashov file package is v `MANIFEST_SHA256.json`.