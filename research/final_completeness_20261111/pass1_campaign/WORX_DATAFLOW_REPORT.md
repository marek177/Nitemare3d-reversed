# WORX — dátové režimy, názvy a producent callbacku

11. 11. 2026. Statická dávka nad obrazom `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. **PARTIAL**, nové DEEP VERIFIED 0 B, runtime testy 0. Pôvodná mapa PASS320 nebola importovaná; žiadny interval sa nepripočítava k jej 57 295 NON-CODE bajtom.

## Reprodukovateľný dôkaz

Skript `audit_worx_dataflow.py IMAGE INSTRUCTIONS_JSON OUT_DIR` bol vykonaný. Výstupy v `worx_dataflow/`: päť CSV inštrukcií, `direct_xrefs.csv`, `data_intervals.csv`, `dataflow_evidence.json`. Bajty, segmentové adresy a SHA inventára sú kontrolované. Dekódovanie je zo staršieho inventára a nie je nezávislou novou disassembláciou. Vyhľadávanie 46 xrefs je obmedzené na doslovné CS adresy v tomto inventári; nevylučuje nepriame/indexované/aliasové prístupy.

| Funkcia | Obraz, koniec exclusive | Inštrukčné bajty | Počet inštrukcií |
|---|---|---:|---:|
| counted_to_asciiz | 18A46–18A66 | 32 | 20 |
| counted_mode_setter | 18A66–18A6D | 7 | 2 |
| container_open | 18EF2–18F4B | 87 | 39 |
| container_close | 18F4B–18F6B | 32 | 12 |
| callback_locate | 17E08–17E39 | 49 | 17 |

Spolu 207 B inštrukcií. Dva ďalšie bajty `90` na 18F20 a 18F3A sú medzery starého inventára, ponechané UNKNOWN. Funkčné hranice sú kandidátne lokálne hranice podopreté návratmi; úplný audit vstupov a všetkých vetiev chýba.

## Konverzia dĺžkovo označeného názvu

`15BF:2E56` = obraz 18A46. Vstup ES:DI ukazuje na bajt dĺžky, za ktorým nasledujú znaky. Pri DF=0 kopíruje presne tento počet znakov do **segmentu pôvodného DS na offset 2BD9**, pridá NUL a vracia ES=pôvodné DS, DI=2BD9. CX, SI a DS obnovuje; ES a DI sú výstupy. AX/BX/DX/BP sa v tele nemenia. FLAGS sa nezachovávajú. Funkcia neobsahuje CLD; platná vstupná/výstupná pamäť a DF=0 sú otvorené predpoklady volajúceho.

```text
count = BYTE ES:[DI]
copy count bytes from ES:[DI+1] to old_DS:[2BD9]  // requires DF=0
old_DS:[2BD9+count] = 0
ES = old_DS
DI = 2BD9
```

Volajúci helper 31CA pred týmto volaním explicitne nastavuje DS=CS. Na tejto konkrétnej ceste teda cieľ leží v CS. Vo všeobecnom kontrakte konvertora nemožno segment natvrdo označiť za CS.

### Podmienená kolízia pri dlhom názve

Režimový bajt CS:2C0C leží `0x2C0C-0x2BD9 = 51` bajtov od začiatku cieľa. Pri count=51 zapisuje NUL presne do tohto príznaku; pri count>=52 kopíruje na jeho miesto znak. Na ceste 31CA sa konvertor volá práve pri nenulovom príznaku. Samotný konvertor nekontroluje hornú hranicu count okrem prirodzeného 8-bitového rozsahu.

To je potvrdený adresný výpočet pod predpokladom DS=CS a DF=0. Nie je to dôkaz, že hra poskytne názov dlžší než 50 znakov, že cieľ má deklarovanú kapacitu 51 alebo že príznak musí po operácii zostať nenulový. Potrebné sú všetky callsites, zdrojové reťazce a kontrakty bufferov. Žiadna herná chyba ani exploitabilita sa netvrdí.

Setter na 18A66 zapisuje CS:2C0C=1 a vracia sa. Jeho volajúci a životnosť tohto režimu zostávajú otvorené.

## Kontajnerový režim a počet záznamov

Open funkcia 18EF2 najprv volá close funkciu 18F4B, normalizuje ES:DI a prípadne prevedie counted string. Následne otvorí názov cez INT21 AX=3D00, uloží handle do CS:2DF3 a žiada čítanie **2 bajtov** do CS:2DF5. Ak CF=0, nastaví CS:2E10=1 a vráti AX=CS:2DF5 s CLC.

V lokálnom kóde po čítaní nie je kontrola AX==2. Krátke úspešné čítanie preto nie je týmto kódom výslovne odmietnuté; reálny výsledok a obsah zostávajúceho bajtu vyžadujú runtime test. Dvojbajtový počet sa neskôr číta na 18E96 ako počet 25-bajtových záznamov pre vyhľadávanie názvu v helperi 31CA.

Close funkcia načíta handle, pri hodnote odlišnej od FFFF volá INT21 AH=3E, potom bez kontroly výsledku nastaví CS:2E10=0 a CS:2DF3=FFFF. AX/BX sa lokálne obnovujú. Ignorovanie výsledku close je statická vlastnosť tejto funkcie, nie potvrdenie zlyhania DOS služby.

## FAR callback

Funkcia 17E08 ukladá vstupné BX na stack, nastaví AX=4310 a vykoná INT2F. Potom uloží BX do CS:21C8 a ES do CS:21CA. Tieto štyri bajty tak majú doloženú interpretáciu FAR ukazovateľa offset:segment na tejto inicializačnej ceste. Presná externá identita služby sa v tejto dávke nepriraďuje podľa podobnosti.

Nasledujú dve nepriame FAR volania cez tento ukazovateľ s AH=0 a AH=9. Pôvodné vstupné BX je medzitým POPnuté do DX; ak druhé volanie vráti AX=1, DX sa uloží do CS:21C6 a funkcia vráti AX=0, inak AX=FFFF. Že DX stále obsahuje pôvodné BX aj po druhom externom volaní, vyžaduje kontrakt callbacku; nesmie sa predpokladať iba z lokálneho POP.

Táto dávka teda identifikuje producentov oboch slov ukazovateľa, ale neuzatvára jeho všetky neskoršie zápisy ani historickú kolíziu s počítadlom 63.

## Katalóg dát a hranice klasifikácie

Šesť intervalov v `data_intervals.csv` zahŕňa 12 B: CS:21C6 (word), CS:21C8 (FAR pointer), CS:2C0C (byte flag), CS:2DF3 (word handle), CS:2DF5 (word record count), CS:2E10 (byte flag). Každý má presné image hranice, počiatočné bajty a hash. Všetky PARTIAL; runtime životnosť, úplné xrefs a členstvo v PASS320 sú neuzavreté.

## Runtime testy DOSBox-X

1. Counted string dĺžok 50/51/52: logovať DS/ES, DF, cieľ a CS:2C0C pred/po. Dlhé umelé názvy označiť ako fault injection; samostatne zbierať prirodzené herné názvy.
2. Open/read hlavičky s 0/1/2 vrátenými bajtmi: zaznamenať AX/CF, CS:2DF5, CS:2E10 a ďalší helper lookup. Chybové injekcie neprezentovať ako prirodzenú dosiahnuteľnosť.
3. Pri callback inicializácii zachytiť skutočný ES:BX po INT2F a registre po oboch FAR volaniach, najmä DX. Potvrdiť konvenciu AH=0/9 a vlastníctvo ukazovateľa.

## Tabuľka 13 oblastí

Nové meranie všade N/A. Výpočet po uzavretí inventárov: sémanticky uzavreté jednotky / všetky jednotky oblasti; jednotkou sú dátové polia, položky tabuliek, funkčné kontrakty alebo vetvy podľa oblasti. Runtime parita sa meria osobitne. Bajtovo zhodné ASM samo nestačí.

| Oblasť | Historicky | Nové zistenie | Neznáme/blokátor | Ďalší konkrétny krok |
|---|---:|---|---|---|
| Mapy/formáty | 99 % | kontajnerový count/header PARTIAL | názov formátu a krátke read | priradiť skutočné súbory |
| Typy/konštanty | 95 % | 12 B lokálnych polí PARTIAL | životnosť a PASS320 ledger | úplné xrefs polí |
| Tabuľky/ukazovatele | 93 % | producent FAR callbacku PARTIAL | externý ABI a aliasy | zachytiť registráciu callbacku |
| Funkcie/ASM/CFG | 90 % | 5 rozsahov, 207 B PARTIAL | globálne vstupy a dekódovanie | nezávislý decoder audit |
| RNG | 97 % | bez nového dôkazu | callsite inventár | RNG caller ledger |
| Scheduler | 96 % | bez nového dôkazu | tick ordering | dispatcher CFG |
| DEMO/vstupy | 96 % | bez nového dôkazu | determinizmus | párové DEMO |
| Renderer/VGA | 94 % | bez nového dôkazu | clipping/VGA stav | framebuffer + DAC |
| GUARD/bossovia | 93 % | bez nového dôkazu | prechody | stavové hrany |
| Zbrane/projektily | 92 % | bez nového dôkazu | slot lifecycle | collision trace |
| Sprity/HUD/paleta | 92 % | bez nového dôkazu | resource binding | draw xrefs |
| SAVE/LOAD | 92 % | bez nového dôkazu | cache po LOAD | serializácia |
| Win16 | 92 % | bez nového dôkazu | NE identity a fixupy | hash a segmentové mapy |

Priorita NON-CODE zostáva otvorená: pôvodný ledger je potrebný na vyčíslenie, ktoré z týchto lokálnych dátových intervalov zasahujú do požadovaných 57 295 B. Staršiu náhradnú mapu z vedľajšieho pracovného priečinka som preveril; sama výslovne uvádza, že PASS320 neimportovala, preto ju nepoužívam ako originálnu baseline.
