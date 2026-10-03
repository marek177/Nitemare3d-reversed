# Nitemare 3D — hlboký audit videí a mapa neznámych

**Dátum:** 23. september 2026  
**Rozsah:** videá súvisiace s Nitemare 3D v knižnici, ich technické metadáta a SHA-256, obrazové vzorky, predchádzajúce časované videoaudity a dostupná statická analýza DOS/Win16 hry a dát.

## Zhrnutie pre rozhodovanie

V knižnici je **181 videí**, ktoré patria do rozsahu Nitemare 3D; ďalších šesť videosúborov v knižnici nesúvisí s hrou a je uvedených v prílohe. Prenos súborov sprístupnil **169 z 181** videí. Dvanásť prenosov zlyhalo s HTTP 502 alebo timeoutom; ich názvy, očakávané veľkosti a stav sú v inventári, ale ich obsah nebol analyzovaný. Očakávaný objem všetkých 181 videosúborov je 14 831 698 698 B; dostupných 169 tvorí 9 786 757 455 B a nedostupných 12 spolu 5 044 941 243 B. Pri všetkých dostupných súboroch sa veľkosť zhodovala s metadátami knižnice.

Dostupné súbory tvoria **146 rôznych obsahov** podľa SHA-256: 144 MP4 a dve varianty FLI. V knižnici sú 23 presných duplicitných kópií navyše rozložených do 20 skupín. Z toho 35 knižničných položiek sa plným SHA-256 zhoduje s predtým auditovanými videami; ide o 25 unikátnych obsahov, takže už existujúce manuálne audity sa započítali bez opakovania ich práce. Jedinečné dostupné MP4 predstavujú spolu **17 h 11 min 15 s**. Kľúčový herný výsledok je, že úroveň sa opakovane dá dokončiť aj s nepriateľmi a tajnými panelmi, ktoré zostali nesplnené. Koniec mapy teda nemožno v rekonštrukcii podmieniť vyčistením mapy. Výsledková obrazovka a bonus sa musia počítať samostatne od podmienky odchodu.

Videá a statický kód spolu vysvetľujú veľkú časť hernej logiky:

- Farebné kľúče sa správajú ako trvalé oprávnenia v inventári, nie ako jednorazové predmety; zelený kľúč sa vo walkthrough E3M8 použije na viacerých dverách. Kľúče a ID karty sú však rozdielne systémy.
- Schody, výťahy, kľúčové warpy, transportačné komory a špeciálne zakončenia majú odlišné pravidlá a rozhrania. Jedna univerzálna funkcia na všetky warpy by zahodila pozorované rozdiely.
- Niektoré stráže používajú smerový test a Bresenhamovu kontrolu viditeľnosti. Úspešný výstrel prebudí stráže s rovnakým nenulovým ID oblasti bez testu vzdialenosti a viditeľnosti v samotnej wake slučke. Je to dôkaz lokálneho budenia podľa oblasti, nie dôkaz globálneho sluchu.
- Win16 EXE mapuje hitscan, osem-slotový projektilový zásobník, poškodenie, skóre, nebezpečenstvo ohňa, dvere, secret panely, push objekty aj skriptované finále. Opravený výklad vzorca poškodenia používa projekčnú súradnicu na obrazovke, nie vzdialenosť v hernom svete.
- Dve finále používajú skriptované cesty: E2M10 ničí plazmové jadro bez bežnej LEVEL_UP dlaždice; E3M10 používa trigger, súboj s Hamersteinom, víťaznú hlášku a ENDING.FLI.
- Jeden záznam obrazovky aplikácie vo Win16 ukazuje titulok Demo Mode a opakujúcu sa podobnú hernú trasu. Obrazová podobnosť ukazuje približne 252-sekundový posun medzi opakovanými snímkami; samotný zdrojový kód nepotvrdzuje tento wall-clock interval.

## Čo bolo skutočne skontrolované

### Rozsah videí

Zoznam obsahoval 187 video alebo FLI položiek. Do auditu hry som zaradil 181 záznamov s Nitemare 3D obsahom; „Raycast_Render_Comparison_v3_Exact_GAMEPAL.mp4“ je zahrnutý, pretože zobrazuje renderovaciu rekonštrukciu hry. Šesť nesúvisiacich súborov je vylúčených.

Z dostupných 169 súborov sa vypočítali plné SHA-256 a ffprobe metadáta; kontrolované boli kodeky, trvanie, rozmery, počet snímok, snímková frekvencia a zvukové streamy. Všetkých **40 priamych klipov pomenovaných podľa levelu** pokrýva 30 rôznych máp E1M1 až E3M10. Ide o skutočné obrazové pokrytie každej mapy, ale nie každý krátky klip ukazuje celý walkthrough alebo obrazovku dokončenia.

Z každého unikátneho priameho levelového klipu vznikli reprezentatívne snímky zo začiatku, stredu a konca. OCR pri 1 snímke za sekundu sa dokončilo na **30 z 30** unikátnych levelových klipov. Z 16 536 jednosekundových vzoriek vzniklo 1 103 kandidátnych OCR zásahov; surové výsledky vrátane textu OCR, hashov a časov sú v súbore Nitemare3D_direct_level_ocr_raw_2026-09-23.json. Časový index obsahuje 90 vybraných časovaných pozorovaní z OCR a predchádzajúcich manuálnych videoauditov. OCR je vyhľadávacia pomôcka: nejasné alebo krátke hlášky sa nepovažujú za potvrdené, kým ich nepotvrdí čitateľný obraz alebo existujúci manuálny audit.

Pre novšie unikátne nelevelové videá sa vytvorili trojbodové storyboardy. Hudobné videá majú statický Nitemare 3D obrázok a zvukovú stopu; samotné hudobné tracky sa tu neanalyzovali po sluchovej ani spektrálnej stránke. Záznamy z Bandicam zahŕňajú skutočnú hru, editorové okná aj neherný obsah. Preview rendererov, realistických textúr a konceptov nie sú kanonické správanie originálnej hry. Nitemare3D_video_visual_evidence_2026-09-23.zip obsahuje všetkých 90 individuálnych levelových snímok, tri epizódové prehľady, 15 nelevelových storyboardov a vybrané tabuľe výsledkov/porovnaní.

### Presnosť a hranice záverov

V správe používam tieto označenia:

| Označenie | Význam |
|---|---|
| **V — video** | Správanie priamo viditeľné v pomenovanom videu a čase. |
| **S — statický kód/dáta** | Správanie odvodené z konkrétne hashovanej binárky alebo párovaných MAP/OBJECTS/WALLS dát; nemusí sa automaticky vzťahovať na každý video-build. |
| **I — inferencia** | Najlepšie vysvetlenie vzoru pozorovaní, ale nie priamy dôkaz v kóde alebo riadenom experimente. |
| **N — neznáme** | Dôkaz zatiaľ nestačí na bezpečný záver. |

