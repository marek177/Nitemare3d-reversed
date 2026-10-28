# Nitemare 3D DOS — Ghidra 12.2 pass 5, 2026-10-28

## Finding

Explicitný, úzko ohraničený real-mode p-code pohľad obnovil 15 ďalších C dekompilácií. Štandardná Ghidra zostáva na 3445/3468; explicitný pohľad má 3460/3468, bez nového dekompilačného zlyhania oproti stock v tom istom projekte. Tieto dva výsledky sa nesmú zamieňať. V oboch modeloch zostáva rovnaká množina kandidátov; žiadne funkcie sa nevyraďovali.

| DOS obraz | Štandardná Ghidra | Explicitný real-mode pohľad | Zlyhania v explicitnom pohľade |
|---|---:|---:|---:|
| 1.0 | 571/575 | 574/575 | 1 |
| 1.1 | 571/577 | 574/577 | 3 |
| 1.2 | 572/578 | 575/578 | 3 |
| 1.5 | 577/579 | 579/579 | 0 |
| 1.7 | 578/580 | 580/580 | 0 |
| V1.9 (vstupy 1.8/1.9) | 576/579 | 578/579 | 1 |

Dodaný vstup označený 1.8 je stále bajtovo totožný s V1.9. Samostatná 1.8 nie je týmito výsledkami doložená. Úspešný C dekompilát nie je sémantické uzavretie funkcie, úplný census entrypointov ani dôkaz parity.

## Evidence

| Status | Zistenie | Zdroj | Confidence |
|---|---|---|---|
| Confirmed | 12 far-data dekompilácií a 3 rendererové zlyhania sa obnovili iba v explicitnom pohľade. | audit/DOS*/explicit_model_results.tsv; evidence/validation.json | High pre výsledok nástroja v uvedenom modeli |
| Confirmed | 98 far-address rewrite miest na obraz, spolu 588; 4 CBRANCH rewrite miesta v rendererových moduloch starších obrazov. | audit/DOS*/explicit_pcode_changes.tsv; evidence/DOS*/scope_audit | High pre presný rozsah zásahov do analytického vstupu |
| Confirmed | Žiadna zmena adries ani bajtov definovaných inštrukcií vo všetkých šiestich projektoch. | porovnanie pass4 a pass5 instructions.tsv validátorom | High pre exportovaný listing |
| Confirmed | 1371 pôvodných post-projection prípadov na obraz, spolu 8226, bez hookov a externých stubov. | evidence/owner_*.json; scripts/verify_owner_crossversion.py | High pre kontrolovaný testovaný blok |
| Confirmed | V 324 prípadoch na obraz, spolu 1944, sa boolean AX líši od boolean AL; správny návratový bajt je AL. | raw_AX/AL v owner výsledkoch; pôvodné návratové opcode | High pre kontrolované prípady a opcode |
| Unknown | Úplná projekcia, rasterizácia, prirodzená dosiahnuteľnosť syntetických stavov a pixel-perfect parita. | Nevykonával sa celý renderer ani VGA | Neuzavreté |

## Exact analytical model

Kód vychádza z overeného DOS2 experimentu N3DExplicitRealModeProbe; v tomto passe sú scope adresy a vstupné EXE odvodené osobitne pre každý obraz. Neaplikuje sa globálna výmena jazyka ani slepé zmeny celej pamäte. Štandardné Ghidra pspec/cspec/JAR a EXE bajty sa nemenili.

1. V dvoch doložených rozsahoch funkcií sa non-SS operácia segment(seg16,off16) nahrádza v callbacku explicitným zext(seg16)<<4 + zext(off16). Výstup má 32 bitov.
2. SS operácie zostávajú pôvodné, aby sa zachoval analytický model stacku. Inštrukcie s internými p-code vetvami sa vynechávajú.
3. Každá nová pomocná unique varnode používa disjunktný rozsah od 0x70000000; scope audit overuje šírky a nekolidovanie s pôvodnými unique varnodes.
4. V rendererovom module sa pri rel16 vypočíta cieľ ako CS*16 + ((IP_next + signed_disp16) & 0xffff). Mení sa iba cieľ existujúcej BRANCH/CBRANCH/CALL operácie; podmienky sa nemenia a conditional vetva sa nemení na unconditional.
5. Pre štyri skutočne zmenené CBRANCH miesta prešlo 64 syntetických vykonaní pôvodných opcode s rôznymi flagmi. Ďalších 94 syntetických ES:BX loadov overilo adresový vzorec. Týchto 158 testov nie je herný kód N3D a nepočíta sa medzi 8226 rendererových prípadov.

