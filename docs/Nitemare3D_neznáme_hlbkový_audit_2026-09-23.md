# Nitemare 3D — hĺbkový audit toho, čo ešte nepoznáme

Stav: 23. 9. 2026. Audit porovnáva presne hashované DOS a Win16 binárky:

- Win16 `nite3w(20260921-205703).exe`, SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.
- DOS `N3D-UNFU(2).exe`, SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.

Adresy Win16 sú `segment:offset`; adresy DOS v tomto audite sú offsety rozbaleného MZ image (fyzický súborový offset je image offset + `0x200`). Raw selector v NE far-call inštrukcii nie je cieľový segment; interné ciele boli potvrdené cez NE relocation chain.

## Nové veci, ktoré už nie sú neznáme

| Téma | Priamy dôkaz | Záver |
|---|---|---|
| Command line `-o` | Win16 `3:1204` zapisuje `DAT_46AB=1`; DOS image `0x4BB4` zapisuje `DAT_3CD0=1` | Obe verzie majú skutočný logger aktivátor `-o`; `-debug` tým nie je dokázaný. |
| Debug logger | Win16 `4:3367–33B8`, DOS image `0x47DB–0x482C` | Flag otvára/appends `debug.txt`, formátuje záznam a súbor zatvára. Win16 zapisuje audio/MIDI inicializačné správy; nie je to dôkaz univerzálneho debug menu. |
| Argumentové vetvy | Win16 prijíma druhé písmeno `b,c,d,e,f,l,o,p,r,s,w`; DOS `a,b,c,d,e,f,l,o,p,q,r,s,t,w,x` | Tabuľky dispatchu sú známe. Semantika viacerých vetiev a hranice medzi buildmi ešte nie. |
| SEQDEF interval | Win16 `3:669A`, `3:9E78`, `3:9ED4` používajú `ADD word [seq+2]`, potom `ADC dword,0` | Interval je 16-bitový; deadline v objekte je 32-bitový. |
| SEQDEF cache | `3:4FB1–5011`; `+00` počet frame-ov, `+02` interval, `+04` near pointer 90 B definície, `+06` pointer frame tabuľky | Cache entry má 8 B; detailná definícia je samostatných 90 B. |
| GUARD `+12` | `3:6F1E` porovnáva cache smeru, `3:6F2F` zapisuje variant 0–7, `3:81F3` dáva 8 | `+12` je smerová sprite cache/invalidácia, nie pain timer. |
| GUARD `+02..05` | `3:8495–849D` nuluje DWORD `+02` a timer `+06`; `3:CE81–CE9D` zapisuje render counter do `+02..05`; `3:8B5D–8B66` ho porovnáva pri hitscane | Je to 32-bitový stamp posledného render/aim kandidáta, ktorý prepája projekciu so zásahom. |
| Budenie po výstrele | `3:8BF3` volá `3:7664`; `3:7664–76FA` nastavuje 64-bajtovú latch tabuľku a budí guardov v rovnakom area ID | Potvrdený lokálny area wake mechanizmus po úspešnej streľbe/projektili; nie je tým dokázané šírenie hluku medzi všetkými oblasťami. |
| Area ID | `3:247A–24BA` hľadá wall class `0x44`, vracia `wall_id-base_id`; guard/player ho ukladajú do `+0E`/`4C1C` | `GUARD+0E` je area/sector ID odvodené od mapovej značky. |
| RNG | Win `2:6EC8`, DOS image `0x150D8`, multiplikátor `0x343FD`, prírastok `0x269EC3`, výstup `(state>>16)&0x7FFF` | DOS/Win používajú rovnaký 32-bitový generátor; Win16 DEMO/reset vetva seeduje 1 a nuluje čítač `53DC`. |
| DOS/Win spoločný helper | Win `2:7118–7149` a DOS image `0x159B8–0x159E9` majú identický 32-bitový násobič | Silný dôkaz spoločného herného jadra. |
| `DAT_53DC` | Win `3:D78C` inkrementuje DWORD pred render pipeline | Je to generácia render/simulácie; presná vzťahová jednotka k millisekundám zostáva otvorená. |

### Presnejší limit percepcie a LOS

Win16 rutina `3:7494–758A` a DOS rutina `image:0x5342–0x5438` majú rovnakých 247 bajtov po normalizácii dvoch adries hráčových súradníc a far-call relokácie. Obe prevedú cieľové X/Y na bunky mapy (`>>6`) a vrátia neúspech, ak je absolútny rozdiel na ktorejkoľvek osi väčší než `8` buniek. Pri bežnom štvrtom argumente `0` vytvoria smerovú masku z aktuálneho smeru stráže a dvoch susedných smerov modulo 8. Pomer osí vyberá masku `0x66` alebo `0x99`; znamienka X/Y vyberú ďalšie masky `0x0F/0xF0` a `0x3C/0xC3`. Kód potvrdzuje trojsmerový filter, ale samotné bajty neoprávňujú pomenovať číselné smery ako svetové alebo kompasové orientácie.