Videá neboli všetky sledované ručne snímku po snímke. Táto správa preto nezamieňa filmstrippy alebo OCR vzorkovanie s úplným manuálnym rozborom. Pri statických kódových tvrdeniach neprebehol v tejto úlohe nový debuggerový beh originálnej hry.

### Verzie hier použité na vysvetlenie

Statické technické správy a dáta v knižnici identifikujú:

- Win16 NITE3W 1.10, SHA-256 **12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481**.
- DOS N3D-UNFU 2.0 a N3D-E-20, SHA-256 **552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301**.
- MAP.1–3, OBJECTS.1–3, WALLS.1–3, IMG.1–3, UIF.DAT, SND.DAT a DEMO.1–3 sú súčasťou porovnávacieho materiálu. Verzie videí sa automaticky nepriraďujú k týmto EXE len podľa názvu.

Časti RNG, line-of-sight a damage helpera sa v porovnaných DOS/Win16 verziách zhodujú po zohľadnení rozdielov adries. To je dobrý dôkaz spoločného herného jadra pre tieto konkrétne rutiny, nie záruka úplnej parity všetkých AI, rendererov alebo levelových skriptov.

Porovnávané mapové balíky majú tieto SHA-256:

| Súbor | SHA-256 |
|---|---|
| MAP.1 | de4eb9cd58fc8e969af4076c1a19e5aa4b70f409205c93f8578b71cbd496200c |
| MAP.2 | 938b7e79c9881eab71fdef4b7afa9b0482c870c808785f599a4ba52093d44756 |
| MAP.3 | 0008775106854b3e9302f36fbcd7001607bcf2fd26cc9d8db6bccc732ead4217 |
| WALLS.1 | 9fbbf889440cf7200c7c2dad271f47c79652baf237c27f1bbb354ee1e8b1cf84 |
| WALLS.2 | 23f9cb3757ad92876d8f43a8ad9987cecc596e3c2d9a9ebb09b10ce0a2af59fe |
| WALLS.3 | abf6c2bc6779e6261998bc26bd03bbbce7e3ea608f28ddc4d78a13fd80a39cae |

## Inventár zbierky

| Skupina | Knižničné súbory | Dostupné | Rôzne dostupné obsahy | Poznámka |
|---|---:|---:|---:|---|
| Priame klipy E1M1–E3M10 | 40 | 40 | 30 | Každá z 30 máp má aspoň jeden priamy klip; dokopy 4 h 35 min unikátneho videa. |
| Hudobné témy a remixy | 15 | 15 | 15 | Statický herný obrázok; 27 min zvuku. |
| MS-DOS gameplay | 5 | 2 | 2 | Dostupné E1M5 a E1M7; chýbajú E1M3, E1M6, E1M8. |
| Old School Gamer | 12 | 12 | 12 | DOS označené walkthrough videá, spolu 2 h 12 min. |
| Map-ranking Shorts | 18 | 18 | 18 | Vertikálne zostrihy levelov, spolu 16 min 42 s; nie kompletné trasy. |
| Let’s Play | 12 | 11 | 11 | Chýba Part 11; 11 dostupných unikátnych videí spolu 3 h 49 min. |
| DOSBox Shareware v1.1 | 8 | 7 | 7 | Chýba E1L8; sedem výsledkových obrazoviek je čitateľných. |
| Hexkwondo walkthroughs | 51 | 44 | 36 | Sedem neprístupných položiek; viacero reuploadov je presne hashovo zhodných. |
| Bandicam/editor záznamy | 11 | 11 | 8 | Obsahujú Win16 Demo Mode, menu a editorové nástroje. |
| ENDING.FLI | 4 | 4 | 2 | Tri súbory majú rovnaký hash; štvrtý sa mierne líši. |
| Renderer / rekonštrukcia / koncept | 5 | 5 | 5 | Zahrnutý je aj generický titul Render Comparison. Nie sú kanonickým dôkazom hry. |

Štruktúrovaný inventár s plnými SHA-256, metadátami, duplikátmi, Library cestami a stavom prenosu je v Nitemare3D_video_inventory_2026-09-23.csv. Časový index udalostí v Nitemare3D_video_event_index_2026-09-23.csv uvádza konkrétne video, SHA-256 a čas.

### Nedostupné videosúbory

Prenos zlyhal pri týchto 12 položkách:

| Súbor | Očakávaná veľkosť |
|---|---:|
| Nitemare 3D E1M6 - MS-DOS Gameplay.mp4 | 518 268 861 B |
| Nitemare 3D E1M8 - MS-DOS Gameplay.mp4 | 364 759 036 B |
| Nitemare 3D E1M3 - MS-DOS Gameplay.mp4 | 353 092 299 B |
| Let's Play Nitemare 3D - Part 11 20.mp4 | 351 738 685 B |
| Nitemare 3D Shareware v1.1 (DOSBox) - E1L8.mp4 | 454 546 608 B |
| Nitemare 3D Walkthrough by Hexkwondo! E3 L4(2).mp4 | 464 631 533 B |
| Nitemare 3D Walkthrough by Hexkwondo! E3 L3(2).mp4 | 463 228 477 B |
| Nitemare 3D Walkthrough by Hexkwondo! E3 L6.mp4 | 218 955 724 B |
| Nitemare 3D Walkthrough by Hexkwondo! E3 L4(1).mp4 | 464 631 533 B |
| Nitemare 3D Walkthrough by Hexkwondo! E3 L3(1).mp4 | 463 228 477 B |
| Nitemare 3D Walkthrough by Hexkwondo! E3 L4.mp4 | 464 631 533 B |
| Nitemare 3D Walkthrough by Hexkwondo! E3 L3.mp4 | 463 228 477 B |

E3 L6 má dostupnú položku E3 L6(1) s hashom zhodným s predtým auditovaným obsahom, takže chýbajúci prenos E3 L6 nezastavuje analýzu tohto konkrétneho walkthrough. Pri E3 L3/L4 nemožno neprístupné reuploady označiť za presné duplikáty bez bajtov; samostatné priame levelové klipy E3M3 a E3M4 však v zbierke sú.

## Čo ukazujú videá o každej mape

Táto tabuľka oddeľuje úplnosť zdroja od istoty o konkrétnej mechanike. Všetkých 30 priamych levelových klipov poskytuje ďalšie vizuálne pokrytie; „podrobné“ znamená, že existuje aj manuálny časovaný audit dlhšieho walkthrough.