Vzorec tu modeluje nemaskovanú real-mode lineárnu adresu s maximom 0x10ffef. Správanie fyzickej A20 linky na konkrétnom DOS stroji sa týmto neoverovalo.

Všetky dodatočné C súbory majú príponu explicit_real_mode_pcode_view.c; stock výstupy majú príponu stock.c. Callback je potrebné znovu spustiť podľa run_pass5.py: otvorenie projektu v obyčajnej Ghidre samo osebe tento pohľad nezapína. Prototypy funkcií sa v tomto passe nemenili. Najmä stock uint návrat rendereru sa nesmie chápať ako dôkaz definovaného AH.

## Original post-projection renderer model

Pripravený vstup je za projekčným volaním a prologue, pred OR AL,AL. Projekčný helper sa nevykonáva ani nestubuje hookom; vložené AL predstavuje jeho výsledok. Test pôvodných inštrukcií potom vykoná clipping, rozhodovanie vlastníkov a návrat cez skutočný RETF. Kontroluje sa celá pripravená owner tabuľka, počítadlo, nezmenené recordy, AL, DS a stack.

| Obraz | Funkcia | Testovaný vstup za projekciou |
|---|---|---|
| 10 | 1f85:0178 | 1f85:0192 |
| 11 | 1fa7:0170 | 1fa7:018a |
| 12 | 1fad:0170 | 1fad:018a |
| 15 | 1fb2:016e | 1fb2:0188 |
| 17 | 1fbc:016a | 1fbc:0184 |
| 18 | 1fd5:016e | 1fd5:0188 |

Signed clipping používa kandidátov interval record+0x14..+0x18 a viewport. Oba konce intervalu sa zahrnú. Prázdny stĺpec dostane kandidáta a 16-bitové počítadlo sa zníži o 1. Výmena nenulového vlastníka počítadlo neznižuje.

Pri signed geometrických wordoch x0=+0x0c, y0=+0x0e, x1=+0x10, y1=+0x12 je nahradenie podporené touto tabuľkou. Všetky porovnania sú strict signed16; rovnosť zabráni nahradeniu.

| Old orientácia | New orientácia | Podmienka |
|---:|---:|---|
| 0 | 2 | old.x0 < new.x0 a old.y0 > new.y0 |
| 0 | 3 | old.x1 > new.x1 a old.y0 > new.y0 |
| 1 | 2 | old.x0 < new.x0 a old.y1 < new.y1 |
| 1 | 3 | old.x1 > new.x1 a old.y1 < new.y1 |
| 2 | 0 | old.x1 < new.x1 a old.y1 > new.y1 |
| 2 | 1 | old.x1 < new.x1 a old.y0 < new.y0 |
| 3 | 0 | old.x0 > new.x0 a old.y1 > new.y1 |
| 3 | 1 | old.x0 > new.x0 a old.y0 < new.y0 |

Ostatné orientačné páry existujúceho vlastníka nemenia. Matica na každý obraz zahŕňa 1296 orientačných kombinácií, 64 signed hraničných konfigurácií, 5 counter/empty-owner prípadov a 6 clipping/reversed/projection-rejected prípadov. Číselné orientácie nemajú v tomto reporte priradené neoverené herné mená.

Návrat z post-projection bloku je AL = (signed16(counter) <= 0). Preto môže odmietnutá projekcia s počítadlom 0 alebo -1 vrátiť AL=1 bez zápisu owner tabuľky. Prologue vetva neaktívneho recordu má iný návrat AL=0; nie je súčasťou emulovaného bloku tohto passu.

