# Sekundárny class lookup 00F7:004E

Stav PARTIAL. Funkcia image [00FBE,00FF3), 53 B / 23 inštrukcií, nezávisle dekódovaná a bajtovo overená proti kanonickému DOS 2.0 obrazu. CFG exportuje cfg_edges.csv. Ide o nový funkčný dôkaz; mapa historických NON-CODE sa touto dávkou nemení.

## ABI a algoritmus

FAR vstup, [SS:BP+6] požadovaná trieda WORD, [SS:BP+8] počiatočný index, z ktorého sa načíta iba BYTE. DS musí byť DGROUP; pri tejto analýze sa pri DS:D40E nachádza 256-bajtová sekundárna tabuľka z MAP hlavičky. SS nezávislý, ES v tele bez použitia, BP sa obnoví, BX je pracovný register. RETF, argumenty upratuje caller.

```c
uint16_t secondary_search(uint16_t key, uint16_t start) {
    uint16_t i = (uint8_t)start;
    for (; i < 256; ++i)
        if ((uint16_t)DS.u8[0xD40E + i] == key) return i;
    error_report(0x00F2, key);
    return AX_after_error_report; // ak sa vôbec vráti
}
```

Horný BYTE key sa nestráca; key=0100h alebo FFFFh nemôže zodpovedať zero-extended BYTE. Počiatočné porovnanie BX>=256 je po SUB BH,BH a MOV BL logicky nepravdivé. Štart 0100h sa mení na 0, 01FFh na 255. Neexistuje opakovanie od nuly po neúspešnom suffix prehľadaní. Chýbajúci záznam volá 0FBA:000C s formátom 00F2h a kľúčom; pôvodný fatal/error wrapper sa tu nevykonáva. Návrat FFFFh nie je explicitný kontrakt tejto funkcie.

## Reálne dáta a obmedzenie GUARD domény

Čítané sú všetky tri pôvodné MAP súbory, z každého file [0102,0202), 256 B. assets.csv uchováva presné cesty, celé SHA aj hash tabuľky. class_domains.csv má pre každú prítomnú triedu prvé/posledné ID, počet, kontinuitu a všetky relatívne ID voči prvému. Kontinuita nie je predpokladaná.

| Epizóda | Počet tried | Triedy s rozsahom relatívnych ID >7 |
|---|---:|---|
|1|39|00h (max 248), 28h (max 53), 2Ah (max 30), 2Bh (max 239), 2Eh (max 69)|
|2|37|00h (max 250), 28h (max 53), 2Ah (max 30), 2Bh (max 84), 2Eh (max 69)|
|3|30|00h (max 250), 28h (max 53), 2Ah (max 30), 2Bh (max 84), 2Eh (max 69)|

Toto nepreukazuje, že uvedené veľké triedy prechádzajú GUARD inicializáciou. Vyšší caller podmieňuje túto cestu bitom 8 vlastnosti objektového descriptoru. Väzba descriptor vlastnosti na class a skutočné mapové inštancie ešte nebola uzavretá. Z tohto dôvodu zostáva dôkaz platného GUARD selectoru otvorený aj po uzavretí lokálneho vyhľadávania.

## Kontrolovaná emulácia

10 836 prípadov = 2 load bázy × 3 reálne sekundárne tabuľky × 258 keys (0..255,0100h,FFFFh) × 7 start WORD (0,1,127,255,256,511,65535). Všetkých 23 inštrukčných začiatkov bolo vykonaných, nulové odchýlky. Úspešné vetvy vykonávajú pôvodnú funkciu bez závislostí. Chybový reporter je jediný model, overuje dva raw argumenty a vráti AX=BEEFh; výsledok BEEFh dokazuje prežitie hodnoty callee, nie prirodzený návrat chybového handlera. Overené SP/BP/DS. Neoveruje sa celé prirodzené mapové načítanie, všetkých 65536 kľúčov ani reálne fatal ukončenie.

Reprodukcia: audit_replay_secondary_class_search.py IMAGE INVENTORY DECODER EMULATOR MAP_DIR OUT. Relokácie sú zo skutočne rozbaleného EXE. Kanonický image SHA-256 e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297; závislosti iced-x86 1.21.0 a Unicorn 2.1.4.

## Meranie

PASS1 zostáva **57 031 B PARTIAL, 220 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Táto dávka nepridáva nový dátový typ do pôvodného NON-CODE; MAP hlavičky sú externé súbory. Prirodzené runtime testy zostávajú 0, nový funkčný rozsah je PARTIAL. Posledná publikovaná GitHub snímka túto dávku ešte neobsahuje.

SHA cases.csv `5c5940289d6dfcac74fb205316f245426bb4b836b964c343d893d9d556f52eda`.

## Aktualizácia 13 oblastí

Nové percento = uzavreté jednotky / úplný inventár oblasti. Bez úplných menovateľov N/A; historické odhady sa nemenia podľa test count ani byte integrity.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|tri sekundárne class tabuľky a domény|prirodzené inštancie|prepojiť mapové objekty|
| Dátové typy a konštanty |95 %|N/A|bez novej reklasifikácie|220 B iba klasifikované|zvyšné intervaly|
| Tabuľky a ukazovatele |93 %|N/A|suffix search a WORD key|descriptor flag|producer väzba|
| Funkcie / ASM / CFG |90 %|N/A|53 B / 23 inštrukcií|fatal callee|handler kontrakt|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|setup|VGA init CFG|
| GUARD / bossovia |93 %|N/A|lookup kontrakt pre selector|platná doména po flag gate|descriptor flag 8|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|bez nového dôkazu|identity|descriptor producer|
| SAVE / LOAD |92 %|N/A|bez nového dôkazu|I/O|config closure|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|lookup parita|nájsť ekvivalent|

## Runtime testy na vykonanie

V DOSBox-X zaznamenať DS:D40E po skutočnom map load a vstupy 00F7:004E pri GUARD ceste. Pri absencii class sledovať pôvodný handler až po prirodzené ukončenie alebo návrat. Overiť, ktoré triedy skutočne spĺňajú descriptor flag 8; samotná hlavička to nedokazuje. Win16 porovnať search wrap pravidlo a error kontrakt. PE32 sa nevytvára.
