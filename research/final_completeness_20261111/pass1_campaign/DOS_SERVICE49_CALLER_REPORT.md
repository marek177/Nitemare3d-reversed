# DOS 2.0 — ohraničené hľadanie callerov service49

11. 11. 2026. PARTIAL; nejde o dôkaz nedosiahnuteľnosti. Kanonický obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`.

## Nové dôkazy

`probe_dos_service49_callers.py` overil bajty, CS:IP mapovanie a nezávislé dekódovanie 35 648 položiek historického `instructions.json`. V týchto položkách nie je priamy encoded NEAR/FAR CALL s cieľom image 17F39 (service49) ani 18CD6 (dispatcher). Kontrola nepokrýva všetky možné inštrukčné začiatky obrazu; bezprostredný FAR cieľ je interpretovaný v nerelokovanom priestore.

V **celých 171 360 bajtoch** sa nenachádza dvojica CD 63. To vylučuje iba staticky uložené doslovné kódovanie INT63 v tomto obraze, nie volanie dispatcher pointerom, upravený kód, externý volajúci modul či vytvorené kódovanie.

Jediná položka s priamym `MOV AH,49h` alebo `MOV AX,49xxh` je image 148F0, po nej súvislo nasleduje `CD21` na 148F2. Toto je iný interrupt a nesmie sa započítať ako dôkaz callerov service49. Výpočet AH cez iné inštrukcie sa týmto skenom nevyriešil.

Prítomnosť servisnej položky zostáva pozitívne doložená: slot pri image 17CA2 obsahuje WORD 2349h, teda NEAR cieľ CS15BF:2349 = image17F39. Samotný slot nie je dôkaz vykonania.

## Dôsledok pre riziko counter=63

Metadata alias z predchádzajúcej dávky je platná lokálna adresná aritmetika. Táto caller kontrola nedokazuje, koľkokrát sa service49 vykoná, či sa vykoná vôbec v bežnom gameplay, ani či má funkčnú alternatívu. Preto count bound a prirodzená dosiahnuteľnosť ostávajú otvorené. Funkcia sa neoznačuje ako dead code ani DEEP VERIFIED.

Najbližší statický krok: producenti adresy handlera, inštalácia/využitie vektorov a nepriame FAR volania. Runtime: breakpoint na image17F39 po dosadení load segmentu, log caller CS:IP a saved interrupt frame, AH, counter pred/po a resetov. Negatívny runtime výsledok z jednej hernej relácie nebude globálnym dôkazom nedosiahnuteľnosti.

## Reprodukcia a mapa

`python probe_dos_service49_callers.py IMAGE HISTORICAL_INSTRUCTIONS ABSOLUTE_DECODER_DIRECTORY OUT_DIR`. Výstupy: `dos_service49_callers/summary.json`, prázdny `direct_call_candidates.csv` s hlavičkou a `ah49_immediate_candidates.csv` s jednou položkou.

Samostatne prebehlo zlúčenie XMS dát do `campaign_catalog`: 280 B nových field záznamov má s predošlou úniou 8 B prekryvu, preto prírastok je **272 B**, výsledná dátová únia **530 B**. Žiadny konflikt s 1 273 lokálnymi kódovými bajtmi. Úplná partition má 54 intervalov a 169 557 B v tejto kampani neposúdených. Kontrola pokrýva presne obraz 171 360 B. Nové DEEP VERIFIED 0 B, runtime testy 0; členstvo pôvodného PASS320 zostáva UNKNOWN.
