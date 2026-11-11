# PASS1: CRT kalendárna tabuľka

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Pole **DS:2488..24A2**, obraz **[29B98,29BB2)**, má 13 signed WORDov, spolu **26 B**. Počiatočné hodnoty sú `-1,30,58,89,119,150,180,211,242,272,303,333,364`: presne `sum(bežné_dĺžky_mesiacov[:index])-1` pre indexy 0..12. Status PARTIAL.

Na 14A45..14A4D kód použije `SI=(month-1)*2` a pridá WORD DS:[SI+2488h] ku dňu v mesiaci. Pre platný mesiac 1..12 a deň tak vzniká zero-based deň v roku. Na 14A54 testuje low2 bity ročného rozdielu (predtým year-1980), a ak sú nulové a mesiac>2, zvýši deň v roku o 1. Ide o lokálnu deliteľnosť štyrmi, **nie dôkaz kompletného gregoriánskeho century pravidla alebo správnosti pre ľubovoľný rok**.

Ďalšie čítania na 14C25/14C35 používajú bázu 2488h a posunutú bázu 248Ah v mesačných výpočtoch. Ich plný dátumový/DST kontrakt ani validácia vstupného mesiaca sa touto dávkou neuzatvárajú. Typ sa opiera o presnú matematickú štruktúru aj vykonateľné indexed čítania, nie iba o podobnosť čísel.

## Susedný kandidát zostáva CLASSIFIED ONLY

Pole **[29B7E,29B98)** má presné kumulatívne hodnoty priestupného roku: `-1,30,59,90,120,151,181,212,243,273,304,334,365`. Skript overil aj jeho vzorec, ale zatiaľ chýba konkrétna spotreba tejto bázy. Preto sa tento susedný rozsah **nepromuje**. Hodnoty a status sú oddelene v `calendar_entries.csv`.

## Reprodukcia a metriky

`audit_pass1_calendar.py IMAGE DECODER_DIR OUT` kontroluje SHA, všetkých 26 WORDov oboch matematických tabuliek, spotrebiteľské bajty a nezávisle dekóduje dve okná. `data_fields.csv` obsahuje iba 26 B bežného roka s doloženými xrefs. `promote_pass1_fields.py` používa predchádzajúcu mapu `pass1_display_selector/noncode_intervals.csv`.

Nových **26 B** prešlo z CLASSIFIED ONLY do PARTIAL. Aktuálne **PARTIAL 50 669 B, CLASSIFIED ONLY 6 582 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 50 643 / 6 608 / 44 / 0 B. Netypované relokačné PARTIAL bajty zostávajú 2 B. Nový prirodzený runtime ani replay sa nevykonal; enumerácia tabuliek nie je runtime test.

DOSBox-X plán: dátumové vstupy vrátane február/marec, rovnaký výpočet v bežnom/priestupnom roku, mesiace mimo platného rozsahu iba v izolovanej kópii stavu. Ďalší krok: spotreba susedného kandidáta a ďalšie CRT static data; výsledok neuzatvára časové API ani celú CRT.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 209 polí/36 zdrojov; calendar table | 2 relokačné B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | 13 WORD cumulative days and indexed consumers | writeri/lifetime | pointer watchpointy |
| Funkcie / ASM / CFG | 90 % | N/A | 34 rozsahov, 1 150 inštrukcií | kontrakty/dosiahnuteľnosť | caller stopy |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | staršie PIT dôkazy zachované | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | bit reversal začlenený | clipping/orientácia | payload spotrebiteľ |
| GUARD / bossovia | 93 % | N/A | nominálne pole 100×26 | AI/lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie/sloty | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | 60 počiatočných UI textov | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | mapové/flagové rozsahy | LOAD parity | párový stav |
| Windows Win16 | 92 % | N/A | staršie NE dôkazy zachované | callback DS/import ABI | runtime selektory |

