# Nitemare 3D Win 1.10 — Ghidra 12.2, prechod 6

## Zistenie

Tento prechod uzatvára konkrétne statické výrezy pre VGA DAC, GDI paletu, page flip a paletový záblesk so zvukovou väzbou. Doplnil som tri ohraničené frameworkové switche, definíciu už overenej formátovacej tabuľky a deväť doložených class stringov. Neklasifikovaných zostáva **1 945 bajtov** kódových segmentov. Počet interných funkčných vstupov sa nemení: **1 535**.

Hra nebola spustená. Modelové kontroly sú statické, nie dôkaz pixelovej, časovej alebo zvukovej runtime parity.

## Identita

EXE: 230 400 B, SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; Windows NE. Ghidra 12.2 build 20261016, Java 25.0.2, headless projekt `WIN110`. Kódové NE segmenty 1–4 sú `1000/1008/1010/1018`, inicializovaný DS segment 10 je `1048`. Závery nie sú automaticky prenosné na DOS alebo Win16 1.8.

## 1. Dve paletové cesty

`1010:3AF4` testuje byte `DS:46B0`. Pri nenulovej hodnote volá `3ACC` (DAC); pri nule `31AA` (GDI). Odovzdáva dva wordy: near DS pointer na RGB dáta a mode. To, že sú prenesené jedným `PUSH DWORD`, **neznamená far pointer**.

| Status | Tvrdenie | Dôkaz | Istota |
|---|---|---|---|
| Confirmed | `3ACC` nastaví DAC write index 0 a zapíše 768 komponentov. | `3AD0–3AEF`: OUT `3C8h,0`, CX=300h, čítanie DS:SI, SHR AL,2, OUT `3C9h`, INC SI. | High |
| Confirmed | Každý komponent je `floor(byte/4)`, výstup 0–63. | Raw SHR2 a vyčerpávajúci model všetkých 256 vstupov. | High |
| Confirmed | `3B16` najprv aktualizuje master RGB na `5B7E + 3*byte(index)`. | `3B19–3B35`. Index aj komponenty sa čítajú ako bajty z wordových argumentov. | High |
| Confirmed | Jednopoložkový priamy update opäť používa komponenty >>2. | `3B58–3B78`: DAC index, tri posuny a OUT. | High |
| Confirmed | Okenný update ide cez `3360` a zachováva RGB8 do BGR0 tabuľky. | `3B39–3B54`; `3360` uloží R na `4D9C+4*i`, G na `4D9B+4*i`, B na `4D9A+4*i`, štvrtý bajt 0; import Ordinal1006 aktualizuje jednu položku. | High |

DAC write helper nečaká na retrace. Číta 768 near DS bajtov s 16-bitovým SI; model reprezentuje bežný neprerušovaný 768-bajtový vstup. Zdrojové RGB8 a fyzický výstup DAC6 sa nesmú považovať za totožné dátové formáty. Skutočný prevod DAC6 na zachytené RGB8, monitor/gamma a OS paletové správanie sa tu neuzatvárajú.

### GDI `1010:31AA`

Pri mode 0 zostaví LOGPALETTE s version `0300h` a count 256 (`31BC` ukladá dword `01000300h`). Získa systémové entries a nuluje ich flags. Následne prepíše RGB8 zo source:

- `reserve = 10`, ak `byte46AF != 0`, inak `reserve = 0`.
- Prepíše indexy `[reserve, 256-reserve)` a nastaví ich flags na 1.
- Vytvorí a realizuje paletu; do DIB tabuľky `4D9A` zapíše 256 položiek B,G,R,0.

Pri mode 2 vždy vytvorí **236 entries pre indexy 10–245**. Pri nenulovom handle `00BE` volá `ANIMATEPALETTE(start=10,count=236)`. Ak `46AF==0`, nasleduje `3100`. Na tejto ceste nemožno z lokálneho kódu tvrdiť, aké farby nakoniec vyberie Windows ovládač.

