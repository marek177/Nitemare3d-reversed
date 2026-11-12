# Scaled sprite renderer: hranice, CFG a prefix clippingu

Funkcia **0156:05DE..07DD**, image **[1B3E,1D3D)**, má span511B, **510 inštrukčných B /201 inštrukcií**. Jeden bajt image1C1Bh (IP06BB) leží medzi unconditional JMP a jeho nasledujúcim blokom a z entry CFG sa nedekóduje; jeho účel sa nevyhlasuje za dokázaný padding. Reprodukovateľný CFG má211 branch/fallthrough hrán, všetky ciele smerujú na overené inštrukčné začiatky. Žiadne callee ani FAR/NEAR calls v tele.

Input je jeden NEAR slot pointer v SS:[BP+6]. Funkcia ukladá BP/SI/DI a neskôr DS, potom obnoví DS/SI/DI/BP a FAR RET bez vlastného odstraňovania argumentu. ES/AX/BX/CX/DX/flags nie sú zachované. Nevyžaduje sa ES=DS na vstupe. Prefix používa zdedený DS pre slot a resource; pri pixelovej slučke DS prejde na resource segment, SS naďalej sprístupňuje lokály a depth tabuľku. Prirodzená rovnosť pôvodného DS/SS zostáva osobitnou caller podmienkou pre SS depth prístupy.

## Polia a presné výpočty pred VGA

Slot+6 je NEAR resource pointer. Resource BYTE+0 je šírkový počet a BYTE+1 výškový počet; WORD+6 je počiatočný source offset a WORD+8 source segment. Slot WORD+8/+A sú X hranice, +C/+E sú Y hranice, +10 je depth hodnota. Slot+2 je FAR object pointer; objektový BYTE+5 bit10h sa používa ako depth-bypass príznak. Tieto lokálne roly neuzatvárajú všetkých producentov, formát resource súborov ani záznamovú životnosť.

Nech `(x1,x2,y1,y2)` sú slot hranice a `(L,R,T,B)` globály DS4548/454A/454C/454E. Všetky WORD operácie zachovávajú16-bit wrap; hraničné vetvy clippingu sú signed16. Prefix má tieto kroky:

```text
h0 = y2-y1+1
step16_16 = (resource_height << 16) / unsigned16(h0)
rows = h0; columns = x2-x1+2
source = resource_offset; source_fraction = 0
if y2 > B: rows += B-y2
if T > y1:
    y_start = T; rows -= T-y1
    advanceY = low32(step16_16*(T-y1))
    source += high16(advanceY)
    source_fraction = low16(advanceY)
if x2 >= R:
    columns = R-x1+1
else if L > x1:
    x_start = L; columns = x2-L+2
    stepXclip = (resource_height << 16) / unsigned16(rows)
    advanceX = low32(stepXclip*(L-x1))
    source += resource_height*high16(advanceX)
    available_source_columns -= high16(advanceX)
    horizontal_fraction = low16(advanceX)
```

Zásadné sú **pravý orez pred ľavým cez else-if**, dva rozdielne X počty `+2`/`+1` a prepočet ľavého posunu z **už orezaného rows**, hoci základný pixelový step zostáva odvodený z pôvodného h0. Funkcia v tomto prefixe nemá univerzálny early-return pre prázdny obdĺžnik. Nezamieňať s ideálnym clipping algoritmom; pseudokód zachytáva originálne vetvy.

## Hraničný divide fault

Dosadený slot `(10,11,10,11)` a clip `(12,18,12,18)` dávajú po top orezaní rows0. Keďže x2<R a L>x1, vykoná sa unsigned DIV ECX na **0156:06EA** s ECX0. Native replay potvrdil **36 očakávaných CPU divide výnimiek** (2load×3width×3height×2objectflag). Ide o vlastnosť dosadeného vstupu; **nie dôkaz prirodzenej chyby v hre**. Caller môže také sloty odfiltrovať, jeho úplná doména ešte nie je uzavretá. Pôvodný DOS INT0 handler sa v tejto prefix skúške nevykonáva.

