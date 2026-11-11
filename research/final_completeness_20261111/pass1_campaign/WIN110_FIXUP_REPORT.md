# Win1.10 — rozbalené NE reťaze a symbolické ciele

11. 11. 2026. Autentifikovaný EXE SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`,230400 B. Stav dôkazov **PARTIAL**; nové DEEP VERIFIED0 B, runtime testy0. DOS2.0 bajtový katalóg sa touto dávkou nemení.

## Merateľný výsledok

| Metrika | Výsledok |
|---|---:|
| Pôvodné8-bajtové fixup records | 446 |
| Expandované zdrojové miesta | 6082 |
| Jedinečné zdrojové miesta | 6082 |
| Únia bajtov zapisovaných fixupmi | 14482 |
| Prekryvy zapisovaných bajtov | 0 |
| Cykly alebo source bounds chyby | 0 |
| Reťaze ukončené FFFF v segmente | 446/446 |
| Relocation-backed FAR CALL opcode kandidáti | 4243 |

446/446 je uzavretá štrukturálna kontrola **dodanej relokačnej tabuľky** podľa uvedeného parsera, nie100% znalosti Win16 hry.14482 bajtov je loader fixup footprint; nesmie sa označiť za14482 novo vysvetlených dátových bajtov. Fixup môže ležať v inštrukčnom operande aj v dátovom ukazovateli.

## Reprodukcia a formátový podklad

Spustený skript `expand_win110_fixups.py WIN110_EXE DECODER_DIR OUT_DIR`:

1. Overí SHA EXE, NE hlavičku, segmentové tabuľky a diskové bounds.
2. Pre každý raw record rozlíši source typ a target flags.
3. Pri neaditívnej relokácii číta ďalší WORD source offset z pôvodného segmentu, až po FFFF. Sleduje visited set, bounds podľa šírky patcha a globálne duplicity/prekryvy.
4. Pri aditívnom zázname by spracoval jedno miesto; v tomto EXE sa taký flag nevyskytol.
5. Rozlíši interný segmentový selector, import ordinal a import name. Movable internal entry a OSFIXUP by boli odmietnuté ako nepodporené; v tomto EXE sa nevyskytli.

Význam chained/additive záznamov a modulových referencií je opísaný v pôvodnej Microsoft dokumentácii archivovanej ako [MS-DOS Encyclopedia, Appendix K](https://www.pcjs.org/documents/books/mspl13/msdos/encyclopedia/appendix-k/). Interpreter konkrétnych source typov2,3,5 je explicitný v skripte; nepredstiera podporu všetkých NE variantov.

Výstupy `win110_fixups/expanded_sites.csv`, `record_chains.csv`, `modules.csv`, `far_candidates.csv`, `summary.json` zachovávajú pôvodné bajty aj cestu ku každému recordu. Pri reťazovej relokácii počiatočný source WORD často obsahuje ďalší link, nie finálny adresný offset; nesmie sa ako taký interpretovať pred loader fixupom.

## Typy a ciele

| Source typ | Šírka | Miesta |
|---|---:|---:|
| 2: selector16 | 2 B | 4904 |
| 3: far pointer32 | 4 B | 1159 |
| 5: offset16 | 2 B | 19 |

Všetkých4904 interných miest v tomto EXE sú selector-only referencie. Symbol `internal_selector:N` preto neznamená FAR adresu N:0000. Pri kandidátskom FAR CALL sa offset preberá z nezmeneného word operandového offsetu pri source mieste, zatiaľ čo loader má vložiť príslušný selector. Tento rozdiel je zachovaný v stĺpcoch effective_internal_segment/effective_internal_offset.

1165 miest odkazuje na imported ordinal,13 na imported name. Názvy modulov sú z pôvodného module-reference/import-name tables, nie odhadnuté podľa API správania.

| Modul | Počet fixup miest |
|---|---:|
| USER | 592 |
| GDI | 307 |
| KERNEL | 212 |
| MMSYSTEM | 41 |
| WING | 9 |
| COMMDLG | 8 |
| KEYBOARD | 4 |
| SHELL | 3 |
| DISPDIB | 2 |

Súčet1178 zahŕňa1165 ordinal a13 name miest. Jediný importovaný názov v tomto korpuse je **KERNEL:__A000H**, použitý na13 miestach. Je to symbolická importná väzba; report ho automaticky neoznačuje za rutinu. Význam importu a jeho runtime hodnota vyžadujú modulový/loader kontrakt.

Ordinal importy sú zapísané ako `MODULE:#ordinal`. Názvy funkcií sa nehádateľne nedopĺňajú podľa moderných Win32 ordinalov. Pre presné názvy treba autentifikované Win16 DLL/export tabuľky príslušného prostredia.

## Kandidátske FAR CALL miesta

4243 source miest má pred fixup operandom byte9A na správnej relatívnej polohe a nezávisle sa dekóduje ako5-bajtový FAR CALL. Žiadny takto zachytený kandidát nebol EA FAR JMP. To nevylučuje iné skoky mimo tohto úzkeho pravidla.

Pri interných kandidátoch sa overilo, že odvodený offset leží v súborovo uloženom cieľovom segmente; žiadny nevyšiel mimo. Trieda cieľového segmentu CODE/DATA z NE flagu je zaznamenaná. **Opcode+relokácia nie je dôkaz dosiahnuteľnosti ani potvrdeného funkčného vstupu.** V dátach sa môžu vyskytovať rovnaké bajty a nepriame callsites toto pravidlo neobsahuje.

Ďalšia brána je spojenie source inštrukcií s nezávislým Win1.10 CFG, potvrdenie ich vstupných koreňov a rozlíšenie thunkov, callbackov, knižničných rutín a hernej logiky. Celkový callgraph zatiaľ uzavretý nie je.

## Čo zostáva otvorené

- Skutočné runtime selektory a načítanie segmentov vo Windows.
- Názvy ordinal importov z konkrétnych autentifikovaných DLL.
- Pôvod DS/ES/SS na každej dátovej referencii; samotný selector fixup toto nedokazuje.
- Úplný Win16 CFG, nepriame pointery a hranice funkcií.
- Behaviorálne porovnanie DOS/Win a prirodzené runtime stopy.
- Originálny NON-CODE ledger PASS320 pre DOS2.0; táto Win16 metadata dávka ho nenahrádza.

Aktualizovaná tabuľka všetkých13 oblastí v `CAMPAIGN_CATALOG_REPORT.md` zaznamenáva nový Win16 výsledok, metodiku, otvorené otázky a ďalší krok. Nové percentá všetkých oblastí zostávajú N/A: plné sémantické menovatele chýbajú. Ostatné oblasti v tejto dávke nezískali nové herné tvrdenia.

## Runtime testy

V autentifikovanom Win1.10 prostredí zachytiť loader priradenie selectorov, symbolické importy a pamäť pred/po fixupoch na vybraných code/data miestach. Porovnať použitie __A000H s DS/ES segmentovými tokmi. Zaznamenať konkrétne DLL SHA, Windows verziu a load map. Tieto testy sa nevykonali; metadata kontrola ich nenahrádza. PE32 port sa nevykonáva.
