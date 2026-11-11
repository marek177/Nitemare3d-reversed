# DOS 2.0 — reprodukcia EXEPACK a helper 15BF:31CA

Dátum: 11. 11. 2026. Stav dávky: **PARTIAL**. Žiadne povýšenie na DEEP VERIFIED; žiadne runtime testy. Pôvodná 1 488-intervalová mapa PASS320 naďalej chýba.

## Reprodukovaný pôvod obrazu

`reproduce_exepack.py` bol spustený proti EXE SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Výsledok má 171 360 B a SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; zhoduje sa bajt po bajte s existujúcim obrazom. Reprodukcia spracovala 158 blokov a 89 086-bajtový nekomprimovaný prefix; spätné zakódovanie komprimovaného prúdu bolo presne zhodné. Relokačná tabuľka má 1 670 unikátnych cieľových slov a končí presne na EOF.

Ide o statickú reprodukciu transformácie podľa zachovaného algoritmu, nie o spustenie originálneho unpackera. Parser je zámerne viazaný na túto identitu EXE a zaznamenáva build-specific offset relokačnej tabuľky `stub+0x132`. Nepredstiera univerzálny parser EXEPACK.

Výstupy: `unpack/unpack_proof.json`, `unpack/unpack_blocks.csv`, `unpack/relocations.csv`, `unpack/reproduced_image.bin`.

## Rozsah helpera a CFG

Adresa obrazu `0x18DBA` zodpovedá `15BF:31CA`, pretože `0x15BF*16=0x15BF0`. Kandidátsky rozsah funkcie je `[0x18DBA,0x18EF2)`, 312 B. Návrat RET je na `0x18EF1`; nasledujúci inventarizovaný vstup začína na `0x18EF2`. Hranice sú lokálne podopreté prologom/epilógom a priamymi hranami, nie dôkazom úplného inventára všetkých vstupov.

Skript `audit_worx_helper.py` overil 116 historických ASM záznamov, spolu 311 B, proti reprodukovanému obrazu. Bajtové nezhody: 0. Priame relatívne ciele CALL/JMP/Jcc/JCXZ prepočítava priamo z bajtov a kontroluje interné ciele proti hraniciam inštrukcií. Mnemoniky ostatných inštrukcií sú zo staršieho inventára; nový nezávislý disassembler zatiaľ nebol použitý.

Medzera inventára `[0x18E81,0x18E82)` má hodnotu `90`. Predchádza jej nepodmienený skok na epilóg a bezprostredne za ňou začína ďalšia vetva. Je to kandidát NOP/paddingu, ale bez globálneho xref auditu zostáva UNKNOWN. Toto nesmie automaticky meniť kategóriu v nedostupnej mape PASS320.

Výstupy: `worx_helper/instructions.csv`, `worx_helper/cfg_edges.csv`, `worx_helper/helper_evidence.json`.

## Lokálny kontrakt a dátové závislosti

Vstupné BX rozlišuje dve cesty po volaní pomocnej rutiny na `0x1A220` (cieľ CS:4630). Presný kontrakt tejto pomocnej rutiny nie je uzavretý.

- Prológ ukladá BX, CX, SI, DI, ES; nastavuje DS z CS. Pôvodné DS sa v tejto funkcii neukladá ani neobnovuje. Konečnú hodnotu DS treba posúdiť aj s kontraktmi volaných helperov.
- Nenulová BX cesta zapisuje režimový bajt CS:312D=1, uloží ES:DI do CS:3129/312B, zapíše BX do CS:2DF7, vynuluje CS:2DF9 a DWORD CS:2DFF; vráti AX=BX s CLC.
- Nulová BX cesta zapisuje režim CS:312D=0. Obsahuje DOS INT21 s AH=3E (close), AX=3D00 (open), AX=4202/4200 (seek) a AH=3F (read). Priradenie názvov DOS službám je interpretácia API operandov; ich reálne výsledky v DOSBox-X zatiaľ neboli zachytené.
- Pri čítaní sa používa 25-bajtový buffer CS:2DF7 a porovnanie reťazca od buffer+12 s ES:DI. Kandidátsky význam: vyhľadanie pomenovaného záznamu v súbore/kontajneri. Presný formát zdroja ani verejný knižničný symbol nie sú potvrdené.
- Úspešná vetva po vyhľadaní používa DWORD z buffer+8 ako cieľ seek a vracia DWORD z buffer+0 v DX:AX.

Katalóg piatich dátových intervalov obsahuje presné hranice, počiatočné bajty a SHA-256 v `worx_helper/data_intervals.csv`. Všetky sú PARTIAL; ich príslušnosť k historickým NON-CODE intervalom je UNKNOWN. Táto tabuľka je lokálny katalóg závislostí, nie náhrada celej mapy 57 295 B.

## Zistená nezrovnalosť chybovej vetvy

Na `0x18E92` je INT21 po AX=4200, CX=0, DX=2. Následný `JB` na `0x18E94` má cieľ `0x18EEC`, priamo epilóg. Obchádza explicitnú normalizáciu chyby na `DX:AX=FFFF:FFFF` na `0x18EE5–0x18EEB`.

