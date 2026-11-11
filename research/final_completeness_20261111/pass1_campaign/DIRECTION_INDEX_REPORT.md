# DOS 2.0: uhol, jednorazová normalizácia a smerový index

## Nový výsledok

V dodanom inventári je deväť priamych pamäťových referencií na DS:4158 a jediný priamy WORD zápis, 0C7D:0096. Zápis je súčasťou funkcie začínajúcej na 0C7D:0068. Táto dávka uzatvára iba **prefix `[0C838,0C869)`, 49 B / 18 inštrukcií**, končí pred 0C7D:0099. Nie je to samostatná funkcia; zvyšok volá trigonometrické helpery a pokračuje v ďalších výpočtoch.

Priame referencie boli overené proti kanonickým bajtom a nezávisle dekódované. Negatívny inventárny výsledok neuzatvára indexované/aliasované zápisy, LOAD bloky ani kód mimo inventára. DS:4156/4158 sú mimo file-backed obrazu; tejto dávke preto nepribúdajú NON-CODE bajty.

## Pseudokód prefixu

```text
n = signed16(SS:[entry_SP+4])   # WORD argument FAR volania
DS:4156 = n
if n < 0:
    DS:4156 += 360
if signed16(DS:4156) >= 360:
    DS:4156 -= 360
AX = trunc_toward_zero(signed16(DS:4156) / 45)
CX = AX
DS:4158 = AX
# stop pred 0099, bez epilógu a bez vykonania trig callee
```

Nejde o modulo cyklus: obe korekcie sa vykonajú najviac raz. Celý signed16 vstupný priestor nemá pri týchto dvoch konkrétnych korekciách aritmetické pretečenie; záporný vstup sa iba zväčší o 360 a veľký nezáporný sa zmenší o 360. Následné IDIV má deliteľ 45.

## Exhaustívny controlled replay

Pôvodný prefix sa vykonal v Unicorn x86-16 pre všetkých **65 536 vstupných WORDov** pri load báze 0 a pre ďalších 12 hraničných vstupov pri load báze 1000h. Celkom **65 548 prípadov, 0 odchýlok** voči uvedenému modelu. Overili sa uložené signed WORDy DS:4156/4158, DS, SP a BP v bode zastavenia. Stack v tomto bode stále obsahuje prologové uloženia, preto sa netestoval návratový ABI celej funkcie.

Presné zistené vstupné množiny, oba konce inclusive:

| Vlastnosť prefixového výstupu | Vstupný signed16 interval |
|---|---|
| Normalizovaný uhol 0..359 | **−360..719** |
| Smerový index 0..7 | **−404..719** |

Rozdiel tvorí 44 vstupov −404..−361: výsledný uhol je −44..−1, ale signed IDIV 45 vytvorí index 0. Preto platný smerový index sám nepotvrdzuje platný uhol pre následný trig lookup. Pri vstupe −405 je index −1; pri 720 je index 8. Prirodzené callery a ich vstupné guardy zostávajú otvorené.

| Vstup | Uložený uhol | Index |
|---:|---:|---:|
| −405 | −45 | −1 |
| −404 | −44 | 0 |
| −361 | −1 | 0 |
| −360 | 0 | 0 |
| −1 | 359 | 7 |
| 359 | 359 | 7 |
| 360 | 0 | 0 |
| 719 | 359 | 7 |
| 720 | 360 | 8 |

Toto je dôkaz lokálneho správania pôvodných inštrukcií pri zadanom stave, nie pozorovanie prirodzenej hry, bezpečnosti všetkých callerov ani úplného prostredia DOS. Nepovyšuje sa na DEEP VERIFIED celého smerového subsystému.

## Reprodukcia a artefakty

`audit_replay_direction_index.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` overí SHA obrazu, 18 pôvodných inštrukcií, deväť priamych referencií a vykoná uvedenú maticu. `direction_index_replay/cases.csv` má každý vstup aj výsledok; SHA-256 `ef0d0bc24270aa1c049cb14bf3cd4a9f7e49ca006aca24ee354b031b104551f7`. Ďalšie artefakty: `instructions.csv`, `inventory_direct_refs.csv`, `summary.json`. Opakované spustenie po doplnení kontroly referencií dalo rovnaký SHA prípadov; nepripočítava sa druhýkrát.

Prefixové prípady sa v centrálnom súhrne vedú osobitne ako `direction_index_prefix_replay_cases=65548`; predchádzajúcich 6 091 controlled replay prípadov sa nemení. Funkčný katalóg zostáva 42 rozsahov / 1 450 inštrukcií / 3 354 B, pretože tento neukončený prefix sa nepridáva ako celá funkcia. Nové prirodzené runtime testy: 0.

PASS1 zostáva **54 638 B PARTIAL, 2 613 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Mapa v `pass1_direction_fields/` sa nemení. Dávka zatiaľ nie je publikovaná na GitHub.

## Aktualizácia 13 oblastí

Metodika nového sémantického percenta: uzavreté jednotky / úplný inventár jednotiek oblasti. Úplné menovatele chýbajú; nové percentá zostávajú N/A a predošlé hodnoty sú orientačné. Prefix je lokálne exhaustívne overený, širšie subsystémy zostávajú PARTIAL.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | prirodzené stavy | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | signed uhol a index | prirodzené hodnoty | caller argumenty |
| Tabuľky a ukazovatele | 93 % | N/A | podmienka indexu 0..7 | alias writeri | LOAD a odvodené zápisy |
| Funkcie / ASM / CFG | 90 % | N/A | 49 B prefix, 65 548 prípadov | zvyšok funkcie | pokračovať od 0099 |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | uhol zo vstupov | prirodzené rotácie |
| Renderer / VGA | 94 % | N/A | podmienená doména DS:4158 | platnosť vstupov | caller guardy |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | objektové indexy | ES:[SI+11h] writeri |
| Zbrane / projektily | 92 % | N/A | podmienená doména krokového indexu | lifecycle | spotrebiteľ +2/+3 |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | obnovenie uhla/indexu | LOAD bloky |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | normalizačný ekvivalent | Win caller CFG |

## Runtime testy na vykonanie

Pri prirodzených otočeniach, LOAD a DEMO zaznamenať argument na vstup 0C7D:0068, DS a uložené DS:4156/4158. Watchpoint na celý WORD DS:4158 má zachytiť aj prípadné nepriame zápisy. Porovnať vstupy s intervalom −360..719 pred následnými trig callee. Mimo tohto intervalu možno vykonať samostatné syntetické testy; neoznačovať ich za prirodzené vstupy hry. DOSBox-X vykonanie zatiaľ chýba.