| Mapa | Video pozorovania a výsledky |
|---|---|
| **E1M1** | **V:** Červená opona/curtain sa po použití otvára po zvislých pruhoch; schody zobrazujú Climb up / Climb down / Cancel; red-key warp vypíše You use the Red key. Dokončenie s 5 nepriateľmi, 14 panelmi a bonusom 0. Dlhý Hexkwondo audit: opona ~00:39–00:42; schody ~04:30; red key ~04:58; green transition ~05:13–05:18. |
| **E1M2** | **V:** Strelba na cintorínsku stenu a následný priechod; tabuľa sa animuje na číslo 333; safe sa pýta na kombináciu a po zadaní 333 sa otvorí; viacvýberový warp; Green-key úspech. Červený/oranžový checker efekt sa objaví bez zmeny HUD súradníc, preto nejde o priestorový teleport. Výsledok: 20 nepriateľov a 19 panelov ostali. |
| **E1M3** | Priamy klip OCR zachytil Pentagram of Power približne v 04:03, Red-key použitie okolo 05:01, schody približne 05:51 a Green-key okolo 07:13. Opakovaný Red-key OCR hit pri ~05:49 môže byť druhá brána alebo zvyšok hlášky; presný počet interakcií treba overiť na snímkach. |
| **E1M4** | Priamy klip zachytáva zamietnutie „You need a Yellow key“ (~01:16), schodový výber (~07:21) a Blue-key hlášku (~08:15). Je to dobrý pár na porovnanie zamietnutého a úspešného keyed warp/door správania. |
| **E1M5** | Dostupný DOS gameplay aj priamy levelový klip. DOSBox Shareware v1.1 „All (Attainable) Secrets“ zobrazuje 0 nepriateľov, 1 nenájdený panel a bonus 5 000. Táto úroveň odlišuje „všetky dosiahnuteľné tajomstvá“ od nulového počtu panelov. |
| **E1M6** | **V/S:** MAP.1 uvádza jeden pushable tombstone; walkthrough navštívi cintorínsku oblasť, ale čistý pred/po posun tombstone nie je izolovaný. Explodable wall záber ukazuje zásah, výbuch/checker animáciu a neskôr priechodný otvor. Priamy klip OCR zachytáva Yellow-key a viaceré Green-key hlášky. |
| **E1M7** | DOS gameplay aj priamy klip sú dostupné. Shareware v1.1 výsledok má 0 nepriateľov, 0 panelov a bonus 10 000. Dlhší Old School Gamer materiál je ďalší DOS kontext; samostatné krátke klipy netreba považovať za úplný route log. |
| **E1M8** | Priamy klip ukazuje Yellow-key použitie a schody; neúspešné MS-DOS gameplay video je nedostupné. V Shareware datasete nie je E1L8 kvôli zlyhanému prenosu. |
| **E1M9** | Priamy OCR zachytáva Green-key a Blue-key úspech v prvých 100 sekundách. DOSBox Shareware výsledok zobrazuje 1 nepriateľa, 0 nenájdených panelov a bonus 5 000. |
| **E1M10** | **V/S:** Pri portáli sa zobrazí, že na Other Side sa nedá prejsť bez všetkých štyroch pentagramov. Nasledujúci príbehový text uvádza Penelope a Dr. Hamersteina. Kódové/mapové dáta rozlišujú tento portál od bežného LEVEL_UP. |
| **E2M1** | Výťah ponúka Floor 1 / Floor 2, bez Cancel; MAP.2 má dva WARP_E1 endpointy. Záver obsahuje Transportation Chamber a green transition. |
| **E2M2** | Schody zobrazujú Climb up / Climb down / Cancel a prenášajú hráča do jaskynnej časti. MAP.2 a OBJECTS.2 uvádzajú všetky štyri farebné kľúče a red ID card. |
| **E2M3** | Jaskynné a interiérové/log oblasti prepojené warp sieťou; časté explodable steny a miznúce gargoyle steny. |
| **E2M4** | Truhlica po otvorení ostáva otvorená; vnútri je Pentagram of Good Health. MAP.2 obsahuje deväť pushable tombstones a Yellow ID card. E2M4 je jeden z najužitočnejších testov persistentného stavu objektov. |
| **E2M5** | Stair selector; Transportation Chamber → LEVEL_UP → zelený prechod. Výsledok: 22 nepriateľov, 1 panel, bonus 0, skóre 16 850. To priamo dokazuje, že odchod nevyžaduje vyčistenú mapu ani nájdenie všetkých panelov. |
| **E2M6** | Niekoľko nezávislých warp rodín, schodový výber, štyri pushable tombstones a Yellow ID card. Výsledok: 12 nepriateľov, 2 panely, bonus 0, skóre 20 100. |
| **E2M7** | Štvorposchodový elevator menu obsahuje Floor 1 až Floor 4 bez Cancel. Výsledok: 7 nepriateľov, 0 panelov, bonus 5 000. |
| **E2M8** | Päťmožnosťový remote-control menu: open/close remote doors, enable/disable remote cannons, cancel. Dáta uvádzajú šesť push objektov, päť OneShot stien a 15 explodable stien. Výsledok: 14 nepriateľov, 1 panel, bonus 0. |
| **E2M9** | Rovnaké control menu; mapa ponúka osem cannon objektov a 59 explodable stien/hedges. Výsledok: 11 nepriateľov, 2 panely, bonus 0. Video potvrdzuje menu, nie presné priradenie každého control panela k jednotlivým objektom. |
| **E2M10** | Scripted finále: remote-control menu, „QUICK! Destroy the plasma core!“, následné „You destroyed the plasma core!“, blast text a červený dopadový efekt. V MAP.2 chýba LEVEL_UP, preto ide o špeciálny ukončovací skript, nie bežný exit. Výsledok: nepriatelia 0, panely 0, bonus 10 000. |
| **E3M1** | Úvodná hláška opisuje výbuch jadra, zaseknuté automatické dvere a rozhádzaný inventár. Blue-key bez kľúča vyvolá „You need a Blue key“; druhá polovica walkthrough ukazuje Yellow-key lock, Demona, transport a dokončenie. Výsledok: 3 nepriatelia, 3 panely, bonus 0, skóre 1 775. V mape sú remote door triggery, ale ich priame video správanie nebolo potvrdené. |
| **E3M2** | Video potvrdzuje red, green aj blue key success hlášky. Yellow ID card existuje v dátach, ale žiadna čitateľná hláška nedokazuje jeho použitie pri komore. Výsledok: 14 nepriateľov, 5 panelov, bonus 0, skóre 5 125. |
| **E3M3** | Existuje priamy levelový klip a reuploady walkthrough, no medzi dostupnými manuálnymi reportmi nie je dokončený časovaný audit tejto mapy. Z kontaktových snímok je potvrdený levelový vizuál, nie úplná trasa alebo všetky mechaniky. Neprístupné Hexkwondo E3 L3 reuploady sú samostatná medzera. |
| **E3M4** | Dlhý walkthrough: explodable red-moss steny, kľúčové úseky, kaplnka, škatule a zelený kľúč, žltý/red lock, tma a oheň, ID karta, schodová pasca s boxmi a súboj s dvoma aliens. Výsledok: 6 nepriateľov, 1 panel, bonus 0, skóre 12 900. Súvislosť boxov so schodovou únikovou cestou je interpretácia trasy, nie univerzálne pravidlo. |
| **E3M5** | Pentagram of Good Health, secret-panel reťaz a schodový výber. Priamy klip OCR navyše číta Pentagram of Power (~01:15) a You use the Blue key (~08:25). Walkthrough má strih na hint-booklet/editorial vložku okolo 06:40 a vracia sa cez menu; preto nejde o súvislý beh. Výsledok: 15 nepriateľov, 4 panely, bonus 0, skóre 17 675. |
| **E3M6** | Red-key, green-key, schody, yellow-key, trunk s +150 skóre, boj a viac druhov ohňa. HP sa v boji mení, ale video samo neurčuje, či zdrojom bol útok, kontakt alebo oheň. Výsledok: 18 nepriateľov, 2 panely, bonus 0, skóre 25 675. |
| **E3M7** | Priamy klip OCR navyše zachytí Red, Blue a Green key hlášky. Dlhý walkthrough potvrdzuje Green a Yellow key na neskorej trase, rozsiahlu poľnú pasáž s ohňom a booth exit. Výsledok: 2 nepriatelia, 2 panely, bonus 0, skóre 33 575. |
| **E3M8** | Green key sa použije najmenej trikrát na rôznych dverách a ostáva dostupný; priame OCR navyše zachytáva Yellow-key, ďalšie Green-key použitia a Blue-key. Výsledok: 27 nepriateľov, 18 panelov, bonus 0, skóre 38 025. Je to najsilnejší video dôkaz, že farebný kľúč sa pri otvorení nespotrebuje. |
| **E3M9** | Elevator Floor 1 / Floor 2 bez Cancel; prasknuté Mirror of Destiny aktivuje zelený prechod. Výsledok: 2 nepriatelia, 4 panely, bonus 0, skóre 44 700. |
| **E3M10** | Schody, trigger text „Look! It’s Penelope! Where’s Dr. Hamerstein?“, súboj a „You’ve won! You’ve won!“, potom ENDING.FLI. Žiadna LEVEL_UP dlaždica. Záverečný výsledok: nepriatelia 0, panely 0, bonus 10 000, skóre 55 700. |