## Recovered C and open candidates

- 1.0 — obnovené iba explicitným modelom: `1000:0ae0`, `1cdc:209a`, `1f85:0736`. Zostáva: `2dec:1cb0`.
- 1.1 — obnovené iba explicitným modelom: `1000:0ae0`, `1d00:207e`, `1fa7:048e`. Zostáva: `2e21:19d0`, `2e21:1b14`, `2e21:1b78`.
- 1.2 — obnovené iba explicitným modelom: `1000:0ae0`, `1d00:2080`, `1fad:048e`. Zostáva: `2e27:19d0`, `2e27:1b14`, `2e27:1b78`.
- 1.5 — obnovené iba explicitným modelom: `1000:0aea`, `1d05:207e`. Zostáva: žiadne zlyhanie medzi aktuálne detegovanými kandidátmi.
- 1.7 — obnovené iba explicitným modelom: `1000:0aea`, `1d0f:207a`. Zostáva: žiadne zlyhanie medzi aktuálne detegovanými kandidátmi.
- V1.9 — obnovené iba explicitným modelom: `1000:0aea`, `1d25:20ae`. Zostáva: `2d0b:2e0e`.

Osem zostávajúcich kandidátov je tých istých osem položiek bez známej incoming referencie z pass3. Neprítomnosť referencií sama nedokazuje neexistenciu funkcie; labely sa ponechali. Výsledok 579/579 alebo 580/580 v dvoch explicitných modeloch neznamená úplnú identifikáciu všetkého skutočného kódu.

## Implementation-ready findings

- Porovnávanie orientácií, signed clipping, zmena ownera, counter decrement a AL návrat sú pripravené na implementáciu v rozsahu testovaného post-projection bloku.
- Boolean AX je nesprávna interpretácia návratu: používať AL; AH môže niesť inú zvyšnú hodnotu.
- Pri odmietnutej projekcii nevracať automaticky false; v aktívnej post-projection vetve rozhoduje počítadlo.
- Obnovené C far-data rutín je ďalší analytický podklad, nie samostatný dôkaz každého herného významu alebo odstránenia všetkých chýb typov.

## Next discriminating tests

1. Overiť a zapísať presné návratové ABI AL pre renderer a DX:AX pre mapový callback pri všetkých verziách; porovnať callerov namiesto slepého prenosu DOS2 metadát.
2. Pri ôsmich kandidátoch preveriť callback tabuľky a relokované pointery; nevyraďovať ich iba kvôli nulovým bajtom či chýbajúcej xref.
3. Prepojiť výsledok projekčného helpera s týmto blokom a následne rasterizáciou; až potom framebuffer/DAC oracle.
4. Overovať runtime reachable stavy, scheduler, SAVE/LOAD a DEMO samostatne.

## Reproduction

Hotové pass5 projekty, stock/explicit výstupy, dôkazy a rekonštruované EXE sú v balíku. Baseline pass4 functions.tsv/instructions.tsv sú priložené pre validátor; startup DS dôkazy z pass3 pre rendererový test tiež. Pre čerstvú prípravu projektov cez prepare_pass5.py treba predchádzajúci pass4 balík a úpravu miestnych Java/Ghidra ciest. Najprv dokončiť run_pass5.py, až potom run_pass5_verify.py; pri súbehu vznikol jeden zamknutý DOS17 projekt a následná úspešná opakovaná kontrola je verify_retry_DOS17.log.

```bash
python3 scripts/verify_owner_crossversion.py
python3 scripts/verify_real_mode_linearization.py
python3 scripts/validate_pass5.py
```

Unicorn 2.1.4. Kontrola pred/po porovnáva celý definovaný inštrukčný listing, aj heuristické položky; samotný počet inštrukcií nedokazuje ich runtime dosiahnuteľnosť.

## Confidence

High pre reprodukovateľné výsledky oboch analytických modelov a testovaný rendererový blok. Úplné pochopenie všetkých funkcií a 1:1 herná/renderovacia parita zostávajú otvorené.
