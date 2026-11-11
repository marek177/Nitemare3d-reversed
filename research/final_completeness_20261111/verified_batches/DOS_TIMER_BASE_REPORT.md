# DOS 2.0 — pôvod menovateľa a hranice nulového vstupu

11. 11. 2026. PARTIAL, nové DEEP VERIFIED0 B, nové runtime testy0. Táto dávka spresňuje interpretáciu predchádzajúcich syntetických testov; nepreukazuje chybu pri bežnom hraní.

## Pole a setter

Image `[190A9,190AB)` = CS15BF:34B9..34BB obsahuje bajty `20 4E`, teda WORD **20000**. Nejde o nulový počiatočný menovateľ. Nasleduje setter `[190AB,190B1)`,6 B/2 inštrukcie:

```text
MOV CS:[34B9],BX
RET
```

Setter zachová registre a FLAGS, zapisuje WORD bez lokálnej validácie. SlotAH=43h pri image17C96 obsahuje34BBh, teda tento NEAR cieľ. V prevzatom priamom CALL inventári nemá setter priameho callera; vektorový/servisný vstup tým nie je vylúčený.

`audit_dos_timer_base.py` overuje hash obrazu, inicializačné bajty, presné inštrukcie, slot a sedem fixných CS pamäťových referencií z prevzatého inventára. Dôkazy sú v `dos_timer_base/fixed_references.csv` a `summary.json`. Sedem referencií = jeden zápis setterom a šesť čítaní; nejde o úplné vylúčenie indexed/alias/external writerov.

## Väzba na zvukové dáta

V časovačovej WAVE ceste sa zo skopírovanej44 B hlavičky načíta WORD CS:59B0 (dolný WORD poľa pri relatívnom offsete24), vynuluje DX a delí sa WORD CS:34B9. Výsledok sa uloží do CS:367C. Nasleduje AX=0 a ďalšie delenie tým istým menovateľom pri zachovanom zvyšku DX; výsledok ide do CS:3675. Toto je dvojkroková príprava podielových hodnôt; úplný kontrakt ich spotrebiteľa ešte nie je uzavretý.

V druhej record ceste predchádza výpočet `1000000 / (256 - input_byte)` a ďalšie delenia CS:34B9. Pôvod a povolený rozsah record byte nie sú touto dávkou uzavreté. Samotná kontrola `256-input_byte !=0` nevylučuje všetky quotient overflow prípady.

Neskôr obe cesty vytvárajú PIT vstup `low8(1191180 / CS:34B9)`. Preto35 nulových výsledkov z predchádzajúceho reportu označuje **hodnoty nastaviteľnej základne**, nie automaticky35 chybných vzorkovacích frekvencií pôvodných zvukových súborov. Hlavičkové pole a konfiguračná základňa sú odlišné polia.

## Čo možno a nemožno uzavrieť

Ak základňa zostane20000 a lokálna vetva je dosiahnutá, `1191180/20000=59`, low8=59. Predchádzajúci mechanizmus nuly z orezania podielu sa pri tejto hodnote neuplatní. Táto podmienková vlastnosť je staticky doložená. Neznamená, že celý prehrávací vstup je vždy platný alebo že sa pole počas hry nezmení.

Setter povoľuje aj0,4650 a iné hodnoty na úrovni svojich dvoch inštrukcií. Nevieme však, či ich reálne nastavuje niektorý prirodzený caller. Predchádzajúce riadené replay s menovateľom4650 je dôkaz mechanizmu pri zadanom stave; **nie dôkaz dosiahnuteľnej chyby originálneho gameplay**. Rovnako nulový setter vstup zostáva hypotetický, kým sa nevysledujú konkrétni producenti BX.

## Reprodukcia a pokrytie

`python audit_dos_timer_base.py IMAGE HISTORICAL_INSTRUCTIONS ABSOLUTE_DECODER_DIRECTORY OUT_DIR`. Rozšírený lifecycle skript vytvára `timer_base_setter.csv` a pridáva2 B dátovej základne do strojového katalógu. Nezávislé zlúčenie prešlo bez code/data konfliktu.

Centrálna partition má19 kandidátnych funkčných rozsahov,726 inštrukcií/1 651 B,550 dátových B,169 159 B aktuálne neposúdených a71 intervalov. Riadené replay prípady zostávajú23, DOSBox-X runtime0. Pôvodné PASS320 členstvo UNKNOWN; nové percentá N/A.

Nasledujúci konkrétny krok: spotrebiteľ CS:3675/367C v timer handleri a jeho závislosť od základne; pri runtime watchpoint naCS:34B9 a zachytenie BX pri AH43. Pokiaľ sa writer neobjaví, zachovať to ako ohraničené negatívne pozorovanie, nie globálny dôkaz nemennosti.
