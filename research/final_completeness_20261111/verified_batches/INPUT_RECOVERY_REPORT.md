# Nitemare 3D — obnovenie vstupov, 11. 11. 2026

## Výsledok dávky

Lokálne čítanie funguje pri schválenom spustení mimo obmedzeného prostredia. Bežné spustenie naďalej zlyháva chybou `registered runtime ownership is missing`. Pôvodné súbory neboli zmenené.

Reprodukcia: spustiť `verify_input_identity.ps1` v PowerShelli. Skript bol úspešne vykonaný; výstupy sú `input_identity.json` a `input_identity.csv`. Overuje aktuálne hashe vstupov, nie sémantiku hry.

## Priamo overené identity

- Lokálny `L:\nite3d\nite3\dos\N3D-UNFU.exe`: 116 606 B, SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.
- Súbory `nite3/dos/N3D-UNFU.exe` a `nite3/dos/N3D-E-20.EXE` v `L:\nite3d\dosbox-n3d.zip` majú rovnakú veľkosť a rovnaký SHA-256 ako lokálny EXE. Druhý názov sa nenachádzal vedľa lokálneho EXE; porovnanie bolo vykonané priamo v ZIP.
- Tri existujúce obrazy majú zhodne 171 360 B a SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`:
  - `2026-10-25/goal-x20-5/outputs/N3D-20/unpacked_image.bin`
  - `2026-11-11/goal-nitemare-3d-dos-2-0/outputs/canonical_load_image.bin`
  - `2026-11-05/preportovanie-dos-2-0-do-pe32/outputs/native-port/evidence/unpacked-unrelocated.bin`

Vyššie relatívne cesty začínajú v `C:\Users\Marek-Medved\Documents\Codex`. Plné cesty obsahuje strojový výstup. Zhodu hashov som overil priamo. Historický pôvod a rozbaľovací algoritmus sú zatiaľ prevzaté z existujúcich skriptov a metadát; ich nové nezávislé vykonanie nie je súčasťou tejto dávky.

## Rozlíšenie adresných priestorov

Dodaný DOS EXE má MZ hlavičku 512 B, nulový počet MZ relokácií a vstup CS:IP `1B72:0010`. Súborový vstup je `0x1B930`, offset po MZ hlavičke `0x1B730`. Surový zvyšok EXE po hlavičke má 116 094 B; nejde o 171 360-bajtový rozbalený obraz.

Existujúci `unpack.json` uvádza 158 EXEPACK blokov, 1 670 vnútorných relokácií, pôvodný CS:IP `11EE:0018` a veľkosť obrazu 171 360. Tieto počty sú v tejto dávke iba prečítané historické metadáta. Nulový počet relokácií MZ preto nesmie viesť k záveru, že rozbalený program nemá relokovateľné ukazovatele.

## Dostupné ďalšie vstupy

`L:\nite3d\N3D_ALL_VERSIONS_ASM.zip` obsahuje 118 položiek: pôvodné DOS/Win16 EXE, DOS load image, Win16 segmenty a lineárne ASM. README výslovne uvádza, že lineárny výstup zahŕňa dáta a nepotvrdzuje funkčné hranice. DOS 2.0 export sa zhoduje s kratším súborovým load image, nie automaticky s rozbalenou mapou PASS320.

Win1.10 metadata uvádzajú EXE 230 400 B, SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`, 10 NE segmentov a vstup `2:3718`. Hash Win1.10 v tejto dávke ešte nebol nezávisle prepočítaný.

## PASS320/321 a obmedzenia

Presná 1 488-intervalová mapa zatiaľ nebola nájdená. Vyhľadávanie názvov PASS320/PASS321 v dostupných priečinkoch Dokumenty/Codex nevydalo zhodu. Niektoré priečinky hlásia odmietnutý prístup; negatívny výsledok teda nie je dôkaz absencie všetkých artefaktov. Dostupné sú iné staršie inventáre (`unclassified_ranges.csv`, `instructions.json`, `functions.csv`, `relocations.csv`), ktoré nemožno bez porovnania vydávať za PASS320.

Historických 57 295 NON-CODE bajtov nie je v tejto dávke znovu overených. Nové DEEP VERIFIED bajty: **0**. Runtime testy: **0**. Nevykonával sa PE32 port.

## Stav 13 oblastí

Všetky nové percentá zostávajú N/A: chýba overený inventár menovateľa a sémantické akceptačné brány. Historické odhady sa nemenia. Spoločný nový výsledok je dostupnosť hashovo zhodných obrazov; nejde o nový poznatok o algoritme hry.

| Oblasť | Historický odhad | Nové meranie | Metodika budúceho merania | Zostávajúce neznáme / blokátor | Najbližší krok |
|---|---:|---|---|---|---|
| Mapy a dátové formáty | 99 % | N/A | uzavreté polia / inventár polí | úplnosť inventára | priradiť dátové konzumenty |
| Dátové typy a konštanty | 95 % | N/A | sémanticky uzavreté bajty / dátový inventár | mapa PASS320 | získať hranice NON-CODE |
| Tabuľky a ukazovatele | 93 % | N/A | uzavreté položky / inventár položiek | segmentové aliasy | overiť relokácie a xrefs |
| Funkcie / ASM / CFG | 90 % | N/A | uzavreté kontrakty / potvrdený inventár funkcií | nepriame hrany | overiť ASM proti obrazu |
| RNG a determinizmus | 97 % | N/A | uzavreté callsites / úplný inventár | poradie volaní | inventár RNG xrefs |
| Scheduler / slučka | 96 % | N/A | uzavreté vetvy / inventár vetiev | poradie tickov | potvrdiť CFG dispatcheru |
| DEMO a vstupy | 96 % | N/A | uzavreté vetvy / inventár vetiev | vzorkovanie a runtime | zachytiť dve rovnaké prehratia |
| Renderer / VGA | 94 % | N/A | uzavreté vetvy; pixelová parita osobitne | clipping a VGA stav | spárovať ASM a framebuffer |
| GUARD / bossovia | 93 % | N/A | uzavreté prechody / inventár prechodov | dosiahnuteľnosť | potvrdiť stavové dispatchery |
| Zbrane / projektily | 92 % | N/A | uzavreté vetvy / inventár vetiev | slot lifecycle | overiť kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | uzavreté operácie / inventár operácií | resource binding | inventár draw konzumentov |
| SAVE / LOAD | 92 % | N/A | uzavreté polia / inventár polí | cache po LOAD | porovnať serializáciu s konzumentmi |
| Windows Win16 | 92 % | N/A | uzavreté funkcie / Win1.10 inventár | NE fixupy a rozdiely | prepočítať hash EXE a segmentov |

## Ďalšia analytická dávka

Overiť pôvod 171 360-bajtového obrazu reprodukciou rozbalenia z hashovo potvrdeného EXE. Potom overiť segmentové mapovanie historických offsetov PASS321 a rekonštruovať xrefs z dostupných inštrukčných inventárov. Staršie mapy ponechať oddelene, kým nebude k dispozícii pôvodný ledger PASS320.