Volajúca rutina má na `0x17F3C` CALL tejto funkcie, na `0x17F3F` porovnáva DX s FFFF a na úspešnej vetve inkrementuje CS:20C4. Týchto šesť bajtov CALL/CMP bolo v tejto relácii porovnaných s obrazom; ich širší kontrakt ešte nie je uzavretý. Nemožno preto všeobecne tvrdiť „každá chyba helpera znamená DX=FFFF“. Rovnako z toho zatiaľ nevyplýva, že chyba seek spôsobí inkrementáciu v reálnej hre: treba uzavrieť režimové vetvy a návratový stav DOS API.

Ďalšia otvorená otázka: po AH=3F read sa v tejto lokálnej sekvencii nevetví podľa CF ani podľa vráteného počtu bajtov pred porovnávaním obsahu bufferu. Skutočné dosahy krátkeho čítania, EOF a zlyhania sú runtime hypotézy, nie potvrdená herná chyba.

## Rekonštruovaný čiastočný pseudokód

```text
save BX,CX,SI,DI,ES
DS := CS
opaque_helper_4630()
if BX != 0:
    mode := memory; saved_pointer := ES:DI
    buffer.dword0 := BX; buffer.dword8 := 0
    AX := BX; CF := 0; goto return
mode := file
optional_helper_2E56()
if alternate_container_mode:
    opaque_helper_48AF()
    DOS_seek(handle, absolute=2)
    if CF: goto return  // bypasses explicit FFFF sentinel
    repeat up to record_count:
        DOS_read(handle, buffer, 25)
        compare NUL string buffer+12 with ES:DI
        if exact match: goto matched
    goto sentinel_error
else:
    close_previous_handle_if_any()
    open_ES_DI_readonly_or_sentinel_error()
    buffer.dword0 := DOS_seek_to_end_result
    buffer.dword8 := 0
    DOS_seek_to_start()
    DX:AX := buffer.dword0; goto return
matched:
    DOS_seek(handle, buffer.dword8)
    DX:AX := buffer.dword0
    if not CF: goto return
sentinel_error:
    CF := 1; DX:AX := FFFF:FFFF
return:
restore ES,DI,SI,CX,BX; RET
```

Helpery, správanie DOS API a predpoklady o zachovaní registrov ostávajú explicitne otvorené. Pseudokód nie je kompletný verejný kontrakt WORX.

## Aktualizácia 13 oblastí

Metodika ostáva: overené sémantické jednotky / úplný autentifikovaný inventár jednotiek. Chýbajúce menovatele znamenajú N/A, nie 0 %. Integrity bajtov sa nesmú počítať ako sémantické pokrytie. Každý riadok nižšie uvádza historický odhad; nové meranie je vo všetkých prípadoch N/A.

| Oblasť | Predtým | Nové potvrdenie / stav | Neznáme a blokátor | Najbližší krok |
|---|---:|---|---|---|
| Mapy/formáty | 99 % | bez nového herného dôkazu | úplný inventár polí | mapovať konzumentov |
| Typy/konštanty | 95 % | 5 lokálnych intervalov PARTIAL | PASS320 hranice | priradiť intervaly k ledgeru |
| Tabuľky/ukazovatele | 93 % | 1 670 relokácií extrahovaných; integrita | vlastníci ukazovateľov | spojiť s dátovými xrefs |
| Funkcie/ASM/CFG | 90 % | 116 byte-matched inštrukcií PARTIAL | externé helpery a alternatívne vstupy | uzavrieť 4630/48AF/2E56 |
| RNG | 97 % | bez nového dôkazu | úplný inventár callsites | sledovať spotrebu RNG |
| Scheduler | 96 % | bez nového dôkazu | poradie tickov | overiť dispatcher |
| DEMO/vstupy | 96 % | bez nového dôkazu | runtime determinizmus | dvojité prehratie |
| Renderer/VGA | 94 % | bez nového dôkazu | clipping/VGA stav | framebuffer + DAC |
| GUARD/bossovia | 93 % | bez nového dôkazu | prechody/dosiahnuteľnosť | uzavrieť stavové hrany |
| Zbrane/projektily | 92 % | bez nového dôkazu | kolízie/slot lifecycle | collision trace |
| Sprity/HUD/paleta | 92 % | bez nového dôkazu | resource binding | draw xrefs |
| SAVE/LOAD | 92 % | bez nového dôkazu | cache po LOAD | serializačné kontrakty |
| Win16 | 92 % | bez nového byte auditu | NE fixupy a identita | autentifikovať segmenty |

## Konkrétne runtime testy DOSBox-X

1. Pri vstupe do helpera zaznamenať BX, ES:DI, DS a režimové globály; pri návrate DX:AX, CF a všetky zmenené registre. Load base musí byť explicitne mapovaná na CS=load+15BF.
2. V samostatnom fault-injection teste vyvolať chybu seek na vetve 18E92 a zaznamenať, či volajúci 17F3F prejde do inkrementácie. Tento test nedokazuje prirodzenú hernú dosiahnuteľnosť.
3. Testovať read=0, krátky read a CF=1 pre 25-bajtový buffer; zaznamenať, aké bajty sa porovnávajú a či ostali zo staršieho záznamu.
4. Pri normálnom behu logovať počet úspešných service49 volaní a producentov CS:21C8; samotné nenájdenie hodnoty 63 v jednej stope nevylučuje jej dosiahnuteľnosť.
