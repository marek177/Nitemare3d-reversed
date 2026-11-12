# PASS1: indexované komponenty GUARD

16 B CLASSIFIED ONLY → PARTIAL. Tabuľky majú dva explicitné základy vzdialené 8 B; nominálna interpretácia je 8 BYTE slotov pre každý komponent. Dôkaz platného rozsahu indexu od callerov zostáva otvorený, preto nejde o úplne uzavreté smerové tabuľky ani DEEP VERIFIED. Kanonický DOS 2.0 obraz má SHA-256 e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297.

| Image interval, koniec exkluzívny | DS | Počiatočné BYTE | Konzument |
|---|---|---|---|
|[2823E,28246)|0B2E|00 00 00 00 00 01 00 FF|04C7:1678, SHL AL,3 → record +13|
|[28246,2824E)|0B36|00 00 00 00 FF 00 01 00|04C7:1683, SHL AL,3 → record +14|

Predchádzajúci nulový BYTE [2823D,2823E) zostáva CLASSIFIED ONLY; nebol priradený k tabuľke. FF << 3 dáva F8, interpretovateľné ako -8 pri signed BYTE, ale fyzické osi a signed použitie nasledujúcich konzumentov sa tu nedokazujú. Prvé štyri sloty oboch tabuliek sú nulové; nenahrádzajú sa očakávanými vektormi podľa hypotézy.

## ASM, ABI a pseudokód

04C7:1660..1692, image [062D0,06302), 50 B / 21 inštrukcií. Vstup FAR, [SS:BP+6] offset destinácie, +8 segment destinácie, +0A WORD selector. Ukladá BP/DI/SI, načíta ES z argumentu a ponechá ho zmenené. DS je vstupný DGROUP kontext, SS nezávislý. Žiadne callee, skokové tabuľky ani vetvy. RETF, caller upratuje tri WORD argumenty.

```c
void set_components(farptr dst, uint16_t selector) {
    ES = dst.segment;
    ES.u8[dst.offset + 0x11] = (selector & 3) * 2;
    ES.u8[dst.offset + 0x13] = (DS.u8[(selector + 0x0B2E) & 0xFFFF] << 3) & 0xFF;
    ES.u8[dst.offset + 0x14] = (DS.u8[(selector + 0x0B36) & 0xFFFF] << 3) & 0xFF;
}
```

Maskovanie AND AL,3 sa týka len výstupu +11: SI používaný pri oboch indexovaných čítaniach ostáva pôvodný WORD. Index 8 preto číta prvý BYTE druhej tabuľky v prvom čítaní a nasledujúci susedný stav v druhom. Toto nie je dôkaz, že prirodzená hra posiela index 8, ani dôkaz chyby.

## Caller kontext

V dodanom inventári je priamy caller 04C7:16EF (PUSH CS + NEAR CALL), ktorý preposiela svoj [BP+0E] ako selector. Jeho funkcia začína 1692 a pracuje so záznamami stride 26. Overený vyšší caller 0AEA:0A8C odovzdáva rozdiel zero-extended objektového BYTE [ES:BX] a výsledku 00F7:004E so zrušeným AH. Táto dávka neuzatvára lookup 004E ani rozsah hodnôt z mapy. Chýba dôkaz domény 0..7; maska pre +11 ho neposkytuje. Relevantné bajty a inštrukcie sú v caller_contexts.csv.

## Kontrolovaná emulácia a reprodukcia

65 552 pôvodných prípadov bez stubov: všetkých 65 536 selector WORD pri load base 0, ďalších 16 boundary selectorov pri base 1000h. Zadané sú skutočné počiatočné image dáta a nulová dodatočná pamäť; hodnoty mimo nominálnych tabuliek sú z tohto modelového DGROUP, nie z prirodzenej hry. Všetkých 26 výstupných bajtov sa porovnáva, takže overené sú aj nezmenené polia. Kontrolujú sa SP/BP/SI/DI, DS a ES. Test neoveruje aliasovanie destinácie so zdrojom ani zvolené hranice segmentového offsetu destinácie. Nulové odchýlky.

Reprodukcia: audit_replay_pass1_direction_vectors.py IMAGE INVENTORY DECODER EMULATOR OUT; potom promote_pass1_fields.py s predchádzajúcou mapou pass1_literal_consumers a verify_pass1_partition.py. Exporty: data_fields.csv, guard_direction_components.csv, caller_contexts.csv, cases.csv a summary.json. Dekódovanie aj pôvodné bajty sú porovnané s inventárom. Prirodzené runtime testy zostávajú 0.

## Meranie

**57 031 B PARTIAL, 220 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Nezávislá kontrola 866 intervalov overila presné členstvo, všetky hash hodnoty, nulové diery a prekryvy. Táto integrita nedokazuje úplnú sémantiku. Nový bounded funkčný rozsah sa pridáva ako PARTIAL; GitHub posledná publikovaná snímka ho zatiaľ neobsahuje.

SHA mapy `176e35e92fbb21cd3db337ac7bce74174b925227ede29a4a74877f653a3aa2bc`; SHA cases `70ecc7f82cd572f63f6b9edc7bd945c5fc94ea08ab700bc4eaa5dedd0503f797`.

## Aktualizácia 13 oblastí

Metodika nového % je počet dôkazmi uzavretých jednotiek / úplný inventár oblasti. Menovatele chýbajú, preto N/A. Staré orientačné percentá sa nemenia podľa úspešných testov alebo integrity byte mapy.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|selector odvodený z objektového BYTE|lookup a doména|uzavrieť 00F7:004E|
| Dátové typy a konštanty |95 %|N/A|16 B PARTIAL|220 B iba klasifikované|zvyšné intervaly|
| Tabuľky a ukazovatele |93 %|N/A|dva BYTE základy vzdialené 8|platný index|mapové zdroje selectorov|
| Funkcie / ASM / CFG |90 %|N/A|50 B / 21 inštrukcií|celá funkcia 1692|uzavrieť initializer|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|setup|VGA init CFG|
| GUARD / bossovia |93 %|N/A|producer polí +11/+13/+14|fyzické osi a doména|následné konzumenty|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|bez nového dôkazu|identity|descriptor producer|
| SAVE / LOAD |92 %|N/A|bez nového dôkazu|I/O|config closure|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|algoritmická parita|nájsť ekvivalent leaf|

## Runtime testy na vykonanie

V DOSBox-X logovať prirodzený selector pri 0AEA:0A80 a 04C7:1660 pre všetky tri epizódy, spolu s triedou mapového objektu a výsledkom lookup. Overiť, či sa vôbec vyskytne hodnota mimo 0..7. Sledovať signed/unsigned použitie +13/+14 počas pohybu GUARD; až potom priradiť osi. Win16 porovnať podľa dátového toku a záznamových polí. Žiadny prirodzený runtime test tejto dávky neprebehol; PE32 port sa nevykonáva.
