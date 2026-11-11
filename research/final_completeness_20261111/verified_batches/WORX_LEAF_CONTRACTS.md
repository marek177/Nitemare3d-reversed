# WORX — kontrakty normalizácie ukazovateľa a zmeny názvu

11. 11. 2026. Nová statická dávka nad obrazom SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Stav **PARTIAL**; DEEP VERIFIED +0 B, runtime testy 0. Príslušnosť k NON-CODE mape PASS320 zostáva UNKNOWN, pretože pôvodný ledger chýba.

## Reprodukcia a presný rozsah dôkazu

`audit_worx_leafs.py IMAGE INSTRUCTIONS_JSON OUT_DIR` bol úspešne vykonaný. Overuje identitu obrazu, hranice a zakódované bajty historických ASM záznamov. SHA inventára je zaznamenaný v `worx_leafs/leaf_evidence.json`. Ide o kontrolu staršieho dekódovania proti bajtom; nový nezávislý disassembler ani emulátor sa v tejto dávke nepoužil.

| Funkcia | Rozsah obrazu, koniec exclusive | Rozsah CS:IP | Bajty inštrukcií | Inštrukcie |
|---|---|---|---:|---:|
| normalize_es_di | 0x1A220–0x1A25A | 15BF:4630–466A | 58 | 30 |
| uppercase_asciiz_in_place | 0x1A49F–0x1A4C9 | 15BF:48AF–48D9 | 41 | 32 |

Druhý rozsah obsahuje ešte bajt `90` na 0x1A4AE, ktorý starší inventár neuvádza. Predchádza mu nepodmienený JMP a nasleduje vetva slučky. Kandidát NOP/paddingu zostáva UNKNOWN do globálneho auditu xrefs. Celkové rozsahy majú 100 B; bajtovo porovnané inštrukcie majú 99 B. Rozdiel sa nesmie zatajiť ani započítať ako ďalší overený kód.

## 15BF:4630 — normalizácia ES:DI

Vstupy: ES, DI. Ak ES=0, funkcia sa vracia bez zmeny oboch registrov. Inak vytvorí rozšírenú adresu `ES*16+DI` pomocou SHL/RCL, ponechá dolný nibble ako nový offset a pravými SHR/RCR vypočíta nový segment.

```text
if ES != 0:
    new_DI = DI & 0x000F
    new_ES = (ES + (DI >> 4)) & 0xFFFF
else:
    new_ES = ES
    new_DI = DI
```

Pri nenulovom ES zostáva lineárna adresa zhodná modulo 2^20. Ak súčet presiahne 0xFFFFF, nezachováva neobmedzenú lineárnu adresu nad 1 MiB. Interpretácia na konkrétnom stroji vyžaduje A20 a pamäťový kontext. Pri ES=0 môže DI zostať väčšie než 15; tento špeciálny prípad je dôležitý pre nulovo-segmentové ukazovatele.

AX a DX sa ukladajú na zásobník a obnovujú. BX, CX, SI, BP, DS a SS sa v tele nemenia. ES/DI sú výstupy, FLAGS nie sú zachované; DF sa nemení. Nie sú tu volania ani dátové zápisy mimo zásobníka. Lokálny stack je vyvážený pri bežnom NEAR CALL/RET; predpokladom je platný zásobník a normálne dokončenie inštrukcií.

Skript porovnal shift/carry algoritmus so zjednodušeným výrazom na 30 hraničných príkladoch. To sú syntetické aritmetické kontroly, nie 30 behov originálneho kódu a nie vyčerpávajúci test všetkých 2^32 vstupov. Všeobecný vzťah vyššie vyplýva z bitových operácií.

## 15BF:48AF — ASCII uppercase in place

Vstup: ES:DI ukazuje na reťazec ukončený nulou. Funkcia uloží AX,BX,CX,DX,BP,DI,SI,DS,ES, nastaví DS=ES a SI=DI. Načítava LODSB, ukončí sa na NUL a zmení len znaky v rozsahu 0x61–0x7A na 0x41–0x5A. Používa unsigned porovnanie po odčítaní 0x61, preto nejde o všeobecnú locale/codepage konverziu.

Pre **DF=0** zodpovedá telo:

```text
p = ES:DI
while *p != 0:
    if 'a' <= *p <= 'z':
        *p = *p - 0x20
    p = offset16(p + 1)
```

