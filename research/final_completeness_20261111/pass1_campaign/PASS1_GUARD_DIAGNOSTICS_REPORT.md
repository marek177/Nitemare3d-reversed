# PASS1: GUARD diagnostika a tile chybové texty

Statická dávka typuje **193 B v štyroch NUL poliach** a pridáva osem presných pozorovaní GUARD record fields. Úroveň PARTIAL: diagnostiky, formatter, chybové ukončenie ani celé AI/tile funkcie sa nevykonávajú. Nové replay prípady 0.

## Vstupy a hranice

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. `audit_pass1_guard_diagnostics.py IMAGE INVENTORY DECODER OUT` overí identity, presné hranice a NUL, literal PUSH offset a konkrétne FAR call ciele. Vybraných 81 pôvodných kontextových inštrukcií sa overí proti obrazu a nezávisle dekóduje. DS mapovanie 2771h je podmienka textových adries.

| Interval, koniec exclusive | Typ / obsah | Konzument |
|---|---|---|
| [28B53,28BAC) | 89 B NUL format class/strength/strategy/state/nextstate/timer/octant/resoct | 083D:0D8B → sprintf 11EE:278C v 0D93 |
| [281F4,2822C) | 56 B NUL guard problem format | 04C7:15BA → 11EE:07E0 v 15BD |
| [27A8A,27A90) | 6 B NUL text `width` | 0277:0551, argument spoločného error callu |
| [27A90,27ABA) | 42 B NUL `Tile %s incorrect (%d), id=0x%x, frame=%d` | 0277:0554 → 0FBA:000C v 0578 |

Presné texty, konverzie, SHA a call adresy sú v `format_catalog.csv`/`data_fields.csv`. Náhodné numerické konštanty, ktoré sa rovnajú offsetu dovnútra reťazca v inom CS/DS kontexte, sa nepovažujú za dátový dôkaz.

## GUARD record pozorovania

V 083D:0D58..0D8A sa čítajú BYTE/WORD z ES:SI a tlačia v opačnom poradí pred variadic callom. Jediné explicitné vynulovanie AH po prvom BYTE čítaní stačí pre následné AL-only čítania bez intervenujúceho callee: tieto BYTE sa formátujú ako kladné zero-extended WORD. Timer sa načítava priamo ako WORD a `%d` ho interpretuje znamienkovo.

| Offset record26 | Šírka | Doložená diagnostická rola | Čítanie |
|---:|---:|---|---|
| +06 | WORD | timer | 083D:0D64 |
| +0A | BYTE | strategy | 083D:0D72 |
| +0B | BYTE | state | 083D:0D6D a 04C7:15B5 |
| +0C | BYTE | nextstate | 083D:0D68 a 04C7:15B0 |
| +0D | BYTE | `o_id` zobrazené ako hex | 04C7:15A9 |
| +10 | BYTE | strength | 083D:0D77 |
| +11 | BYTE | octant | 083D:0D5F |
| +12 | BYTE | resoct | 083D:0D58 |

Tieto názvy sú odvodené z presného textu a argumentového poradia, nie z pôvodných symbolov ani úplného writer auditu. `o_id` na +0Dh sa nesmie zameniť so signed WORD linked-object indexom na +8, doloženým predchádzajúcou dávkou. Obidve polia môžu mať súvisiaci širší význam, ale táto dávka takú ekvivalenciu netvrdí.

Diagnostický class argument sa získava cez WORD[guard+8]×28 a ďalšie ES-based object čítanie. V tomto bloku sa nezískava z GUARD BYTE +0Dh. Objektovému poľu sa nepriraďuje nový record offset bez samostatného overenia base konvencie a ES. AI state transition význam, povolené hodnoty a všetky writeri ostávajú otvorené.

Guard problem call odovzdá tri WORD z BYTE +0B/+0C/+0D a následne volá CRT 11EE:01EB(1). Statický call sled nie je vykonané ukončenie ani dôkaz prirodzene dosiahnutej chyby.

## Tile error vetva

Pri 0277:053A..0557 sa width BYTE porovná s 80h a 40h. Iná hodnota pripraví argumenty: frame WORD[BP+0C]+1, id WORD[BP+0A], zero-extended width BYTE[SI], text `width`, potom spoločný format pointer a error call. Vetva skáče do 0578, preto callee nie je bezprostredne po format PUSH, ale je preukázaný lokálnym JMP cieľom.

Susedná size vetva používa ten istý formát s iným popisom a vypočítanou veľkosťou; jej dáta mimo tejto dávky sa nepretypujú. Presný rozsah všetkých tile validator vstupov, kapacity a chybový callee zostávajú otvorené. Nemožno z toho vyhlásiť celý asset formát alebo renderer za uzavretý.

## Artefakty a meranie

`instruction_contexts.csv` zachováva bajty 81 vybraných inštrukcií; nie sú to celé funkcie alebo všetky ich CFG vetvy. `consumer_field_roles.csv` pridáva osem pozorovaní do centrálneho katalógu; ten má teraz 14 evidence riadkov vrátane starších, nie nutne 14 unikátnych úplne uzavretých polí. Zdroj a SHA každého pozorovania sú zachované.

193 B CLASSIFIED ONLY → PARTIAL. Aktuálna mapa: **56473 B PARTIAL, 778 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 804 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `fdf62f387ea4d7eb9213451cb331927e6c46ec68b24e84a713d590065d46dd2a`. Integrita mapy nie je dôkaz sémantickej úplnosti.

Bounded katalóg zostáva 90 funkčných rozsahov, 3235 inštrukcií / 8125 B. Typované dáta celého obrazu 57359 B; historického NON-CODE 56471 B a 2 PARTIAL netypované relokačné bajty. Controlled replay bez zmeny 679723 plus osobitne 65548 smerových prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, nové percentá N/A, predošlé orientačné. Diagnostické názvy ani lokálne typovanie nenahrádzajú úplný AI audit.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | width error argumenty | celý validator | asset header CFG |
| Dátové typy a konštanty | 95 % | N/A | 193 B / 4 NUL polia | zvyšné intervaly | ďalší textový blok |
| Tabuľky a ukazovatele | 93 % | N/A | GUARD a linked-object polia odlíšené | ES/base konvencie | class field address |
| Funkcie / ASM / CFG | 90 % | N/A | 81 kontextových inštrukcií | celé funkcie | validator closure |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | timer je WORD | writer cadence | timer producer |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | driver ABI | input closure |
| Renderer / VGA | 94 % | N/A | konkrétne width kontroly | format/kapacity | validator vstupy |
| GUARD / bossovia | 93 % | N/A | 8 field roles z argumentov | state transitions/writeri | field writer graph |
| Zbrane / projektily | 92 % | N/A | strength BYTE doložené | damage význam | strength writer |
| Sprity / HUD / paleta | 92 % | N/A | width BYTE 40h/80h vetvy | prirodzené assets | asset crosscheck |
| SAVE / LOAD | 92 % | N/A | bez nového SAVE dôkazu | record persistencia | SAVE ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | GUARD record parity | Win field consumer |

## Runtime testy na vykonanie

Zachytiť ES:SI a presné raw argumenty oboch GUARD diagnostík v izolovanom scenári; porovnať +0Dh a +8 bez predpokladu rovnosti. Overiť tile width vetvy s kontrolovanými asset hlavičkami a správanie error callee. Následne vystopovať writerov strategy/state/nextstate/timer/strength/octant. Pôvodné DOSBox-X vykonanie a Win16 parity zostávajú otvorené.
