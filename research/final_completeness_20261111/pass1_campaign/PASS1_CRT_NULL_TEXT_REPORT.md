# DOS 2.0: counted `(null)` a near/FAR argumentové helpery

## Presné dátové hranice

Na **DS:2323**, obraz **[29A33,29A39)**, je presne šesť ASCII bajtov `(null)`. Nie je za nimi NUL terminátor: bezprostredne nasleduje WORD **DS:2329, [29A39,29A3B)** s hodnotou **6** (`06 00`). Typovať prvých sedem bajtov ako NUL reťazec by bolo nesprávne. Tieto dve polia, spolu 8 B, majú konkrétneho spotrebiteľa 11EE:17EC/17EF a samostatné SHA v `data_fields.csv`.

V string vetve formátovača 11EE:17DD..180B sa najprv získa pointer cez 1A67. Ak DI != 0, pokračuje sa bežným scanom. Ak DI == 0, testuje sa aj ES. Fallback nastáva **iba pre ES:DI = 0000:0000**: ES sa nastaví na DS, DI na 2323h, CX sa načíta zo statického WORDu 2329h a skočí sa na spoločný bod 19C8. Nie je potrebný strlen scan fallbacku.

Pri nenulovom pointeri sa cez REPNE SCASB hľadá NUL najviac podľa pôvodného limitu SS:[BP-0Ch]; pri nulovom limite sa scan nevykoná. Výsledkom pri vstupe do 19C8 je pôvodný pointer a zistený počet BYTE bez terminátora. Fallback do tohto bodu posiela CX=6 nezávisle od limitu. To je lokálny výsledok pred spoločným výstupom/paddingom, nie tvrdenie o kompletnom konečnom správaní formátovača.

## Tri presné NEAR helpery

| Vstup | Interval obrazu, koniec exclusive | B | Inštrukcie | Lokálna rola pri DF=0 |
|---|---|---:|---:|---|
| 11EE:1A53 | [13933,1393B) | 8 | 4 | načíta WORD do AX, posunie cursor o 2 |
| 11EE:1A5B | [1393B,13947) | 12 | 7 | načíta DWORD do DX:AX, posunie cursor o 4 |
| 11EE:1A67 | [13947,13964) | 29 | 15 | vyberie near/FAR string pointer podľa flagu 20h |

Všetky končia NEAR RET a používajú zdedený BP rámec, nie vlastný štandardný prolog. Cursor je near WORD uložený na SS:[BP+0Ah]; LODSW číta samotné argumenty cez DS:SI. Helpery zapisujú nový cursor späť do SS rámca a menia SI. DF nie je lokálne nastavovaný: posuny +2/+4 platia pri DF=0; s DF=1 by LODSW postupoval opačne. Úplný runtime ABI okolitého formátovača zostáva otvorený.

```text
fetch_word():
    SI = WORD SS:[BP+0Ah]
    AX = WORD DS:[SI]
    SI += 2                       # podmienka DF=0
    WORD SS:[BP+0Ah] = SI
    return near

fetch_dword():
    analogicky dve LODSW; DX:AX = high:low; cursor += 4

fetch_string_pointer():
    if BYTE SS:[BP-4] & 20h:
        fetch_dword()
        ES = DX; DI = AX
    else:
        fetch_word()
        DI = AX
        ES = AX == 0 ? 0 : DS
    return near
```

Near offset 0 sa teda osobitne prevedie na nulový ES:DI. Pri FAR argumente sa pointer netestuje ani nenormalizuje v helperi: ES=0/DI!=0 a ES!=0/DI=0 zostávajú nenulové. Získanie pointera samo nekontroluje jeho platnosť, segmentové hranice ani dostupnosť textu.

## Controlled replay a reprodukcia

`audit_replay_pass1_crt_null_text.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` overí SHA obrazu, všetky tri helpery a string vetvu proti pôvodným bajtom a nezávislému dekóderu. Vykoná 6 pointerových variantov × 5 limitov (0,1,3,6,FFFFh) × 2 load bázy, spolu **60 prípadov, 0 odchýlok**.

Používa sa pôvodná string vetva aj jej pôvodné NEAR helpery, bez mock callees. Nenulové pointery dostanú seedovaný text `ABCDE\0`; DF=0 a DS/SS/BP/cursor sú seedované. Overuje sa ES:DI, CX, nový cursor a vyváženie lokálnych PUSH/POP pri zastavení pred 19C8. Nevykonáva sa zvyšok formátovača ani výstup textu. Prípady s nulovým segmentom a nenulovým offsetom či naopak sa testujú ako reálnomódové adresové kombinácie, nie ako dôkaz prirodzených herných argumentov.

Výstupy `pass1_crt_null_text/`: `crt_fetch_word.csv`, `crt_fetch_dword.csv`, `crt_fetch_string_pointer.csv`, `string_branch.csv`, `data_fields.csv`, `cases.csv`, `summary.json`; ďalej nová CSV/JSON mapa, promotion summary a nezávislá partition kontrola.

## Pokrytie

8 B prešlo z CLASSIFIED ONLY do PARTIAL. Nová mapa: **54 843 B PARTIAL, 2 408 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Nezávisle overených je 664 intervalov, SHA a presné členstvo bez dier či prekryvov.

Centrálny katalóg po pridaní troch celých NEAR helperov: **51 funkčných rozsahov, 1 717 inštrukcií / 4 077 B kódu**. String vetva sa nepridáva ako celá funkcia. Typované dáta celého obrazu sú 55 689 B, z historického NON-CODE 54 841 B; 2 PARTIAL relokačné B zostávajú bez uzavretej roly. Prijaté controlled replay prípady: 12 065 plus samostatne 65 548 normalizačných prefixových prípadov. Prirodzené runtime testy 0.

Nové polia, helpery aj celý formátovač zostávajú PARTIAL; exhaustívny alebo riadený lokálny test neuzatvára ich prirodzené prostredie. Najnovšia overená GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto novú dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového sémantického percenta: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto nové percentá zostávajú N/A a predošlé hodnoty sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | prirodzené stavy | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 6 B counted text + WORD length | ďalší susedný stav | jeho spotrebitelia |
| Tabuľky a ukazovatele | 93 % | N/A | near/FAR null rozlíšenie | pointer lifetime/bounds | prirodzené argumenty |
| Funkcie / ASM / CFG | 90 % | N/A | tri celé NEAR helpery, 60 prípadov | plný output handler | pokračovať od 19C8 |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | prirodzené poradie | tick stopy |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | render stopa |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | AI/lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | string pointer a limit kontrakt | finálny výstup | padding/output |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | parity | serializačné stopy |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | CRT ABI parity | Win fetch helpery |

## Runtime testy na vykonanie

Pri prirodzenom formátovacom volaní zachytiť BP rámec, DS/SS, DF, near/FAR flag a varargs cursor. Overiť, či sa nulové stringy vôbec objavujú v hre; oddelene zachytiť stav na 19C8 a skutočný výsledný výstup s limitom/paddingom. Syntetické neplatné pointery nie sú prirodzené herné pokrytie. DOSBox-X vykonanie zatiaľ chýba.