Po range a smerovom teste obe verzie volajú Bresenham LOS s limitom 8 mapových krokov. Win16 `3:D50A–D66A` a DOS `image:0xBB60–0xBCC0` sú bajtovo zhodné po normalizácii mapových adries, segmentových hodnôt a far-call relokácií. V prvej rovine blokuje kombinácia bitov `0x02` a `0x04`; pri kombinácii `0x02` a `0x08` sa volajú validátory `3:1296` a `3:1476`. Ak tretí argument LOS-u je `1`, skúma sa aj druhá rovina a kombinácia bitu `0x02` bez `0x20` blokuje priechod. Významy bitov zatiaľ nepomenúvam, kým sa nedohľadajú ich zapisovatelia a triedy mapových dát.

Wrapper Win16 `3:7594–762B` / DOS `image:0x5442–0x54CE` nastavuje príznak LOS na `GUARD+0x17` a samostatný príznak blízkosti na `GUARD+0x18`, keď oba world-coordinate rozdiely nepresiahnu `0x40`. Kombinované príznaky `0x00010001` obchádzajú smerový filter a zapínajú kontrolu druhej roviny. Selektor `GUARD+0x16=0` vracia blízkosť (`+18`); hodnoty `1` a `2` vracajú LOS (`+17`). Win16 inicializácia nastaví predvolene `+16=1`; triedy objektov `08–0A`, `11–14` a `1A` dostanú režim `0`. Zapisovateľ hodnoty `2` zatiaľ nebol potvrdený.

Potvrdené páry volajúcich stavov: Win16 state 7 (`3:7D55`) a 8 (`3:7DD3`) zodpovedajú DOS `image:0x5BE5` a `0x5C5D`; obe verzie odovzdajú nulové príznaky, takže používajú smerový filter aj druhú rovinu LOS-u. State `0x15` (`3:82AE` / DOS `image:0x612B`) odovzdá `0x00010000`, obíde smer a vypne test druhej roviny, pričom uloží surový výsledok do `+17`. Wrapper používajú aj states 3, 4 a 10 (Win16 `3:7C49`, `3:7C93`, `3:7F59`; DOS `image:0x5AE2`, `0x5B28`, `0x5DDB`). To ešte nie je úplný zoznam priamych a nepriamych čitateľov v celej AI state machine.

Fallback pohyb Win16 `3:76FC` / DOS `image:0x55A8` používa oba príznaky: `+17=0` vyberá 4 náhodné kandidátne smery, `+17=1` osem. Ak `+18` hovorí, že hráč je blízko, nastaví oneskorenie 8 tickov; bez blízkosti a bez LOS-u 24 tickov; pri LOS-e volí 8–15 tickov a škáluje ich difficulty poľom (`DAT_4C14` / DOS `0x4180`, kód 2 polovica a kód 0 dvojnásobok). Presné názvy smerových tried, význam mapových bitov, ostatní konzumenti v state machine a šírenie poplachu medzi oblasťami zostávajú otvorené.

### GUARD AI dispatcher: potvrdené vetvy Win16

Win16 `FUN_1010_7b56` (`3:7B56–80A9`) prepína podľa GUARD byte `+0x0B`; raw disassembly je priložená v evidence. Z kódu sa dajú potvrdiť tieto operácie bez toho, aby sa číselným stavom priraďovali neoverené mená:

| Stav | Potvrdená operácia |
|---:|---|
| `00` | Posúva frame a timer; po vypršaní obnoví stav z `+0x0C`. |
| `01` | Odpočítava timer a po nule nastaví `02`. |
| `02` | Volá `b862`, potom načíta class-table sekvenciu z `+0x34` a nastaví `03`. |
| `03` | Vnímanie cez wrapper; neúspech ide na fallback `05`, úspech nastaví sekvenciu `+0x36` a stav `04`. |
| `04` | Pri úspešnom perception teste volá `b5e4` a `8c0a`; okrem runtime mode `46B4==2` potom plánuje stav `05` cez sekvenciu `+0x38`. |
| `05` | Fallback steering; spotrebuje `+0x17/+0x18` podľa už doloženej LOS/blízkosti logiky. |
| `06` | Pohybová/anim. vetva s countdownom; po nule prejde na `03`. |
| `07` | Najprv aktualizuje pohyb; ak `4BE7==0` a FOV/LOS uspeje, prejde na `02`, alebo na `13` keď byte `+0x0A==3`. |
| `08` | Aktualizuje orientáciu/pohyb; ak návratový stav `+0x0C==2`, `4BE7==0` a perception uspeje, nastaví `02`. |
| `09` | Útočná vetva `a0ee`; pri hitscan mode volá `b6a0`. Pri konkrétnych wall/object flagoch nastaví nájdenému OBJECT-u `+0x0C=4`, `+0x0D=0`. |
| `0A–0B` | V recovered switchi nemajú explicitné case vetvy; možné nepriame použitie alebo chybný/širší dispatcher zostáva otvorené. |
| `0C–0D` | Prechádzajú spoločným `6ee0` call path s príznakom 0; presný herný účel zatiaľ nepomenovaný. |
| `0E–10` | `51A5` prepína cyklus `0E/0F`; pri timeout-e sa zhodné area ID môže odovzdať cez `b5e4`, stav `10` čaká a potom cez perception môže spustiť `8c0a`. |
| `11` | Po timeri vyberie smer cez `d454`, vynuluje pohybové odchýlky a vráti sa do `07`. |
| `12` | Posúva frame, znižuje OBJECT `+0x1A` po 5 a čaká aj na timer; potom obnoví stav z `+0x0C`. |
| `13` | Časovaný pohybová vetva `7a44`; `7a06` ju inicializuje náhodným timerom 8–87 a smerovou tabuľkou. |
| `14` | Odpočítava timer; pri hodnote pod `0x60` volá pohybovú rutinu `71dc`; pri štarte bez času volá `ae56(1)`. |
| `15` | Posúva frame do konca sekvencie a obnoví stav z `+0x0C`. |

To spresňuje behaviorálnu mapu viacerých predtým otvorených stavov, no zatiaľ iba pre Win16. DOS Ghidra export zlúčil oblasť okolo `FUN_1000_5f74` a obsahuje nespoľahlivé hranice/control flow; byte parity a presné DOS state-to-state mapovanie preto nie sú uzavreté. Zostáva pomenovať stratégie, sledovať všetkých writerov `+0x0B/+0x0C`, overiť chýbajúce `0A/0B`, alarm šírenie a boss/episode callery.

### Renderer: vector/span pipeline, nie klasický jeden-ray-na-stĺpec model

Novšia kontrola dekompilátu Win16 1.10 spája projekciu steny, výber viditeľného vlastníka stĺpca a tvorbu span záznamov. Toto je oprava staršieho zjednodušeného DDA prototypu: renderer stien sa v tejto vetve neopiera iba o nezávislý lúč pre každý obrazový stĺpec. Zatiaľ ide o statické pochopenie Win16 cesty; DOS VGA pixelová parita nie je potvrdená.

- `FUN_1010_e798` číta 28-bajtový vektor; jeho koncové world súradnice sú na `+0x0C/+0x0E` a `+0x10/+0x12`. Po odčítaní polohy hráča a použití smerových komponentov `4C46/4C48` zapisuje projektované konce do `+0x14..+0x1A`. Orezáva blízku rovinu na `0x4000` a horizontálny rozsah na `53E4..53E6`.
- `FUN_1018_3940` prechádza štyri orientačne zoradené vektorové zoznamy. `FUN_1018_3564` odmietne vektor bez eligibility bitu 0 na `+0x05`, premietne/oreže ho a priraďuje far pointer vlastníka do 4-bajtovej položky na stĺpec v bufferi `53FE`. Pri obsadenom stĺpci porovnáva orientáciu `+0x07`, endpointy a smer hrany; kandidát môže nahradiť doterajšieho vlastníka. `53FC` sleduje počet ešte nepriradených stĺpcov.
- `FUN_1010_6266` zlúči susedné stĺpce s rovnakým vlastníkom do najviac 50 záznamov po 20 bajtov v `5E88`; počet je v `5E7E`. `FUN_1010_6152` dopočíta sklon a vertikálne hodnoty na hranách spanu.

| Span offset | Priamo podporovaný význam |
|---:|---|
| `+00/+02` | far pointer na vector záznam |
| `+04/+08` | prvý a posledný X stĺpec |
| `+06/+0A` | interpolované Y na oboch koncoch |
| `+0C` | 16.16 sklon `dY/dX` |
| `+10` | počiatočná zlomková časť interpolácie |
| `+12` | vertikálna základňa voči stredu projekcie |