## Zvyšok funkcie: staticky potvrdené, zatiaľ bez pixel replay

Po0738 nastaví ES zo stránky DS012E, vypočíta video offset cez lowBYTE(y)*80 + unsigned16(x)>>2, zapíše sequencer index2 na3C4h a rotujúcu masku11h na3C5h. DS potom načíta zo source segmentu. Pri object bit10h=0 porovnáva unsigned WORD zo SS depth tabuľky `47E4+2*x` s depth parametrom; vyššia hodnota preskočí stĺpec. Bit10h test obíde. Pixel BYTE1Fh je transparentný; ostatné sa zapisujú ES:[DI], DI+=80. Fixed-point source posun používa ADD/ADC a ďalší stĺpec aktualizuje map mask/offset. Presné VGA plane správanie, nulové/negatívne počty LOOP a vyrovnanie ešte vyžadujú samostatnú skúšku.

## Reprodukcia, výsledky a pokrytie

`audit_replay_sprite_clip_prefix.py IMAGE INVENTORY ABS_DECODER ABS_EMULATOR OUT` overuje obraz a nezávislé dekódovanie všetkých CFG inštrukcií proti existujúcemu inventáru. Dve load bázy používajú1670 reálnych relokácií. Spúšťa648 scenárov (2load×3width×3height×6rect×3clip×2objectflag): **612 dôjde presne na0738 pred VGA,36 skončí očakávanou výnimkou na06EA,0 neočakávaných odchýlok**. Kontroluje20 lokálnych WORD hodnôt, object flag a DS proti samostatnému výpočtovému modelu. Prefix dosiahol131 rôznych inštrukčných začiatkov; všetkých201 statických inštrukcií sa tým nevyhlasuje za vykonaných. `cases.csv`, `cfg_edges.csv`, `prefix_visited_starts.csv`, `sprite_scaled_clip.csv` a summary uchovávajú reprodukciu.

SHA cases `2baf291bc866279cdac38f8605ca7c0705a8e4d56fea156a722fe740efa8a2db`. Pribúda1 PARTIAL funkčný rozsah/201inštrukcií/510B a648 seeded scenárov. PASS1 nemení57102PARTIAL/149CLASSIFIED ONLY/44UNKNOWN/0DEEP VERIFIED. Prirodzené runtime zostáva3scenáre. Žiadna Win16 parity ani nová GitHub publikácia v tejto dávke.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|skutočný BSF54 B load/decode|iné BSF/role blokov|resource sloty v runtime|
| Dátové typy a konštanty |95 %|N/A|511 runtime DWORD mimo file|149 B iba klasifikované, 44 B UNKNOWN|nepriame segmentové prístupy|
| Tabuľky a ukazovatele |93 %|N/A|12 lokálnych FAR konštrukcií 21FD:264E odlíšených od DS:264E|aliasy/dynamické indexy|watchpointy na 44 UNKNOWN B|
| Funkcie / ASM / CFG |90 %|N/A|renderer201inštrukcií/CFG211hrán; prefix648scenárov|zvyšok pixelovej slučky|port/pixel replay|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|clock init prebehol medzi bodmi|main loop/scheduler|loop vstup|
| DEMO a vstupy |96 %|N/A|bez input/demo runtime|driver a demo|prirodzené demo|
| Renderer / VGA |94 %|N/A|clipping precedence a36 očakávaných divide faultov|caller validácia a VGA výstup|clipping caller domény|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|VGA init, nie vizuálna parita|paleta/sprity|resource load|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|bez Win runtime|NE prostredie|samostatný Win16 test|

## Runtime testy na vykonanie

Overiť prirodzené sloty a všetkých štyroch clip globálov pri vstupe0156:05DE. Zaznamenať doménu h0/rows pred oboma DIV a caller filtrovanie prázdnych rozsahov. Samostatne overiť pixel loop cez VGA plane model, transparentnosť1Fh, depth unsigned porovnanie a bypass bit10h. Potom prirodzený DOSBox screenshot/video-memory záznam; seeded výpočtový prefix nie je renderer parity.
