# Nitemare 3D – statická analýza funkcií, vstupná etapa

Dátum: 2026-09-26. Zdroj: používateľom dodaný `nitemare.zip` (74 420 204 bajtov). Tento dokument uvádza **overené výsledky inventúry**, nie hotový rozbor všetkých funkcií. Nie je poctivé vyhlásiť tisíce inštrukcií za preskúmané iba podľa prítomnosti databázy IDA alebo podľa výsledku automatického rozpoznávania funkcií.

## Overené vstupy

| Zostava | Program | Formát | Vstupný bod | SHA-256 |
|---|---|---|---|---|
| DOS 1.0 | nd-3-10/N3D-E-10.EXE | MZ, rozbalená kópia | 1B1B:0010 | 7035d185d27a4629 |
| DOS 1.7 | nd-3-17/N3D-E-17.EXE | MZ, rozbalená kópia | 1B52:0010 | 6abf5745d1b28622 |
| DOS 1.8 | nd-3-18/N3D-E-18.EXE | MZ, rozbalená kópia | 1B6F:0010 | 1cbb55c193b75424 |
| DOS 1.9 | nd-3-19/N3D-E-19.EXE | MZ, rozbalená kópia | 1B6F:0010 | 1cbb55c193b75424 |
| DOS 2.0 | nd-3-20/N3D-E-20.EXE | MZ, rozbalená kópia | 1B72:0010 | 552d250ef773014a |
| Win 1.3 | nw-3-13/nite3w13/NITE3W.EXE | NE | 0002:3718 | 926c0001944b9822 |
| Win 1.6 | nw-3-16/n3w16/NITE3W.EXE | NE | 0002:3718 | 5851849bacd8b03e |
| Win 1.8 | nw3-18/NITE3W.EXE | NE | 0002:3718 | 144e96bb649c5463 |

SHA-256 je skrátený na 16 hexadecimálnych znakov; plné hodnoty sú v sprievodnom `executable_inventory.csv`. V archíve sú aj zabalené DOS `N3D.EXE` a databázy IDA `.i64` pre päť rozbalených DOS verzií; pre Windows zostavy tu databázy `.i64` neboli nájdené.

## Zistenia a istota

| Stav | Zistenie | Dôkaz | Istota |
|---|---|---|---|
| Potvrdené | Rozbalené DOS 1.8 a 1.9 sú bajtovo identické. | SHA-256 `1cbb55c193b75424…`, oba súbory po 116 556 bajtov | Vysoká |
| Potvrdené | Zabalené DOS 1.8 a 1.9 sú tiež bajtovo identické. | SHA-256 `ea9cbea5896a304c…`, oba súbory po 74 426 bajtov | Vysoká |
| Potvrdené | Tri uvedené Windows súbory sú 16-bitové NE, každý s vstupným bodom `0002:3718`. | NE hlavičky konkrétnych EXE | Vysoká |
| Neznáme | Presný počet funkcií a ich hranice v každej zostave. | Treba analyzovať segmenty, priame/nepriame volania, skoky, návraty a dáta oddelene. | — |
| Neznáme | Účel a vnútro každej funkcie. | Zatiaľ nie sú pre každú funkciu overené xref, parametre, vedľajšie účinky a volajúca cesta. | — |

## Postup na dokončenie analýzy všetkých funkcií

1. Pre DOS použiť rozbalené `N3D-E-*.EXE`; analyzovať 1.8/1.9 iba raz a výsledok previazať na oba názvy. Overiť segmenty, relokácie a vstupný bod; IDA `.i64` používať ako pomôcku, nie ako dôkaz významu názvov.
2. Pre Win16 rozobrať NE tabuľku segmentov, vstupné body, importy, presmerovania a relokácie. Segment:offset nepremieňať na offset v súbore bez tabuľky segmentov.
3. Vytvoriť pre každú zostavu zoznam funkcií s poľami: segment:offset, rozsah, vstupná cesta, priame/nepriame volania, čítané a zapisované globálne údaje, argumenty, návrat, rozpoznané vetvy, názov a `Potvrdené/Odvodené/Neznáme`.
4. Každú funkciu preveriť inštrukciu po inštrukcii; zvlášť zachytiť prepínače, skokové tabuľky, callbacky, thunk funkcie, prekryvy a kód zdieľaný s dátami. Porovnať zmenené funkcie medzi verziami pomocou kódu a xref, nie iba rovnakých adries.
5. Pri herných funkciách sledovať prenos od `MAP`/`OBJECTS`/`WALLS` cez inicializáciu a runtime záznam k zmenám stavu; pri nejasných vetvách pripraviť konkrétny debugger test.

**Stav pokrytia:** dokončená inventúra základných vstupov a jedna verzová deduplikácia. Hlbokú analýzu všetkých funkcií nemožno zatiaľ označiť za dokončenú a z tejto fázy nemožno vyvodiť poctivé percento pokrytia ani tvrdenie o kóde 1:1.