### Výsledkové obrazovky a bonus

Sedem dostupných DOSBox Shareware v1.1 videí má tieto výsledky:

| Úroveň | Zostávajúci nepriatelia | Nenájdené panely | Bonus | Skóre |
|---|---:|---:|---:|---:|
| E1L1 | 0 | 0 | 10 000 | 11 700 |
| E1L2 | 0 | 0 | 10 000 | 27 900 |
| E1L3 | 0 | 0 | 10 000 | 43 850 |
| E1L5 | 0 | 1 | 5 000 | 71 600 |
| E1L7 | 0 | 0 | 10 000 | 103 625 |
| E1L9 | 1 | 0 | 5 000 | 127 450 |
| E1L10 | 0 | 0 | 10 000 | 137 675 |

**I — vysoká istota:** V tomto DOS shareware súbore vzor presne zodpovedá bonusu 5 000 za nulový počet zostávajúcich nepriateľov a ďalších 5 000 za nulový počet nenájdených panelov. Rovnakú interpretáciu podporujú E2M7 (7 nepriateľov, 0 panelov, bonus 5 000), E2M10/E3M10 (0/0, bonus 10 000) a E3M7/E3M8/E3M9 (aspoň jedna podmienka nesplnená, bonus 0). Vzorec je silno podložený naprieč videami; presná rutina v kóde by ho ešte formálne uzavrela.

## Mechaniky a vysvetlenie správania

### Mapa, koordináty a typy

**S:** Mapa má 64 × 64 buniek; každá bunka drží oddelene ID steny a ID objektu. Svetová bunka sa počíta posunom koordináty doprava o 6 bitov, teda bunka má 64 interných jednotiek. MAP hlavička má 514 bajtov: počet levelov a dve 256-bajtové tabuľky ID → class. Každý level blok má 8 192 bajtov. Kontrolované MAP súbory majú dokopy 31 blokov: po 10 bežných máp v každej z troch epizód a jeden extra E1M11 demo blok. Pri E1M11 sa zhoduje wall geometria E1M3, ale 17 buniek object plane je iných.

Wall class a object class, asset ID a weapon selector sú štyri rozdielne identifikátory. Číselná zhoda neznamená rovnakú vec. Pri portovaní treba zachovať surové ID aj dekódovanú class a neznáme ID neskrývať cez „najbližší“ známy typ. V párovaných dátach je napríklad E2M4 wall ID 0x37 nevyhodnotený a mapové tabuľky sa môžu meniť podľa epizódy.

Win16 1.10 runtime limity, ktoré treba pri parsovaní udržať:

| Runtime pole | Kapacita | Veľkosť záznamu |
|---|---:|---:|
| wall vectors | 1 000 | 28 B |
| visible wall spans | 50 | 20 B |
| world objects | 350 | 28 B |
| guard records | 100 | 26 B |
| door / paired-wall records | 64 | 22 B |
| secret-panel records | 32 | 22 B |
| push-object slots | 12 | 6 B |
| projectile slots | 8 | 42 B |

Tieto sú kapacity Win16 builda, nie automatický limit DOS alebo iného klonu. Kontrolovať ich treba oproti príslušnej binárke a SAVE formátu.

### Aplikácia, menu a vstup

**V:** Video aplikácie ukazuje Main Menu položky New game, Configure game, Load game, Instructions, Demo a Quit. Iné klipy zachytávajú herné menu, Please Wait prechod a samotný Demo Mode.

**S, Win16:** Arrow keys menia vstupnú masku; Escape, Space a Enter prechádzajú do UI/event dispatcheru. Q a R prepínajú hudbu a zvukové efekty a zobrazia on/off text. Alt+Enter prepína fullscreen/window cestu; Alt+S čistí input a posiela custom window message, ktorého účel nie je uzavretý. Príkazový argument -o zapína logger, ktorý otvára alebo dopĺňa debug.txt a zapisuje nájdené audio/MIDI inicializačné správy. Samotný názov -debug ani všeobecné debug menu tým dokázané nie sú.

### Interakcie, dvere, kľúče a warp systémy

**V:** Schodová obrazovka typicky ponúka Climb up / Climb down / Cancel. Výťahové obrazovky ponúkajú konkrétne Floor N položky a vo vzorkovaných dvoch- a štvorposchodových výťahoch nemajú Cancel. Remote panel má štyri príkazy pre vzdialené dvere a delá plus Cancel. Tieto tri obrazovky sa nesmú zameniť.