Kľúčový vedľajší účinok: zdrojový názov sa mení v pôvodnej pamäti; nevzniká kópia. Všetky explicitne uložené registre sa obnovia. FLAGS sa neukladajú; posledné AND AL,AL pracuje s nulovým terminátorom. Funkcia neobsahuje CLD ani hornú hranicu dĺžky reťazca.

DF je súčasťou kontraktu, nie nepodstatný detail. Pri DF=1 LODSB dekrementuje SI, ale zápis stále používa `[SI-1]`, takže pre konvertovaný znak smeruje dva bajty pred jeho načítanú polohu. Toto je statický dôsledok adresovania, nie potvrdenie, že hra volá funkciu s DF=1. Pri chýbajúcom terminátore môže offset pretekať; rozsah platnej zapisovateľnej pamäte treba dokázať u volajúceho.

## Doplnenie predchádzajúceho helpera 15BF:31CA

V `WORX_HELPER_BATCH_REPORT.md` boli kontrakty oboch helperov otvorené:

- `opaque_helper_4630()` možno spresniť na `normalize_ES_DI()`. Helper nemení BX, takže nemení následné rozhodnutie podľa BX v 31CA. Môže meniť ES:DI, pričom zachováva adresu modulo 1 MiB pre nenulový segment.
- `opaque_helper_48AF()` možno spresniť na `uppercase_ES_DI_in_place_assuming_DF0()`. Volanie je pred prehľadávaním záznamov, preto názov porovnávaný s buffer+12 môže byť už prepísaný na veľké ASCII písmená.
- Helper 2E56, režimové globály, životnosť názvu a predpoklad DF=0 ešte nie sú uzavreté. Nález nezvyšuje historické percentá ani nemení záver o otvorenej chybovej vetve seek.

## Runtime testy

1. Pri volaní 48AF zaznamenať FLAGS.DF a presné bajty názvu pred/po; overiť, či pamäť patrí zapisovateľnému bufferu a kde je NUL.
2. Pri 4630 zaznamenať ES:DI pred/po a stav A20; hraničný prípad nad 1 MiB testovať oddelene od bežného herného vstupu.
3. DF=1 testovať iba ako označený fault-injection scenár; nevydávať ho za prirodzene dosiahnutú chybu hry.

## Aktualizácia 13 oblastí

Nové percento je vo všetkých riadkoch **N/A**. Metodika: počet sémanticky uzavretých jednotiek / úplný autentifikovaný inventár jednotiek danej oblasti. Menovatele zatiaľ nie sú uzavreté. Bajtová integrita, syntetický model a runtime zhoda sa vykazujú osobitne.

| Oblasť | Historicky | Nové zistenie / stav | Neznáme alebo blokátor | Najbližší krok |
|---|---:|---|---|---|
| Mapy/formáty | 99 % | žiadne nové | inventár polí | dátoví konzumenti |
| Typy/konštanty | 95 % | ASCII rozsahy a in-place názov, PARTIAL | vlastník a životnosť bufferu | ES:DI producenti |
| Tabuľky/ukazovatele | 93 % | normalizácia ES:DI, PARTIAL | A20 a volajúce kontexty | globálne xrefs |
| Funkcie/ASM/CFG | 90 % | 2 lokálne kontrakty, 99 B inštrukcií, PARTIAL | úplné hranice a nezávislé dekódovanie | helper 2E56 |
| RNG | 97 % | žiadne nové | caller ledger | spotreba RNG |
| Scheduler | 96 % | žiadne nové | poradie tickov | dispatcher CFG |
| DEMO/vstupy | 96 % | žiadne nové | runtime determinizmus | párové prehratie |
| Renderer/VGA | 94 % | žiadne nové | clipping a VGA stav | framebuffer/DAC |
| GUARD/bossovia | 93 % | žiadne nové | dosiahnuteľnosť prechodov | stavový graf |
| Zbrane/projektily | 92 % | žiadne nové | kolízie a sloty | collision trace |
| Sprity/HUD/paleta | 92 % | žiadne nové | resource binding | draw xrefs |
| SAVE/LOAD | 92 % | žiadne nové | cache po LOAD | serializačné kontrakty |
| Win16 | 92 % | žiadne nové | NE fixupy | hash a segmenty |

Pôvodné 57 295 NON-CODE bajty nemožno zatiaľ priradiť k týmto rozsahom. Táto dávka uzatvára časť závislostí analýzy WORX; nenahrádza požadovaný audit celej NON-CODE mapy.
