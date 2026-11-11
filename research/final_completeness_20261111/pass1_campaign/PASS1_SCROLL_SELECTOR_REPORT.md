# PASS1: indexovaný selector správ zvitkov

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Funkcia **083D:2804**, obraz **[ABD4,AC00)**, načíta WORD index z SS:[BP+6], vynásobí ho 4 modulo 16 bitov a vloží DWORD DS:[1174h+BX] ako argument helpera 11EE:278C. Ďalšie argumenty sú formát DS:15B4 a NEAR pointer lokálneho bufferu BP-100h. Výsledný SS buffer odovzdá message helperu 0D29:0750.

Potvrdené tri počiatočné FAR položky na DS:1174,1178,117C smerujú do default DS reťazcov: LF, tri medzery a úvodzovkami ohraničené `01532`, `080993`, `372535`. Ich segmentové WORDy majú skutočné EXEPACK relokácie a hodnotu 2771h. Formát je **`The scroll says:`**, LF, **`%s`**, NUL. Presné adresy, dĺžky a SHA všetkých siedmich objektov sú v `pass1_scroll_selector/data_fields.csv`.

```text
format_scroll(index):
    selected = DWORD_DS[(0x1174 + ((index*4)&0xffff)) & 0xffff]
    format(local_buffer, "The scroll says:\n%s", selected)
    message(SS:local_buffer)
```

Ide o potvrdenie konkrétnych počiatočných buniek pre indexy 0/1/2, **nie uzavretú kapacitu tabuľky alebo caller bounds**. Selector nemá lokálnu kontrolu. Dostupný priamy caller B7BE..B7C5 zero-extenduje BYTE objektu +1, ale v tomto okne nedokazuje, že hodnota je 0..2. Celý objektový dispatcher, producent subtype a nepriamych callerov treba ešte uzavrieť. 16-bitové násobenie umožňuje aliasy pri veľkých indexoch.

Funkcia má FAR návrat a buffer 100h v SS. Na konci vykoná LEAVE aj bez explicitného ADD SP po message volaní; LEAVE zahodí lokálne argumenty. To nie je dôkaz nekorektného zásobníka. Kompletný formátovací a prirodzený render kontrakt zostáva otvorený.

## Reprodukcia a metriky

`audit_pass1_scroll_selector.py IMAGE DECODER_DIR OUT` kontroluje SHA, segmentové relokácie, presné tri texty a formát, indexové bajty a nezávislé dekódovanie celého ohraničeného tela. `promote_pass1_fields.py` používa predchádzajúcu mapu `pass1_id_card_selector/noncode_intervals.csv`. Výstupy sú v `pass1_scroll_selector/`.

70 B objektov zahŕňa 6 segmentových bajtov už PARTIAL. Nových **64 B** pochádza z CLASSIFIED ONLY. Aktuálne **PARTIAL 49 931 B, CLASSIFIED ONLY 7 320 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 49 867 / 7 384 / 44 / 0 B. Netypované relokačné PARTIAL bajty klesli zo 44 na **38 B**, odlišné od 44 UNKNOWN bajtov. Nový prirodzený runtime ani replay sa nevykonal.

DOSBox-X plán: prirodzené subtype/index hodnoty, vybraný FAR pointer, výstup formátu a životnosť stack bufferu. Ďalší krok: dispatcher guard pre objektový subtype a ďalšie indexované porovnávacie texty; prirodzené caller bounds sa nepredpokladajú iba z počtu troch relokácií.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 171 polí/30 zdrojov; scroll selector | 38 relokačných B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | three initial FAR scroll fields; bounds open | writeri/lifetime | pointer watchpointy |
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