**V:** „You use the Red/Green/Blue/Yellow key“ je úspešná vetva; „You need a Yellow/Blue key“ je zamietnutá vetva. **V/S:** opakované použitie zeleného kľúča a HUD podporujú trvalý inventárny príznak, nie odčítanie kusu po každom otvorení.

**S:** USE je v analyzovanom Win16 vstupe bit 0x0200. Kľúčové WARP_L, stair warpy, elevators, mirror warp, transportačné dvere a LEVEL_UP zdieľajú niektoré helpery, ale predstavujú rôzne triedy. Transportačná komora a ID-card kontrola sa musí držať oddelene od farebných zámkov. Video neukazuje čistú „You use ID card“ hlášku pri viacerých exit komorách, preto spotreba karty a presný gate test ostávajú otvorené.

**S:** Secret panel má vlastný 32-záznamový pool, až štyri pridružené wall/door záznamy a sound event 0x27. DAT_51A4 je bitová maska stavu panel-wall pair, nie kód safe kombinácie. Safe ID-y 0xD2–0xD7 používajú inú kombináciovú vetvu; pri E1M2 je vizuálne potvrdená kombinácia 333.

**S:** Paired walls/doors majú až 64 záznamov; panelov je 32 a push slotov 12. Dvere sa v analyzovanej Win16 rutine posunú o 2 interné jednotky na update. Automatické zatvorenie čaká 32 updatov a pri blokovaní skúsi znovu po 4. Nie je bezpečné z týchto tickov vyrátať sekundy bez zmerania frekvencie update.

### Nepriatelia a vnímanie hráča

**V:** V mnohých úrovniach hráč odíde s nepriateľmi nažive; nepriateľské AI preto nemá byť podmienkou level exit. Videá ukazujú rôzne nepriateľské sprite triedy, výstrely, zásahy a health HUD, ale samotný obraz bez kontrolovanej testovacej série neurčí presný stav AI alebo zdroj každého HP poklesu.

**S, Win16 1.10:** Stráž má 26-bajtový GUARD záznam a je prepojená s 28-bajtovým OBJECT/render záznamom. Dispatcher používa číselné stavy 0x00–0x15; stavy 0x0A/0x0B nemajú v obnovenom switchi explicitné vetvy. Stavové čísla v portovanom kóde je vhodné pomenovať podľa pozorovanej operácie, nie podľa vymysleného pôvodného názvu.

**S, Win16 a DOS helper:** Vnímanie najprv prevedie hráča a stráž na bunky mapy. Ak rozdiel na jednej osi prekročí 8 buniek, cieľ sa odmietne. Bežná vetva vytvorí smerovú masku z aktuálneho smeru stráže a dvoch susedných smerov z ôsmich; potom skúša Bresenhamovu line-of-sight dráhu maximálne 8 mapových krokov. Niektorí volajúci obídu facing filter alebo vynechajú druhú rovinu. Nie je tam jedna univerzálna geometria FOV.

Blízkosť je samostatný test: oba world-coordinate rozdiely musia byť najviac 0x40. Je to štvorcový test po osiach, nie euklidovský kruh. Volajúci vyberajú proximity alebo LOS cez samostatný selector field.

**S:** Po úspešnom výstrele si Win16 kód označí nenulové area ID v 64-bajtovej tabuľke a zobudí stráže s rovnakým ID, ak sú v príslušných waiting states. Wake loop netestuje vzdialenosť ani LOS a priradí krátky náhodný timer. **I:** To pravdepodobne vysvetľuje, prečo sa skupina môže aktivovať aj mimo aktuálneho výhľadu. **N:** „nepriateľ počuje streľbu“ nie je bezpečný všeobecný záver; globálne šírenie alarmu ani všetky zvukové cesty preukázané nie sú.

Fallback steering volí štyri náhodné smery, ak hráč nie je vo viditeľnostnom stave, a osem, keď LOS prešiel. Na krátku vzdialenosť, viditeľný cieľ a neviditeľný cieľ používa rozdielne čakacie časy. Stratégie 2 a 3 majú preukázateľne random wait/displacement vetvy. Kanonické mená týchto stavov a presná väzba každého sprite typu na správanie zostávajú predmetom ďalšieho traceovania.

Kontaktové poškodenie je oddelené od projektilového. V analyzovanej Win16 vetve sa mení podľa class a vzdialenosti; difficulty 2 ho polovičí, difficulty 0 zdvojnásobí. Video E3M6 zachytí pokles HP počas boja, ale neurčí príčinu samostatne.

Číselné stavy GUARD dispatcheru v Win16 1.10 majú zatiaľ tieto operácie; tabuľka nepredstiera pôvodné názvy stavov:

| GUARD state | Potvrdená operácia |
|---:|---|
| 0x00–0x02 | posun sekvencie/timeru, čakanie, inicializácia nasledujúcej sekvencie |
| 0x03–0x05 | test vnímania, útok/interakcia, fallback smerovanie |
| 0x06–0x08 | časovaný pohyb, orientácia a opätovné získanie cieľa |
| 0x09 | útok alebo interakcia s naviazaným OBJECT |
| 0x0A–0x0B | v obnovenom switchi nemajú explicitné vetvy; možné nepriame použitie alebo hranica dekompilácie |
| 0x0C–0x0D | spoločná helper vetva, presný herný účel neurčený |
| 0x0E–0x10 | časovaný cyklus Cannon; DAT_51A5 povoľuje alebo vypína útočnú vetvu |
| 0x11 | vyberie smer a vráti sa do pohybovej vetvy |
| 0x12 | posunie sekvenciu a OBJECT výškový/offset field, potom obnoví uložený stav |
| 0x13–0x14 | časované displacement/pohybové vetvy |
| 0x15 | hit/reaction sekvencia; presná väzba každej class na animáciu je neúplná |

Kontaktné poškodenie pred difficulty úpravou: class 0x08 dáva random 0–7; 0x09–0x0A random 0–15; 0x0B štvrtinu vzdialenostného základu; 0x0C/0x1D/0x1E používajú základ; 0x11–0x14 random 0–31; 0x16 dáva 33 pri level/event podmienke inak 100; Cannon class 0x19 dáva 100; ďalšie spracované vetvy používajú polovicu základu. Základ sa odvodzuje od euklidovskej vzdialenosti v mapových bunkách, s náhradou 100 pri vzdialenosti pod jednu bunku. Toto je konkrétna Win16 contact helper vetva, nie univerzálna damage tabuľka pre všetky útoky.

### Zbrane, projektily, zásah a poškodenie

**S, Win16 1.10:**

