# PASS1 — štyri spotrebiteľsky doložené FAR label pointery

11. 11. 2026. PARTIAL, DEEP VERIFIED0 B. Nových46 B prešlo zCLASSIFIED ONLY naPARTIAL; ide o konkrétne pointerové/textové objekty, nie iba počiatočný byte pattern.

## Presné objekty

Default DS báza27710h je doložená predchádzajúcou startup dávkou. Nasledujúce inicializačné pointery majú offset WORD a relokované segment WORD2771h:

| Index | Pointer image end-exclusive | DS offset pointera | Text image end-exclusive | Text vrátane NUL |
|---:|---|---|---|---|
| 0 | 2841Ah..2841Eh | 0D0Ah | 28412h..2841Ah | `Red key` /8 B |
| 1 | 28428h..2842Ch | 0D18h | 2841Eh..28428h | `Green key` /10 B |
| 2 | 28436h..2843Ah | 0D26h | 2842Ch..28435h | `Blue key` /9 B |
| 3 | 28446h..2844Ah | 0D36h | 2843Ah..28445h | `Yellow key` /11 B |

Štyri pointery16 B a štyri ASCIIZ texty38 B tvoria54 jedinečných bajtov. Dva samostatné nulové bajty pri28435h a28445h sa nezahrnuli ako potvrdený alignment/padding. Ich konkrétna úloha zostáva otvorená.

Pôvodný raw ASCII vzor pri28410h začínajúci `q'` nesmie slúžiť ako hranica `Red key`: tieto dva bajty patria segmentu **predchádzajúceho** pointera. Pointer na samotný Red key je až za jeho textom, na2841Ah. Príslušné zdrojové objekty teda netvoria jednoduché súvislé FAR pointer pole v súbore.

## Reálny spotrebiteľ

Funkčný kandidát083D:1F36, image `[0A306,0A33A)`, má52 B/17 inštrukcií, bez vetiev a volaní, končí RETF. ENTER10h vytvorí16 B lokálny rámec. Štyri `MOV EAX,DS:[0D0A/0D18/0D26/0D36]` uložia4-bajtové hodnoty do štyroch miest naSS stacku. Zo vstupuSS:[BP+6] vypočíta16-bitové SI=index*4 a vybraný pár WORD vráti cez AX/DX.

Lokálny algoritmus pre kontrakt index0..3:

```text
locals[0] = dword DS:0D0A
locals[1] = dword DS:0D18
locals[2] = dword DS:0D26
locals[3] = dword DS:0D36
SI = (word(SS:BP+6) * 4) & FFFFh
AX = word(SS:BP+SI-10h)
DX = word(SS:BP+SI-0Eh)
restore SI, BP; RETF
```

**Funkcia index nekontroluje.** Podmienka0..3 je analytický kontrakt platných štyroch lokálnych položiek, nie vykonaná ochrana. Pre iné indexy môže čítať iné stack miesta alebo16-bitové aliasy. Prirodzené caller indexy zatiaľ nie sú uzavreté.

FAR interpretáciu podporuje úplný reťazec: konkrétny4 B load, rozdelenie výsledku doAX/DX, skutočná segmentová relokácia a výsledný cieľ na presne overenomASCIIZ texte. Nejde len o odhad z dvoch susedných WORDov. Kontrakt zároveň vyžaduje správny incoming DS; táto funkcia ho sama nenastavuje. Úplný inventár writerov a runtime životnosť stringov/pointerov zostáva otvorený.

## Osem riadených replay prípadov

`replay_pass1_key_selector.py` vykonal pôvodné inštrukcie pre indexy0..3 pri syntetických load segmentoch0 a1000h. Pred každou sadou aplikoval všetkých1670 skutočných relokačných miest na čerstvú kópiu obrazu. DS bol výslovne nastavený naload+2771h, stack a FAR return frame syntetické.

Všetkých8 assertions prešlo: presnýDX:AX, cieľové textové bajty, zachovanieSI/BP/BX/CX/DS/ES/SS a SP poRETF. Dvojbajtový argument zostáva na caller stacku. Overenie nevykonáva DOS loader, prirodzeného callera ani renderovanie textu; nie je dôkazom celkového správania inventára kľúčov. Invalid indexy sa netestovali a nemenia sa na potvrdený gameplay bug.

`pass1_key_selector_replay/evidence.json` uchováva load/index, výsledné adresy, text a inštrukčné stopy aj hash Unicorn DLL. Prijaté controlled replay prípady kampane sú teraz40; DOSBox-X/originálny runtime0.

## Typová mapa a súčty

`audit_pass1_key_labels.py` kontroluje image identitu, konkrétne load bajty, pointery, segmentové relokácie, presné ASCIIZ hranice a predchádzajúcu PASS1 mapu. Výstupy `pass1_key_labels/labels.csv`, `data_fields.csv`, `selector_instructions.csv`, `noncode_intervals.csv` a `.json` zachovávajú konkrétne typy a odkazy. Nová258-intervalová mapa stále pokrýva presne57295 B.

| Stav | Predchádzajúca dávka | Aktuálne |
|---|---:|---:|
| PARTIAL | 260 B | **306 B** |
| CLASSIFIED ONLY | 9695 B | 9649 B |
| UNKNOWN | 47340 B | 47340 B |
| DEEP VERIFIED | 0 B | 0 B |

Metodika prírastku:54 B objektovej únie mínus8 B relokačných WORDov, ktoré už boliPARTIAL =46 novýchPARTIAL bajtov. Nijaké dvojité započítanie pointerových segmentov. Všetky tieto objekty patria pôvodnému baseline intervalu1487; pôvodný source ID je v novej mape zachovaný.

Centrálny lokálny code/data katalóg po zlúčení selector code a týchto objektov obsahuje33 rozsahov,1127 inštrukcií/2609 B,902 dátových B. **54 B tejto centrálnej dátovej únie teraz má presný prienik s pôvodným NON-CODE**; skorší výsledok0 B bol stav pred touto dávkou. Ostatné loader-only WORDy ostávajú v samostatnej PASS1 vrstve.

Reprodukcia: `python audit_pass1_key_labels.py IMAGE RELOCS PRIOR_PASS1_MAP ABSOLUTE_DECODER_DIRECTORY OUT_DIR`; replay: `python replay_pass1_key_selector.py IMAGE RELOCS UNICORN_DIRECTORY OUT_DIR`.

Ďalší krok: uzavrieť prirodzené DS a indexy callerov selectoru, potom analogické ID-card pointery a nasledujúcu správu. Širšie gameplay/HUD významy sa neodvodzujú len z anglického názvu textu. Percentá13 oblastí zostávajú N/A bez ich vlastných úplných menovateľov.