Tým sú projekcia, clipping, stĺpcový owner buffer a span layout dobre zmapované pre Win16. Otvorený je finálny texel-write cyklus, všetky párové pravidlá prekrytia, transparent/masked steny a dvere, fixed-point hraničné zaokrúhľovanie, sprite sorting/occlusion a porovnanie DOS VGA proti WinG. Starší generický 320-column DDA smoke test sa preto nesmie považovať za dôkaz vernosti originálnemu wall rendereru.

### Klávesy a farebné stmavenie

Win16 klávesový dispatcher `FUN_1010_8cd2` mapuje ľavý/pravý Shift na bity `0x40/0x20`, Ctrl na `0x80`, Escape na `0x01`, šípky na `0x08/0x02/0x10/0x04`, Space na `DAT_1048_3757` bit `0x02` a Alt na druhý stavový byte bit `0x01`. `Q` prepína hudbu, `R` zvukové efekty a Alt+Enter prepína fullscreen/okno cez režimy 3/4. Alt+S odošle vlastnú správu; jej význam nebol potvrdený. Zmapovanie bitov ešte neznamená, že všetci ich konzumenti v simulácii sú uzavretí.

`DAT_1048_7E60` je farebná úroveň stmavenia. `FUN_1010_29be` používa úrovne `{0,4,8,12,16,20,30,40}`, pre každú z 236 farieb zníži RGB kanály o štvornásobok úrovne (s nulovým spodným limitom) a vyberie najbližšiu základnú farbu podľa súčtu absolútnych rozdielov. Výsledky zapisuje do remap tabuľky pre indexy 10–245. `FUN_1010_c5e2` použije nezáporný `4698`, inak nastaví úroveň 2; pri story/event príznaku `51AB` použije úroveň 6. Rozsah a všetky render vetvy, ktoré remap obchádzajú, zostávajú na kontrolu.

### SEQDEF dispatcher a exploding-wall cleanup

Win16 `FUN_1010_65a6` a DOS `FUN_1000_241e` majú rovnaký základ animačného dispatchu: porovnajú 32-bitový deadline objektu `+0x08` s globálnym časom, pri splatnosti zvýšia frame `+0x03` a naplánujú ďalší termín ako `global_time + seqdef.interval` (`seqdef+2`). SEQDEF frame count je na `+0`; optional pointer `+4` vyberá alternatívne vetvy. Pre triedu `object+6 >= 0x30` používa dispatcher osem 16-bitových položiek; dolný bajt určuje počiatočný frame, horný dĺžku vetvy a `object+2` drží vybraný slot. Po dohraní vyberá náhodný slot s nenulovou dĺžkou. Triedy `0x2F`, `0x07` a `0x2D` majú zvláštne dokončenie.

Vo Win16 projektilová kolízia s wall property bit `0x10` prehrá SFX `0x29` a nastaví runtime objekt do triedy `0x2D`. Po dokončení sekvencie `FUN_1018_3c0c` odstráni bit 0 eligibility a nuluje prvé bajty buniek pozdĺž odvodenej horizontálnej alebo vertikálnej stopy; potom podrží frame na poslednom indexe. To podporuje záver, že cleanup mení aj mapový blocking stav, nielen kreslenie. Presná stopa/ukončenie vnútorného hľadania potrebuje raw assembler alebo runtime kontrolu. DOS má analogickú `0x2D` vetvu, ale jej call target zatiaľ nie je bezpečne priradený, preto DOS cleanup parity zostáva otvorená.

Funkčný inventár obsahuje 519 DOS a 967 Win16 definícií; 1 358 z 1 486 (91,4 %) je spárovaných identitou alebo silnou podobnosťou. Toto je miera mapovania kódu medzi buildmi, nie percento pochopenia herných funkcií.

### Nové rozloženie projektilového slotu

Win16 allocator `3:9AAC–9B63` prechádza osem slotov po `0x2A = 42` bajtov a začína slot na `0x4C4A + index*0x2A`. Zápisy a update rutina `3:9D30–9E1E` dávajú tento potvrdený model:

| Offset slotu | Veľkosť | Potvrdená funkcia |
|---:|---:|---|
| `+00` | 2 B | prepínač hlavnej osi DDA; podľa neho sa prírastok aplikuje na X alebo Y |
| `+02` | 2 B | DDA chyba/akumulátor |
| `+04` | 2 B | jeden z korekčných prírastkov |
| `+06` | 2 B | druhý korekčný prírastok |
| `+08` | 2 B | hlavný krok X alebo Y podľa `+00` |
| `+0A` | 2 B | hlavný krok druhej osi |
| `+0C` | 1 B | lifecycle: `0` voľný, `1` let, `2` dopadová animácia |
| `+0D` | 1 B | v analyzovaných blokoch bez potvrdeného čitateľa/zapisovateľa; zostáva otvorený |
| `+0E..+29` | 28 B | vložený OBJECT/render záznam |