- Weapon selector 2 používa hitscan; selectory 0, 1 a 3 idú projektílovou cestou.
- Projektilový zásobník má 8 slotov po 42 bajtov. Sloty majú Bresenham/DDA postup, stav 0 voľný, 1 letí, 2 impact; zvyšok obsahuje embedded OBJECT/render záznam.
- Projektil pri malých subkrokoch testuje mapu, stenu a stráž; zásah stráže vyžaduje rozdiel menší než 10 interných jednotiek na oboch osiach.
- Ak sa slot nepodarí alokovať, v kontrolovanej vetve sa pred ammo helperom skončí, takže sa náboj nespotrebuje.
- Pri bežnom ammo decremente sa pre weapon selector 0/1/2 volá zvuková udalosť 8/9/7. Presné priradenie SND.DAT udalostí k audio payloadom ešte nie je dekódované.
- Explodable wall pri trafení spustí sound event 0x29, zmení runtime objekt na class 0x2D a začne explóziu. Win16 cleanup po sekvencii odstráni blokovanie/prítomnosť steny. Ekvivalent DOS cleanup zatiaľ nie je uzavretý.

Opravený damage helper je kriticky dôležitý pre vysvetlenie správania. Jeho semeno je:

    seed = 8 × signed16(OBJECT+0x18 − viewport_center_y) + (RNG % 25)

OBJECT+0x18 je v analyzovanom kóde projektovaná a orezaná vertikálna obrazovková pozícia cieľa, nie vzdialenosť v hernom svete. Zásahy sa potom upravia podľa OBJECT class, weapon selectora a difficulty; horný limit je 255. Damage a score sú dve rozdielne vetvy. Preto zo samotného počtu pixelov, zvukového zásahu či skóre nemožno spätne určiť HP damage bez triedy, výšky na projekcii, zbrane, obtiažnosti a RNG.

Staticky potvrdené class/weapon transformácie pred difficulty úpravou sú tieto; „>>“ znamená aritmetický posun doprava:

| OBJECT class | Damage transformácia |
|---:|---|
| 12, 29 | seed >> 3 |
| 13 | weapon 1 alebo 2: seed >> 1; inak seed >> 3 |
| 14, 17, 20 | weapon 2: seed >> 1; inak seed >> 3 |
| 15, 16 | weapon 1: 0; inak seed >> 1 |
| 18, 19 | weapon 1: 0; inak seed >> 2 |
| 21 | zavolá zatiaľ nepomenovaný helper a potom nastaví damage na 0 |
| 22 | 3 damage len v Episode 3, inak 0 |
| 23 | weapon 1: seed >> 8; inak seed >> 2 |
| 24 | weapon 1: seed >> 8; weapon 2: seed >> 4; inak seed >> 3 |
| 25 | 0 |
| 26 | weapon 1: seed >> 1; inak 0 |
| 27, 28 | seed >> 1 |
| 30 | weapon 1: 0; inak seed >> 3 |
| 31 | weapon 1: 0; inak seed >> 2 |

Výstup sa v kóde hore orezáva na 0xFF; explicitný dolný clamp v tejto helper vetve nie je potvrdený. Damage helper nie je vhodné kopírovať do portu ako neznamienkové aritmetiky bez testu záporného seed.

Score helper je separátny: class 9 dáva 75; 10/25/32 dávajú 50; 11/15/16/23/27/28 dávajú 100; 12/21/29/30 dávajú −1000; 13/18/19 dávajú 150; 14/20/24/31 dávajú 200; 17 dáva 250; 22 dáva 1 000; 26 dáva 0. Pre class 8 sa volá neidentifikovaný helper. Tieto čísla sú Win16 helper evidence a nie sú automaticky identitou každého viditeľného sprite v neznámom build.

**S, Win16 1.10:** Oheň class 0x07 má v dátach large/medium/small typy s ID 0x3B/0x3C/0x3D a dáva 100/10/2 HP za simulation update. Veľký oheň tak môže pri 100 HP zabiť jedným update. Fyzický interval update nie je priamo odvodený, preto tieto čísla nie sú DPS. Video E3M6 a E3M7 potvrdzuje, že oheň tvorí prekážku a hráč mu prispôsobuje trasu; presné tickové poškodenie pochádza z kódu, nie z video odhadu.

### Renderer, animácia, čas a random

**S, Win16 1.10:** Wall renderer je vector/span cesta s per-column ownership a clipping; nie je potvrdený ako klasický Wolf3D DDA raycaster. Kód pracuje s 320 stĺpcovým ownership bufferom a span záznamami, ktoré sa skladajú do rasterizovanej steny. Sprite transparency/occlusion má oddelenú vetvu od wall pixelov. Presné edge rounding, všetky IMG sequence/frame selektory, farebná paleta/shading a pixelovo presná zhoda medzi DOS VGA a Win16 výstupom ostávajú otvorené.

**S:** IMG má dve 0x400-bajtové offset directory tabuľky; object/special wall cesty používajú high-bank selector. Sekvenčná definícia má v kontrolovanom formáte 90 B, runtime cache záznam 8 B a samostatné frame záznamy. Nezamieňať ID assetu za runtime sequence selector. Kompletné priradenie všetkých 31 levelov a všetkých IMG sekvencií ešte nie je uzavreté.

**S:** Porovnané buildy používajú LCG s násobiteľom 0x343FD a prírastkom 0x269EC3; výstup je horných 15 bitov po posune o 16. Globálny Win16 counter DAT_53DC sa zvýši pred render pipeline a DEMO playback ho používa. Presný wall-clock tick a poradie každej AI/kolíznej vetvy vo frame loop nie sú uzavreté. Door, fire a guard časovače preto treba modelovať v update jednotkách, kým ich frekvencia nebude odmeraná.

### Tajomstvá, skóre a exit

**V/S:** Z viacerých výsledkových obrazoviek vyplýva, že enemies remaining a panels not found sú štatistiky výsledku, nie povinné brány na dokončenie mapy. Najčistejšie príklady sú E2M5, E3M7, E3M8 a E3M9. Pre rekonštrukciu treba oddeliť:

1. podmienku, ktorá aktivuje exit alebo scripted finale;
2. zmenu level indexu a green transition;
3. výsledkové počítadlá;
4. bonus za vyčistenie nepriateľov/panelov;
5. celkové skóre.

Bonusový vzorec 5 000 za každú z dvoch nulových podmienok je silná inferencia podporená DOS shareware aj ďalšími walkthroughmi. Video potvrdzuje výsledky; presný kódový výpočet treba uzavrieť cieleným traceom pri výsledkovej obrazovke.

### Skriptované levelové udalosti

V statickom Win16 1.10 kóde a párovaných MAP dátach sú rozpoznané TRIGGER1/TRIGGER2 oblasti a texty:

- E1 level-index 6: „Oh dear! The storm seems to have fused the lights!“; špeciálny fuse box potom môže hlásiť „Well done! You fixed the power!“.
- E1 level-index 8: stavová vetva zobrazí „Your weapon appears to be jammed!“.
- E1 level-index 9/10: boss texty, Penelope/Hamerstein a víťazná hláška.
- E2 level-index 9: „QUICK! Destroy the plasma core!“.
- E3 level-index 0: úvodná správa, že výbuch jadra zasekol dvere a rozhádzal inventár.
- E3 level-index 9: „Look! It’s Penelope! Where’s Dr. Hamerstein?“.