`3360` animuje jedinú položku iba pri `00BE != 0 && 46AF != 0`, ale BGR0 tabuľku a DIB update vykoná aj bez tejto podmienky.

`win110_palette_model.py` zachováva oddelene DAC port trace, GDI entry payload a DIB BGR0 payload. Kontroly pokrývajú 256 komponentov, tri RGB fixtures, 768 jednotlivých entry prípadov a šesť kombinácií inicializácie GDI. Model je dátová špecifikácia, nie emulácia Windows ovládača.

## 2. Page flip a status polling

Pôvodný dátový segment inicializuje word `00C0=A000h`, `00C2=A400h`. `1010:3A7A` v priamej vetve robí:

1. Prehodí `00C0` a `00C2`.
2. Číta port `3DAh`, kým bit 01h nie je 0.
3. Vykoná CLI.
4. Zapíše word do portu `3D4h`: AL=0Ch, AH=`(high_byte(new00C0)<<4)&FFh`.
5. Vykoná STI.
6. Číta `3DAh`, kým bit 08h nie je 1.

Pre štandardné dve inicializačné hodnoty sa striedajú word zápisy **`400Ch` a `000Ch`**, teda CRTC high-address dáta 40h/00h pri indexe 0Ch. Tým je priamo podopretá väzba na capture funkciu z prechodu 5: jej page base je 0 pre `00C0=A000h`, inak 4000h.

Pri `46B0==0` táto funkcia namiesto výmeny a portov zavolá `3080` a vráti sa. Známe CLI/STI poradie je statický fakt; správanie privilegovaných inštrukcií v konkrétnom Windows prostredí vyžaduje runtime.

Samostatný helper **`1010:3AC2` čaká na úroveň**, nie na novú hranu: `IN 3DAh; TEST AL,8; JZ loop`. Ak je bit už 1, skončí po prvom čítaní. Nie je tu timeout ani predchádzajúce čakanie na vyčistenie bitu. Z jedného volania preto nevyplýva jeden nový snímok.

Model overil 100 štandardných page swaps, všetkých 256 high-byte vstupov CRTC aritmetiky a štyri status trace fixtures. Nemeria FPS ani dĺžku retrace.

## 3. Paletový efekt `1010:BA74`

### Potvrdený model

| Podmienka/operácia | Primárne miesto |
|---|---|
| Epizóda 2 sa preskočí; epizóda 3 sa preskočí pri signed16(level_index+1) < 10. | `BA77–BA8F` |
| Inicializácia: phase byte `38F0=0`, countdown word `38EE=80`. | `BA99–BAA3` |
| Prejde 256 bajtov tabuľky `8094`; hodnoty DAh prepíše na DBh. | `BAA4–BAB7` |
| Potom nastaví `DS:816E=DAh`. **816E = 8094 + DA**, teda ide o `table[DA]=DA`, nie inú premennú. | `BABE–BAC0`, overená adresová aritmetika |
| Inicializácia nastaví palette entry DA na čiernu. | `BAB9–BB1F` argumentová cesta do `3B16` |
| Update najprv uloží countdown-1, ale vetví podľa pôvodnej hodnoty. | `BAC6–BACF` |
| Ak pôvodný countdown bol 0 a phase=0: phase=1, countdown=3, RGB DA=255/255/255. | `BB08–BB1F` |
| Ak pôvodný countdown bol 0 a phase!=0: phase=0, RNG `%240+160`, RGB DA=0/0/0, potom zvuk. | `BAD8–BB07` |
| Zvuková cesta `ACEE` odovzdá wordy `66,0,2` do `E3B0`. | Raw PUSH dword 00020000h, PUSH word 0042h, CALL E3B0 |

Pri preskočenej epizóde/úrovni sa nevykoná ani inicializačný remap či zmena palety. Pri normálnom countdown update sa word wrapne modulo 65536; na pôvodnej nule sa teda krátko uloží FFFFh, potom ho branch prepíše novou hodnotou.

Implementačne podopreté intervaly v **počte volaní**, nie sekundách:

- Po inicializačnej hodnote 80 príde biela fáza až pri **81. update**.
- Biela hodnota 3 znamená návrat do čiernej pri **4. update**.
- Nová čierna hodnota je 160–399, teda ďalšia biela nastane po **161–400 update volaniach**.
- Jeden RNG výsledok sa odoberá pri návrate do čiernej, pred čiernym palette write a pred zvukom.

Python model overuje 32 768 možných 15-bitových RNG výsledkov, sekvenciu 81/4 volaní, epizódové guardy a alias tabuľky. Test s identity mapou zostáva po inicializácii identity; test s celou tabuľkou plnou DA skončí s DB všade okrem `table[DA]=DA`. Tým sa zachováva aj druhý zápis na prekrývajúcu sa adresu.

Zvukový **slot 66 a argumenty 0/2** sú potvrdené. Presná zvuková vzorka, vizuálny asset, názov efektu typu „blesk/hrom“ a fyzické trvanie zostávajú Inferred/Unknown. DOS indexy alebo timing sa na tento Win16 model nepreberajú.

## 4. Ďalšia klasifikácia kódu a dát

Obnovil som explicitné ciele troch existujúcich switchov:

| Owner | Branch/table | Wordy | Podopretý guard |
|---|---|---:|---|
| `1000:D32E` | `D35B/D360` | 8 | priamy index 0–7 |
| `1000:6F5C` | `6F90/6F95` | 20 | normalizácia vstupu, shift >>3, **byte offset** <=26h; preto 20 wordov, nie 39 |
| `1008:18B4` | `1918/191D` | 13 | word hodnota-1 v rozsahu 0–12 |

Pri `6F5C` sú dosiahnuteľné iba párne byte offsety 0,2,…,26h; pôvodné vstupné hodnoty po maskovaní patria k F000h–F130h. Presné UI úlohy všetkých branchov sa týmto neuzatvárajú. Dátovo som označil aj skôr overených osem wordov `1008:4E14` a deväť class stringov s nulovým terminátorom (66 B). Žiadny nový funkčný vstup sa v tomto prechode nepridával.

## Pokrytie

| Metrika | Pred prechodom 6 | Po prechode 6 |
|---|---:|---:|
| Interné funkčné vstupy | 1 535 | 1 535 |
| Dokončené interné dekompilácie | 1 535 | 1 535 |
| EXTERNAL položky | 310 | 310 |
| Inštrukčné bajty | 159 467 | 159 674 |
| Definované dáta v code segmentoch | 7 905 | 8 069 |
| Neklasifikované bajty | 2 316 | 1 945 |

Pribudlo 207 B inštrukcií a 164 B dát: 98 B tabuliek + 66 B stringov. Tento pokles je klasifikácia bajtov, nie percento dokončenej hry.

## Reprodukcia a otvorené dôkazy

- `win110_palette_model.py`: raw anchor checks, DAC/GDI/BGR0 a page/status modely.
- `win110_palette_flash_model.py`: raw guardy, countdown/RNG/event model a table alias.
- `verify_remaining_switches.py`: raw tabuľkové wordy a guardy; 16-bitová aritmetika; count a dĺžky nových stringov.
- Ghidra skripty `N3DRecoverRemainingSwitches.java`, `N3DDefineClassStrings.java`, explicitné anotácie a nový C/listing/reference export.

Ďalší runtime dôkaz musí zachytiť DAC port trace a RGB source pred/po flash update, GDI systémové farby a návratové hodnoty, stav read-map/DAC/CRTC pri prepnutí strán a skutočný počet update volaní za čas. Pre flash treba spárovať slot 66 so SND dátami a konkrétnym assetom. Kompletné framebuffer a DAC porovnanie stále nie je vykonané.

**Istota:** High pre uvedené lokálne bajty, poradie, formáty a alias; Medium pre širšiu UI/GDI interpretáciu; Unknown pre runtime timing, asset identitu a 1:1 paritu.
