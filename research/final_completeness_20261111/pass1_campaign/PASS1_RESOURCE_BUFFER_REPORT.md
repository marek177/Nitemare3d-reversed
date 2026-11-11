# PASS1: 15 000-bajtový načítavací buffer

SHA-256 obrazu `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Nerelokovaný segment 1D0Fh má bázu 1D0F0h. Nominálny maximálny cieľ čítania je **[1D0F0,20B88), 15 000 B**, celý počiatočne nulový. Typ je BYTE buffer, status PARTIAL. Nuly neurčovali hranice.

## Reťazec dôkazov

Loader `0C2B:039E`, obraz C64E..C686, dostane WORD index v SS:[BP+6]. Vypočíta BX=index*6 modulo 16 bitov. WORD DS:[BX+3F64] je veľkosť, DWORD DS:[BX+3F66] zdrojový offset. Na C65E porovná veľkosť unsigned s 3A98h (15 000); C664 pri väčšej hodnote skočí priamo na C67D.

Pri povolenej veľkosti vloží veľkosť, DWORD zdrojového offseta a FAR cieľ 1D0F:0000 do argumentov `0277:008A`. Segmentové WORDy na C670 a C681 majú skutočné EXEPACK relokácie. Po načítaní teda cieľ aj vrátený pointer používajú segment load+1D0Fh. C67D/C680 vždy nastavia DX:AX na tento pointer, vrátane vetvy size>15000.

Helper 0277:008A, obraz 27FA..285B, prípadne otvorí súbor cez CRT, vykoná seek s DWORD offsetom a origin=0, potom volá `0FBA:009E` s handle, FAR cieľom a WORD počtom. Porovná vrátený počet s požadovanou dĺžkou; pri nezhode volá už analyzovaný error helper 0FBA:000C. Jeho podmienečný exit kontrakt nie je bezpodmienečne uzavretý. Seek výsledok sa pred read explicitne nekontroluje.

Primitív `0FBA:009E`, obraz FC3E..FC57, zachová DS, nastaví BX=handle, LDS DX=cieľ, CX=dĺžka a AH=3Fh, vykoná INT 21h. Pri CF nastaví AX=FFFFh, inak ponechá počet prečítaných bajtov. Obnoví DS a vráti sa FAR. Tým je dokázané, že nominálna veľkosť z loadera je počet bajtov zápisu do cieľového bufferu, nie počet prvkov väčšieho typu.

```text
load(index):
    entry = DS + ((index * 6) & 0xffff) + 0x3f64
    size = WORD[entry]
    if unsigned(size) <= 15000:
        seek_and_read(1d0f:0000, DWORD[entry+2], size)
    return 1d0f:0000
```

## Obmedzenia a nové riziko

Pri size>15000 sa buffer **nevymaže ani nenaplní**, ale jeho adresa sa vráti. Môže teda obsahovať počiatočné nuly alebo staršie dáta. Toto je staticky potvrdená lokálna cesta; prirodzený výskyt takého resource záznamu nebol overený. Index nie je lokálne ohraničený, caller DS a všetci writeri tabuľky/bufferu zostávajú otvorení. Rozsah je nominálny maximálny zápis tejto cesty, nie dôkaz globálnej alokačnej kapacity, runtime bezpečnosti alebo úplnej sémantiky zvukového formátu.

Oblasť za 20B88h až po ďalšiu známu segmentovú bázu 20B90h sa touto dávkou neoznačuje ako padding. Ostatné UNKNOWN intervaly sa nemenia.

## Reprodukcia a meranie

`audit_pass1_resource_buffer.py IMAGE PRIOR_MAP DECODER_DIR OUT` vyžaduje vedľa IMAGE aj `relocations.csv` z reprodukcie EXEPACK. Kontroluje identitu obrazu, oba relokačné segmenty, rozhodujúce ASM bajty, počiatočné nuly, SHA každého vstupného intervalu a presný súčet. Dekóduje loader, seek/read helper a DOS read primitív. CSV/JSON v `pass1_resource_buffer/` zachovávajú hranice a SHA.

Predošlá mapa: PARTIAL 12 211 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 35 862 B. Nová mapa: **PARTIAL 27 211 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 20 862 B, DEEP VERIFIED 0 B**. Všetkých nových 15 000 B bolo UNKNOWN. Súčet je 57 295 B. Nový prirodzený runtime ani replay sa v tejto dávke nespustil; predchádzajúci prijatý replay súčet zostáva 1 579.

DOSBox-X plán: sledovať cieľ pri dĺžkach 0,15000,15001, výsledok seek, short read a návrat pointera po preskočení. Testovať v izolovanej kópii stavu; porovnať buffer pred/po načítaní a zistiť prirodzené caller indexy. Ďalší statický krok: šesťbajtová resource tabuľka DS:3F64 a jej producer/caller bounds, potom zostávajúce veľké UNKNOWN rozsahy.

## Aktualizácia 13 oblastí

Nové sémantické percento všade N/A: chýba úplný inventár kontraktov/polí/vetiev. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické čísla sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | size/offset resource read | formát a bounds | DS:3F64 producent |
| Dátové typy a konštanty | 95 % | N/A | 15 000 B buffer PARTIAL | ostatní writeri | write xrefs |
| Tabuľky a ukazovatele | 93 % | N/A | relokovaný FAR buffer pointer | resource index | caller bounds |
| Funkcie / ASM / CFG | 90 % | N/A | limit a stale-buffer vetva | prirodzená dosiahnuteľnosť | runtime dĺžky |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | resource binding | draw xrefs |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
