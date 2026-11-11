# INT63 — lookup okno nie je jedna servisná tabuľka

11. 11. 2026. Nová nezávislá statická kontrola nad obrazom SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. **PARTIAL**, DEEP VERIFIED +0 B, runtime testy 0. Historické tvrdenia PASS318–321 sú tu overované proti dostupnému obrazu, nie preberané ako dôkaz.

## Dispatcher

Rozsah obrazu `[18CD6,18D19)`, teda CS `15BF`, IP `30E6–3129`, má 67 B a 36 nezávisle dekódovaných inštrukcií. Končí IRET na 18D18. Dekódovanie za IRET sa nezapočítava do funkcie.

```text
increment nesting_word CS:3ED4
save AX,BX,CX,DX,BP,DI,SI,DS,ES
DS = CS
DF = 0                     // CLD at 18CE6
ES = incoming_DX
SI = 2 * unsigned(incoming_AH)
near_call CS:[SI+2020]
CS:30E2 = AX; CS:30E4 = DX
restore ES,DS,SI,DI,BP,DX,CX,BX,AX
decrement nesting_word
AX = CS:30E2; DX = CS:30E4
IRET
```

Adresný výpočet AH→SI je potvrdený presnými bajtmi, nie iba textom dekódera. V tomto lokálnom dispatcheri nie je kontrola horného limitu selektora ani kontrola hodnoty slotu pred CALL. Globálne obmedzenia volajúcich ešte nie sú uzavreté.

## Presné dátové hranice

| Oblasť | CS offset, end-exclusive | Image rozsah | Význam |
|---|---|---|---|
| Kandidátske pôvodné servisné položky | 2020–20C4 | 17C10–17CB4 | 82 little-endian near-offset slov, 164 B |
| Susedné počítadlo | 20C4–20C6 | 17CB4–17CB6 | word používaný inými rutinnými zápismi |
| Uložený výsledok AX/DX | 30E2–30E6 | 18CD2–18CD6 | dve word scratch hodnoty dispatchera |
| Hĺbka vstupov | 3ED4–3ED6 | 19AC4–19AC6 | word inkrementovaný/dekrementovaný dispatcherom |
| Celé adresovateľné lookup okno | 2020–2220 | 17C10–17E10 | 256 možných slov, 512 B; zmiešaný obsah |

82 položiek je lokálna kandidátska inicializovaná oblasť, nie dôkaz kapacity verejného API. Hranicu podopiera aj doložené použitie nasledujúceho slova ako počítadla. Celé 512-bajtové okno sa nesmie klasifikovať ako 256-entry service table.

Skript vypísal všetkých 256 počiatočných slov aj ich efektívne NEAR CALL ciele. Sú to hodnoty pôvodného obrazu; runtime zápisy ich môžu meniť.

## Selektory zasahujúce susedný obsah

- AH=52h číta ako offset slovo **CS:20C4**, známe počítadlo.
- AH=D4h/D5h číta slová **CS:21C8/21CA**, ktoré na potvrdenej registračnej ceste tvoria offset/segment FAR callbacku.
- AH=FCh číta **CS:2218 = image 17E08**, čo je začiatok už analyzovaného kódu callback_locate. Tieto bajty by interpretoval ako NEAR offset.

Toto sú potvrdené adresné aliasy, nie dôkaz, že hra uvedené selektory volá. Na ich základe nemožno označiť celý lookup rozsah za dáta ani tvrdiť hernú chybu.

Počiatočné nulové slová medzi kandidátskymi slotmi sú AH=00h,27h,28h. **Near offset 0000 nie je automaticky neplatný/null ukazovateľ**: inštrukcia CALL by smerovala na CS:0000, v tomto priestore image 15BF0. Význam a dosiahnuteľnosť tohto cieľa zostávajú otvorené. Nulové hodnoty samy osebe nedokazujú neprítomnosť servisnej funkcie.

## DF kontrakt služby 49h

Slot 49h obsahuje 2349h a smeruje na image 17F39. Presné bajty na tomto vstupe sú `BB 00 00 E8 7B 0E`, čiže BX=0 a priamy NEAR CALL na image 18DBA / 15BF:31CA. Dispatcher vykonáva CLD pred servisným CALL; po ceste k úvodnej normalizácii ES:DI v 31CA nie je medzi tým žiadny externý callback.

Pre túto konkrétnu staticky doloženú vstupnú cestu preto platí DF=0 pri prípadnej konverzii counted string v 2E56. To spresňuje predchádzajúcu všeobecnú požiadavku DF=0; nevylučuje priame volanie helpera inou cestou s iným DF ani neskoršie zmeny FLAGS vo volaných funkciách.

IRET obnovuje uložené FLAGS, teda nemožno zamieňať interné CLD/CF s konečnými príznakmi volajúceho. Obsluha tu priamo nemení interrupt FLAGS frame. Úplné vylúčenie nepriamych zápisov do rámca vyžaduje audit servisov a callbackov.

## Reprodukcia a stav katalógu

`audit_int63_window.py DECODER_DIR IMAGE OUT_DIR` vytvára `int63/dispatcher_instructions.csv`, `int63/lookup_window.csv`, `int63/int63_evidence.json`. Bol vykonaný; kontroluje SHA obrazu, kritické opcodes a cieľ služby49. Používa iced-x86 1.21.0, 16-bit.

Po prepočítaní `independent_decode_and_catalog.py` má aktuálna kampaň 9 funkčných rozsahov, **304 inštrukcií / 684 B kódu**, **214 B lokálnych dát**, 170 462 B neposúdených a 38 intervalov. Je to pracovná partition celých 171 360 B, nie originál PASS320. Všetko lokálne posúdené zostáva PARTIAL; žiadne nové DEEP VERIFIED.

Aktualizovaná tabuľka všetkých 13 oblastí, historické odhady, metodika, blokátory a ďalšie kroky sú v `CAMPAIGN_CATALOG_REPORT.md`. Nové percentá všetkých oblastí zostávajú N/A: nie je uzavretý menovateľ ani prienik s historickými 57 295 NON-CODE bajtmi. Táto dávka pridáva dôkazy oblastiam dátových typov, tabuliek a funkcií; ostatných desať oblastí nedostáva nové behaviorálne tvrdenia.

## Runtime overenie

1. Logovať AH každého skutočného INT63 volania a efektívne CS:IP ciele. Absencia vysokých selektorov v jednej stope nie je dôkaz globálneho limitu.
2. Zachytiť DF pri vstupe do 31CA a 2E56 na skutočnej ceste service49; osobitne evidovať prípadné priame volania mimo dispatchera.
3. Watchpointy na 20C4,21C8/21CA a interrupt FLAGS frame; sledovať producentov a reentranciu scratch výsledkov 30E2/30E4.
4. Selektory52/D4/D5/FC nevolať ako bežný herný test bez samostatného označenia fault injection. Ich adresový výpočet už je staticky doložený, dosiahnuteľnosť nie.