Pri zásahu do steny sa `+0C` nastaví na `2` a frame `+11` sa resetuje. Dopadová sekvencia postupuje podľa počtu frame-ov v SEQDEF; po dosiahnutí tohto počtu sa status vráti na `0`. Číslo `20` je strop výškovej hodnoty outer-slot `+28`, nie limit frame indexu. Zásah guard-a používa `abs(dx) < 10` a `abs(dy) < 10`, potom volá spoločnú damage rutinu `3:80F8`. Pohybový/lifecycle model je tým z veľkej časti uzavretý a vybrané DOS/Win16 cesty sú spárované; zostávajú header `+0D`, owner, presná DDA škála a mapovanie uhla podľa weapon selectora. Damage cesta bola doplnená nižšie.

Inicializátor `3:E516–E5D6` prijíma uhol v jednotkách `0..0x167` (360 jednotiek; záporná hodnota sa normalizuje pripočítaním `0x168`). Z uhla vytvorí dva signed fixed-point smerové komponenty `4C46` a `4C48`, zvolí hlavnú os podľa absolútnej veľkosti a vypočíta DDA chybu/prírastky do `4C06`, `4C08`, `4C0A`, `4C0C`. Allocator `3:9AAC` tieto hodnoty kopíruje do projektilového slotu. Takže „rýchlosť“ nie je jedno neznáme pole: je to kombinácia uhlových komponentov a DDA kroku. Ešte treba zmerať škálu komponentov, zdroj uhla pre každý typ zbrane a prípadný rozdiel medzi hitscan a projectile vetvou.

### Nové uzavretie: damage nie je vzdialenosť projektilu

Rutina `3:9FA2` teraz umožňuje presne oddeliť tri veci, ktoré sa predtým miešali:

1. **Základný seed poškodenia** číta `OBJECT+0x18`, odčíta `DAT_53EE`, posunie výsledok doľava o 3 a pripočíta zvyšok RNG po delení `25`. Staticky teda platí:

   `seed = 8 * signed16(OBJECT+0x18 − DAT_53EE) + R`, kde `R ∈ {0,…,24}`.

2. **`OBJECT+0x18` nie je world-range projektilu.** Projekčná rutina `3:CD80–CE5E` doň zapisuje `[bp−6]`, teda vybraný/orezaný vertikálny riadok renderu. Kamera pri `3:5207–5254` ukladá `DAT_53EE` ako strednú vertikálnu súradnicu viewportu. Damage seed je preto podpísaná obrazovková odchýlka cieľa od stredu zamerania, nie vzdialenosť hráč–cieľ. Ak cieľ nebol v aktuálnom render priechode prepísaný, hodnota `+18` môže byť stará; samotná `9FA2` čerstvosť stampu netestuje.

3. **Trieda cieľa a zbraň seed ďalej preškálujú.** Jump table `3:9FE8` pokrýva `OBJECT+6 = 12..31`:

| Trieda `OBJECT+6` | Transformácia `seed` pred obtiažnosťou |
|---:|---|
| 12, 29 | `sar 3` |
| 13 | zbraň 1/2: `sar 1`; inak `sar 3` |
| 14, 17, 20 | zbraň 2: `sar 1`; inak `sar 3` |
| 15, 16 | zbraň 1: `0`; inak `sar 1` |
| 18, 19 | zbraň 1: `0`; inak `sar 2` |
| 21 | volá neidentifikovaný helper s `DS:0192`, potom nastaví `0` |
| 22 | výsledok `3`, iba ak `DS:7E52 == 3`, inak `0` |
| 23 | zbraň 1: `sar 8`; inak `sar 2` |
| 24 | zbraň 1: `sar 8`, zbraň 2: `sar 4`, inak `sar 3` |
| 25 | `0` |
| 26 | zbraň 1: `sar 1`; inak `0` |
| 27, 28 | `sar 1` |
| 30 | zbraň 1: `0`; inak `sar 3` |
| 31 | zbraň 1: `0`; inak `sar 2` |

Potom globál `4C14` vykoná difficulty transformáciu: hodnota `2` delí 2, hodnota `0` násobí 2 a ostatné hodnoty ju nemenia. Na konci je potvrdený horný clamp na `0xFF`; dolný clamp sa v `9FA2` nenachádza. Skutočná interpretácia záporného medzivýsledku je preto stále runtime otázka (caller používa nízky byte pri odčítaní HP). Základná damage formula je staticky známa, ale presné priradenie tried `12..31` ku konkrétnym nepriateľom a význam špeciálnej triedy `21` ešte nie.

