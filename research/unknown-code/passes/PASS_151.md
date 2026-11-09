# Nitemare 3D — PASS 151: audit identity DOS 1.8/1.9 v existujúcich výsledkoch

Dátum: 2026-11-09. Metóda: krížová kontrola uložených reportov a JSON dôkazov; bez opätovného čítania originálneho EXE alebo runtime testu.

## Overený rozpor v metadátach

- PASS 150 `N3D_PASS150_evidence.json` obsahuje položku `DOS_1.8` s veľkosťou normalizovaného obrazu 171296 B a SHA-256 `e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e`.
- Audit `Nitemare3D_DOS_dalsia_analyza_neznamych_2026-09-24.md` identifikuje presne takýto normalizovaný obraz ako DOS v1.9. Výslovne uvádza, že skutočná samostatná DOS v1.8 nebola v jeho vzorkách dostupná a jeden kandidát `N3D(5).EXE` sa po úplnom rozbalení zhodoval s v1.9.
- PASS150 spracúva v archíve adresár `pass019/analysis/DOS_1.8/`; názov adresára však nie je nezávislým dôkazom verzie. SHA-256 je jednoznačným dôkazom identity bajtového obrazu, nie jeho marketingového čísla.

## Dôsledok

Výsledky PASS 150 pre záznam `DOS_1.8` musia byť až do nezávislej kontroly pôvodného súboru vedené ako **obraz 171296 B / e29a8d...**, pravdepodobne DOS 1.9, NIE ako nezávislé potvrdenie DOS 1.8. Porovnanie medzi týmto obrazom a DOS 2.0 zostáva bajtovo definované. Nedokazuje však rozdiel DOS 1.8 vs. DOS 2.0.

## Technický dôsledok na analýzu segmentového bloku

Pozorovania nulových 30 bajtov a zistené absolútne operandové referencie zostávajú pozorovaniami o príslušných normalizovaných obrazoch. Nezávislosť dvoch historických verzií 1.8 a 1.9 z toho nevyplýva. Najbližší krok: získať konkrétny pôvodný EXE, overiť distribučné označenie a vyrobiť normalizovaný load image so SHA-256; následne mapovať skutočných producentov DS:2550–256C vrátane relokácií, indirect stores a bulk copy.

## Stav dôkazu

VERIFIED (cross-report): rovnaký SHA-256 a veľkosť pri konfliktnom označení DOS_1.8/DOS v1.9.
STRONGLY SUPPORTED: PASS150 `DOS_1.8` môže byť premenovaný kandidát DOS v1.9.
UNKNOWN: identita originálneho distribučného súboru PASS100 bez jeho nezávislého rozbalenia a kontroly. Nie je doložené, že PASS150 originálna DOS 1.8 existuje.