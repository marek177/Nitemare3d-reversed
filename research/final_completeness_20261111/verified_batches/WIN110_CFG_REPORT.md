# Win1.10 — vstupy, priame CFG a konflikt dekódovania

11. 11. 2026. Stav **PARTIAL**, nové DEEP VERIFIED 0 B, runtime testy 0. Zdroj: originálny NE EXE SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.

## Rozsah dôkazu

Skript `explore_win110_cfg.py` začína deklarovaným vstupom programu `2:3718` a jedinou položkou NE entry tabuľky, ordinal 1, `1:53CA`. Sleduje priame vetvy a vytvára kandidátov funkcií z priamych volaní. FAR ciele viaže na rozbalené relokácie; surové nezrelokované selektory nepovažuje za platné runtime adresy. Všetky adresy v tomto reporte sú **NE segment index:offset**, nie DOS real-mode CS:IP.

Výsledok: 27 kandidátov vstupov, 1 154 jedinečných začiatkov inštrukcií, únia 2 713 dekódovaných bajtov. Toto nie je počet potvrdených vykonateľných bajtov. Tri bajty majú konfliktné dekódovanie. Nevznikli výstupy mimo súborom podložených CODE segmentov ani neplatné inštrukcie; tieto kontroly samy osebe nepotvrdzujú dosiahnuteľnosť.

CFG eviduje 21 interných FAR volaní, 22 NEAR volaní, 38 externých FAR volaní, 114 podmienených taken hrán, 37 NEAR skokov a 23 return miest. Otvorených je 12 nepriamych volaní, jeden nepriamy skok a päť interrupt miest. Po volaní alebo interrupte je 98 pokračovaní založených na predpoklade možného návratu. Počty hrán sú deduplikované podľa zdroja a cieľa, nie dynamické počty vykonaní.

## Presný konflikt

| Miesto | Bajty | Dekódovanie / dôkaz |
|---|---|---|
| 2:3C71 | 9A FF FF 00 00 | relokácia viaže volanie na `KERNEL:#137` |
| 2:3C76 | B8 FF 00 | MOV AX,00FFh |
| 2:3C79 | 50 | PUSH AX |
| 2:3C7A | 9A FF FF 00 00 | relokácia viaže volanie na `KERNEL:#1` |
| 2:3C7F | 00 8C D8 90 | pri predpoklade návratu: ADD [SI-6F28h],CL |
| 2:3C80 | 8C D8 | priamy cieľ NEAR volaní z 2:3C48 a 2:3CCD: MOV AX,DS |
| 2:3C82 | 90 | NOP pri dekódovaní od 2:3C80 |

Konfliktná únia je presne `[2:3C80,2:3C83)`. `decode_conflicts.csv` obsahuje šesť záznamov: pre každý z troch bajtov oba dekódované vlastnícke začiatky. Príčina sporného vstupu 2:3C7F je explicitná may-return hrana z 2:3C7A. Hypotéza: import má kontrakt bez návratu a bajt 2:3C7F je medzera pred ďalšou funkciou. **Názov importu, jeho kontrakt ani padding status zatiaľ nie sú potvrdené dodaným modulom KERNEL; hypotéza sa neaplikovala ako filter.** Neexistuje nový dôkaz úmyselného overlapping-code triku.

## Reprodukcia a artefakty

```text
python explore_win110_cfg.py WIN110_EXE ABSOLUTE_ICED_X86_DIRECTORY FIXUP_DIRECTORY OUTPUT_DIRECTORY
```

V tomto prostredí musí byť cesta k natívnemu dekóderu absolútna; relatívna cesta vyvolala DLL load error, opakovanie s absolútnou cestou prešlo. Vstupný EXE sa nemení.

`win110_cfg/entry_table.csv`, `function_candidates.csv`, `instructions.csv`, `edges.csv`, `blocked_flow.csv`, `decode_conflicts.csv` a `summary.json` obsahujú reprodukovateľné položky a počty. Katalóg nepredstavuje úplný inventár funkcií, uzavreté hranice ani sémantické kontrakty. Vlastníctvo inštrukcie viacerými koreňmi môže znamenať spoločný epilóg alebo tail vetvu, nie nevyhnutne samostatnú funkciu. DS/ES/SS, nepriame callbacky a API ABI ostávajú otvorené.

## Ďalšie overenie

1. Získať dôveryhodnú ordinal tabuľku alebo konkrétny Win16 KERNEL modul a doložiť kontrakt ordinal 1; až potom vytvoriť explicitnú alternatívu CFG bez návratu.
2. Pri runtime trasovaní Win16 zaznamenať volanie 2:3C7A a prípadný návrat na 2:3C7F. DOSBox-X DOS konfigurácia sama o sebe tento Windows runtime test nenahrádza.
3. Pre každý z 13 nepriamych control sites doplniť producentov pointerov, segmentový kontext a konečný zoznam cieľov. Dovtedy nie je možné tvrdiť úplnosť CFG ani gameplay parity.

Percentá 13 oblastí ostávajú N/A podľa centrálnej metodiky. Originálna PASS320 intervalová mapa stále chýba; táto Win16 dávka neurčuje žiadny prienik s 57 295 DOS NON-CODE bajtmi.
