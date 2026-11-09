# Nitemare 3D — PASS 153: FAR ukazovateľ a hranice dôkazu

Dátum: 2026-11-09. Zdroj: `N3D_PASS150_evidence.json`. Metóda: samostatná štruktúrna kontrola už publikovaných inštrukcií; **bez novej disassemblácie EXE a bez runtime testu**.

## Kontrolovaný výsledok

- Pre každý z dvoch obrazov existuje v 53 explicitných referenciách **51 čítaní segmentu do ES, jedno čítanie do CX a jeden nepriamy FAR `LJMP`**.
- Starší obraz: `11EA:397E mov cx,[2552h]` a `11EA:3984 ljmp [2550h]`.
- DOS 2.0: `11EE:397A mov cx,[2554h]` a `11EE:3980 ljmp [2552h]`.
- Pre 16-bitový `LJMP m16:16` predstavujú štyri bajty od adresy operandu dvojicu `IP` (nižší WORD) a `CS` (vyšší WORD). Čítanie `CX` v oboch obrazoch referuje presne na **horný WORD** tohto FAR ukazovateľa.
- Rozdiel medzi začiatočnými adresami `mov cx` a `ljmp` je v oboch prípadoch **6 bajtov**. Keďže `mov cx,[disp16]` má typicky štyri bajty, medzi inštrukciami zostávajú **dva neanalyzované bajty**. Nedá sa preto tvrdiť, že CX pri skoku nevyhnutne obsahuje segment cieľa, pokiaľ nepoznáme vloženú inštrukciu.
- Všetkých 53 odvodených párov zachováva posun operandov o +2; to nie je dôkaz presného dôvodu posunu ani iniciátora zápisov.

## Layout známy z použitých operandov

| Obraz | FAR offset (IP) | FAR segment (CS) | Čítanie segmentu do CX |
|---|---|---|---|
| Starší (v archíve DOS_1.8, identita sporná) | DS:2550 | DS:2552 | 11EA:397E |
| DOS 2.0 | DS:2552 | DS:2554 | 11EE:397A |

Tento layout je **interpretácia inštrukcie**, nie dôkaz, že celá oblasť obsahuje iba ukazovatele. V DOS 2.0 `DS:2550` nie je v úzkom súpise explicitne referované, ale to neimplikuje nepoužiteľnosť ani absenciu zápisu.

## Čo zostáva neznáme

1. Obsah dvoch medziľahlých bajtov medzi `mov cx` a `ljmp` a ich účinky na CX, DS, FLAGS a zásobník.
2. Producent 4-bajtovej hodnoty v `DS:2552–2555` (DOS 2.0): priamy zápis, pamäťová kópia, relokácia alebo aliasovaný ukazovateľ.
3. Cieľový `CS:IP` v runtime a dosiahnuteľnosť skoku.
4. Inicializácia susedných segmentových premenných a validita pred LOAD a pri prvom snímku.
5. Overenie identity staršieho normalizovaného obrazu podľa skutočného EXE, nie podľa názvu priečinka.

## Ďalší cielený krok

Získať pôvodný normalizovaný EXE alebo kompletný ASM úsek `11EE:397A–3983`, dekódovať medzibajty; následne hľadať def-use a všetkých writerov rozsahu `DS:2552..2555`, vrátane implicitných zápisov a relokácií. Pri DOSBox-X trace logovať posledný writer pre každý zo 4 bajtov a adresu cieľa v momente skoku.

Záver: **preukázané prekrývanie čítania CX s druhým WORD nepriameho FAR cieľa**, nie ešte producent ani runtime hodnota.