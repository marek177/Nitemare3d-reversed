# PASS1: porovnávacie texty a CRT ASCII comparator

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Štyri počiatočné FAR bunky DS:110A/110E/1112/1116 obsahujú texty **333, 01532, 080993, 372535**. Segmenty sú 2771h so skutočnými EXEPACK relokáciami. Pointery a štyri NUL objekty majú spolu **40 B**, status PARTIAL. Presné rozsahy a SHA sú v `pass1_comparison_strings/data_fields.csv`.

Caller na 931A..933F načíta BYTE objektu, odčíta zero-extended AL helpera 00F7:0004, výsledok v BX vynásobí 4 a vloží DWORD DS:[BX+110Ah]. Následne vloží FAR pointer lokálneho SS textu a volá **11EE:3C68**. Výsledok porovná s nulou. Tieto štyri počiatočné bunky sú doložené lokálne pre indexy 0..3, ale prirodzené obmedzenie vypočítaného rozdielu nie je uzavreté. Počet štyri nie je vyhlásený za globálnu kapacitu iba podľa štyroch relokácií.

## Comparator 11EE:3C68

Obraz **[15B48,15B8D)** obsahuje FAR rutinu s dvoma FAR string argumentmi v SS:[BP+6] a SS:[BP+0A]. Prvý načíta do ES:BX, druhý do DS:SI. Pri rovnakých bajtoch pokračuje až po spoločné NUL. Pri rozdiele prevedie iba ASCII A..Z na a..z a porovná znova. Výstup AX je **-1,0,+1**, podľa unsigned poradia normalizovaných bajtov. Zachová DS, SI, BP, má FAR RET a argumenty ponechá callerovi. DX sa používa ako záloha SI, ostatné registre a FLAGS nie sú všeobecne zachované. Vyžaduje DF=0 pre postupné LODSB; CLD v rutine nie je.

```text
compare(first, second):
    loop:
        a = next_byte(first); b = next_byte(second)
        if a == b:
            if a == 0: return 0
            continue
        a = ascii_upper_to_lower(a)
        b = ascii_upper_to_lower(b)
        if a != b: return -1 if unsigned(a)<unsigned(b) else +1
```

Tento algoritmus nepredstavuje locale-aware Unicode porovnávanie. Identita konkrétnej značky CRT knižnice sa bez signatúr nepriraďuje.

## Reprodukcia a výsledky

`audit_pass1_comparison_strings.py IMAGE DECODER_DIR OUT` overuje identitu, pointery/texty/relokácie, caller výpočet a nezávisle dekóduje caller okno aj comparator. `promote_pass1_fields.py` použije predchádzajúcu mapu `pass1_scroll_selector/noncode_intervals.csv`.

`replay_crt_string_compare.py IMAGE UNICORN_DIR OUT` vykonal **32 prípadov bez zlyhania**: 16 dvojíc pri dvoch load segmentoch. Testuje prázdne reťazce, prefixy, case folding, interpunkciu, vysoké bajty a ignorovanie obsahu po NUL; kontroluje AX, DS/SI/BP/SP a nemennosť vstupných stringov. Stav je dosadený, DF=0; nejde o prirodzený runtime. Replay súčet kampane je teraz **2 635**, prirodzené runtime testy zostávajú 0.

Zo 40 B bolo 8 segmentových bajtov už PARTIAL. Nových **32 B** pochádza z CLASSIFIED ONLY. Aktuálne **PARTIAL 49 963 B, CLASSIFIED ONLY 7 288 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 49 931 / 7 320 / 44 / 0 B. Netypované relokačné PARTIAL bajty klesli na **30 B**.

DOSBox-X plán: prirodzené indexy, vstupný text z UI, DS a DF comparatora, rozhodnutie po nulovom/nenulovom výsledku. Ďalší krok: caller guards a zostávajúce pointery; lokálny comparator replay neuzatvára hernú autentizačnú či puzzle logiku.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 179 polí/31 zdrojov; comparison strings | 30 relokačných B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | 4 comparison fields; comparator 32 replay cases | writeri/lifetime | pointer watchpointy |
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