### DOS parity damage/score je už potvrdená

Rovnakú logiku obsahuje aj DOS image, takže „DOS ekvivalent damage“ už nie je otvorená diera:

| Win16 | DOS image | Potvrdená zhoda |
|---|---:|---|
| `3:9F10` score helper | `0x84FE` | rovnaký class dispatch `OBJECT+6−8`, rovnaké score konštanty |
| `3:9FA2` damage | `0x8590` | `OBJECT+18 − center`, `<<3`, RNG remainder `/25`, class table 12..31, clamp `0xFF` |
| `DAT_53EE` viewport center | `DAT_4552` | DOS centrum sa zapisuje v `0x3371–337B` |
| `4C23` weapon selector | `DAT_418F` | rovnaké weapon shift vetvy |
| `4C14` difficulty | `DAT_4180` | rovnaké `2 → /2`, `0 → ×2` |

DOS damage helper volá rovnaký RNG wrapper v segmente `0x0FBA` (cieľ `0x01A0`). To je silná parity väzba medzi buildmi; stále však nepreukazuje, že DOS projectile allocator, 42-bajtový slot a všetky cadence vetvy sú byte-for-byte identické.

### Damage, score a metadata sú tri rôzne kanály

`3:80F8` je spoločný damage dispatcher pre hitscan aj projectile collision. `3:9FA2` vracia damage; pri lethal zásahu sa HP nastaví na nulu, pri neletalnom sa odčíta nízky byte damage. Následne sa volá hit animácia, pri projectile mode aj `3:B6A0` (sekundárny/knockback efekt), a zvuk `3:A3B6(4)`.

Odmena nie je `9FA2`: helper `3:9F10` používa samostatnú tabuľku podľa `OBJECT+6` a jeho návrat sa v `3:819B–81A8` pripočítava do skóre `4C16:4C18`. Potvrdené konštantné skupiny sú:

| Trieda | Score |
|---|---:|
| 9 | 75 |
| 10, 25, 32 | 50 |
| 11, 15, 16, 23, 27, 28 | 100 |
| 12, 21, 29, 30 | −1000 |
| 13, 18, 19 | 150 |
| 14, 20, 24, 31 | 200 |
| 17 | 250 |
| 22 | 1000 |
| 26 | 0 |
| 8 | volá neidentifikovaný helper; návrat nie je staticky redukovateľný |

Na konci `80F8` sa číta `+0D` **prvého argumentu**, ktorý call-site analýza identifikuje ako GUARD record, nie ako projektilový slot ani vložený OBJECT; byte sa kopíruje do linked OBJECT `+1`. To je potvrdená metadata väzba, nie dôkaz vlastníctva projektilu.

### Čo z toho vyplýva pre owner/friendly fire

V projectile collision vetve `3:9B64–9D17` sa najprv rozlíši mapa, potom `3:8308` vráti GUARD record a jeho OBJECT. Pri kolízii sa do `80F8` posiela práve tento GUARD/OBJECT pár; v kóde nie je potvrdený ďalší source/owner pointer, porovnanie owner ID ani čítanie projektilového headera `+0D`. Najopatrnejší záver je: **owner/friendly-fire pravidlo nie je v potvrdenej collision ceste staticky reprezentované**. Môže byť implicitné v globálnom weapon stave alebo v nepriamom helperi, ale bez runtime nemožno tvrdiť, či je friendly fire nemožný, povolený alebo filtrovaný inde.

### OBJECT `+4` pri spawnovanom projektili

`3:A930` vracia byte z malej tabuľky indexovanej `4C23` a pripočítava `DAT_8397`; `9AAC` ho ukladá do vloženého OBJECT `+4`. Pre lokálne indexy 0..3 sú bázy `{0, 2, 0, 0}`. `DAT_8397` sa nastavuje v `3:507C` z aktuálneho class/render kontextu. Je teda potvrdená weapon-dependent OBJECT hodnota, ale jej presný význam (sprite/sequence trieda, nie „owner“ ani damage) zostáva otvorený.

### Čiastočne uzavretý weapon selector, ammo a cadence

Prechodová rutina `3:A362–A375` poskytuje pevnú väzbu selector → shot mode: čakajúci selector `4C24` sa skopíruje do `4C23`; **iba selector `2` nastaví `4C26=1` (hitscan)**, zatiaľ čo všetky ostatné hodnoty nastavia `4C26=2` (projektilová vetva). To je statický fakt, nie ešte identifikácia názvov zbraní.

Obe vetvy majú ammo gate, iba na inom mieste:

| Vetva | Kde sa volá `A97C` | Potvrdený resource counter | SFX pri úspešnom odpočte |
|---|---|---|---:|
| hitscan (`4C26=1`) | dispatcher `3:8B36` pred GUARD scanom | selector 0 → `4C20`; 1 → `4C44`; 2 → `4C1F` | 8 / 9 / 7 |
| projectile (`4C26=2`) | allocator `3:9ACC` pred zápisom slotu | rovnaké mapovanie | 8 / 9 / 7 |

`A97C` pri `DAT_4BE5 != 0` vracia úspech bez odpočtu (override/debug-like cesta). Pri bežnom stave selector 0/1/2 vracia predchádzajúcu nenulovú hodnotu countera a zníži ju o 1; selector 3 nemá bežnú ammo vetvu a prepadá do neúspechu. Preto `4C23=3` môže byť rezervovaný alebo vyžaduje override — jeho herný význam zostáva otvorený.

Úspešný výstrel nastaví na `3:8C00` latch `4C30=1`. Pomocná rutina `3:A2CE–A3B4` potom pracuje s fázovým stavom `4C3A` a číta globálny limit `DS:01F2`: vo fáze 2 dekrementuje `4C3C` do nuly, prepne na fázu 1 a nainštaluje `4C23=4C24` s príslušným mode; vo fáze 1 inkrementuje `4C3C` až po `01F2`, prepne na fázu 0 a vyšle SFX `0x0C`. Vo fáze 0 latch `4C30` pridáva do lokálneho timingového poľa `+6` pre hitscan alebo `+3` pre projektil a latch vynuluje. Toto uzatvára mechanickú cadence/transition cestu, ale jednotka `01F2`, presný caller timing a finálne používateľské cooldown pravidlo ešte nie sú dokázané.

## Čo stále nie je dôkladne uzavreté

| Priorita | Oblasť | Konkrétna zostávajúca neznalosť | Čo treba urobiť |
|---|---|---|---|
| P0 | GUARD AI | Konzumenti percepcie v celej state machine, mená smerových tried/mapových bitov a hearing propagation mimo lokálnej latch tabuľky | Základný FOV/LOS kód je bajtovo spárovaný medzi DOS a Win16; doplniť všetky priame/nepriame state callery, map-bit writerov a šírenie alarmu medzi oblasťami. |
| P0 | GUARD state machine | Mená stratégií, chýbajúce explicitné `0A/0B`, úplní writeri `+0B/+0C`, DOS state parity a boss/episode callery | Win16 vetvy `00–15` sú zmapované na priame operácie; DOS control flow okolo `5F74` je zlúčené. Dokončiť raw DOS hranice, writers a runtime prechody/alarmy. |
| P0 | Zbrane | Mená selectorov, zdroj uhla pre každý typ a runtime časová jednotka/cadence limitu `01F2` | Ammo gate, counter mapping, selector→shot mode a fázy cadence sú staticky známe; sledovať caller timing a mapovanie selectorov na herné zbrane, potom overiť runtime cadence. |
| P0 | Projektily | `+0D`, owner/friendly fire, presná sémantika OBJECT `+4`, číselná škála DDA a uhol pre každý weapon selector | Vybrané DOS/Win16 spawn, pohyb, dopad a trig tabuľky sú spárované; uzavrieť zvyšnú reader/writer maticu 42 B slotu, dohľadať angle source a runtime owner pravidlá. Damage/score parity je potvrdená. |
| P0 | Steny a animácie | Obsah konkrétnych SEQDEF tabuliek, časová jednotka, asset/SFX väzby a úplná DOS cleanup parity triedy `0x2D` | Dispatcher a Win16 exploding-wall cleanup sú zmapované; potvrdiť raw DOS cieľ, mapovú stopu a intervaly s runtime alebo mapovými dátami. |
| P0 | Level scripts | Univerzálne významy `51A6–51AB`, TRIGGER1/2, reset pri LOAD, E3 finále a boss podmienky | Vyťažiť všetkých writerov a callerov, potom spätne označiť každé použitie v mapách. |
| P0 | Runtime čas | Presný vzťah `53DC`, millisekúnd, cadence a DEMO času; pause/menu/load rebase | Nájsť update loop a porovnať viac po sebe idúcich tickov v DOS/Win. |
| P1 | OBJECT | Zvyšné polia 28 B podľa triedy, životnosť +18 projekčnej cache, všetky nepriame dispatchy | Reader/writer tabuľka po offsetoch a class ID. |
| P1 | Renderer | Finálny texel-write cyklus, všetky overlap dvojice, transparent/masked steny a dvere, sprite occlusion/clipping, fixed-point hraničné prípady a VGA/WinG parita | Vector projekcia, owner buffer, clipping a span layout sú staticky zmapované pre Win16; treba doplniť raw pixel loop a obrazové porovnania z oboch buildov. |
| P1 | Hazards | Presný damage, interval, vrstvenie s guard/player hitom a dverami | Prejsť hazard dispatch a SFX/damage call chain; následne hraničné runtime testy. |
| P1 | GUARD25/26 a bossovia | Či ide o orphan asset, Dancers, transformáciu alebo epizódový scripted actor; všetky podmienky Hammerstein/Penelope | Prepojiť OBJECTS/WALLS/SEQDEF s mapovým použitím a finálnym scriptom. |
| P1 | Save/load | Zvyšné polia hráčskeho 0x5E bloku, všetky `51A6–51AB`, rebasing všetkých timerov a pointerov | Reader/writer mapa + load/save round-trip v DOSBox/Win16. |
| P1 | DEMO | Bitová mapa vstupu, jednotka času, level selection DEMO.2/.3, RNG consumption a EOF | Dekódovať súbory a pustiť rovnaký záznam v oboch buildoch. |
| P1 | Debug/CMD | Kompletný zoznam podporovaných parametrov, `-p/-w/-e/-s`, všetci writ eri logger flagu | Staticky dohľadať všetkých writerov; potom overiť `-o` v kompatibilnom OS. |
| P2 | SND.DAT/IMG/UIF | Chunk/VOC detaily, event→SND ID, IMG metadata, UIF sloty 0–31 | Parser + mapovanie všetkých runtime readerov. |
| P2 | ENDING.FLI | 488 vs 489 blokov, padding a presné koncové pravidlo | Frame indexer a prehrávač s binárnym porovnaním. |
| P2 | DOS hranice | Poškodené alebo nepresne rozdelené bloky `0x0AEA`, `0x4A86`, `2000:9364` | Ručné rozdelenie funkcií cez call/return a porovnanie s Win16 ekvivalentom. |
| P2 | Verzie | Rozdiely shareware/full, build fingerprint a platformové odchýlky | Hashovať všetky dostupné buildy a viesť per-build evidence. |

