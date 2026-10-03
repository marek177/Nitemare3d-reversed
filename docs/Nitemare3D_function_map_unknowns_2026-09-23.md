# Nitemare 3D — mapa známych a otvorených funkcií

Stav k 2026-09-23. Zhrnutie vychádza z existujúceho auditu Win16 `NITE3W` a DOS `N3D`, z Ghidra C exportov a z kontroly dodaných herných dát. „Potvrdené“ znamená oporu v konkrétnych vetvách, čítaniach/zápisoch, limitoch alebo surových bajtoch; pomenovania bez takej opory sú označené ako čiastočné alebo otvorené.

## Odpoveď na otázku

**Nie, všetky funkcie celej hry ešte nepoznáme.** Máme počty rozpoznaných funkcií a rozsiahlu mapu subsystémov, ale nie každá funkcia má spoľahlivý názov, prototyp a vysvetlené všetky vedľajšie účinky. Niektoré dekompilované hranice sú nesprávne a niektoré závery sa líšia medzi DOS a Win16 verziami.

Ghidra exporty obsahujú 519 rozpoznaných funkcií pre DOS v2.0 a 967 pre Win16 v1.10, spolu 1 486 deklarácií `FUN_*`. Sú to počty rozpoznané v konkrétnych exportoch, nie zaručený počet pôvodných zdrojových funkcií. Audit priradil všetky 1 486 položky k pravdepodobnej oblasti; prvých 200 DOS a 200 Win16 funkcií bolo rozobratých podrobnejšie, zvyšných 1 086 je prevažne klasifikovaných podľa volaní, konštánt, globálov a API. To nie je to isté ako úplné funkčné vysvetlenie každej položky.

| Build | Rozpoznané deklarácie `FUN_*` |
|---|---:|
| DOS E-10 / E-17 / E-18 / E-20 | 493 / 514 / 526 / 519 |
| Win16 1.3 / 1.6 / 1.8 / 1.10 | 959 / 965 / 965 / 967 |

Celkové percento reverznej analýzy sa nedá poctivo vypočítať z týchto počtov. Percentá nižšie sú pracovné odhady pokrytia jednotlivých podsystémov, nie percento dekódovaných funkcií celej hry.

## Čo je dobre zmapované

| Subsystém | Potvrdené zistenia | Stav |
|---|---|---|
| MAP a levely | Hlavička, tabuľky wall/object tried a formát buniek sú dekódované; skontrolovaných je všetkých 31 blokov levelov. E1M11 zdieľa geometriu s E1M3, ale má 17 zmien objektov. E2M4 obsahuje jeden výskyt wall ID `0x37` bez definície vo `WALLS.2`. | Vysoké štrukturálne pokrytie; význam jednotlivých skriptov a anomálie ostávajú oddelené otázky. |
| Runtime limity a záznamy | Limity dverí 64, panelov 32, push objektov 12, objektov 350, guardov 100, renderovaných segmentov 50, VEC 1000 a VECLIST 333 sú potvrdené. Object runtime záznam má 28 B, guard 26 B, door/panel 22 B. | Limity a stride potvrdené; viaceré polia ešte nemajú presný význam. |
| Wall flags a USE | Odvodená wall-property tabuľka a centrálna USE vetva sú z veľkej časti vysvetlené. Známe sú farebné kľúče, ID karty, pickup vetvy, základné dvere a väčšina WARP rodín. | Pracovný odhad: wall flags 95 %, USE 94 %, WARP_L 95 %, WARP_S 95 %, WARP_1..8 85 %, WARP_E 90 %. |
| Remote dvere a triggery | Remote menu ide cez wall/object class `03`, kontrolu ID karty a príkazy `0x1E/0x1F` pre otvorenie/zatvorenie skupiny DOORVR/DOORHR. Pohybové TRIGGER1/2 sú samostatná epizódová vetva; univerzálne prepojenie trigger → CONTROL → remote doors sa nepotvrdilo. | Základná cesta potvrdená; niektoré triedy, skupiny, parametre a správanie v hre treba ešte spárovať. |
| WARP a špeciálne steny | WARP_L sú farebné key-gate triedy; WARP_S1→S2 je jednosmerný portal po získaní štyroch pentagramov. WARP_1..8 a WARP_E1..8 používajú generické výberové dispatchery. | Väčšina hlavnej logiky známa; presná orientácia po presune a niektoré UI voľby nie. |
| Guard/combat | Guard record má 26 B; známe sú state bajty, timer, väzba na world object a HP/strength. Dispatcher má stavy `0x00–0x15`. Class-specific score, damage vetvy a difficulty scaling sú čiastočne až numericky dekódované. | Základné prechody a vzorce známe; nie všetky stavy, stratégie a herné podmienky. |
| NITE3D.BSF | Súbor je XOR-kódovaný kontajner textových blokov/príručky, nie symboly ani zdrojový kód. Dešifrovanie a základné bloky sú zmapované. | Pre formát súboru vysoké pokrytie; BSF nepomôže odhaliť ďalšie kódové funkcie hry. |

## Hlavné neznáme podľa priority

### P0 — herné správanie, ktoré ešte bráni vernej reprodukcii

