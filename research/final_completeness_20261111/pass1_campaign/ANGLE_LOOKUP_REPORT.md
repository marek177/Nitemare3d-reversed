> Boundary correction verified against Win16: trailing D12B byte excluded. See WIN110_TRIG_HELPERS_REPORT.md.

# Celočíselný pomerový výpočet uhla

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Funkcia **0C7D:08C6**, obraz **[D096,D12B)**, má 149 B / 62 nezávisle dekódovaných inštrukcií. Nepridáva nové NON-CODE bajty: používa už analyzovanú saturovanú tabuľku T na DS:1954.

## Presný lokálny algoritmus

FAR ABI má dva signed WORD vstupy v SS:[BP+6] a SS:[BP+8], tu označené n,d. Význam herných osí sa zatiaľ neuzatvára. Kód sign-extenduje n do EAX, posunie o 10, a pri d!=0 vykoná signed 32-bitové delenie sign-extended d. Následne vytvorí absolútnu hodnotu pomeru a lineárne hľadá prvú T[i]>=ratio. Hľadanie skončí tiež pri i==91, bez čítania T[91]. Pri d==0 sa nastaví i=90 a delenie sa preskočí.

```text
if d == 0:
    i = 90
else:
    ratio = abs(trunc_toward_zero((signed32(n)*1024)/d))
    i = 0
    while i < 91 and T[i] < ratio:
        i += 1
if n < 0:
    result = i + 180 if d >= 0 else 360 - i
else:
    result = 180 - i if d > 0 else i
return result
```

Pre signed WORD n,d je numerator po posune v signed 32-bitovom rozsahu. Pri n=-32768,d=-1 nedochádza k 32-bitovému IDIV overflow; delenie nulou obchádza explicitná vetva. Tieto aritmetické vlastnosti nie sú dôkazom správnosti herných callerov či vhodnosti výsledku.

## Hraničné výsledky

| n,d | Lookup index | Výsledok |
|---|---:|---:|
| 0,0 | 90 | 90 |
| 0,+1 | 0 | 180 |
| 0,-1 | 0 | 0 |
| +1,0 | 90 | 90 |
| -1,0 | 90 | 270 |
| 32767,1024 | 89 | 91 |
| 32767,1 | 91 | 89 |
| -32768,1024 | 91 | 271 |

Tabuľka má T[89]=T[90]=32767. Prvý splňujúci index pre ratio=32767 je preto 89; pre ratio>32767 žiadny prvok nevyhovuje a výsledný index je 91. Táto hrana sa nesmie nahradiť clampom na 90 pri rekonštrukcii. Nie je doložené, že všetky také páry nastávajú v prirodzenom gameplay; výsledok je lokálny potvrdený kontrakt, nie automatické označenie herného bugu.

AX je výsledok, SI/DI/BP/DS sa obnovujú alebo nemenia. FAR RET ponechá dva argumenty callerovi. EAX/EDX/ECX, BX a FLAGS môžu byť zmenené. Funkcia používa zdedený DS pre T; prirodzený DS všetkých callerov zostáva otvorený.

## Reprodukcia a replay

`audit_replay_angle_lookup.py IMAGE DECODER_DIR UNICORN_DIR OUT` kontroluje SHA a rozhodujúce division/search/quadrant bajty, nezávisle dekóduje celé telo a vytvára model z pôvodných T WORDov. **1 274 prípadov, 0 zlyhaní**: 637 unikátnych vstupných párov pri dvoch load bázach, vrátane 17×17 signed gridu, osí a všetkých tabuľkových prahov so znamienkovými kombináciami. V 132 prípadoch vznikol index 91. Overuje AX, SP/BP/SI/DI/DS a nemennosť T po dávke. Nejde o exhaustívny test všetkých 2^32 dvojíc ani prirodzený runtime.

Artefakty sú v `angle_lookup/instructions.csv`, `cases.json`, `summary.json`. Celý rozsah bol začlenený do centrálneho funkčného katalógu. Prijatý replay súčet kampane je **6 091**, prirodzené runtime testy zostávajú 0.

PASS1 mapa sa nemení: **54 164 B PARTIAL, 3 087 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**. DOSBox-X plán: prirodzené n,d, caller DS, použitá orientácia osí a následná normalizácia uhla. Ďalší krok: caller inventár a cross-version porovnanie helperov, bez predpokladu štandardnej atan2 sémantiky.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | data counts unchanged; integer angle contract | 2 relokačné B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | 150 B angle helper; 1274 replay cases | writeri/lifetime | pointer watchpointy |
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

