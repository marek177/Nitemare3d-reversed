# PASS1: päť textov a prompt helper 0D29:0720

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Päť počiatočných FAR polí má konkrétny DWORD PUSH z DS a bezprostredné FAR volanie **0D29:0720**. Pointery a NUL texty tvoria **148 B**, status PARTIAL.

Texty sú `I have nothing left!`, `It's empty!`, `Let's find some dance music!`, `You already fixed it!` a dvojriadkový text o zablokovanej ceste. Presné texty, hranice, SHA, pointer sloty a caller bajty sú v `pass1_prompt_fields/message_references.csv` a `data_fields.csv`. Segmentové WORDy majú skutočné EXEPACK relokácie s počiatočnou hodnotou 2771h.

## Helper a hranice kontraktu

Celé ohraničené telo **[D9B0,D9DF)** má 47 B / 20 nezávisle dekódovaných inštrukcií. FAR string argument v SS:[BP+6] odovzdá spolu s adresou lokálneho rámca helperu 0D29:052E. Následne bez podmienky volá input helper **06B0:03BE**, uloží AL do lokálneho BYTE a CBW ho znamienkovo rozšíri do AX. Toto odlišuje helper 0720 od už analyzovaného 0750, kde čakanie závisí od globálneho stavu a konkrétnych vstupných bajtov.

AX sa použije ako signed index do BYTE DS:[2369h+BX]. Ak je nastavený bit 02h, AL sa zníži o 20h; inak sa vráti pôvodný lokálny BYTE v AL. Presný význam klasifikačného bitu a rozsah všetkých input hodnôt ešte nie sú uzavreté. AH po úprave AL sa znovu nenormalizuje, preto všeobecný výstup sa dokumentuje ako AL a vedľajšie účinky, nie čistý unsigned WORD kód. Funkcia má LEAVE/RETF a argument ponechá callerovi. DS je zdedený, SI/DI sa v tomto tele explicitne nemenia, ale podvolania nemajú v tejto dávke uzavreté ABI.

```text
render_message(text, local_state)
key_byte = input_helper()
idx = signed8(key_byte)
if BYTE_DS[0x2369 + idx] & 2:
    AL = (key_byte - 0x20) & 0xff
else:
    AL = key_byte
return_far
```

Dôkaz odovzdania pointera a následného input volania neuzatvára prirodzené vykreslenie, aktuálny DS ani všetky návratové cesty input helpera. Konkrétna textová situácia v hre sa neodvodzuje iba zo slov správy.

## Reprodukcia a metriky

`audit_pass1_prompt_fields.py IMAGE INVENTORY DECODER_DIR OUT` kontroluje SHA, pôvodné caller bajty/CS:IP, FAR páry, relokácie a textové terminátory; nezávisle dekóduje celé telo 0720. `promote_pass1_fields.py` používa predchádzajúcu mapu `pass1_comparison_strings/noncode_intervals.csv`. Centrálna kontrola začlenila celé telo ako samostatný funkčný rozsah a overila neprítomnosť konfliktov.

Z 148 B bolo 10 segmentových bajtov už PARTIAL. Nových **138 B** pochádza z CLASSIFIED ONLY. Aktuálne **PARTIAL 50 101 B, CLASSIFIED ONLY 7 150 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 49 963 / 7 288 / 44 / 0 B. Netypované relokačné PARTIAL bajty klesli na **20 B**.

Centrálny katalóg má 35 funkčných rozsahov, 1 170 inštrukcií / 2 713 B kódu, 50 929 B typovaných dát. Prijatý replay súčet zostáva 2 635; nový prirodzený runtime ani replay sa nevykonal. DOSBox-X plán: caller DS, pointer a text, input AL a klasifikačný BYTE vrátane vysokých hodnôt. Ďalší krok: input helper, klasifikačná tabuľka a zostávajúce pointery.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 189 polí/32 zdrojov; prompt fields | 20 relokačných B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | 5 FAR prompt fields and bounded input helper | writeri/lifetime | pointer watchpointy |
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