1. **GUARD AI a percepcia:** presný význam všetkých stavov `0x02–0x14`, tabuľka strategy hodnôt, sight/FOV/range, line-of-sight, reakcia na výstrel a osobitné správanie GUARD25/GUARD26. Číselné stavy sú viditeľné, ale ich názvy a prechody ešte nie sú všade potvrdené.
2. **Čas a animácie:** intervaly v sekvenčných definíciách, reálna jednotka času a vzťah k frame rate. Počet obrázkov v IMG neurčuje delay. Chýba potvrdenie loop, ping-pong a one-shot správania viacerých stien.
3. **Projectile, zbrane a hazardy:** presná rýchlosť, lifetime, hitbox/radius, zásahová kontrola, range/spread a damage jednotlivých projektilov; presný damage/tick interval ohňa.
4. **Špeciálne wall/object triedy:** správanie a trigger pre `ONE_SHOT`, `SPECIAL1` a zostávajúce wall/object classy `03–06`, `26–29`; úplné prepojenie class ID na grafické ID a mapové použitie.
5. **Kolízie:** presné okraje hráčskeho radiusu/sliding, guard-door interakcia, blokovanie pri zatváraní a zvláštne prípady teleportu/push objektov.

### P1 — runtime dáta a presná zhoda s originálom

| Oblasť | Otvorená otázka |
|---|---|
| Save hry | Význam blokov 336 B pri `0xC403`, 32 B pri `0xC3E3`, 8 B pri `0xC553`, 4096 B pri `0xC5A3`, 64 B pri `0xD5A3` a 256 B pri `0xD5E3`; tiež ktoré časovače sa pri load rebazujú. |
| Renderer | Kompletné polia 28 B VEC záznamu, vlastníctvo/životnosť štyroch 333-prvkových VECLIST skupín a 20 B visible-span záznamu; sprite sorting/occlusion, presný FOV, shade/angle tabuľky a čiastočne otvorené dvere. Existujúca C++ rekonštrukcia overuje architektúru, nie pixel-perfect zhodu. |
| Assety | SND.DAT má 160 slotov a 88 nenulových položiek, ale úplný sample/codec/rate model a prečo niektoré exporty znejú zle nie sú uzavreté. UIF sloty 0–2 nemajú potvrdený formát/účel; sloty 17–31 sú v dodanej verzii prázdne. ENDING.FLI hlási 488 frames, fyzicky obsahuje 489 blokov vrátane najmenej šiestich prázdnych koncových blokov. |
| DEMO | 6-bajtová hlavička a 8-bajtové záznamy sú zmerané; presné mapovanie hodnôt na ovládanie, level selection a dĺžka ticku nie sú potvrdené. Z dát samotných sa nedá určiť level DEMO.2/3. |
| Levelové udalosti | Finálny reťazec E3M10 (trigger → Penelope/Hammerstein → smrť bossa → FLI → score/menu) nie je celý zmapovaný. Niektoré eventy sú podmienené konkrétnym levelom a wall class. |
| Input a platformy | Presný joystick/gamepad scaling a dead-zone, kalibrácia, spoločná definícia game ticku a rozdiely DOS VGA vs Win16/WinG. |

## Nová oprava: údajný Windows command-line parser

Predchádzajúca poznámka označila `NITE3W 1000:5D24` a `1000:5E94` za parser prepínačov príkazového riadka. Kontrola ich tiel v `nite3w110.exe.c` tomu odporuje:

- `FUN_1000_5d24` nastavuje veľkosť message queue, získava systémové metriky/proc address, pripravuje callback a volá `SETWINDOWSHOOK` alebo `SETWINDOWSHOOKEX`; v osobitnej vetve registruje Windows triedy. Je to Windows hook/window setup, nie dôkaz tokenizácie command line.
- `FUN_1000_5e94` číta cestu modulu, odvodzuje názvy/cesty súborov a pripravuje resource/string údaje do runtime štruktúry. Ani jej viditeľné telo neparsuje command-line tokeny.
- V tomto C exporte sa nenašla identifikácia `GetCommandLine`/`COMMANDLINE`. To samo osebe nedokazuje, že parser neexistuje; jeho skutočný vstupný bod ostáva neidentifikovaný.

Preto sa `1000:5D24/5E94` nesmie ďalej uvádzať ako potvrdený parser ani ako dôkaz debug prepínača. Najprv treba nájsť vstupnú WinMain/štartovaciu vetvu, zistiť dostupné parametre a porovnať ich s raw NE assemblerom. Podobne aj klasifikácia funkcie `1000:04BE` pre explodujúcu stenu bola v staršom výstupe opravená: surové DOS bajty ukazujú rozpor medzi Ghidra hranicou a adresou callu; odstránenie steny/kolízie zatiaľ nie je potvrdené.

## Ďalší pracovný postup

1. **Udržať inventár po binárkach:** každá funkcia má mať build, segment:offset, potvrdenú hranicu, callees/callers, read/write globály a úroveň istoty. Nepovažovať názov generovaný z heuristiky za dôkaz.
2. **Dokončiť časovač a sequence dispatcher:** získať raw kód a dynamicky logovať global time, `object+0x08`, seqdef interval, frame a wall/object class. Tým sa naraz uzavrú animácie, dvere a časť AI.
3. **Zmapovať GUARD podľa writer/reader reťazcov:** pri každom stave sledovať kto ho zapisuje, aký handler ho číta, timer, pohyb, zvuk a útok; potom kontrolovane overiť v hre.
4. **Rozlúštiť save bloky párovaním read/write XREF:** zapisovanie pri save a načítanie po load treba spojiť po bajtoch; samotná dĺžka bloku nestačí.
5. **Overiť renderer proti snímkam originálu:** po stabilizovaní FOV, fixed-point zaokrúhľovania, angle/shade tabuliek a partial-door geometry porovnať tie isté pozície/kamery pixel po pixeli.
6. **Uzavrieť audio, UI a DEMO cez loader callsites:** najprv určiť interpretáciu adresára v EXE, až potom pomenovať payloady a správanie.

Najvyššiu hodnotu má teraz spojenie **tick/sequence logiky + GUARD state machine + dynamických testov**. Statická dekompilácia sama nestačí na potvrdenie detailov, kde sa hranice funkcií alebo far-call prototypy rozchádzajú.