Kód potvrdzuje statické vetvy, texty, flagy a mapové bunky. Neznamená to, že každú udalosť možno z videa považovať za aktivovanú, alebo že rovnaký trigger platí pre všetky vydania.

### DEMO, ENDING.FLI a neherný obsah

**DEMO — V/S:** Bandicam záznam zobrazuje aplikáciu Nitemare-3D, menu a Demo Mode. Porovnanie znížených grayscale snímok po jednej za sekundu našlo najlepšie zarovnanie s posunom 252 s: mnoho párov snímok pri t→t+252 vyzerá takmer rovnako. Video preto silno naznačuje opakovanie podobnej demo trasy približne každé 4 min 12 s; nejde o dôkaz, že engine používa presne taký časovač.

**DEMO — S:** Win16 obsahuje nahrávanie a prehrávanie vstupov. Súbory DEMO.1–3 začínajú 6-bajtovou hlavičkou s troma little-endian wordmi 10, 5, 20 a pokračujú 8-bajtovými záznamami: key-event byte, 16-bit input mask, nevyužitý/nezaradený byte a 32-bit čas. Záznamy vznikajú pri zmene vstupu, nie každý frame. Časová jednotka a EOF správanie ostávajú otvorené; sémantická kompatibilita naprieč buildmi nie je dokázaná.

Presnejšie, zaznamenané Win16 DEMO.1/.2/.3 majú 203/271/286 vstupných záznamov. Všetky majú hlavičku 10,5,20 a každý záznam má dĺžku 8 B; byte +3 je v súbore nulový a v pozorovaných playback vetvách sa nečíta. DOS v2.0 používa odlišné rozloženie key/event poľa, preto ho nemožno parsovať ako Win16 súbor bez build-specific adaptera.

**ENDING.FLI — V:** Tri FLI kópie sú bajtovo zhodné; štvrtá sa líši veľkosťou. Obe varianty sa dekódujú na 489 snímok. Priemerný pixelový rozdiel je veľmi malý a scéna i dialóg sú vizuálne rovnaké; jemné rozdiely sú bez ďalšej analýzy príčiny, napríklad palety/enkódovania, nevysvetlené. Editované žlté titulky v walkthrough videu nie sú súčasť originálnej FLI.

**Editor záznamy:** SND slot editor, Nitemare3DEdit 1.0.1, IMG editor a ďalšie nástroje sú viditeľné v záznamoch. Jedna snímková sekvencia ukazuje Explorer s Nitemare 3D for Windows v1.10 a otvdm; ďalšia obsahuje pre-release ChaosEdit/Wolf map. Tieto okná sú dôkazom pracovného prostredia, nie samotného herného správania.

## Implementačný náčrt

Nasledujúci pseudokód zachováva preukázané oddelenia. Nie je to pôvodný zdrojový kód; miesta označené unknown musia zostať modulárne.

    interactWithWall(player, wall):
        kind = resolveWallClass(wall.episode, wall.wallId)

        if kind is KeyedWarp:
            if not player.inventory.has(kind.requiredKey):
                show("You need a " + kind.requiredKeyName)
                return
            show("You use the " + kind.requiredKeyName)
            enterWarp(kind.destination, adjacentArrivalCell=true)
            return

        if kind is StairWarp:
            choice = menu("Climb up", "Climb down", "Cancel")
            if choice != Cancel:
                moveToAdjacentEndpoint(choice)
            return

        if kind is Elevator:
            floor = menu(kind.availableFloors)
            moveToAdjacentEndpoint(floor)
            return

        if kind is TransportationChamber:
            if not transportGatePasses(player.inventory, levelState):
                return
            enterChamberThenLevelExit()
            return

        if kind is ExplodableWall and wall.hitPoints <= 0:
            startImpactAnimation()
            onAnimationFinished:
                clearBlockingMapCell()
                removeOrTransformWallObject()
            return

        if kind is RemoteControl:
            choice = menu(
                "Open remote doors",
                "Close remote doors",
                "Enable remote cannons",
                "Disable remote cannons",
                "Cancel")
            dispatchByControlRecord(choice)  // target mapping still open

    guardPerception(guard, player):
        if abs(cellX(player) - cellX(guard)) > 8 or
           abs(cellY(player) - cellY(guard)) > 8:
            return false

        near = abs(player.x - guard.x) <= 0x40 and
               abs(player.y - guard.y) <= 0x40

        // Ordinary callers apply 3-of-8 facing sectors and LOS.
        // Some analyzed states explicitly bypass one or both filters.
        visible = callerSpecificSectorTest(guard, player) and
                  bresenhamLineClear(maxSteps=8)

        return callerSpecificSelector(near, visible)

    shoot(player, weapon):
        if weapon.usesProjectile:
            slot = allocateOneOfEightProjectileSlots()
            if slot == none:
                return                    // observed path does not spend ammo
            initializeProjectile(slot)
            spendAmmoIfApplicable(weapon)
            advanceProjectileBySmallSimulationSubsteps()
        else:
            candidates = currentGenerationRenderedTargets()
            for target in candidates:
                damage = enemyClassDamage(
                    projectedRow=target.screenY,
                    viewportCenter=viewport.centerY,
                    rng=gameRng,
                    weapon=weapon,
                    difficulty=gameDifficulty)
                applyDamage(target, damage)
                updateScoreSeparately(target)

    computeLevelBonus(stats):
        bonus = 0
        if stats.enemiesRemaining == 0:
            bonus += 5000            // high-confidence inference
        if stats.panelsNotFound == 0:
            bonus += 5000            // high-confidence inference
        return bonus

Pre skutočný port je dôležité zachovať jednotlivé epizódové MAP/OBJECTS/WALLS tabuľky, pôvodné interné jednotky a tickové časovače. Neprepočítavať čas na milisekundy bez merania a nevyplniť neznáme správanie „typickými FPS“ predpokladmi.

### Odporúčaný dátový model pre implementáciu