## Tabuľka po pôvodných 12 oblastiach

| # | Stav detailného pochopenia | Hlavná otvorená diera |
|---:|---|---|
| 1 AI | vysoký pre FOV/LOS a Win16 state dispatcher | mená stratégií, DOS state parity, hearing mimo area, boss/episode vetvy |
| 2 renderer | vysoký pre Win16 vector/span a clipping model | texel emitter, transparency/dvere, sprite occlusion a DOS/WinG pixel parity |
| 3 projektily | vysoký pre statické jadro | header `+0D`, owner/friendly-fire, úplná sémantika OBJECT `+4`, DDA škála a všetky zdroje uhlov |
| 4 OBJECT | stredný | všetky offsety a triedy |
| 5 SEQDEF | vysoký pre dispatcher jadro a Win16 class `0x2D` cleanup | skutočné SEQDEF dáta, timebase, event/SFX väzby a DOS cleanup parity |
| 6 zbrane | stredný až vysoký | presné názvy selectorov, zdroj uhla, `01F2` timing a runtime cadence; ammo a mode mapping sú známe |
| 7 steny | stredný | completion a DOS parity |
| 8 USE | vysoký | zvyšné special handlery a varianty |
| 9 USER.SAV | vysoký na blokovej úrovni | hráčsky blok, flags, rebasing hrany |
| 10 DEMO | stredný | vstupné bity, časová jednotka, mapy |
| 11 debug/CMD | flag a logger potvrdené | úplný parser a aktivácia všetkých ciest |
| 12 resources | stredný | UIF/IMG/SND/FLI payload a parity |

## Dôležité hranice tvrdení

Statická kontrola nebola runtime spustenie originálu. Nevieme preto tvrdiť, že `-o` vytvorí súbor v každej platformovej konfigurácii, že area wake zasiahne každého guard-a, ani že DEMO bude bez ďalších podmienok deterministické. Neznámy kód sa nemá zamieňať s neexistujúcou funkciou: nulový priamy XREF môže byť callback alebo nepriamy dispatch.

Hlavný verifier prešiel 65 kontrolami vrátane 446 NE relocation records, 6 082 rozbalených relocation sites a 66 540 testovaných RNG stavov; zahŕňa Win/DOS damage-score parity, projekčný `OBJECT+18`, GUARD metadata, OBJECT `+4`, ammo gate a weapon cadence. Samostatný projectile verifier prešiel 40 kontrolami a guard FOV/LOS verifier ďalšími 40. Všetky sú statické kontroly presne hashovaných EXE; originál hry nebol spustený. Výstupy a adresovaná disassembláž sú v evidence balíku.