| Modul | Minimálny obsah | Prečo oddeliť |
|---|---|---|
| EpisodeResources | build/hash, MAP, WALLS, OBJECTS, IMG, UIF, SND | Udrží epizódové ID/class tabuľky spolu a dovolí presne pomenovať neznáme ID. |
| MapCell | raw wall ID, raw object ID, resolved wall class, resolved object class | Mapa ukladá dve ID v jednom cell zázname, ale vyhľadáva ich cez odlišné class lookupy. |
| WallRuntime | class, linked partner, phase/state, timer, target, animation sequence | Bežné dvere, paired wall, keyed warp, panel, elevator a scripted exit zdieľajú iba časť lifecycle. |
| PlayerInventory | samostatné bitové sady key/card/pentagram a počty munície | Video podporuje trvalé farebné kľúče; karty a pentagramy majú oddelené účely. |
| GuardRuntime | trieda objektu, numerický AI state, timer, strategy, area ID, LOS/near cache, naviazaný OBJECT | AI číta samostatné percepčné a vykresľovacie hodnoty; neprekrývať ich bez dôkazu. |
| ProjectilePool | presne 8 slotov, DDA polia, lifecycle, embedded render record | Projektily majú vlastný limit, kolízne kroky a render metadata. |
| LevelEventState | DAT_51A4 až DAT_51AB ekvivalent, trigger latches a per-level flags | Secret-panels, cannons, dark state a level script nepoužívajú jeden spoločný progress byte. |
| LevelCompletion | exit condition, remaining enemies, missing panels, bonus, total score | Videá dokazujú, že dokončenie mapy neznamená vyčistiť všetky štatistiky. |

Každý dekódovaný field má mať aj provenienciu: zdrojový build/hash, offset alebo MAP cell, istotu a posledný test. Neznáme bajty sa majú zachovať pri načítaní/uložení, nie zahodiť.

## Zostávajúce neznáme zoradené podľa hodnoty

| Priorita | Otázka | Čo ju vyrieši |
|---|---|---|
| **P0** | Ktoré video patrí ku ktorému presnému DOS/Win16 buildu? | Vizuálny fingerprint obrazovky a HUD, porovnanie s rovnakou binárkou, zaznamenať EXE hash pri každom replayi. |
| **P0** | Presné poradie update: input, hráč, AI, kolízia, projektil, trigger, render? | Riadený trace v originálnom EXE; korelovať vstup/tick, framebuffer a pamäťové zmeny. |
| **P0** | Môže projectile zásah čítať starý OBJECT+0x18 render-row? Aký je záporný/okrajový damage? | Jeden cieľ, fixná zbraň/difficulty, zámerne zastaraný render candidate, zaznamenať RNG/HP. |
| **P0** | Aký je kompletný enemy state graph a class → animácia/útok? | Zostaviť graf writer → state dispatcher → timer → movement → sound/attack; porovnať DOS/Win16. |
| **P0** | Aký je wall-clock význam DEMO countera a čo spraví EOF? | Prehrať DEMO.1–3, zaznamenať 0x53DC proti reálnemu času, posledný záznam, návrat do menu. |
| **P1** | Ako presne fungujú ID karty a transportačné komory? Spotrebujú sa? | Pripraviť uložený stav pred komorou, prejsť s/bez karty a porovnať inventár/map cell. |
| **P1** | Ktorý remote panel ovláda ktoré dvere/delá? | Každú z piatich možností otestovať samostatne v E2M8/E2M9 a porovnať MAP runtime flagy. |
| **P1** | Je budenie nepriateľov lokálne, globálne alebo podľa viac než jedného area ID? | Výstrel v kontrolovanej vzdialenosti a cez inú trigger oblasť; sledovať GUARD state a area ID. |
| **P1** | Sú explodable wall triedy a cleanup rovnaké v DOS? | Snímať príslušnú map cell/door record pred zásahom, počas výbuchu a po animácii v každom builde. |
| **P1** | Aká je skutočná jednotka AI/door/fire timera? | Časovať update counter pri známej frekvencii simulácie a opakovať pri odlišnej render frekvencii. |
| **P1** | Je bonus 5 000 + 5 000 rovnaký vo všetkých registrovaných/Shareware buildoch? | Trace výsledkovej rutiny a kontrolné behy 0/1 zostávajúci nepriateľ × 0/1 panel. |
| **P2** | Čo spôsobuje červený/oranžový checker efekt a prečo chalkboard mení sequence interval? | Trace zdrojového wall/object eventu a sekvencie; porovnať paletu, frame index a stav objektu. |
| **P2** | Aké zvuky zodpovedajú SND.DAT slotom, ktoré hrajú pri jednotlivých udalostiach? | Extrahovať/dekódovať SND.DAT, zachytiť zvuk s frame timestampom, porovnať s event ID. |
| **P2** | Prečo sa mierne líšia dve ENDING.FLI verzie? | Rozobrať paletu, chunk sequence, ring frame a decoded RGB po blokoch; zatiaľ vizuálne ide o rovnakú scénu. |
| **P2** | Ktoré nepopísané GUARD/OBJECT polia majú gameplay význam a ktoré sú renderer cache? | Systematická reader/writer tabuľka s breakpointmi na zmenách konkrétnych polí. |

## Správy a zdroje, na ktoré audit nadväzuje

Statické technické a predchádzajúce videoaudity v knižnici obsahujú viac detailov, než sa zmestí do tohto súhrnného auditu. Základné referencie:

- Nitemare3D_Reverse_Engineering_Master_Reference_2026-09-23.md
- Nitemare3D_neznáme_hlbkový_audit_2026-09-23.md
- Nitemare3D_mapa_neznamych_oblasti_cela_hra_2026-09-23.md
- Nitemare3D_deep_unknowns_2026-09-23.md
- Nitemare3D_unknown_logic_audit_2026-09-23.md
- Nitemare3D_DEMO_playback_analysis_2026-09-23.md
- Nitemare3D_projectile_pool_deep_map_2026-09-23.md
- Nitemare3D_12_areas_evidence_audit_2026-09-23.md
- Nite3W_GUARD_audit_2026-09-23.md
- Nite3W_all_addresses_and_fields_2026-09-23.md
- Nite3W_function_checklist_unknowns_audit_2026-09-23.md
- NITE3W_all_numeric_constants_audit_2026-09-23.md
- Predchádzajúce časované videoaudity: E1M1–E1M2; E1M6/E2M1–E2M6; E2M5; E2M7–E2M10; E3M1/E3M2/E3M10; E3M4/E3M5; E3M6; E3M7–E3M9.

## Príloha: položky v knižnici vylúčené z rozsahu

- YTDown.com_YouTube_FRA909-Tv-KLAUDIA-GAWLAS-_-TIME-WARP-201_Media_1oietKsDSLg_002_720p.mp4
- Vrillion_1977_speech_enhanced.mp4
- Vrillion The Ashtar Galactic Command - The Southern Television broadcast interruption, 1977 UK..mp4
- Bl. Zdenka Schelingová - Relikvie - Milosrdné sestry sv. kríža.mp4
- Rally_Championship_2000_Soundtrack_1_RESTORED_MAX.mp4
- Rally Championship 2000 - Soundtrack #1.mp4

---

Tento dokument je výsledkový audit a implementačná mapa; videozdroje a statické dôkazy treba naďalej držať oddelene. Inventár CSV zachováva hashovanú stopu každého z 181 in-scope záznamov. Časový index zachováva konkrétne pozorovania a časy bez toho, aby z nich robil nepodložené tvrdenia o vnútornom kóde.